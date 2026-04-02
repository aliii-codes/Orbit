# Orbit 

**Orbit** is a developer-focused daily digest agent that aggregates activity from GitHub, HuggingFace, Reddit, Dev.to, and GitHub Trending. It generates a concise AI-powered digest and delivers it to your inbox — with a sleek dark GUI to manage everything.

## Features

- **GitHub Activity** — commits, issues, and pull requests for tracked repos
- **HuggingFace Trending** — latest papers and trending models
- **Reddit Highlights** — hot posts from r/MachineLearning, r/artificial, r/learnpython
- **Dev.to Articles** — top articles by tag (python, ai, machinelearning)
- **GitHub Trending** — trending Python repositories daily
- **Email Digest** — AI-summarized digest sent via Gmail SMTP
- **Digest History** — view past digests in the GUI

## Tech Stack

- **Language**: Python 3.10
- **GUI**: PyQt6
- **AI**: Groq (llama-3.3-70b-versatile)
- **Libraries**: `requests`, `beautifulsoup4`, `PyGithub`, `groq`, `python-dotenv`, `schedule`

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/aliii-codes/Orbit.git
   cd Orbit
```

2. Install dependencies with uv:
```bash
   uv sync
```

3. Set up environment variables in a `.env` file:
```env
   GITHUB_TOKEN=your_github_token
   GROQ_API_KEY=your_groq_api_key
   GMAIL_USER=your_gmail@gmail.com
   GMAIL_APP_PASSWORD=your_gmail_app_password
```

## Usage

Run the GUI:
```bash
python main.py
```

- Enter your GitHub username and fetch repos
- Select repos to monitor and save config
- Hit **SEND DIGEST NOW** to generate and email your digest
- View past digests in the **HISTORY** tab

## Project Structure
```
Orbit/
├── Backend/
│   ├── devto_fetcher.py
│   ├── digest_generator.py
│   ├── emailer.py
│   ├── gh_trending_fetcher.py
│   ├── github_fetcher.py
│   ├── hf_fetcher.py
│   ├── reddit_fetcher.py
│   └── scheduler.py
├── Frontend/
│   ├── GUI.py
│   └── Data/
│       └── config.json
├── main.py
└── README.md
```

## License

MIT License