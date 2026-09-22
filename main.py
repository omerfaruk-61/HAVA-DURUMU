from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "bd5e378503939ddaee76f12ad7a97608"

def init_db():
    conn = sqlite3.connect("weather_history.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            temperature REAL NOT NULL,
            searched_at DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def clean_old_history():
    conn = sqlite3.connect("weather_history.db")
    cursor = conn.cursor()
    cutoff_time = datetime.now() - timedelta(hours=12)
    cursor.execute("DELETE FROM search_history WHERE searched_at < ?", (cutoff_time,))
    conn.commit()
    conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(clean_old_history, 'interval', hours=1)
scheduler.start()

@app.get("/weather")
def get_weather(city: str):
    # Anlık Hava Durumu
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=tr"
    response = requests.get(url).json()

    if response.get("cod") == 200:
        temp = response["main"]["temp"]
        conn = sqlite3.connect("weather_history.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO search_history (city_name, temperature, searched_at) VALUES (?, ?, ?)",
            (city, temp, datetime.now())
        )
        conn.commit()
        conn.close()

    return response

# --- YENİ EKLENEN: 5 Günlük Hava Tahmini Endpoint'i ---
@app.get("/forecast")
def get_forecast(city: str):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=tr"
    response = requests.get(url).json()
    return response

@app.get("/history")
def get_history():
    conn = sqlite3.connect("weather_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, city_name, temperature, searched_at FROM search_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "city": r[1], "temp": r[2], "date": r[3]} for r in rows]

@app.delete("/history")
def clear_history():
    conn = sqlite3.connect("weather_history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history")
    conn.commit()
    conn.close()
    return {"message": "Geçmiş temizlendi"}