import requests

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://instagram.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Steam": "https://steamcommunity.com/id/{}",
    "Twitch": "https://www.twitch.tv/{}",
    "Medium": "https://medium.com/@{}",
    "Pinterest": "https://pinterest.com/{}",
    "SoundCloud": "https://soundcloud.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "DeviantArt": "https://deviantart.com/{}"
}

def search_username_web(username):
    found = []
    not_found = []
    errors = []

    for platform, url_template in PLATFORMS.items():
        url = url_template.format(username)
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                found.append((platform, url))
            elif r.status_code == 404:
                not_found.append(platform)
            else:
                errors.append((platform, f"Code {r.status_code}"))
        except Exception as e:
            errors.append((platform, str(e)))

    return {
        "username": username,
        "found": found,
        "not_found": not_found,
        "errors": errors
    }
