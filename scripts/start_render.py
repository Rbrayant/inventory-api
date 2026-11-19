"""Initialize Render storage and start the inventory API."""
import os
import subprocess
import sys

os.environ["APP_REVISION"] = os.getenv("RENDER_GIT_COMMIT", "render")

subprocess.run(
    [sys.executable, "-m", "flask", "--app", "app.main", "init-db"],
    check=True,
)

os.execvp("gunicorn", [
    "gunicorn",
    "--bind", "0.0.0.0:" + os.getenv("PORT", "10000"),
    "--workers", "2",
    "app.main:app",
])
