# Job Board Application

A full-featured job board application built with Python, Flask, and SQLAlchemy. This application allows employers to post jobs and job seekers to browse and apply for positions.

## Features

- User authentication (register, login, password reset)
- Job posting and management
- Company profiles
- Job search with filters
- Application tracking
- RESTful API
- Email notifications

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite (included with Python)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd job-board
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   FLASK_APP=wsgi.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///app.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=1
   MAIL_USERNAME=your-account@example.invalid
   MAIL_PASSWORD=your-email-password
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

## Running the Application

1. Start the development server:
   ```bash
   flask run
   ```

2. Open your browser and go to:
   ```
   http://localhost:5000
   ```

## API Documentation

The API is available at `/api` and follows RESTful principles. You can use tools like Postman or cURL to interact with the API.

### Authentication

Most API endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-token>
```

### Available Endpoints

- `GET /api/jobs` - Get all jobs
- `POST /api/jobs` - Create a new job
- `GET /api/jobs/<id>` - Get a specific job
- `PUT /api/jobs/<id>` - Update a job
- `DELETE /api/jobs/<id>` - Delete a job
- `GET /api/jobs/<id>/applications` - Get applications for a job
- `POST /api/applications` - Submit a job application

## Project Structure

```
job-board/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   └── api/
│       ├── __init__.py
│       ├── jobs.py
│       └── auth.py
├── migrations/
├── static/
├── templates/
├── tests/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── wsgi.py
```

## Testing

To run the test suite:

```bash
pytest
```

## Deployment

For production deployment, consider using:
- Gunicorn or uWSGI as the application server
- Nginx as the reverse proxy
- PostgreSQL as the database
- Redis for caching and task queue

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
