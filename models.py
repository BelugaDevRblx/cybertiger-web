from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pseudo = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    messages = db.relationship('Message', backref='user', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(10))  # user / assistant / system
    content = db.Column(db.Text)
