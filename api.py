from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
import os, sqlite3, time, openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
openai.api_key = OPENAI_API_KEY

app = FastAPI(title="Chethiya-MD API")
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_PATH = os.path.join("db","history.db")
os.makedirs("db", exist_ok=True)
conn = sqlite3.connect(DB_PATH)
conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT, created_at INTEGER)")
conn.commit(); conn.close()

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html","r",encoding="utf-8") as f: return HTMLResponse(f.read())

@app.post("/api/chat")
async def chat(payload: dict):
    user = payload.get("message","")
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall(); conn.close()
    history = [{"role":r,"content":c} for r,c in reversed(rows)]
    messages = [{"role":"system","content":"You are Chethiya-MD, helpful AI assistant."}]+history+[{"role":"user","content":user}]
    try:
        resp = openai.ChatCompletion.create(model=MODEL, messages=messages)
        reply = resp["choices"][0]["message"]["content"].strip()
        conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
        cur.execute("INSERT INTO messages (role, content, created_at) VALUES (?,?,?)",("user",user,int(time.time())))
        cur.execute("INSERT INTO messages (role, content, created_at) VALUES (?,?,?)",("assistant",reply,int(time.time())))
        conn.commit(); conn.close()
        return {"reply": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error":str(e)})