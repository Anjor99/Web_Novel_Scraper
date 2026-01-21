# WebNovel PDF Telegram Bot
[![Telegram](https://img.shields.io/badge/Telegram-Open%20Bot-blue?logo=telegram)](https://t.me/Anjor_pdf_buddy_bot)
> 🧪 **Fun fact:** This bot is proudly hosted on my old Android phone using Termux.  
> If it ever goes offline, the phone probably needed charging 🔋😄


A production-grade, job-based Telegram bot that scrapes web novels chapter-by-chapter, generates professional PDFs, and delivers them directly to users with real-time progress tracking and automatic fault recovery.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-Latest-blue.svg)](https://core.telegram.org/bots/api)

## Overview

This bot provides a seamless experience for downloading web novels as properly formatted PDFs. Built with reliability and scalability in mind, it handles long-running scraping operations while providing users with real-time feedback through an intuitive Telegram interface.

### Key Features

- **🤖 Interactive Telegram Interface** - Inline buttons and commands for effortless navigation
- **📖 Chapter-wise Scraping** - Efficient, granular content retrieval
- **📄 High-Quality PDF Generation** - Professional formatting and layout
- **📊 Real-time Progress Tracking** - Visual progress bars via `/status` command
- **🔁 Intelligent Retry Logic** - Automatic recovery from network failures
- **♻️ Crash-safe Architecture** - Jobs survive bot restarts
- **🗂️ Multi-user Support** - Concurrent job processing per user
- **🧹 Automatic Cleanup** - Self-managing file system
- **📦 Zero-database Design** - File-based persistence for simplicity

## Architecture

```
┌─────────────────┐
│  Telegram Bot   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Job Creation   │
│ (novel_flow.py) │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│ Background Scraper   │
│   (subprocess)       │
│                      │
│  • Scrapes chapters  │
│  • Updates progress  │
│  • Generates PDF     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Auto-Send Worker    │
│                      │
│  • Detects new PDFs  │
│  • Sends to users    │
│  • Cleanup files     │
└──────────────────────┘
```

**Design Principles:**
- Restart-safe operations
- Database-free architecture
- Event-driven PDF delivery
- Comprehensive error handling

## Project Structure

```
webnovel_pdf_bot/
│
├── main.py                      # Application entry point
│
├── bot/
│   ├── bot.py                   # Telegram bot initialization
│   ├── handlers.py              # Command and message handlers
│   ├── state.py                 # User state management
│   └── auto_send.py             # Automated PDF delivery service
│
├── scraper/
│   └── chapter_scraper.py       # Chapter scraping and PDF generation
│
├── registry/
│   └── novel_registry.py        # Novel catalog management
│
├── flow/
│   └── novel_flow.py            # Job orchestration layer
│
├── config/
│   └── settings.py              # Configuration and environment loading
│
├── utils/
│   ├── logger.py                # Centralized logging
│   └── validator.py             # Input validation utilities
│
├── jobs/                        # Job state tracking (JSON)
├── outputs/                     # Generated PDF storage
├── backups/                     # Optional PDF archiving
│
├── requirements.txt             # Python dependencies
├── .env                         # Environment configuration
└── README.md                    # Project documentation
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token ([obtain from @BotFather](https://t.me/botfather))
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/webnovel-pdf-bot.git
   cd webnovel-pdf-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   OUTPUT_DIR=outputs
   JOB_DIR=jobs
   CHECK_OUTPUT_INTERVAL=5
   ```

   ⚠️ **Security Note:** Never commit `.env` to version control. Add it to `.gitignore`.

## Usage

### Starting the Bot

1. **Launch the main bot process**
   ```bash
   python main.py
   ```
   
   This initializes:
   - Telegram polling service
   - Job handler
   - Message router

2. **Start the auto-send worker** (in a separate terminal)
   ```bash
   python -m bot.auto_send
   ```
   
   This worker:
   - Monitors for completed PDFs
   - Delivers files to users
   - Performs cleanup operations
   - Recovers unsent PDFs on restart

### Telegram Commands

#### `/start`
Begin interaction and access the novel selection menu.

#### Chapter Download Flow
1. Select a novel from the inline menu
2. Enter start chapter number
3. Enter end chapter number
4. Job launches in background

#### `/status`
Monitor progress of active jobs.

**Example output for running job:**
```
📖 My Werewolf System
Job: 1768572917
[██████░░░░] 63%
Chapter 1520 / 1687
Status: ⏳ running
```

**Example output for failed job:**
```
📖 My Werewolf System
Job: 1768572917
Status: ❌ failed
Error: Chapter text not found
```

## Job Management

### Job Lifecycle

Jobs progress through the following states:
- `running` - Actively scraping and generating PDF
- `completed` - Successfully finished, PDF ready
- `failed` - Encountered unrecoverable error

### Job State Files

Each job is tracked via `jobs/<job_id>.json`:

```json
{
  "job_id": "1768572917",
  "chat_id": "7511978276",
  "novel": "My Werewolf System",
  "start": 1,
  "end": 25,
  "current": 14,
  "status": "running"
}
```

## Fault Tolerance

The system is designed for reliability:

| Scenario | Behavior |
|----------|----------|
| Scraper crashes | Job marked as `failed` |
| Bot restarts | Active jobs remain queryable |
| Auto-send restarts | Unsent PDFs automatically delivered |
| Network failures | Automatic retry with exponential backoff |
| Partial job files | Safely ignored, no corruption |

**No job progress is lost during failures or restarts.**

## Debugging

### Troubleshooting Checklist

1. **Check job states**
   ```bash
   ls jobs/
   cat jobs/<job_id>.json
   ```

2. **Verify PDF generation**
   ```bash
   ls outputs/
   ```

3. **Review logs**
   - Look for `[JOB <id>]` entries
   - Check error messages and stack traces

4. **Monitor active
