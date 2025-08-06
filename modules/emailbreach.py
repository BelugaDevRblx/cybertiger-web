def generate_email_leak_links(email):
    return {
        "email": email,
        "hibp_url": f"https://haveibeenpwned.com/unifiedsearch/{email}",
        "leakcheck_url": f"https://leakcheck.io/search?query={email}",
        "dehashed_url": f"https://www.dehashed.com/search?query={email}"
    }
