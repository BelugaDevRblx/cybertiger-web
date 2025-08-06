from flask import Flask, render_template, request
import modules.domain_tools as domain_tools
import modules.anonymous_mailer as anonymous_mailer
import modules.usercheck as usercheck
import modules.emailbreach as emailbreach
import os

app = Flask(__name__)

# Accueil
@app.route('/')
def index():
    return render_template("index.html")

# WHOIS & DNS Lookup
@app.route('/whois', methods=['GET', 'POST'])
def whois_lookup():
    result = None
    if request.method == 'POST':
        domain = request.form.get('domain')
        result = domain_tools.get_whois_info(domain)
    return render_template("tools/whois.html", result=result)

# Email Anonyme
@app.route('/anonymous-email', methods=['GET', 'POST'])
def anonymous_email():
    status = None
    if request.method == 'POST':
        email = request.form.get('to_email')
        status = anonymous_mailer.send_anonymous_email_web(email)
    return render_template("tools/anonymous_email.html", status=status)

# Username Checker
@app.route('/usercheck', methods=['GET', 'POST'])
def user_checker():
    results = None
    if request.method == 'POST':
        username = request.form.get('username')
        results = usercheck.search_username_web(username)
    return render_template("tools/usercheck.html", results=results)

# Email Breach Checker (affichage de liens de vérification)
@app.route('/emailbreach', methods=['GET', 'POST'])
def email_breach():
    links = None
    if request.method == 'POST':
        email = request.form.get('email')
        links = emailbreach.generate_email_leak_links(email)
    return render_template("tools/emailbreach.html", links=links)

@app.route('/credits')
def credits():
    return render_template("credits.html")

# Lancement
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
