from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import openai

# Init app
app = Flask(__name__)
app.secret_key = 'cybertiger-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

# DB & login
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# === MODELS ===
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pseudo = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    messages = db.relationship('Message', backref='user', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(10))
    content = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === ROUTES ===

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pseudo = request.form['pseudo']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(username=username).first():
            flash('Nom d’utilisateur déjà utilisé.')
            return redirect(url_for('register'))

        user = User(username=username, pseudo=pseudo, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Inscription réussie.")
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/profile')
@login_required
def profile():
    total_messages = Message.query.filter_by(user_id=current_user.id).count()
    return render_template('profile.html', user=current_user, total=total_messages)

@app.route('/reset_chat')
@login_required
def reset_chat():
    Message.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("💬 Historique du chat supprimé.")
    return redirect(url_for('chat'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('chat'))

        flash('Identifiants incorrects.')
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    history = Message.query.filter_by(user_id=current_user.id).all()
    response = None

    if request.method == 'POST':
        user_input = request.form.get("user_input")

        # Ajouter le message utilisateur à l'historique
        db.session.add(Message(user_id=current_user.id, role="user", content=user_input))
        db.session.commit()

        # Créer les messages à envoyer à OpenAI
        history_msgs = [{"role": m.role, "content": m.content} for m in Message.query.filter_by(user_id=current_user.id).all()]

        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es l'assistant CyberTiger, spécialisé en OSINT et cybersécurité."},
                    *history_msgs
                ]
            )
            assistant_reply = completion.choices[0].message.content

            # Enregistrer la réponse dans l'historique
            db.session.add(Message(user_id=current_user.id, role="assistant", content=assistant_reply))
            db.session.commit()
            response = assistant_reply

        except Exception as e:
            response = f"Erreur : {e}"

    return render_template("tools/chat.html", history=history, response=response, pseudo=current_user.pseudo)

# === DB INIT ===
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
