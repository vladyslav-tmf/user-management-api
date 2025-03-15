# 👥 User Management API

A RESTful API for user management built with Flask, SQLAlchemy, and PostgreSQL.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [Environment Variables](#-environment-variables)
- [API Documentation](#-api-documentation)
- [Database Structure](#-database-structure)
- [Testing](#-testing)
- [API Examples](#-api-examples)

## 🌐 Overview

User Management API is a secure, scalable REST API service for managing user data. It provides endpoints for CRUD operations on user information, with robust validation, password hashing, and a clean separation of concerns.

## ✨ Features

- User CRUD operations (Create, Read, Update, Delete)
- Secure password handling with bcrypt hashing
- Data validation with Marshmallow
- PostgreSQL database integration
- Database migrations with Flask-Migrate
- RESTful API design
- Swagger API documentation
- Comprehensive test suite
- Docker containerization

## 🛠 Tech Stack

- **Python 3.12**
- **Flask 3.1.0**
- **SQLAlchemy & Flask-SQLAlchemy**
- **Flask-Migrate (Alembic)**
- **Marshmallow & Flask-Marshmallow**
- **Flask-Bcrypt**
- **Flask-RESTx (Swagger documentation)**
- **PostgreSQL**
- **Docker & Docker Compose**
- **Poetry (dependency management)**

## 💻 System Requirements

- Python 3.12+
- PostgreSQL
- Docker & Docker Compose (for containerized setup)

## 🚀 Installation

Follow these steps to set up and run the project:

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vladyslav-tmf/user-management-api.git
   cd user-management-api
   ```

2. Create and activate virtual environment:
    - Linux/Mac:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - Windows:
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

3. Install dependencies with Poetry:
   ```bash
   # If you don't have Poetry installed:
   # Option 1: Install with pip
   pip install poetry
   
   # Option 2: Install with pipx (recommended for global installation)
   # python -m pip install pipx
   # pipx install poetry
   
   # Option 3: Follow the official installation guide
   # https://python-poetry.org/docs/#installation
   
   # Install project dependencies
   poetry install
   ```

4. Create .env file:
   ```bash
   cp .env.sample .env
   # Edit .env file with your configurations
   ```

5. Apply database migrations:
   ```bash
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   flask run
   # Or alternatively:
   python run.py
   ```

The application will be available at:
- API: http://localhost:5000/api/v1/users/
- API Documentation: http://localhost:5000/api/docs/

### Docker Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vladyslav-tmf/user-management-api.git
   cd user-management-api
   ```

2. Create .env file:
   ```bash
   cp .env.sample .env
   # The default values in .env.sample are configured for Docker
   ```

3. Build and run containers:
   ```bash
   docker-compose up -d
   ```

The application will be available at:
- API: http://localhost:5000/api/v1/users/
- API Documentation: http://localhost:5000/api/docs/

## 🔐 Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# PostgreSQL Database settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db  # Use 'localhost' for local setup
POSTGRES_PORT=5432
POSTGRES_DB=users

# Flask settings
FLASK_APP=run.py
FLASK_DEBUG=1
```

## 📚 API Documentation

The API documentation is available in Swagger UI format at `/api/docs/` when the server is running. It provides detailed information about:

- Available endpoints
- Request/Response formats
- Required parameters
- Response codes

### API Endpoints

- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{id}` - Get user by ID
- `POST /api/v1/users/` - Create a new user
- `PUT /api/v1/users/{id}` - Update an existing user
- `DELETE /api/v1/users/{id}` - Delete a user

## 🗄 Database Structure

The project uses PostgreSQL and includes the following main model:

- **User**:
  - `id`: Integer, primary key
  - `name`: String(255), required
  - `email`: String(255), required, unique, indexed
  - `_password`: String(255), required (stored as a bcrypt hash)
  - `created_at`: DateTime, automatically set on creation

## 🧪 Testing

The project includes comprehensive tests for models, routes, and schemas.

Run tests using:
```bash
# Local environment
python -m pytest

# Check test coverage
python -m pytest --cov=app

# Docker environment
docker-compose exec app python -m pytest
```

## 📝 API Examples

### Create a User
```bash
curl -X POST http://localhost:5000/api/v1/users/ \
    -H "Content-Type: application/json" \
    -d '{
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123"
    }'
```

### Get All Users
```bash
curl -X GET http://localhost:5000/api/v1/users/
```

### Get User by ID
```bash
curl -X GET http://localhost:5000/api/v1/users/1
```

### Update User
```bash
curl -X PUT http://localhost:5000/api/v1/users/1 \
    -H "Content-Type: application/json" \
    -d '{
        "name": "John Updated",
        "email": "john.updated@example.com",
        "password": "NewPassword123"
    }'
```

### Delete User
```bash
curl -X DELETE http://localhost:5000/api/v1/users/1
```
