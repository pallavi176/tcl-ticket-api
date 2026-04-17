"""Container entrypoint: bind to PORT from the environment (Railway, Render, Fly, etc.).

Railway may invoke a custom start command with a literal ``$PORT`` string (no shell
expansion), which breaks ``uvicorn --port $PORT``. Reading the port in Python avoids that.
"""

import os

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
