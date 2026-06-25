# 📊 GitHub Stats Visualizer

Fetches your GitHub repo data using a Personal Access Token and generates a chart showing:
- **Top 10 repos by stars**
- **Language breakdown** across all your repos
- **Original vs Forked** repo split

## Setup

### 1. Install dependencies
```bash
pip install requests matplotlib python-dotenv
```

### 2. Create your `.env` file
```bash
cp .env.example .env
```
Then open `.env` and fill in:
```
GITHUB_PAT=ghp_your_real_token_here
GITHUB_USERNAME=your_github_username
```

### 3. Create a PAT on GitHub
Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**

Required scopes: `read:user`, `public_repo`

### 4. Run it
```bash
python github_viz.py
```

Outputs a `<username>_github_stats.png` file and opens it.

## Project structure
```
github_viz/
├── github_viz.py     ← main script
├── .env.example      ← template (safe to commit)
├── .env              ← your real secrets (NEVER commit)
├── .gitignore        ← keeps .env out of git
└── README.md
```

## Security note
Your `.env` file contains a real PAT — treat it like a password.
- Never commit it (`.gitignore` handles this)
- Never paste it in chat, issues, or Stack Overflow
- If you accidentally expose it, revoke it immediately at `github.com/settings/tokens`
