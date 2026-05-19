import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def get_poster_from_detail(link, headers):
    try:
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        img = soup.find("img", class_="attachment-post-thumbnail")
        if img:
            return img.get("data-src") or img.get("src")
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


def search_anime(query):
    url = f"https://myanimelist.net/anime.php?q={query}&cat=anime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    anime_results = []

    # Find the table containing search results
    table = soup.find("table", class_="js-category-list")
    if not table:
        return {"error": "No results found or table structure changed"}

    # Iterate through rows, skipping the header row
    for row in table.find_all("tr")[1:]:
        columns = row.find_all("td")
        if len(columns) < 2:  # Ensure there are enough columns
            continue

        title_tag = columns[1].find("a", class_="hoverinfo")
        title = title_tag.text.strip() if title_tag else "N/A"
        detail_link = title_tag["href"] if title_tag else "N/A"

        # Extract cover image
        img_tag = columns[0].find("img")
        cover_url = img_tag["data-src"] if img_tag and "data-src" in img_tag.attrs else (img_tag["src"] if img_tag else "N/A")

        # Extract episodes (usually 4th column, but can vary)
        episodes = "N/A"
        episodes_col = columns[3] if len(columns) > 3 else None
        if episodes_col:
            episodes_text = episodes_col.text.strip()
            if episodes_text.isdigit():
                episodes = int(episodes_text)

        # Extract rating (usually 5th column, but can vary)
        rating = "N/A"
        rating_col = columns[4] if len(columns) > 4 else None
        if rating_col:
            rating_text = rating_col.text.strip()
            try:
                rating = float(rating_text)
            except ValueError:
                pass

        anime_results.append({
            "title": title,
            "episodes": episodes,
            "rating": rating,
            "cover_url": cover_url,
            "detail_link": detail_link
        })

    return anime_results

@app.route("/anime/search", methods=["GET"])
def anime_search():
    query = request.args.get("title", "")
    if not query:
        return jsonify({"error": "Provide a title parameter"}), 400
    results = search_anime(query)
    return jsonify(results)


