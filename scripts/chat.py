#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_config, post, print_response

base_url, api_key = get_config()
user_prompt = input("User prompt: ").strip()

status, body = post(f"{base_url}/chat", api_key, {"user_prompt": user_prompt})
print_response(status, body)
