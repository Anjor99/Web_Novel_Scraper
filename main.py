import subprocess
import os
from bot.bot import run_bot

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    subprocess.Popen(
        ["python", "-m", "bot.auto_send"],
        cwd=PROJECT_ROOT,  # 👈 THIS IS THE FIX
        stdout=open(os.path.join(PROJECT_ROOT, "logs/auto_send.log"), "a"),
        stderr=open(os.path.join(PROJECT_ROOT, "logs/auto_send_error.log"), "a"),
    )

    run_bot()