def search_lyrics(artist, song):
    url = f"https://api.lyrics.ovh/v1/{artist}/{song}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        lyrics_data = response.json()
        if "lyrics" in lyrics_data:
            return {"artist": artist, "song": song, "lyrics": lyrics_data["lyrics"]}
        else:
            return {"error": "Lyrics not found"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch lyrics: {str(e)}"}
    except ValueError:
        return {"error": "Failed to parse lyrics data. Artist or song not found."}

@app.route("/lyrics", methods=["GET"])
def lyrics_search():
    artist = request.args.get("artist", "")
    song = request.args.get("song", "")
    if not artist or not song:
        return jsonify({"error": "Provide both artist and song parameters"}), 400
    results = search_lyrics(artist, song)
    return jsonify(results)


def search_quotes():
    url = "http://quotes.toscrape.com/random"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch quotes: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    
    quote_element = soup.find("div", class_="quote")
    if quote_element:
        text = quote_element.find("span", class_="text").text.strip()
        author = quote_element.find("small", class_="author").text.strip()
        return {"quote": text, "author": author}

    return {"error": "Quote not found. The website structure might have changed."}

@app.route("/quotes/random", methods=["GET"])
def random_quotes():
    results = search_quotes()
    return jsonify(results)


def get_random_joke():
    url = "https://icanhazdadjoke.com/"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        joke_data = response.json()
        if "joke" in joke_data:
            return {"joke": joke_data["joke"]}
        else:
            return {"error": "Joke not found"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch joke: {str(e)}"}
    except ValueError:
        return {"error": "Failed to parse joke data."}

@app.route("/jokes/random", methods=["GET"])
def random_jokes_api():
    joke = get_random_joke()
    return jsonify(joke)


def get_news_headlines():
    url = "http://feeds.bbci.co.uk/news/rss.xml"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch news: {str(e)}"}

    soup = BeautifulSoup(response.text, "xml") # Parse as XML for RSS feed
    headlines = []

    for item in soup.find_all("item"):
        title = item.find("title").text.strip() if item.find("title") else "N/A"
        link = item.find("link").text.strip() if item.find("link") else "N/A"
        headlines.append({"title": title, "url": link})
    
    if not headlines:
        return {"error": "Could not find news headlines. The RSS feed structure might have changed."}

    return headlines

@app.route("/news", methods=["GET"])
def latest_news():
    headlines = get_news_headlines()
    return jsonify(headlines)


def get_weather_data(city):
    url = f"https://wttr.in/{city}?format=j1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        # Extract relevant information
        current_condition = weather_data["current_condition"][0]
        weather = {
            "city": city,
            "temperature": current_condition["temp_C"],
            "feels_like": current_condition["FeelsLikeC"],
            "description": current_condition["weatherDesc"][0]["value"],
            "humidity": current_condition["humidity"],
            "wind_speed": current_condition["windspeedKmph"]
        }
        return weather
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        return {"error": f"Failed to parse weather data: {str(e)}. Please check the city name.", "details": response.text if response else "No response"}

@app.route("/weather", methods=["GET"])
def weather_route():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Please provide a city parameter."}), 400
    weather = get_weather_data(city)
    return jsonify(weather)


def get_crypto_prices():
    url = "https://www.coingecko.com/en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch crypto prices: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    crypto_data = []

    # Find the table containing cryptocurrency data
    # Coingecko uses a table with class 'table-responsive'
    table = soup.find("table", class_="table-responsive")
    if not table:
        return {"error": "Could not find crypto data. The website structure might have changed."}

    # Iterate through table rows, skipping the header
    for row in table.find("tbody").find_all("tr"):
        columns = row.find_all("td")
        if len(columns) > 2:
            name_tag = columns[2].find("a")
            symbol_tag = columns[2].find("span", class_="coin-symbol")
            price_tag = columns[3].find("span")

            if name_tag and symbol_tag and price_tag:
                name = name_tag.text.strip()
                symbol = symbol_tag.text.strip()
                price = price_tag.text.strip()
                crypto_data.append({"name": name, "symbol": symbol, "price": price})
                if len(crypto_data) >= 10:
                    break
    
    if not crypto_data:
        return {"error": "Could not find crypto data. The website structure might have changed."}

    return crypto_data

@app.route("/crypto/prices", methods=["GET"])
def crypto_prices():
    prices = get_crypto_prices()
    return jsonify(prices)


@app.route("/football/scores", methods=["GET"])
def get_football_scores():
    url = "https://www.bbc.co.uk/sport/football/scores-fixtures"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch football scores: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    scores = []

    # BBC Sport uses a more complex structure, often with JavaScript rendering.
    # We will try to target a common structure for match results.
    # This might require more specific selectors or a different approach if the structure is too dynamic.
    matches = soup.find_all("div", class_="gs-o-media-grid__item")

    for match in matches:
        try:
            competition = match.find("h3", class_="gs-c-section-header__title").text.strip() if match.find("h3", class_="gs-c-section-header__title") else "N/A"
            home_team = match.find("span", class_="gs-u-display-block gs-u-truncate-alt").text.strip() if match.find("span", class_="gs-u-display-block gs-u-truncate-alt") else "N/A"
            away_team = match.find_all("span", class_="gs-u-display-block gs-u-truncate-alt")[1].text.strip() if len(match.find_all("span", class_="gs-u-display-block gs-u-truncate-alt")) > 1 else "N/A"
            score = match.find("span", class_="gs-o-score").text.strip() if match.find("span", class_="gs-o-score") else "N/A"
            status = match.find("span", class_="gel-long-primer gs-u-display-block").text.strip() if match.find("span", class_="gel-long-primer gs-u-display-block") else "N/A"

            scores.append({
                "competition": competition,
                "home_team": home_team,
                "away_team": away_team,
                "score": score,
                "status": status
            })
        except AttributeError:
            continue
    
    if not scores:
        return {"error": "Could not find football scores. The website structure might have changed or no matches are available."}

    return scores

@app.route("/football/scores", methods=["GET"])
def football_scores():
    scores = get_football_scores()
    return jsonify(scores)


def get_bible_verse(book, chapter, verse):
    url = f"https://bible-api.com/{book}{chapter}:{verse}?translation=kjv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        bible_data = response.json()
        if "text" in bible_data and len(bible_data["text"]) > 0:
            return {"book": book, "chapter": chapter, "verse": verse, "text": bible_data["text"]}
        else:
            return {"error": "Verse not found or invalid reference."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Bible verse: {str(e)}"}
    except ValueError:
        return {"error": "Failed to parse Bible data."}

@app.route("/bible", methods=["GET"])
def bible_verse():
    book = request.args.get("book", "")
    chapter = request.args.get("chapter", "")
    verse = request.args.get("verse", "")

    if not book or not chapter or not verse:
        return jsonify({"error": "Please provide book, chapter, and verse parameters."}), 400
    
    result = get_bible_verse(book, chapter, verse)
    return jsonify(result)
