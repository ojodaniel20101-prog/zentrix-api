from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_poster_from_detail(link, headers):
    try:
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        img = soup.find("img", class_="attachment-post-thumbnail")
        if img:
            return img.get("data-src") or img.get("src")
        # fallback - get first image in post content
        content = soup.find("div", class_="entry-content")
        if content:
            img = content.find("img")
            if img:
                return img.get("data-src") or img.get("src")
    except:
        pass
    return "N/A"

def search_movies(query):
    url = f"https://www.movie-box.com.ng/?s={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    movies = []

    movie_elements = soup.find_all("div", class_="magsoul-grid-post")

    if not movie_elements:
        return {"error": "No results found"}

    for movie in movie_elements:
        title_tag = movie.find("h3", class_="magsoul-grid-post-title")
        title = title_tag.find("a").text.strip() if title_tag else "N/A"
        link = title_tag.find("a")["href"] if title_tag else "N/A"

        img_tag = movie.find("img")
        poster = img_tag.get("data-src") or img_tag.get("src") if img_tag else None

        if not poster or poster == "N/A":
            poster = get_poster_from_detail(link, headers)

        movies.append({
            "title": title,
            "poster_url": poster,
            "detail_link": link
        })

    return movies

@app.route("/movies/search", methods=["GET"])
def movie_search():
    query = request.args.get("title", "")
    if not query:
        return jsonify({"error": "Provide a title parameter"}), 400
    results = search_movies(query)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
