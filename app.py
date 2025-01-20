import requests
import sqlite3
from textblob import TextBlob
from flask import Flask, render_template, request
import feedparser
import praw
from pytrends.request import TrendReq

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

# Print all data from the database
def print_all_data():
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trends")
    rows = cursor.fetchall()
    conn.close()
    print(f"All data in database: {rows}")

# Fetch data from an RSS feed
def fetch_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    print(f"Fetching RSS feed: {feed_url}")
    for entry in feed.entries:
        topic = entry.title
        content = entry.summary if 'summary' in entry else entry.description
        sentiment = TextBlob(content).sentiment.polarity
        date = entry.published if 'published' in entry else "Unknown"
        save_to_db("RSS Feed", topic, content, sentiment, date)
        print(f"Added RSS trend: {topic} with sentiment {sentiment}")

# Fetch Google Trends
def fetch_google_trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    trending_searches = pytrends.trending_searches()
    print("Fetching Google Trends...")
    for index, row in trending_searches.iterrows():
        topic = row[0]
        content = f"Trending on Google: {topic}"
        sentiment = TextBlob(content).sentiment.polarity
        save_to_db("Google Trends", topic, content, sentiment, "Unknown")
        print(f"Added Google trend: {topic} with sentiment {sentiment}")

# Fetch Reddit Trends
def fetch_reddit_trends():
    reddit = praw.Reddit(
        client_id='lrVT6QJkGF14uzjxK-Z3Kg',
        client_secret='kbaq0S-FnCuyCCueBUddQDwa-U4YjQ',
        user_agent='nooscope'
    )
    print("Fetching Reddit Trends...")
    for submission in reddit.subreddit('all').hot(limit=10):
        topic = submission.title
        content = f"Trending on Reddit: {topic}"
        sentiment = TextBlob(content).sentiment.polarity
        date = submission.created_utc
        save_to_db("Reddit Trends", topic, content, sentiment, date)
        print(f"Added Reddit trend: {topic} with sentiment {sentiment}")
    print("Finished fetching Reddit Trends.")

# Flask routes
@app.route('/')
def index():
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()
    # Разделяем данные по источникам
    cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'RSS Feed'")
    rss_data = cursor.fetchall()
    cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Google Trends'")
    google_data = cursor.fetchall()
    cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Reddit Trends'")
    reddit_data = cursor.fetchall()
    conn.close()

    # Логируем данные
    print(f"RSS Data: {rss_data}")
    print(f"Google Trends Data: {google_data}")
    print(f"Reddit Data: {reddit_data}")

    return render_template('index.html', rss_data=rss_data, google_data=google_data, reddit_data=reddit_data)

@app.route('/add-source', methods=['POST'])
def add_source():
    url = request.form['url']
    fetch_rss_feed(url)
    return "RSS feed data added successfully!"

# Initialize database and fetch initial data
if __name__ == '__main__':
    init_db()
    fetch_google_trends()
    fetch_reddit_trends()
    fetch_rss_feed("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml")
    print_all_data()  # Логируем все данные из базы
    app.run(host="0.0.0.0", port=5000, debug=True)
