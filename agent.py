import re
import random
import logging
import aiohttp
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
    FunctionTool,
    function_tool,
)
from livekit.rtc import ParticipantKind
from livekit.plugins import openai, deepgram, elevenlabs, silero, turn_detector


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

# Lazy loading variables
embedding_model = None
pc = None
index = None

def initialize_knowledge_base():
    """Initialize Pinecone and embedding model when needed"""
    global embedding_model, pc, index
    
    if embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            from pinecone import Pinecone
            
            logger.info("Initializing embedding model and Pinecone client...")
            embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            pc = Pinecone(api_key="pcsk_7DtsGY_7WW3N5kLpmNdmezDrhnB1aDY8ADcWPdGBmecMKFCobuiR4G2fisim1diAajFfxz")
            index = pc.Index("document-collection")
            logger.info("Knowledge base initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            raise

async def get_questionAnswer_info(question: str) -> str:
    """
    Get detailed information to answer a student's question by searching the knowledge base.
    """
    try:
        # Initialize knowledge base if not already done
        initialize_knowledge_base()
        
        logger.info(f"Searching knowledge base for: {question}")

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

def get_time() -> str:
    """Get the current local time"""
    return datetime.now().strftime("%H:%M:%S")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
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

    # This project is configured to use Deepgram STT, OpenAI LLM and ElevenLabs TTS plugins
    # Other providers exist like Cerebras, Cartesia, Groq, Play.ht, Rime, and more
    # Learn more and pick the best one for your app:
    # https://docs.livekit.io/agents/plugins
    from livekit.agents import Agent, AgentSession
    
    agent = Agent(
        instructions=(
            "You are a friendly and helpful course advisor assistant. Your interface with users will be voice. "
            "Your role is to answer student questions using the knowledge base. "
            "\n\nCRITICAL RULES:\n"
            "1. When a user asks a question, call get_questionAnswer_info EXACTLY ONCE with their question\n"
            "2. Wait for the response and use it to answer the user\n"
            "3. NEVER call the same function again if you already have results\n"
            "4. If the user asks a follow-up about the same topic, use the information you already have\n"
            "5. Only call the function again if the user asks a COMPLETELY NEW question\n"
            "6. Be conversational, friendly, and concise in your responses\n"
            "7. Add page references if the data are present in context - this is priority\n"
            "\nWORKFLOW:\n"
            "- User asks question → Call function once → Present answer clearly\n"
            "- User asks follow-up → Answer using existing context (NO new function call)\n"
            "- User asks new question → Call function once with new question"
        ),
        tools=[
            function_tool(
                get_questionAnswer_info,
                name="get_questionAnswer_info", 
                description="Search the knowledge base for information about the user's question"
            ),
            function_tool(
                get_time,
                name="get_time",
                description="Get the current local time"
            ),
        ],
    )

    session = AgentSession(
        llm=openai.LLM.with_cerebras(
            model="llama-3.3-70b",
            temperature=0.7,
        ),
        stt=deepgram.STT(model=dg_model),
        tts=deepgram.TTS(),
        vad=ctx.proc.userdata["vad"],
    )

    usage_collector = metrics.UsageCollector()

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Summary Usage: {summary}")

    # At shutdown, generate and log the summary from the usage collector
    ctx.add_shutdown_callback(log_usage)

    # Start the agent session
    await session.start(agent=agent, room=ctx.room)

    # The agent greeting when the user joins
    await session.say("Hello! I'm your course advisor assistant. I can help answer questions about your courses using our knowledge base. What would you like to know?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            agent_name="inbound-agent",
        ),
    )
