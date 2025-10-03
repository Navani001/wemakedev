import re
import random
import logging
import aiohttp
import asyncio
import sys
from datetime import datetime
from typing import Annotated, Literal
from enum import Enum
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    ChatContext,
    FunctionTool,
    JobContext,
    JobProcess,
    ModelSettings,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
)
from livekit.rtc import ParticipantKind
from livekit.plugins import openai, deepgram, elevenlabs, silero


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

# Initialize these ONCE at module level to avoid reloading
try:
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    pc = Pinecone(api_key="pcsk_7DtsGY_7WW3N5kLpmNdmezDrhnB1aDY8ADcWPdGBmecMKFCobuiR4G2fisim1diAajFfxz")
    index = pc.Index("document-collection")
except Exception as e:
    logger.warning(f"Could not initialize Pinecone/SentenceTransformers: {e}")
    embedding_model = None
    pc = None
    index = None


class MyAgent(Agent):
    def __init__(self, instructions: str, tools: list[FunctionTool]) -> None:
        super().__init__(instructions=instructions, tools=tools)


@function_tool
async def get_weather(location: str):
    """Called when the user asks about the weather. This function will return the weather for the given location.
    
    Args:
        location: The location to get the weather for
    """
    # Clean the location string of special characters
    location = re.sub(r"[^a-zA-Z0-9]+", " ", location).strip()

    logger.info(f"getting weather for {location}")
    url = f"https://wttr.in/{location}?format=%C+%t"
    weather_data = ""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                weather_data = (f"The weather in {location} is {await response.text()}.")
                logger.info(f"weather data: {weather_data}")
            else:
                raise f"Failed to get weather data, status code: {response.status}"
            
    return weather_data


@function_tool
async def get_time():
    """called to retrieve the current local time"""
    return datetime.now().strftime("%H:%M:%S")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    
    @function_tool
    async def search_knowledge_base(question: str) -> str:
        """
        Search the knowledge base for information about the user's question.
        
        Args:
            question: The user's question to search for
        """
        try:
            logger.info(f"Searching knowledge base for: {question}")

            if not embedding_model or not index:
                return "Knowledge base is not available. Please ask general questions and I'll try to help."

            # Use the actual question for embedding
            query_embedding = embedding_model.encode(question).tolist()

            # Query Pinecone
            query_params = {
                "vector": query_embedding,
                "top_k": 3,
                "include_metadata": True
            }
            results = index.query(**query_params)

            logger.info(f"Found {len(results.matches)} results")

            # Extract context from results
            if not results.matches:
                return "I couldn't find any relevant information in the knowledge base for this question. Could you rephrase or ask something else?"

            contexts = [
                match.metadata['text']
                for match in results.matches
                if 'text' in match.metadata
            ]

            if not contexts:
                return "I found some results but they don't contain text information. Please contact support."

            # Return clear, structured response
            context = "\n\n".join(contexts)
            return f"Based on the knowledge base, here's what I found:\n\n{context}"

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return f"I encountered an error while searching: {str(e)}. Please try again or rephrase your question."

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")
    logger.info(f"participant.name: {participant.name}")
    logger.info(f"participant.attributes: {participant.attributes}")

    dg_model = "nova-2-general"
    if participant.kind == ParticipantKind.PARTICIPANT_KIND_SIP:
        # use a model optimized for telephony
        dg_model = "nova-2-phonecall"

    # Create agent with enhanced functionality
    agent = MyAgent(
        instructions="""You are a friendly and helpful course advisor assistant. Your role is to answer student questions using the knowledge base and provide weather and time information when needed.

IMPORTANT RULES:
1. For course-related questions: Call search_knowledge_base function ONCE with the user's question, then provide a complete answer based on the results
2. For weather questions: Use get_weather function
3. For time questions: Use get_time function
4. Be conversational, friendly, and concise
5. Include page numbers when available in the context
6. Do NOT call the same function multiple times for the same question
7. Answer directly after getting the function result

Example workflow:
User: "What is the phone?"
You: Call search_knowledge_base("What is the phone") → Get results → Provide complete answer

Do NOT call functions repeatedly. One call per question.""",
        tools=[
            search_knowledge_base,
            get_weather,
            get_time
        ],
    )

    # Configure the session
    session = AgentSession(
        llm=openai.LLM.with_cerebras(
            model="llama-3.3-70b",
            temperature=0.7,
        ),
        stt=deepgram.STT(model=dg_model),
        tts=deepgram.TTS(),
        vad=ctx.proc.userdata["vad"]
    )

    usage_collector = metrics.UsageCollector()

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Summary Usage: {summary}")

    # At shutdown, generate and log the summary from the usage collector
    ctx.add_shutdown_callback(log_usage)

    logger.info("Starting agent session")
    await session.start(agent, room=ctx.room)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            agent_name="inbound-agent",
        ),
    )
