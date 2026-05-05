# Orbit 🪐

**Your daily developer digest, delivered.**

![GitHub stars](https://img.shields.io/github/stars/aliii-codes/Orbit?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/aliii-codes/Orbit?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/aliii-codes/Orbit?style=for-the-badge)
![License](https://img.shields.io/github/license/aliii-codes/Orbit?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-orange?style=for-the-badge&logo=qt)
![Groq](https://img.shields.io/badge/Groq-AI-brightgreen?style=for-the-badge&logo=groq)
![LiteLLM](https://img.shields.io/badge/LiteLLM-Multi--LLM-purple?style=for-the-badge)

---

## 🚀 Highlights in v0.2.0

- **Multi-LLM Support** 🎉  
  Use Groq, OpenAI, Anthropic, or Ollama via LiteLLM for digest generation.
- **Plugin Architecture** 🧩  
  Extensible source system for adding new data sources.
- **Parallel Fetching** ⚡  
  All sources fetched concurrently for faster performance.
- **Rate Limit Awareness** 🛡️  
  Auto-waits when GitHub API rate limits are hit.

---

## ✨ Features

| Category | Features |
|----------|----------|
| 🔗 **Data Sources** | **GitHub activity** (commits, PRs, issues), **HuggingFace trending** (papers & models), **Reddit highlights** (configurable subreddits), **Dev.to articles** (by tags), **GitHub Trending** (by language) |
| 📬 **Digest Delivery** | **Email digest** (Markdown→HTML via Gmail SMTP), **Slack & Discord** webhooks, **Digest preview** before sending |
| 🎛️ **Customization & Control** | **Configurable schedule**, **Multi‑LLM support** (Groq, OpenAI, Anthropic, Ollama via LiteLLM), **Plugin architecture** for custom sources |
| 🖥️ **UI & Experience** | **First‑run wizard** for API keys, **Digest history** (search/export), **System tray** with background scheduler |
| ⚡ **Performance & Reliability** | **Parallel fetching** for speed, **Retry logic** with exponential backoff, **Rate limit awareness** with auto‑wait |


## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Core** | Python 3.10+, PyQt6, Groq/LiteLLM |
| **Data Fetching** | `requests`, `beautifulsoup4`, `PyGithub` |
| **Utilities** | `mistune`, `tenacity`, `python-dotenv`, `schedule` |
| **Testing** | `pytest`, `pytest-qt`, `responses` |

## 🚀 Installation

1. **Clone & Install**  
   ```bash
   git clone https://github.com/aliii-codes/Orbit.git
   cd Orbit
   uv sync  # or pip install -r requirements.txt
   ```

2. **Environment Variables**  
   Create a `.env` file:
   ```env
   GITHUB_TOKEN=your_github_token
   GROQ_API_KEY=your_groq_api_key
   GMAIL_USER=your_gmail@gmail.com
   GMAIL_APP_PASSWORD=your_gmail_app_password
   ```

3. **Run**  
   ```bash
   python main.py
   ```
   *First-run wizard will guide you through setup*

## ▶️ Usage

| Action | Command/Steps |
|--------|---------------|
| **Fetch Repos** | Enter GitHub username → Click "FETCH REPOS" |
| **Monitor Repos** | Select repos → Click "+ ADD SELECTED" |
| **Send Digest** | Click "SEND DIGEST NOW" → Review preview → Confirm |
| **View History** | Switch to HISTORY tab → Search/export digests |
| **Configure** | SETTINGS tab → Adjust sources, schedule, notifications |

## 📁 Project Structure
```
Orbit/
├── Backend/                      # Core logic & data sources
│   ├── config.py                 # Shared config & history management
│   ├── digest_generator.py       # LLM-powered digest creation
│   ├── emailer.py                # Email, Slack, Discord notifications
│   ├── devto_fetcher.py          # Dev.to API fetcher
│   ├── gh_trending_fetcher.py    # GitHub Trending scraper
│   ├── github_fetcher.py         # GitHub repo activity (commits, PRs, issues)
│   ├── hf_fetcher.py             # HuggingFace papers & models
│   ├── reddit_fetcher.py         # Reddit hot posts fetcher
│   ├── scheduler.py              # Daily schedule runner (background)
│   └── sources/                  # Plugin architecture
│       ├── base.py               # SourcePlugin abstract base class
│       ├── github_source.py
│       ├── hf_source.py
│       ├── reddit_source.py
│       ├── devto_source.py
│       └── gh_trending_source.py
├── Frontend/                     # GUI
│   ├── GUI.py                    # PyQt6 main window, tray, preview, first-run wizard
│   └── Data/
│       ├── config.json
│       └── history.json
├── tests/                        # pytest test suite
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_hf_fetcher.py
│   ├── test_reddit_fetcher.py
│   ├── test_devto_fetcher.py
│   ├── test_digest_generator.py
│   └── test_emailer.py
├── Orbit.spec                    # PyInstaller build spec
├── main.py                       # Entry point
└── pyproject.toml
```
## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -m 'Add fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Open a pull request

## 🐞 Bug Reports & Feature Requests

Use the [issue tracker](https://github.com/aliii-codes/Orbit/issues) for:
- Bug reports (use the bug template)
- Feature requests (use the feature template)

## 📜 License

[MIT License](LICENSE)

**Acknowledgements**  
Built with ❤️ using PyQt6, Groq, LiteLLM, and many other open-source libraries. Special thanks to the maintainers of these projects.
