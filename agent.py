import requests
import json
import re
import os
from datetime import datetime

ACCESS_TOKEN = "EAGJWzt7D2rABRlLiUdzlcKtfuZBhWZAKcXZCwZAj0TAzhwnwLCt4AqKzC6S4Q44vLvAGn9r2JjQLBY3eoUVIReXT7BnSYtZBcgysw61JviXFopgTb1LjZCmZBoZChZA87FPZBp4CRULpHxcIu2fKIFtGcI0npSfufNZAKMSsD2329X2dx9L8qwHRcVq7ZA3jbu5OCZBF86LZCrpCrZCXDRkCMG35KE8oJn30shuPHQeYqbEvt4ZBuYLN4mQstSmuUsZAapewZCN3iSscJtdqW5UQYZD"
IG_USER_ID = "17841417547403100"

GRAPH_API_VERSION = "v19.0"

RULES_FILE = "rules.json"
DB_FILE = "processed_comments.json"


# =========================
# INPUTS FROM GITHUB
# =========================
POST_URL = os.getenv("INPUT_POST_URL", "")
KEYWORD = os.getenv("INPUT_KEYWORD", "").lower()
COMMENT_REPLY = os.getenv("INPUT_COMMENT_REPLY", "")
DM_REPLY = os.getenv("INPUT_DM_REPLY", "")


def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


def extract_shortcode(url):
    match = re.search(r"(?:p|reel)/([^/?&]+)", url)
    return match.group(1) if match else None


def main():
    print("🤖 Bot started:", datetime.now())

    rules = load_json(RULES_FILE)
    processed = load_json(DB_FILE)

    # =========================
    # CREATE NEW RULE FROM INPUT
    # =========================
    if POST_URL and KEYWORD and COMMENT_REPLY:
        shortcode = extract_shortcode(POST_URL)

        if shortcode:
            rules[shortcode] = {
                "keyword": KEYWORD,
                "comment_reply": COMMENT_REPLY,
                "dm_reply": DM_REPLY
            }

            save_json(RULES_FILE, rules)
            print(f"✅ Rule created for {shortcode}")

    if not rules:
        print("⚠️ No rules found")
        return

    # =========================
    # SCAN POSTS
    # =========================
    media_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{IG_USER_ID}/media?fields=id,shortcode&access_token={ACCESS_TOKEN}"
    media = requests.get(media_url).json().get("data", [])

    for post in media:
        shortcode = post.get("shortcode")

        if shortcode not in rules:
            continue

        rule = rules[shortcode]

        comments_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{post['id']}/comments?access_token={ACCESS_TOKEN}"
        comments = requests.get(comments_url).json().get("data", [])

        for c in comments:
            cid = c["id"]
            text = c.get("text", "").lower()

            if rule["keyword"] in text and cid not in processed:

                print("🎯 Trigger:", cid)

                # COMMENT REPLY
                reply_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{cid}/replies"

                requests.post(reply_url, data={
                    "message": rule["comment_reply"],
                    "access_token": ACCESS_TOKEN
                })

                # DM (optional)
                try:
                    user_id = c.get("from", {}).get("id")

                    if user_id and rule["dm_reply"]:
                        dm_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/me/messages"

                        requests.post(dm_url, json={
                            "recipient": {"id": user_id},
                            "message": {"text": rule["dm_reply"]},
                            "access_token": ACCESS_TOKEN
                        })

                except Exception as e:
                    print("DM error:", e)

                processed.append(cid)

    save_json(DB_FILE, processed)
    print("🏁 Done")


if __name__ == "__main__":
    main()
