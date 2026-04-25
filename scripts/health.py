#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import get, get_config, print_response

base_url, api_key = get_config()
status, body = get(f"{base_url}/health", api_key)
print_response(status, body)
