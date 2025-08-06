import whois
import socket

def get_whois_info(domain):
    try:
        # WHOIS
        w = whois.whois(domain)

        # IP Lookup
        try:
            ip = socket.gethostbyname(domain)
        except:
            ip = "Impossible de résoudre l’IP"

        # Résultat structuré pour affichage HTML
        return {
            "success": True,
            "domain": domain,
            "ip": ip,
            "registrar": w.registrar,
            "creation_date": w.creation_date,
            "expiration_date": w.expiration_date,
            "name_servers": w.name_servers,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
