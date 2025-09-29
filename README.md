# Flask Application

A modern Flask web application with RESTful API endpoints, error handling, and proper project structure.

## Features

- RESTful API endpoints
- Error handling and custom error pages
- Environment-based configuration
- Health check endpoint
- CORS support ready
- CLI commands
- Production-ready setup with Gunicorn

## Project Structure

```
rag/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── .env               # Environment variables (create this)
├── .gitignore         # Git ignore rules
└── config.py          # Configuration settings
```

## Quick Start

### 1. Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### 2. Installation

Clone or download this project, then navigate to the project directory:

```bash
cd rag
```

### 3. Set up Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Environment Setup

Create a `.env` file in the project root:

```bash
# .env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000
```

### 6. Run the Application

```bash
# Development mode
python app.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health` - Returns application health status

### Users
- **GET** `/api/users` - Get all users
- **POST** `/api/users` - Create a new user
- **GET** `/api/users/<id>` - Get user by ID
- **PUT** `/api/users/<id>` - Update user by ID
- **DELETE** `/api/users/<id>` - Delete user by ID

### Examples

#### Get all users
```bash
curl http://localhost:5000/api/users
```

#### Create a new user
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

#### Health check
```bash
curl http://localhost:5000/api/health
```

## Configuration

The application uses environment-based configuration:

- `FLASK_ENV`: Set to `development` for development mode
- `SECRET_KEY`: Secret key for session management
- `PORT`: Port number (default: 5000)

## Development

### Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-flask

# Run tests
pytest
```

### Code Structure

- `app.py`: Main application file with routes and configuration
- `requirements.txt`: All Python dependencies
- `.env`: Environment variables (create this file)
- `config.py`: Configuration classes

### Adding New Routes

Add new routes in `app.py`:

```python
@app.route('/api/your-endpoint')
def your_function():
    return jsonify({'message': 'Hello World'})
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables for Production

```bash
export FLASK_ENV=production
export SECRET_KEY=your-super-secret-key
export PORT=5000
```

## Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t flask-app .
docker run -p 5000:5000 flask-app
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you've activated your virtual environment and installed dependencies
2. **Port Already in Use**: Change the PORT in your `.env` file or kill the process using the port
3. **Secret Key Error**: Make sure you've set the SECRET_KEY in your `.env` file

### Getting Help

- Check the Flask documentation: https://flask.palletsprojects.com/
- Create an issue in the repository for bugs or feature requests