# Orbit 

**Orbit** is a developer-focused daily digest agent that aggregates activity from GitHub, HuggingFace, Reddit, Dev.to, and GitHub Trending. It generates a concise AI-powered digest and delivers it to your inbox — with a sleek dark GUI to manage everything.

## Features

- **GitHub Activity** — commits, issues, and pull requests for tracked repos
- **HuggingFace Trending** — latest papers and trending models
- **Reddit Highlights** — hot posts from configurable subreddits
- **Dev.to Articles** — top articles by configurable tags
- **GitHub Trending** — trending repos for configurable languages
- **Email Digest** — AI-summarized digest sent via Gmail SMTP (with Markdown→HTML rendering)
- **Slack & Discord** — send digests via webhooks
- **Digest Preview** — review the AI digest before sending
- **Digest History** — view, search, and export past digests
- **System Tray** — minimize to tray, scheduler runs in background
- **First-Run Wizard** — guided setup for API keys on first launch
- **Configurable Schedule** — set digest time from the GUI
- **Multi-LLM Support** — Groq, OpenAI, Anthropic, Ollama via LiteLLM
- **Plugin Architecture** — extensible source system for adding new data sources
- **Parallel Fetching** — all sources fetched concurrently for speed
- **Retry Logic** — automatic retries with exponential backoff for API calls
- **Rate Limit Awareness** — GitHub API rate limit checking and auto-wait

## Tech Stack

- **Language**: Python 3.10+
- **GUI**: PyQt6 (dark theme, system tray)
- **AI**: Groq / LiteLLM (multi-provider)
- **Libraries**: `requests`, `beautifulsoup4`, `PyGithub`, `groq`, `litellm`, `mistune`, `tenacity`, `python-dotenv`, `schedule`

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

3. Run the app — a setup wizard will guide you through API keys on first launch:
```bash
   python main.py
```

Or manually create a `.env` file:
```env
   GITHUB_TOKEN=your_github_token
   GROQ_API_KEY=your_groq_api_key
   GMAIL_USER=your_gmail@gmail.com
   GMAIL_APP_PASSWORD=your_gmail_app_password
```

## Usage

- Enter your GitHub username and fetch repos
- Select repos to monitor and save config
- Hit **SEND DIGEST NOW** to generate a digest (preview before sending)
- View past digests in the **HISTORY** tab (search & export)
- Configure sources, schedule time, and notification channels in **SETTINGS**
- Close the window to minimize to system tray — scheduler keeps running

## Project Structure
```
Orbit/
├── Backend/
│   ├── config.py              # Shared config/history management
│   ├── devto_fetcher.py       # Dev.to API fetcher
│   ├── digest_generator.py    # LLM-powered digest generation
│   ├── emailer.py             # Email/Slack/Discord notifications
│   ├── gh_trending_fetcher.py # GitHub Trending scraper
│   ├── github_fetcher.py      # GitHub repo activity fetcher
│   ├── hf_fetcher.py          # HuggingFace papers & models
│   ├── reddit_fetcher.py      # Reddit hot posts fetcher
│   ├── scheduler.py           # Daily schedule runner
│   └── sources/               # Plugin architecture
│       ├── base.py            # SourcePlugin ABC
│       ├── github_source.py
│       ├── hf_source.py
│       ├── reddit_source.py
│       ├── devto_source.py
│       └── gh_trending_source.py
├── Frontend/
│   ├── GUI.py                 # PyQt6 main window, tray, preview, wizard
│   └── Data/
│       ├── config.json
│       └── history.json
├── tests/                     # pytest test suite
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_hf_fetcher.py
│   ├── test_reddit_fetcher.py
│   ├── test_devto_fetcher.py
│   ├── test_digest_generator.py
│   └── test_emailer.py
├── Orbit.spec                 # PyInstaller build spec
├── main.py                    # Entry point
└── pyproject.toml
```

## Testing

```bash
uv run pytest tests/ -v
```

## Building a Standalone Executable

```bash
uv run pyinstaller Orbit.spec
```

Output: `dist/Orbit.exe` (Windows) — a single-file executable with no console window.

## License

MIT License