"""Allow running as `python -m celebi`.

The frozen bundle (PyInstaller) reuses this entry point to host the
background servers as child processes of the same binary:

    celebi --serve-proxy                  # FastAPI proxy (ports via env)
    celebi --serve-litellm --config <yaml> --port <n>   # LiteLLM proxy

This keeps per-project env isolation without needing `uv` or a system
Python on the user's machine.
"""

import argparse
import os
import sys
from pathlib import Path


def _find_api_dir() -> Path:
    """Locate the bundled `api/` dir.

    `__file__` is unreliable for the frozen entry script, so probe every
    plausible base: sys._MEIPASS, the frozen exe dir (+ _internal), and the
    source-tree layout. Returns the first candidate containing app/main.py.
    """
    candidates: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(meipass)
        candidates += [base / "api", base / "_internal" / "api"]
    exe = Path(sys.executable).resolve()
    if exe.name and exe.parent != Path("."):
        candidates += [exe.parent / "api", exe.parent / "_internal" / "api"]
    # Source checkout: <repo>/celebi/__main__.py -> <repo>/api
    candidates.append(Path(__file__).resolve().parent.parent / "api")

    seen = []
    for cand in candidates:
        marker = cand / "app" / "main.py"
        seen.append(str(cand))
        if marker.is_file():
            return cand
    raise FileNotFoundError(
        "Could not locate bundled api/ dir (looked for app/main.py in: " + ", ".join(seen) + ")"
    )


def _serve_proxy() -> int:
    proxy_port = int(os.environ.get("CELEBI_PROXY_PORT", "8000"))
    api_dir = _find_api_dir()
    print(f"[celebi] serving proxy API from {api_dir}", flush=True)
    if str(api_dir) not in sys.path:
        sys.path.insert(0, str(api_dir))

    from uvicorn import Config, Server

    from app.main import app

    server = Server(Config(app=app, host="127.0.0.1", port=proxy_port, log_level="info"))
    server.run()
    return 0


def _serve_litellm(config_path: str, port: int) -> int:
    # litellm's proxy startup loads the YAML pointed to by CONFIG_FILE_PATH.
    os.environ["CONFIG_FILE_PATH"] = config_path

    from litellm.proxy.proxy_server import app
    from uvicorn import Config, Server

    server = Server(Config(app=app, host="127.0.0.1", port=port, log_level="info"))
    server.run()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="celebi", add_help=False)
    parser.add_argument("--serve-proxy", action="store_true")
    parser.add_argument("--serve-litellm", action="store_true")
    parser.add_argument("--config", default=None)
    parser.add_argument("--port", default=None)
    args, _unknown = parser.parse_known_args()

    if args.serve_proxy:
        return _serve_proxy()
    if args.serve_litellm:
        if not args.config or not args.port:
            print("error: --serve-litellm requires --config <yaml> --port <n>", file=sys.stderr)
            return 2
        return _serve_litellm(args.config, int(args.port))

    from celebi.app import main as gui_main

    gui_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
