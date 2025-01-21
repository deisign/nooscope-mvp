from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

# Убедимся, что база данных существует и инициализируем её
DB_PATH = 'db/noscope.db'
if not os.path.exists('db'):
    os.makedirs('db')
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            date TEXT NOT NULL,
            source TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получение данных из базы данных
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
    # Используем переменную окружения PORT для Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
