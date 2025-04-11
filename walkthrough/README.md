## 🔍 Walkthrough

1.**Discovering the Bug**
   - Tthe public app will make server-side requests (or "ping" URLs) exactly as submitted.
   - Since the application trusts and fetches any URL that starts with `http://` or `https://` without additional verification, it will issue the request from the environment in which it is deployed.
   - This means that internal URLs relative to the hosting environment can be accessed. For instance, if other Flask apps (like an admin panel) are running locally on the same server on port 5001, you can target them directly.

2.**Exploiting the Vulnerability**
   - Test various URLs using the form on the homepage. Since many Flask admin applications tend to run on port 5001, try submitting an internal URL like:
     ```
     http://127.0.0.1:5001/flag
     ```
   - The deployed app will "ping" that URL from its own network context, and if the admin endpoint is running, it will fetch the flag.

3.**Retrieving the Flag**
   - After submitting the internal URL, the result page should display the retrieved content (i.e., the flag stored in the `.env` file).
   - Additionally, you can use the "View HTML Source Code" button to inspect the raw response containing the flag.