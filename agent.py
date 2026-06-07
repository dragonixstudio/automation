import requests
import json
import re
from datetime import datetime

# --- HARD CODED CONFIG (TEMP TEST ONLY) ---
ACCESS_TOKEN = "EAGJWzt7D2rABRlLiUdzlcKtfuZBhWZAKcXZCwZAj0TAzhwnwLCt4AqKzC6S4Q44vLvAGn9r2JjQLBY3eoUVIReXT7BnSYtZBcgysw61JviXFopgTb1LjZCmZBoZChZA87FPZBp4CRULpHxcIu2fKIFtGcI0npSfufNZAKMSsD2329X2dx9L8qwHRcVq7ZA3jbu5OCZBF86LZCrpCrZCXDRkCMG35KE8oJn30shuPHQeYqbEvt4ZBuYLN4mQstSmuUsZAapewZCN3iSscJtdqW5UQYZD"
IG_USER_ID = "17841417547403100"

GRAPH_API_VERSION = "v19.0"

DB_FILE = "processed_comments.json"
RULES_FILE = "rules.json"


def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {} if filepath == RULES_FILE else []


def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def extract_shortcode(url):
    match = re.search(r"(?:p|reel)/([^/?#&]+)", url)
    return match.group(1) if match else url


def main():
    if not ACCESS_TOKEN or not IG_USER_ID:
        print("❌ Missing credentials")
        return

    rules = load_json(RULES_FILE)

    if not rules:
        print("⚠️ No rules set")
        return

    processed = load_json(DB_FILE)

    print(f"🤖 Bot started {datetime.now()}")

    media_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media?fields=id,shortcode&access_token={ACCESS_TOKEN}"
    media = requests.get(media_url).json().get("data", [])

    for m in media:
        shortcode = m.get("shortcode")

        if shortcode in rules:
            rule = rules[shortcode]

            comments_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{m['id']}/comments?access_token={ACCESS_TOKEN}"
            comments = requests.get(comments_url).json().get("data", [])

            for c in comments:
                cid = c["id"]
                text = c.get("text", "").lower()

                if rule["keyword"] in text and cid not in processed:
                    print("Match:", cid)

                    reply_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{cid}/replies"
                    r = requests.post(reply_url, data={
                        "message": rule["reply_text"],
                        "access_token": ACCESS_TOKEN
                    }).json()

                    print("Reply:", r)

                    processed.append(cid)

    save_json(DB_FILE, processed)
    print("Done")


if __name__ == "__main__":
    main()
