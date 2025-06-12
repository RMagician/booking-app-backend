# Booking App Backend

A FastAPI application for managing bookings, built with Python, Poetry, and MongoDB.

## Features

- FastAPI-based RESTful API
- MongoDB database integration with Motor
- Environment configuration using python-dotenv
- Health check endpoint
- Poetry for dependency management

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry
- MongoDB 

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/booking-app-backend.git
cd booking-app-backend
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Set up environment variables:
```
# Create a .env file in the project root with the following variables
MONGODB_URI=mongodb://localhost:27017
ENV=development
MONGODB_DB_NAME=booking_app
```

### Running the Application

```bash
poetry run python run.py
```

Or use the VS Code task:
```bash
# In VS Code
Ctrl+Shift+P > Tasks: Run Task > pipenv run
```

The API will be available at http://localhost:8000/api

API Documentation: http://localhost:8000/api/docs