from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('noscope.db')
    cursor = conn.cursor()

    # Получение данных для отображения
    cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'RSS Feed'")
    rss_data = cursor.fetchall()
    cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Google Trends'")
    google_data = cursor.fetchall()
    cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Reddit Trends'")
    reddit_data = cursor.fetchall()

    conn.close()

    return render_template('index.html', rss_data=rss_data, google_data=google_data, reddit_data=reddit_data)

if __name__ == '__main__':
    app.run(debug=True)
