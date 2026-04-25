#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_config, post, print_response

base_url, api_key = get_config()
confirm = input("Delete all model files except the current one? (yes/no): ").strip().lower()
if confirm != "yes":
    print("Aborted.")
    sys.exit(0)

status, body = post(f"{base_url}/cleanup_models", api_key, {})
print_response(status, body)
