# Bus Complaint Management System

A comprehensive system for managing bus-related complaints and feedback.

## Tech Stack

### Frontend
- React.js (for dynamic UI)
- Material-UI (for styled components)
- Axios (for API requests)

### Backend
- Flask (Python web framework)
- MongoDB (Database)
- JWT (Authentication)
- Gmail SMTP (Email notifications)

## Features

### User Features
- User registration and authentication
- Submit complaints with categories
- Track complaints using unique IDs
- Receive email notifications for status updates
- Optional image upload for complaints

### Admin Features
- Comprehensive dashboard
- View and manage all complaints
- Filter complaints by category, status, and date
- Update complaint status
- Prioritize complaints
- Export complaint data

### Complaint Categories
- Bus Delays
- Overcrowding
- Driver Behavior
- Route Issues
- Accessibility Problems
- Bus Cleanliness
- Lost Items
- Fare Collection Problems
- Suggestions for Improvement

## Project Structure

```
/
├── frontend/           # React frontend application
├── backend/            # Flask backend application
├── docker/             # Docker configuration files
└── docs/              # Documentation files
```

## Setup Instructions

1. Clone the repository
2. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```
3. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

## Environment Variables

Create `.env` files in both frontend and backend directories with the following variables:

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000
```

### Backend (.env)
```
MONGODB_URI=your_mongodb_uri
JWT_SECRET_KEY=your_jwt_secret
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## License

MIT License