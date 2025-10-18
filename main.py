#!/usr/bin/env python3
import os, time, sqlite3
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from voice import tts_play, record_seconds

load_dotenv()
OPENAI_API_KEY ="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"
MODEL = os.getenv("MODEL", "gpt-3.5-turbo")
ENABLE_VOICE = os.getenv("ENABLE_VOICE","false").lower() == "true"

DB_DIR = os.path.join(os.path.dirname(__file__), "db")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "history.db")

console = Console()
import openai
openai.api_key = OPENAI_API_KEY

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT, created_at INTEGER)")
    conn.commit(); conn.close()

def save_msg(role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)", (role, content, int(time.time())))
    conn.commit(); conn.close()

def load_history(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT role, content FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall(); conn.close()
    return list(reversed(rows))

def ask_openai(messages):
    try:
        resp = openai.ChatCompletion.create(model=MODEL, messages=messages)
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[ERROR] {e}"

def main():
    console.print("[bold green]Chethiya-MD (Terminal + Voice)[/bold green]")
    init_db()
    while True:
        user = Prompt.ask("[cyan]You[/cyan]").strip()
        if not user: continue
        if user.lower() in ("/exit","/quit"):
            console.print("[yellow]Goodbye![/yellow]"); break
        if user.lower() == "/clear":
            conn = sqlite3.connect(DB_PATH); conn.execute("DELETE FROM messages"); conn.commit(); conn.close()
            console.print("[green]Cleared history[/green]"); continue
        if user.lower() == "/record":
            wav = record_seconds(5)
            console.print(f"Recorded: {wav}"); continue

        save_msg("user", user)
        history = load_history(10)
        system = {"role":"system","content":"You are Chethiya-MD, a helpful AI assistant."}
        messages = [system]+[{"role":r,"content":c} for r,c in history]+[{"role":"user","content":user}]
        console.print("[italic]Thinking...[/italic]")
        reply = ask_openai(messages)
        save_msg("assistant", reply)
        console.print(Markdown(reply))
        if ENABLE_VOICE: tts_play(reply)
        console.print()
        
if __name__=="__main__":
    main()
