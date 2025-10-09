# AI Review Analyzer - FastAPI Version

A SaaS web application that provides AI-generated analytical reports based on customer reviews for restaurants, cafes, and service companies.

**Live Demo:** https://easy-owls-fold.lindy.site

## Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Jinja2 Templates + Custom CSS
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Authentication:** JWT tokens with HTTP-only cookies
- **Password Hashing:** Passlib with bcrypt

## Features

- ✅ Clean, professional design with white background and black accents
- ✅ User authentication (signup/login) with secure password hashing
- ✅ User dashboard for submitting analysis requests
- ✅ Order history tracking with status management
- ✅ Pricing page with 3 tiers (Basic, Pro, Enterprise)
- ✅ Homepage with hero section and 3-step process
- ✅ Privacy Policy and Terms of Service pages
- ✅ Responsive navigation and footer
- ✅ PostgreSQL database integration

## Project Structure

```
ai-review-analyzer-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication utilities
│   ├── static/
│   │   └── css/
│   │       └── style.css    # Custom CSS styling
│   └── templates/           # Jinja2 templates
│       ├── base.html        # Base template with nav/footer
│       ├── index.html       # Homepage
│       ├── pricing.html     # Pricing page
│       ├── login.html       # Login page
│       ├── signup.html      # Signup page
│       ├── dashboard.html   # User dashboard
│       ├── privacy.html     # Privacy policy
│       └── terms.html       # Terms of service
├── init_db.py               # Database initialization script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
└── README.md               # This file
```

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 12+

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-review-analyzer-fastapi
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database:**
   ```bash
   createdb ai_review_analyzer_fastapi
   ```

5. **Configure environment variables:**
   
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/ai_review_analyzer_fastapi
   SECRET_KEY=your-secret-key-here-change-in-production
   ```

6. **Initialize the database:**
   ```bash
   python3 init_db.py
   ```

7. **Run the application:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

8. **Access the application:**
   
   Open your browser and navigate to: http://localhost:8000

## Database Models

### User Model
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `password`: Hashed password (bcrypt)
- `created_at`: Timestamp

### Order Model
- `id`: Primary key
- `user_id`: Foreign key to User
- `business_name`: Name of the business to analyze
- `business_address`: Address of the business
- `status`: Order status (pending, processing, completed)
- `created_at`: Timestamp

## API Routes

### Public Routes
- `GET /` - Homepage
- `GET /pricing` - Pricing page
- `GET /login` - Login page
- `POST /login` - Login form submission
- `GET /signup` - Signup page
- `POST /signup` - Signup form submission
- `GET /privacy` - Privacy policy
- `GET /terms` - Terms of service

### Protected Routes (Require Authentication)
- `GET /dashboard` - User dashboard
- `POST /dashboard` - Submit new analysis request
- `GET /logout` - Logout user

## Authentication

The application uses JWT tokens stored in HTTP-only cookies for authentication:

1. User signs up or logs in
2. Server generates JWT token with user email
3. Token is stored in HTTP-only cookie
4. Protected routes verify token from cookie
5. User information is retrieved from database

## Deployment

### Production Considerations

1. **Environment Variables:**
   - Use strong, random SECRET_KEY
   - Use production database credentials
   - Never commit .env file to version control

2. **Database:**
   - Use managed PostgreSQL service (AWS RDS, DigitalOcean, etc.)
   - Enable SSL connections
   - Regular backups

3. **Security:**
   - Use HTTPS in production
   - Set secure cookie flags
   - Enable CORS properly
   - Rate limiting on authentication endpoints

4. **Server:**
   ```bash
   # Production server with Gunicorn
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

5. **Reverse Proxy:**
   - Use Nginx or similar for SSL termination
   - Configure proper headers
   - Enable gzip compression

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Clearing Python Cache

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
```

## GitHub SSH Deploy Key

To push this code to GitHub, you'll need to add the SSH public key to your repository:

**SSH Public Key:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDQQGLz/b6lZYbHEdcsjsvRG3gpUpKscAiKa58UsvSws mstislaviv@gmail.com
```

**Steps to add deploy key:**

1. Go to your GitHub repository: https://github.com/mstislaviv/Review-Analyzer
2. Click on **Settings** → **Deploy keys** → **Add deploy key**
3. Title: "FastAPI Server Deploy Key"
4. Paste the public key above
5. Check "Allow write access" if you want to push from the server
6. Click "Add key"

**Or add as personal SSH key:**

1. Go to GitHub Settings: https://github.com/settings/keys
2. Click **New SSH key**
3. Title: "AI Review Analyzer FastAPI"
4. Paste the public key above
5. Click "Add SSH key"

## License

© 2025 AI Review Analyzer. All rights reserved.

## Contact

For questions or support, please contact: mstislaviv@gmail.com
