import requests

def send_anonymous_email_web(to_email):
    subject = "Message Anonyme de CyberTiger"
    message = (
        "Bonjour,\n\n"
        "Ce message a été envoyé anonymement depuis CyberTiger.\n"
        "Protège ta vie privée, reste vigilant.\n\n"
        "-- L’équipe CyberTiger"
    )

    payload = {
        "to": to_email,
        "subject": subject,
        "text": message
    }

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post("https://anonymousemail.me/", data=payload, headers=headers, timeout=15)

        if "Thanks" in response.text or response.status_code == 200:
            return {"success": True, "message": "Email envoyé anonymement avec succès !"}
        else:
            return {"success": False, "message": "Échec de l'envoi. Le service est peut-être indisponible."}

    except Exception as e:
        return {"success": False, "message": f"Erreur réseau : {e}"}
