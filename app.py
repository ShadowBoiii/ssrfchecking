from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import socket

load_dotenv()

app = Flask(__name__)

if not os.path.exists('.env') and os.path.exists('.env.example'):
    with open('.env.example', 'r') as example, open('.env', 'w') as real:
        real.write(example.read())

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get', methods=['POST'])
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

@app.route('/flag')
def flag():
    try:
        # Get the IP of the host machine (container or local)
        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]

        if request.remote_addr not in local_ips and not request.remote_addr.startswith("127.") and request.remote_addr != "::1":
            return jsonify({"error": "Forbidden"}), 403

        return os.getenv("FLAG")

    except Exception as e:
        return jsonify({"error": "Error checking local access", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
