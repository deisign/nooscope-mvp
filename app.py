import requests
import sqlite3
from textblob import TextBlob
from flask import Flask, render_template, request
import feedparser
import praw
import tweepy
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

# Fetch data from an RSS feed
def fetch_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        topic = entry.title
        content = entry.summary if 'summary' in entry else entry.description
        sentiment = TextBlob(content).sentiment.polarity
        date = entry.published if 'published' in entry else "Unknown"
        save_to_db("RSS Feed", topic, content, sentiment, date)

# Fetch Google Trends
def fetch_google_trends():
    pytrends = TrendReq(hl='en-US', tz=360)
    trending_searches = pytrends.trending_searches()
    for index, row in trending_searches.iterrows():
        topic = row[0]
        content = f"Trending on Google: {topic}"
        sentiment = TextBlob(content).sentiment.polarity
        save_to_db("Google Trends", topic, content, sentiment, "Unknown")

# Fetch Reddit Trends
def fetch_reddit_trends():
    reddit = praw.Reddit(
        client_id='lrVT6QJkGF14uzjxK-Z3Kg',
        client_secret='kbaq0S-FnCuyCCueBUddQDwa-U4YjQ',
        user_agent='nooscope'
    )
    for submission in reddit.subreddit('all').hot(limit=10):
        topic = submission.title
        content = f"Trending on Reddit: {topic}"
        sentiment = TextBlob(content).sentiment.polarity
        date = submission.created_utc
        save_to_db("Reddit Trends", topic, content, sentiment, date)

# Fetch Twitter Trends
def fetch_twitter_trends():
    client = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAACBnyQEAAAAAswY40ue8%2FaTrgouJcqlpHqwrkRw%3DHP9019TkXpIfad8tZ1s6IPJho5TSxb7w5Yurz9q1eRkCx8WtmK')
    # Twitter trends use a direct API request for WOEID
    trends = client.get_trends_place(id=1)  # WOEID 1 = Worldwide
    if trends:
        for trend in trends[0]['trends'][:10]:
            topic = trend['name']
            content = f"Trending on Twitter: {topic}"
            sentiment = TextBlob(content).sentiment.polarity
            save_to_db("Twitter Trends", topic, content, sentiment, "Unknown")

# Flask routes
@app.route('/')
def index():
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()
    cursor.execute("SELECT source, topic, sentiment, date FROM trends ORDER BY date DESC LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', trends=rows)

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
    fetch_twitter_trends()
    fetch_rss_feed("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml")
    fetch_rss_feed("https://rss.nytimes.com/services/xml/rss/nyt/World.xml")
    fetch_rss_feed("https://feeds.bbci.co.uk/news/rss.xml")
    fetch_rss_feed("https://www.theguardian.com/world/rss")
    app.run(host="0.0.0.0", port=5000, debug=True)
