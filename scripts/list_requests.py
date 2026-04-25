#!/usr/bin/env python3
import sys
import tempfile
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get, get_config

base_url, api_key = get_config()
status, body = get(f"{base_url}/requests", api_key)

if status != 200:
    print(f"Status: {status}")
    print(body)
    sys.exit(1)

tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
tmp.write(body)
tmp.close()

print(f"Opening {tmp.name} in browser...")
webbrowser.open(f"file://{tmp.name}")
