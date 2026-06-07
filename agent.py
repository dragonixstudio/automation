import os
import requests
import json
import re
from datetime import datetime

# =========================
# CONFIG (TEMP TEST MODE)
# =========================
ACCESS_TOKEN = "EAGJWzt7D2rABRlLiUdzlcKtfuZBhWZAKcXZCwZAj0TAzhwnwLCt4AqKzC6S4Q44vLvAGn9r2JjQLBY3eoUVIReXT7BnSYtZBcgysw61JviXFopgTb1LjZCmZBoZChZA87FPZBp4CRULpHxcIu2fKIFtGcI0npSfufNZAKMSsD2329X2dx9L8qwHRcVq7ZA3jbu5OCZBF86LZCrpCrZCXDRkCMG35KE8oJn30shuPHQeYqbEvt4ZBuYLN4mQstSmuUsZAapewZCN3iSscJtdqW5UQYZD"
IG_USER_ID = "17841417547403100"

GRAPH_API_VERSION = "v19.0"

RULES_FILE = "rules.json"
DB_FILE = "processed_comments.json"

# =========================
# INPUTS FROM GITHUB
# =========================
INPUT_POST_URL = os.getenv("INPUT_POST_URL", "").strip()
INPUT_KEYWORD = os.getenv("INPUT_KEYWORD", "").strip().lower()
INPUT_REPLY = os.getenv("INPUT_REPLY", "").strip()


def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {} if file == RULES_FILE else []


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


def extract_shortcode(url):
    match = re.search(r"(?:p|reel)/([^/?&]+)", url)
    return match.group(1) if match else None


def main():
    print("🤖 Dragonix Bot Started:", datetime.now())

    rules = load_json(RULES_FILE)
    processed = load_json(DB_FILE)

    # =========================
    # CREATE RULE FROM INPUT
    # =========================
    if INPUT_POST_URL and INPUT_KEYWORD and INPUT_REPLY:
        shortcode = extract_shortcode(INPUT_POST_URL)

        if shortcode:
            rules[shortcode] = {
                "keyword": INPUT_KEYWORD,
                "reply_text": INPUT_REPLY
            }

            save_json(RULES_FILE, rules)
            print(f"✅ Rule saved for post: {shortcode}")

    if not rules:
        print("⚠️ No rules found. Add one from GitHub workflow.")
        return

    # =========================
    # FETCH IG POSTS
    # =========================
    media_url = (
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/"
        f"{IG_USER_ID}/media?fields=id,shortcode&access_token={ACCESS_TOKEN}"
    )

    media = requests.get(media_url).json().get("data", [])

    for post in media:
        shortcode = post.get("shortcode")

        if shortcode not in rules:
            continue

        rule = rules[shortcode]

        comments_url = (
            f"https://graph.facebook.com/{GRAPH_API_VERSION}/"
            f"{post['id']}/comments?access_token={ACCESS_TOKEN}"
        )

        comments = requests.get(comments_url).json().get("data", [])

        for c in comments:
            cid = c["id"]
            text = c.get("text", "").lower()

            if rule["keyword"] in text and cid not in processed:
                print(f"🎯 Match found: {cid}")

                reply_url = (
                    f"https://graph.facebook.com/{GRAPH_API_VERSION}/"
                    f"{cid}/replies"
                )

                res = requests.post(reply_url, data={
                    "message": rule["reply_text"],
                    "access_token": ACCESS_TOKEN
                }).json()

                print("Reply response:", res)

                processed.append(cid)

    save_json(DB_FILE, processed)
    print("🏁 Bot finished")


if __name__ == "__main__":
    main()
