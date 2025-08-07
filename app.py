from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import openai
import socket
import whois as whois_lib
import requests

# === INIT APP ===
app = Flask(__name__)
app.secret_key = 'cybertiger-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

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

# === AUTH ===

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

# === PROFILE ===

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
    flash("💬 Historique supprimé.")
    return redirect(url_for('chat'))

# === CHATGPT ===

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    history = Message.query.filter_by(user_id=current_user.id).all()
    response = None

    if request.method == 'POST':
        user_input = request.form.get("user_input")
        db.session.add(Message(user_id=current_user.id, role="user", content=user_input))
        db.session.commit()

        history_msgs = [{"role": m.role, "content": m.content} for m in history]

        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es l’assistant OSINT & cybersécurité de CyberTiger."},
                    *history_msgs,
                    {"role": "user", "content": user_input}
                ]
            )
            assistant_reply = completion.choices[0].message.content
            db.session.add(Message(user_id=current_user.id, role="assistant", content=assistant_reply))
            db.session.commit()
            response = assistant_reply

        except Exception as e:
            response = f"Erreur GPT : {e}"

    return render_template("tools/chat.html", history=history, response=response, pseudo=current_user.pseudo)

# === WHOIS TOOL ===

@app.route('/whois', methods=['GET', 'POST'])
@login_required
def whois():
    result = None
    if request.method == 'POST':
        domain = request.form.get('domain')
        try:
            w = whois_lib.whois(domain)
            ip = socket.gethostbyname(domain)
            result = {'whois': w, 'ip': ip, 'domain': domain}
        except Exception as e:
            result = {'error': str(e)}
    return render_template('tools/whois.html', result=result)

# === USERNAME CHECKER ===

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitch": "https://www.twitch.tv/{}"
}

@app.route('/usercheck', methods=['GET', 'POST'])
@login_required
def usercheck():
    username = request.form.get('username') if request.method == 'POST' else None
    results = {}
    if username:
        for platform, url in PLATFORMS.items():
            full_url = url.format(username)
            try:
                r = requests.get(full_url, timeout=5)
                results[platform] = r.status_code == 200
            except:
                results[platform] = None
    return render_template("tools/usercheck.html", username=username, results=results)

# === EMAIL BREACH ===

@app.route('/emailbreach', methods=['GET', 'POST'])
@login_required
def emailbreach():
    email = request.form.get('email') if request.method == 'POST' else None
    hibp = f"https://haveibeenpwned.com/unifiedsearch/{email}" if email else None
    leakcheck = f"https://leakcheck.io/search?query={email}" if email else None
    dehashed = f"https://www.dehashed.com/search?query={email}" if email else None
    return render_template("tools/emailbreach.html", email=email, hibp=hibp, leakcheck=leakcheck, dehashed=dehashed)

# === INIT DB ===

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
