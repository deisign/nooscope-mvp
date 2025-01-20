import requests
import sqlite3
from bs4 import BeautifulSoup
from textblob import TextBlob
from flask import Flask, render_template, request

# Initialize Flask app
app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            topic TEXT,
            content TEXT,
            sentiment REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Save data to database
def save_to_db(source, topic, content, sentiment, date):
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trends (source, topic, content, sentiment, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (source, topic, content, sentiment, date))
    conn.commit()
    conn.close()

# Fetch data from a news API
def fetch_news():
    api_key = "your_api_key_here"  # Replace with your API key
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        for article in articles:
            source = article['source']['name']
            topic = article['title']
            content = article['description'] or ''
            sentiment = TextBlob(content).sentiment.polarity
            date = article['publishedAt']
            save_to_db(source, topic, content, sentiment, date)

# Web scraper for additional sources
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('h2')  # Adjust tag based on the website structure
    for article in articles:
        topic = article.get_text()
        content = article.get_text()
        sentiment = TextBlob(content).sentiment.polarity
        save_to_db("Custom Source", topic, content, sentiment, "2025-01-20")

# Flask routes
@app.route('/')
def index():
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()
    cursor.execute("SELECT source, topic, sentiment, date FROM trends ORDER BY date DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', trends=rows)

@app.route('/add-source', methods=['POST'])
def add_source():
    url = request.form['url']
    scrape_website(url)
    return "Data scraped successfully!"

# Initialize database and fetch initial data
if __name__ == '__main__':
    init_db()
    fetch_news()
    app.run(host="0.0.0.0", port=5000, debug=True)
