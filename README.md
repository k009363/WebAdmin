# Dynamic Websites — Admin API

A Flask-based REST API for managing dynamic websites, users, domains, templates, and content. Built with MongoDB, JWT authentication, and role-based access control (RBAC).

## Features

- **User Management** - Create, update, and manage admin users with role-based permissions
- **Domain Management** - Register and manage multiple domains
- **Template System** - Manage website templates and configurations
- **Blog Management** - Create, edit, and publish blog posts
- **Contact Management** - Handle contact form submissions
- **Feedback System** - Collect and manage user feedback
- **Subscription Management** - Manage subscription plans and user subscriptions
- **Site Configuration** - Global site settings and customization
- **Notifications** - Send and track notifications
- **Authentication** - JWT-based authentication with secure token management
- **Rate Limiting** - Built-in rate limiting for API endpoints
- **Security Headers** - CORS, CSP, and other security headers configured

## Tech Stack

- **Framework**: Flask 3.0+
- **Database**: MongoDB 4.6+
- **Authentication**: Flask-JWT-Extended
- **Image Storage**: Cloudinary
- **Security**: bcrypt for password hashing
- **CORS**: flask-cors for cross-origin requests

## Prerequisites

- Python 3.8+
- MongoDB instance
- Cloudinary API credentials (for image uploads)
- Environment variables configured

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/k009363/WebAdmin.git
   cd WebAdmin
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will start on `http://localhost:5000` (default port) or the port specified in `.env`

## Environment Variables

```env
FLASK_ENV=development           # development or production
PORT=5000                       # Server port
JWT_SECRET_KEY=your-secret-key  # JWT signing key
MONGO_URI=mongodb://...         # MongoDB connection string
CLOUDINARY_URL=cloudinary://... # Cloudinary API credentials
ADMIN_USERNAME=admin            # Default admin username
ADMIN_PASSWORD=admin123         # Default admin password
ALLOWED_ORIGINS=*               # CORS allowed origins
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/register` - Register new admin user

### Users
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/:id` - Get user details
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Domains
- `GET /api/domains` - List all domains
- `POST /api/domains` - Register new domain
- `GET /api/domains/:id` - Get domain details
- `PUT /api/domains/:id` - Update domain
- `DELETE /api/domains/:id` - Delete domain

### Templates
- `GET /api/templates` - List all templates
- `POST /api/templates` - Create new template
- `GET /api/templates/:id` - Get template details
- `PUT /api/templates/:id` - Update template
- `DELETE /api/templates/:id` - Delete template

### Blog
- `GET /api/blog` - List all blog posts
- `POST /api/blog` - Create new blog post
- `GET /api/blog/:id` - Get blog post details
- `PUT /api/blog/:id` - Update blog post
- `DELETE /api/blog/:id` - Delete blog post

### Settings
- `GET /api/settings` - Get global settings
- `PUT /api/settings` - Update settings

### Contacts & Feedback
- `GET /api/contacts` - List contact submissions
- `POST /api/contacts` - Submit contact form
- `GET /api/feedback` - List feedback
- `POST /api/feedback` - Submit feedback

### Health Check
- `GET /api/health` - Health check endpoint

## Project Structure

```
.
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── middleware/             # Custom middleware
│   ├── rbac.py            # Role-based access control
│   └── permissions.py     # Permission decorators
├── routes/                # API route handlers
│   ├── auth.py
│   ├── users.py
│   ├── domains.py
│   ├── templates.py
│   ├── blog.py
│   ├── contacts.py
│   ├── feedback.py
│   ├── settings.py
│   ├── subscriptions.py
│   ├── notifications.py
│   └── site_config.py
├── services/              # Business logic and services
├── models/                # Database models
├── migrations/            # Database migration scripts
└── seed_data.py          # Initial data seeding

```

## Security Features

- **JWT Authentication** - Secure token-based authentication
- **RBAC** - Role-based access control for endpoints
- **Password Hashing** - bcrypt for secure password storage
- **Security Headers** - X-Content-Type-Options, X-Frame-Options, etc.
- **CORS** - Configurable cross-origin requests
- **Rate Limiting** - Protection against brute force and DDoS
- **HSTS** - HTTPS enforcement in production

## Development

### Running with debug mode
```bash
FLASK_ENV=development python app.py
```

### Database Migrations
```bash
python migrate_subscriptions.py
python migrate_admin_mapping.py
```

### Seed Data
```bash
python seed_data.py
```

## Deployment

For production deployment:

1. Set `FLASK_ENV=production`
2. Change `JWT_SECRET_KEY` to a strong secret
3. Configure MongoDB with authentication
4. Update `ALLOWED_ORIGINS` with actual domain(s)
5. Enable HTTPS/TLS
6. Use a production WSGI server (Gunicorn, uWSGI)

```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

All rights reserved.

## Support

For issues and questions, please open an issue on GitHub.
