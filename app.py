from flask import Flask, render_template, request, jsonify
import sqlite3
from textblob import TextBlob

app = Flask(__name__)

# Функция для генерации саммари
def generate_summary(data):
    if not data:
        return {"keywords": [], "sentiment": 0}

    try:
        # Извлекаем темы
        topics = [row[0] for row in data]
        # Объединяем их в один текст
        combined_text = " ".join(topics)
        # Анализируем текст с TextBlob
        blob = TextBlob(combined_text)
        keywords = list(blob.noun_phrases)[:5]  # Топ-5 ключевых слов
        sentiment = blob.sentiment.polarity  # Общая тональность
        return {"keywords": keywords, "sentiment": sentiment}
    except Exception as e:
        print("Error in generate_summary:", e)
        return {"keywords": [], "sentiment": 0}

# Маршрут для главной страницы
@app.route('/')
def index():
    try:
        conn = sqlite3.connect('noscope.db')
        cursor = conn.cursor()

        # Получаем данные для вкладок
        cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'RSS Feed'")
        rss_data = cursor.fetchall()
        print("RSS Data:", rss_data)

        cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Google Trends'")
        google_data = cursor.fetchall()
        print("Google Data:", google_data)

        cursor.execute("SELECT topic, sentiment, date FROM trends WHERE source = 'Reddit Trends'")
        reddit_data = cursor.fetchall()
        print("Reddit Data:", reddit_data)

        conn.close()

        # Генерация саммари
        rss_summary = generate_summary(rss_data)
        google_summary = generate_summary(google_data)
        reddit_summary = generate_summary(reddit_data)

        return render_template(
            'index.html',
            rss_data=rss_data,
            google_data=google_data,
            reddit_data=reddit_data,
            rss_summary=rss_summary,
            google_summary=google_summary,
            reddit_summary=reddit_summary
        )
    except Exception as e:
        print("Error in index:", e)
        return "Failed to load data", 500

if __name__ == '__main__':
    app.run(debug=True)
