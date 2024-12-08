# Flask Voting System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask 2.3.3](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-orange.svg)](https://www.sqlalchemy.org/)

A secure and user-friendly web-based voting system built with Flask, featuring user authentication, real-time vote counting, and an admin dashboard.

## Features

- Secure user authentication and registration
- Real-time vote counting and results
- Admin dashboard for election management
- Responsive design for all devices
- Built-in security features

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone and setup:
```bash
git clone https://github.com/yourusername/flask-voting-system.git
cd flask-voting-system
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Initialize database:
```bash
flask db upgrade
```

5. Run the application:
```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

## Security

- Store sensitive data in `.env` (never commit to version control)
- Use strong passwords for admin accounts
- Keep dependencies updated
- Configure all security-related environment variables in production

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, open an issue first.

## License

This project is licensed under the MIT License - see the LICENSE file for details.