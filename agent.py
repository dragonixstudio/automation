import requests
import json
import re
from datetime import datetime

# ===== HARD CODED (TEMP TEST ONLY) =====
ACCESS_TOKEN = "EAGJWzt7D2rABRlLiUdzlcKtfuZBhWZAKcXZCwZAj0TAzhwnwLCt4AqKzC6S4Q44vLvAGn9r2JjQLBY3eoUVIReXT7BnSYtZBcgysw61JviXFopgTb1LjZCmZBoZChZA87FPZBp4CRULpHxcIu2fKIFtGcI0npSfufNZAKMSsD2329X2dx9L8qwHRcVq7ZA3jbu5OCZBF86LZCrpCrZCXDRkCMG35KE8oJn30shuPHQeYqbEvt4ZBuYLN4mQstSmuUsZAapewZCN3iSscJtdqW5UQYZD"
IG_USER_ID = "17841417547403100"

GRAPH_API_VERSION = "v19.0"

DB_FILE = "processed_comments.json"
RULES_FILE = "rules.json"


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {} if path == RULES_FILE else []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    print("🤖 Dragonix Bot Started:", datetime.now())

    media_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media?fields=id,shortcode&access_token={ACCESS_TOKEN}"
    media = requests.get(media_url).json().get("data", [])

    rules = load_json(RULES_FILE)
    processed = load_json(DB_FILE)

    if not rules:
        print("⚠️ No rules found")
        return

    for m in media:
        shortcode = m.get("shortcode")

        if shortcode not in rules:
            continue

        rule = rules[shortcode]

        comments_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{m['id']}/comments?access_token={ACCESS_TOKEN}"
        comments = requests.get(comments_url).json().get("data", [])

        for c in comments:
            cid = c["id"]
            text = c.get("text", "").lower()

            if rule["keyword"] in text and cid not in processed:
                print("🎯 Match found:", cid)

                reply_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{cid}/replies"
                res = requests.post(reply_url, data={
                    "message": rule["reply_text"],
                    "access_token": ACCESS_TOKEN
                }).json()

                print("Reply result:", res)

                processed.append(cid)

    save_json(DB_FILE, processed)
    print("🏁 Done")


if __name__ == "__main__":
    main()
