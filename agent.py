import requests
import json
import re
from datetime import datetime

# =========================
# CONFIG (PUT YOUR NEW TOKEN HERE)
# =========================
ACCESS_TOKEN = "EAGJWzt7D2rABRlLiUdzlcKtfuZBhWZAKcXZCwZAj0TAzhwnwLCt4AqKzC6S4Q44vLvAGn9r2JjQLBY3eoUVIReXT7BnSYtZBcgysw61JviXFopgTb1LjZCmZBoZChZA87FPZBp4CRULpHxcIu2fKIFtGcI0npSfufNZAKMSsD2329X2dx9L8qwHRcVq7ZA3jbu5OCZBF86LZCrpCrZCXDRkCMG35KE8oJn30shuPHQeYqbEvt4ZBuYLN4mQstSmuUsZAapewZCN3iSscJtdqW5UQYZD"
IG_USER_ID = "1784141754740310"

GRAPH_API_VERSION = "v19.0"

RULES_FILE = "rules.json"
DB_FILE = "processed_comments.json"


def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {} if file == RULES_FILE else []


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


def main():
    print("🤖 Bot started:", datetime.now())

    rules = load_json(RULES_FILE)
    processed = load_json(DB_FILE)

    if not rules:
        print("⚠️ No rules found")
        return

    media_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media?fields=id,shortcode&access_token={ACCESS_TOKEN}"
    media = requests.get(media_url).json().get("data", [])

    for post in media:
        comments_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{post['id']}/comments?access_token={ACCESS_TOKEN}"
        comments = requests.get(comments_url).json().get("data", [])

        for c in comments:
            cid = c["id"]
            text = c.get("text", "").lower()

            if cid in processed:
                continue

            # 🔥 GLOBAL TRIGGER SYSTEM (like ManyChat)
            if "course" in text:

                print("🎯 Trigger found:", cid)

                # Public reply
                reply_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{cid}/replies"

                requests.post(reply_url, data={
                    "message": "Here is your course link 👇",
                    "access_token": ACCESS_TOKEN
                })

                # Optional DM attempt (only works if permissions allow)
                try:
                    user_id = c.get("from", {}).get("id")

                    if user_id:
                        dm_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/messages"

                        requests.post(dm_url, json={
                            "recipient": {"id": user_id},
                            "message": {"text": "Here is your course link 👇"},
                            "access_token": ACCESS_TOKEN
                        })

                except Exception as e:
                    print("DM error:", e)

                processed.append(cid)

    save_json(DB_FILE, processed)
    print("🏁 Done")


if __name__ == "__main__":
    main()
