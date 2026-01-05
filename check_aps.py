import requests
import json
import os
from bs4 import BeautifulSoup
from notifier import send_email

# --- Config ---
URL = "https://candidat.francetravail.fr/formations/recherche?filtreEstFormationEnCoursOuAVenir=formEnCours&filtreEstFormationTerminee=formEnCours&ou=COMMUNE-97411&quoi=Agent+de+pr%C3%A9vention+et+de+s%C3%A9curit%C3%A9&range=0-9&tri=0"
STATE_FILE = "state.json"

# ---- Functions ----

def fetch_html(url):
	resp = requests.get(url, timeout=10)
	resp.raise_for_status()
	return resp.text

def parse_formations(html):
	soup = BeautifulSoup(html, "html.parse")
	results = []
	# Each result starts with heading  ##
	for heading in soup.find_all(["h2", "h3"]):
		title = heading.get_text(strip=True)
		if "Agent de prévention et de sécurité" in title:
			# find next text nodes or siblings for date
			next_text = heading.find_next(text=True)
			if next_text:
				results.append(f"{title} | {next_text.strip()}")
			else:
				results.append(title)
	return results

def load_state():
	if os.path.exists(STATE_FILE):
		with open(STATE_FILE, "r") as f:
			return json.load(f)
	return []

def save_state(state):
	with open(STATE_FILE, "w") as f:
		return json.load(f)
	return []

def main():
	html = fetch_html(URL)
	current = parse_formations(html)

	old = load_state()
	new_items = [item for item in current if item not in old]

	if new_items:
        subject = f"[🚨] Nouvelles formations APS – {len(new_items)} trouvé(s)"
        body = "Nouvelles formations :\n\n" + "\n".join(new_items)
        send_email(subject, body)
        save_state(current)
    else:
        print("Pas de nouveau item.")

if __name__ == "__main__":
	main()
