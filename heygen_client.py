# heygen_client.py
import time
import json
from typing import Any, Dict, Optional

import requests


HEYGEN_API_BASE = "https://api.heygen.com"
# You can pass in the key explicitly, or pull from env / Streamlit secrets.
# For CourseCreator + Streamlit, you'll probably do:
#   import streamlit as st
#   HEYGEN_API_KEY = st.secrets["HEYGEN_API_KEY"]
HEYGEN_API_KEY: Optional[str] = None


class HeyGenError(Exception):
    pass


def _get_headers() -> Dict[str, str]:
    if not HEYGEN_API_KEY:
        raise HeyGenError("HEYGEN_API_KEY is not set in heygen_client.HEYGEN_API_KEY")
    return {
        "x-api-key": HEYGEN_API_KEY,  # documented header name
        "accept": "application/json",
        "Content-Type": "application/json",
    }


def list_avatars() -> Dict[str, Any]:
    """
    List all available avatars (including your own). Mainly for setup / admin UI.
    GET /v2/avatars
    """
    url = f"{HEYGEN_API_BASE}/v2/avatars"
    resp = requests.get(url, headers=_get_headers())
    if not resp.ok:
        raise HeyGenError(f"List avatars failed: {resp.status_code} {resp.text}")
    return resp.json()


def list_voices() -> Dict[str, Any]:
    """
    List all available voices so you can choose a default.
    GET /v2/voices
    """
    url = f"{HEYGEN_API_BASE}/v2/voices"
    resp = requests.get(url, headers=_get_headers())
    if not resp.ok:
        raise HeyGenError(f"List voices failed: {resp.status_code} {resp.text}")
    return resp.json()


def create_avatar_video(
    script_text: str,
    avatar_id: str,
    voice_id: str,
    *,
    test: bool = False,
    width: int = 1280,
    height: int = 720,
    background_color: str = "#FFFFFF",
) -> str:
    """
    Create an avatar video for a single script.

    Returns:
        video_id (string) you can use with the status endpoint.
    """
    url = f"{HEYGEN_API_BASE}/v2/video/generate"

    payload: Dict[str, Any] = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script_text,
                    "voice_id": voice_id,
                    # You can add "speed" or "pitch" here if you want later.
                },
                "background": {
                    "type": "color",
                    "value": background_color,
                },
            }
        ],
        "dimension": {"width": width, "height": height},
        "aspect_ratio": "16:9",
        "test": test,
    }

    resp = requests.post(url, headers=_get_headers(), data=json.dumps(payload))
    if not resp.ok:
        raise HeyGenError(f"Create avatar video failed: {resp.status_code} {resp.text}")

    data = resp.json()
    # Per HeyGen docs, the response returns a video_id you then use to check status.
    video_id = data.get("data", {}).get("video_id") or data.get("video_id")
    if not video_id:
        raise HeyGenError(f"video_id not found in response: {data}")
    return video_id


def get_video_status(video_id: str) -> Dict[str, Any]:
    """
    Retrieve video status and URLs.
    GET /v1/video_status.get?video_id=...
    """
    url = f"{HEYGEN_API_BASE}/v1/video_status.get"
    params = {"video_id": video_id}
    resp = requests.get(url, headers=_get_headers(), params=params)
    if not resp.ok:
        raise HeyGenError(f"Get video status failed: {resp.status_code} {resp.text}")
    return resp.json()


def wait_for_video(
    video_id: str,
    *,
    poll_interval: int = 5,
    timeout_seconds: int = 600,
) -> Dict[str, Any]:
    """
    Polls status until video is 'completed' or 'failed', or times out.

    Returns:
        Final status JSON. Look for status + video_url in the response.
    """
    start = time.time()
    while True:
        status_data = get_video_status(video_id)
        status = (
            status_data.get("data", {}).get("status")
            or status_data.get("status")
        )
        if status in {"completed", "failed"}:
            return status_data

        if time.time() - start > timeout_seconds:
            raise HeyGenError(f"Timeout waiting for video {video_id}; last status: {status_data}")

        time.sleep(poll_interval)
