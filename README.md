# Gift Market Bot

This is a complete Telegram NFT gift marketplace bot built using Python, aiogram 3.x, PostgreSQL, SQLAlchemy, Alembic, and Redis.

## Getting Started

### 1. Configure the Environment
Copy the `\.env.example` file to a new file named `\.env` and replace the placeholder values with your real keys.
```bash
cp .env.example .env
```

Ensure you configure the `MANIFEST_URL` pointing to your TonConnect manifest JSON file, for instance using a public manifest like:
`https://raw.githubusercontent.com/ton-community/tutorials/main/03-client/test/public/tonconnect-manifest.json`

### 2. Run with Docker Compose
The recommended way to run this application is via Docker Compose.
```bash
docker compose up --build -d
```

### 3. Run Locally (SQLite)
Alternatively, you can run the bot natively with SQLite, ensuring you have Redis running in the background for storage:
```bash
DB_HOST=sqlite alembic upgrade head
DB_HOST=sqlite python main.py
```
