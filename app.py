import requests
import threading
import os
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv

public_app = Flask(__name__)
admin_app = Flask(__name__)
load_dotenv()

if not os.path.exists('.env') and os.path.exists('.env.example'):
    with open('.env.example', 'r') as example, open('.env', 'w') as real:
        real.write(example.read())

# =======================
# Public App Routes
# =======================

@public_app.route('/')
def index():
    return render_template("index.html")

@public_app.route('/get', methods=['POST'])
def twitter_card_checker():
    url = request.form.get("url")
    view_html = request.form.get("view_html")

    if not url.startswith("http://") and not url.startswith("https://"):
        return jsonify({"error": "Invalid URL"}), 400

    try:
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch page: {response.status_code}"}), 400

        soup = BeautifulSoup(response.content, "html.parser")

        card_data = {
            "title": None,
            "description": None,
            "image": None,
        }

        twitter_title = soup.find("meta", property="twitter:title")
        twitter_description = soup.find("meta", property="twitter:description")
        twitter_image = soup.find("meta", property="twitter:image")

        og_title = soup.find("meta", property="og:title")
        og_description = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")

        if twitter_title:
            card_data["title"] = twitter_title["content"]
        elif og_title:
            card_data["title"] = og_title["content"]

        if twitter_description:
            card_data["description"] = twitter_description["content"]
        elif og_description:
            card_data["description"] = og_description["content"]

        if twitter_image:
            card_data["image"] = twitter_image["content"]
        elif og_image:
            card_data["image"] = og_image["content"]

        if view_html:
            return render_template("sourcecode.html", html_code=response.text)

        return render_template("result.html", card_data=card_data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# /flag on PUBLIC app calls internal /flag on ADMIN app
@public_app.route('/flag')
def proxy_flag():
    try:
        internal_response = requests.get("http://127.0.0.1:5001/flag", timeout=2)
        return internal_response.text, internal_response.status_code
    except Exception as e:
        return jsonify({"error": "Could not reach internal service"}), 500


# =======================
# Admin App Routes (local only)
# =======================

@admin_app.route('/flag')
def flag():
    return os.getenv("FLAG") or "CTF{dummy_flag_for_testing}"


# =======================
# Run both apps
# =======================

def run_admin():
    admin_app.run(host='127.0.0.1', port=5001)

if __name__ == '__main__':
    threading.Thread(target=run_admin, daemon=True).start()
    public_app.run(host='0.0.0.0', port=5000)
