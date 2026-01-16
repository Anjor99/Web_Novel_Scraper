import subprocess
from bot.bot import run_bot

if __name__ == "__main__":
    # Start auto sender in background
    subprocess.Popen(
        ["python", "-m", "bot.auto_send"],
        stdout=open("logs/auto_send.log", "a"),
        stderr=open("logs/auto_send_error.log", "a")
    )

    # Start Telegram bot
    run_bot()
