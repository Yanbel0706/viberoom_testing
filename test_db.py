from run import app, db, User

with app.app_context():
    db.create_all()  # Créer les tables
    user = User(username='testuser')
    db.session.add(user)
    db.session.commit()

    users = User.query.all()
    print(users)
