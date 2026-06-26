#!/usr/bin/env python3
"""
The Safe House — Instagram Auto-Poster
Reads schedule.json, finds today's post, posts as a carousel via Meta Graph API.

Required environment variables (set as GitHub Secrets):
  INSTAGRAM_ACCESS_TOKEN  — non-expiring system user token
  INSTAGRAM_USER_ID       — numeric Instagram Business user ID
  GITHUB_RAW_BASE         — set automatically by the Actions workflow
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────
ACCESS_TOKEN   = os.environ["INSTAGRAM_ACCESS_TOKEN"]
IG_USER_ID     = os.environ["INSTAGRAM_USER_ID"]
REPO_RAW_BASE  = os.environ["GITHUB_RAW_BASE"]   # e.g. https://raw.githubusercontent.com/yourname/the-safe-house-ig/main
API_BASE       = "https://graph.facebook.com/v19.0"


# ── Helpers ───────────────────────────────────────────────────────────────────
def belgium_today() -> str:
    """Return today's date in Belgium (CEST/CET) as YYYY-MM-DD."""
    now_utc = datetime.now(timezone.utc)
    # CEST (UTC+2): last Sunday March → last Sunday October
    # Rough approximation sufficient for a daily scheduler
    month = now_utc.month
    offset = 2 if 3 < month < 11 else 1
    local_dt = now_utc + timedelta(hours=offset)
    return local_dt.date().isoformat()


def api_post(endpoint: str, params: dict) -> dict:
    params["access_token"] = ACCESS_TOKEN
    resp = requests.post(f"{API_BASE}/{endpoint}", params=params, timeout=30)
    if not resp.ok:
        print(f"  API error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
    return resp.json()


def create_image_container(image_url: str) -> str:
    """Upload a single image as a carousel item and return its container ID."""
    data = api_post(
        f"{IG_USER_ID}/media",
        {"image_url": image_url, "is_carousel_item": "true"},
    )
    return data["id"]


def create_carousel_container(children: list[str], caption: str) -> str:
    """Create a carousel container from a list of child container IDs."""
    data = api_post(
        f"{IG_USER_ID}/media",
        {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption},
    )
    return data["id"]


def publish(container_id: str) -> str:
    """Publish a media container and return the published media ID."""
    data = api_post(
        f"{IG_USER_ID}/media_publish",
        {"creation_id": container_id},
    )
    return data["id"]


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    today = belgium_today()
    print(f"Date (Belgium): {today}")

    with open("schedule.json") as f:
        schedule = json.load(f)

    post = next((p for p in schedule["posts"] if p["date"] == today), None)

    if not post:
        print(f"No post scheduled for {today}. Nothing to do.")
        sys.exit(0)

    print(f"Posting: {post['title']}")

    # Step 1 — upload each slide as a carousel item
    child_ids = []
    for i, slide_path in enumerate(post["slides"]):
        url = f"{REPO_RAW_BASE}/{slide_path}"
        print(f"  [{i+1}/8] Uploading {Path(slide_path).name}")
        cid = create_image_container(url)
        child_ids.append(cid)
        time.sleep(2)   # rate-limit breathing room

    # Step 2 — assemble carousel container
    print("Creating carousel container…")
    carousel_id = create_carousel_container(child_ids, post["caption"])

    # Step 3 — short wait recommended by Meta before publishing
    print("Waiting 8 s before publishing…")
    time.sleep(8)

    # Step 4 — publish
    print("Publishing…")
    media_id = publish(carousel_id)
    print(f"Done. Media ID: {media_id}")


if __name__ == "__main__":
    main()
