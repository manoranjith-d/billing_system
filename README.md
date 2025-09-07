# FastAPI Billing System

A production-ready billing system built with FastAPI and PostgreSQL.

## Assumptions
- Done the ceil for total payable amount post tax - (Paisa/cents issue)
- Used SMTP Mail service (Gmail)
- Added Customer given denominsations into denomination Table
- Didn't added any authentication/logins for admin routes
- Used AI agents to work on the UI templates 

## How to use

- run the application and hit the billing page api from static module.
- http://127.0.0.1:8000/api/v1/

## Demo
- Find the SS on /Demo
- Video - https://drive.google.com/file/d/1s2wiCT3TIrbchZW8RDdNqdyTZ2GmSVT6/view?usp=sharing

## Features

- Product & Denomination management with CRUD operations under admin
- Dynamic billing calculation
- Asynchronous email notifications
- Customer purchase history
- Balance denomination calculation

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Virtual environment (recommended)

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd billing-system
```

2. Create and activate virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following content:

```env
DATABASE_URL=postgresql://postgres:mano@localhost:5432/billing_db
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password # generated from Google APP Password (16 char)
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

5. Initialize the database (optional - [automatically creates when app starts]):

```bash
python scripts/init_db.py
```

6. Seed initial data (optional - [automatically creates when app starts]):

```bash
python scripts/seed_data.py
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

```bash
pytest
```

## Project Structure

```
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── db/             # Database configuration
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── templates/      # HTML templates
├── scripts/            # Utility scripts
└── tests/              # Test cases
```

## License

MIT
