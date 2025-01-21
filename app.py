from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    try:
        conn = sqlite3.connect('noscope.db')
        cursor = conn.cursor()

        # Проверка и выполнение запросов
        cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'RSS Feed'")
        rss_data = cursor.fetchall()
        
        cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Google Trends'")
        google_data = cursor.fetchall()
        
        cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Reddit Trends'")
        reddit_data = cursor.fetchall()

        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        rss_data, google_data, reddit_data = [], [], []
    except Exception as e:
        print(f"Unexpected error: {e}")
        rss_data, google_data, reddit_data = [], [], []

    return render_template('index.html', rss_data=rss_data, google_data=google_data, reddit_data=reddit_data)

if __name__ == '__main__':
    app.run(debug=True)
