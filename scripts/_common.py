import json
import urllib.error
import urllib.request
from pathlib import Path


def _load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    env_file = Path(__file__).parent / ".env"
    try:
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env


def get_config() -> tuple[str, str]:
    env = _load_env()
    base_url = env.get("BASE_URL") or input("Base URL (e.g. http://your-vps): ").strip()
    api_key = env.get("API_KEY") or input("API key: ").strip()
    return base_url.rstrip("/"), api_key


def get(url: str, api_key: str, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"X-API-Key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def post(url: str, api_key: str, body: dict, timeout: int = 3600) -> tuple[int, str]:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def print_response(status: int, body: str) -> None:
    print(f"Status: {status}")
    try:
        print(json.dumps(json.loads(body), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(body)
