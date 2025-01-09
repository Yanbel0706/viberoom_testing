```
# Chat Application - Flask

This project is a simple real-time chat application built with Flask, Socket.IO, and SQL, allowing users to join rooms, send and receive messages instantly. The app includes user authentication, dynamic message display, and real-time updates.

## Features

- **User Authentication**: Users can sign up, log in, and stay authenticated across sessions.
- **Room Management**: Users can create or join chat rooms using a code.
- **Real-time Messaging**: Messages are sent and received instantly within the room.
- **User Presence**: Displays which users are in the room, with real-time updates when a user joins or leaves.
- **Responsive Design**: The interface is responsive, adapting to both desktop and mobile devices.
- **Message Display**: User messages appear on the right for the sender and on the left for others.

## Technologies Used

- **Backend**:
  - Flask (Python Web Framework)
  - Flask-SocketIO (Real-time communication)
  - SQL (Database for user and message storage)
- **Frontend**:
  - HTML
  - CSS (for basic styling and layout)
  - JavaScript (for handling Socket.IO interactions)

## Installation

Follow these steps to get your development environment up and running.

### Prerequisites

Ensure you have the following installed on your machine:

- Python 3.x
- Flask
- Flask-SocketIO
- SQL database (such as SQLite, MySQL, or PostgreSQL)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/chat-app-flask.git
   cd chat-app-flask
```

