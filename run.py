
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yanbel0706'  # Remplacez par une clé secrète sécurisée
socketio = SocketIO(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Fichier SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

# Modèle pour les utilisateurs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec les messages
    messages = db.relationship('Message', backref='author', lazy=True)
    # Relation avec les chambres via la table intermédiaire RoomUser
    rooms = db.relationship('Room', secondary='room_user', lazy='subquery')
# Modèle pour les messages

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    room = db.relationship('Room', backref=db.backref('messages', lazy=True))  # Relation avec Room
    user = db.relationship('User', lazy=True)  # Relation avec User


# Modèle pour les rooms
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', secondary='room_user', backref='rooms_in_user', lazy='subquery')

class RoomUser(db.Model):
    __tablename__ = 'room_user'
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

# Générer un code de room aléatoire
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# Créer la base de données et les tables
with app.app_context():
    db.create_all()  # Crée toutes les tables si elles n'existent pas



@app.route('/')
def index():
    return redirect(url_for('login'))  # Redirection vers la page de création/join de room

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Cet utilisateur existe déjà !', 'danger')
            return redirect(url_for('signup'))

        # Hacher le mot de passe
        hashed_password = generate_password_hash(password)

        # Créer un nouvel utilisateur
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Inscription réussie ! Vous pouvez vous connecter maintenant.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Trouver l'utilisateur
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Connexion réussie !', 'success')
            return redirect(url_for('create_or_join_room'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'danger')

    return render_template('login.html')


@app.route('/create_or_join_room', methods=['GET', 'POST'])
def create_or_join_room():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Pour la création d'une room
        if 'create_room' in request.form:
            room_name = request.form['room_name']
            room_code = generate_room_code()

            # Créer la room
            new_room = Room(name=room_name, code=room_code)
            db.session.add(new_room)
            db.session.commit()

            # Associer l'utilisateur à la room
            room = Room.query.filter_by(code=room_code).first()
            user = User.query.get(session['user_id'])
            room.users.append(user)
            db.session.commit()

            flash(f'Room créée avec le code : {room_code}', 'success')
            return redirect(url_for('chat', room_code=room_code))  # Redirection vers la room

        # Pour rejoindre une room
        elif 'join_room' in request.form:
            room_code = request.form['room_code']
            room = Room.query.filter_by(code=room_code).first()

            if room:
                user = User.query.get(session['user_id'])
                # Vérifier si l'utilisateur n'est pas déjà dans la room
                if user not in room.users:
                    room.users.append(user)
                    db.session.commit()
                    flash(f'Vous avez rejoint la room avec le code : {room_code}', 'success')
                    return redirect(url_for('chat', room_code=room_code))  # Redirection vers la room
                else:
                    flash('Vous êtes déjà dans cette room.', 'danger')
            else:
                flash('Code de room invalide', 'danger')

    return render_template('create_or_join_room.html')
       

@app.route('/chat/<room_code>', methods=['GET', 'POST'])
def chat(room_code):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    room = Room.query.filter_by(code=room_code).first()
    if room:
        if request.method == 'POST':
            message_content = request.form['message']
            user = User.query.get(session['user_id'])

            # Ajouter le message dans la base de données
            message = Message(user_id=user.id, room_id=room.id, content=message_content)
            db.session.add(message)
            db.session.commit()

        # Afficher les messages de la room
        messages = Message.query.filter_by(room_id=room.id).all()
        return render_template('chat.html', room=room, messages=messages)
    else:
        flash('Room not found', 'danger')
        return redirect(url_for('create_or_join_room'))

@socketio.on('message')
def handle_message(msg):
    user = db.session.get(User, session['user_id']) # Récupérer l'utilisateur actuel
    room_code = msg.get('room_code')  # Assurez-vous que la room_code soit envoyée avec le message
    room = Room.query.filter_by(code=room_code).first()  # Trouver la room à partir du code

    if room:
        # Créer un nouveau message et l'ajouter à la base de données
        message = Message(user_id=user.id, room_id=room.id, content=msg['message'])
        db.session.add(message)
        db.session.commit()

        # Émettre le message à tous les clients connectés à la room
        socketio.emit('message', {
            'user': user.username,
            'message': msg['message'],
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }, room=room_code)  # Diffuser le message à la room
    else:
        print("Room not found.")


if __name__ == '__main__':
    socketio.run(app, debug=True)
