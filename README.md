# termux-ai



# 1. Clone repo
git clone <https://github.com/ChethiyaMD/termux-ai.git> chethiya-md
cd chethiya-md

# 2. Setup venv (optional)
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy .env
cp .env.example .env
nano .env   # set OPENAI_API_KEY

# 5a. Run CLI (Terminal + Voice)
python main.py

# 5b. Run Web UI
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# 5c. Run via Docker
docker-compose up -d
