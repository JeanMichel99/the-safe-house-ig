# The Safe House — Auto-Poster Setup Guide

One-time setup (~90 min). After this, every post goes live automatically with zero input from you.

---

## What this does

A GitHub Actions workflow runs every Monday, Wednesday, and Friday at 12:00 CEST. It reads `schedule.json`, finds today's post, and publishes it as an Instagram carousel via the Meta Graph API — fully automatically.

Cost: **€0** (GitHub free tier + Meta Graph API free tier).

---

## Prerequisites

- Instagram **Business** or **Creator** account (not a personal account)
- A Facebook **Page** connected to that Instagram account
- A free GitHub account

---

## Part 1 — Meta developer setup (~45 min, once ever)

### 1.1 Create a Meta developer app

1. Go to [developers.facebook.com](https://developers.facebook.com) and log in with your Facebook account.
2. Click **My Apps → Create App**.
3. Use case: **Other** → Next.
4. App type: **Business** → Next.
5. Give it any name (e.g. `the-safe-house-poster`). Click **Create App**.
6. On the dashboard, click **Add Product** → find **Instagram Graph API** → click **Set up**.

### 1.2 Connect your Facebook Page and Instagram account

1. In the left sidebar go to **Instagram Graph API → Getting Started**.
2. Follow the prompts to connect your Facebook Page.
3. Make sure your Instagram Business account is linked to that Page (Instagram app → Settings → Account type → Switch to Professional → link to your Page).

### 1.3 Get a non-expiring System User token

This is the critical step. A regular access token expires in 60 days. A System User token never expires.

1. Go to [Meta Business Suite](https://business.facebook.com) → **Settings** (gear icon, bottom left).
2. In the left menu: **Users → System Users**.
3. Click **Add** → give it a name (e.g. `autoposter`) → Role: **Admin** → Create system user.
4. Click **Generate New Token** on the system user you just created.
5. Select your app (`the-safe-house-poster`).
6. Grant these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
7. Click **Generate Token** and **copy it immediately** — you won't see it again.

### 1.4 Find your Instagram User ID

1. Open this URL in your browser (replace `YOUR_TOKEN`):
   ```
   https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_TOKEN
   ```
2. Find your Page in the response. Note the `id` field — that's your Page ID.
3. Then open:
   ```
   https://graph.facebook.com/v19.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_TOKEN
   ```
4. The `id` inside `instagram_business_account` is your **Instagram User ID**. Save this.

---

## Part 2 — GitHub repo setup (~30 min, once ever)

### 2.1 Create the repository

1. Go to [github.com](https://github.com) → **New repository**.
2. Name: `the-safe-house-ig` (or anything you like).
3. Visibility: **Public** ← important. The Meta API needs to fetch image URLs, and GitHub raw URLs are only publicly accessible for public repos.
4. Click **Create repository**.

### 2.2 Upload the files

Upload everything from this zip into the repo root, maintaining the folder structure:

```
the-safe-house-ig/
├── .github/
│   └── workflows/
│       └── post_instagram.yml   ← the scheduler
├── the-safe-house/
│   └── images/
│       ├── post-01-monday-2026-07-06/
│       │   ├── slide-01-hook.png
│       │   └── ... (8 slides)
│       └── ... (11 more post folders)
├── post_instagram.py            ← the posting script
└── schedule.json                ← the posting schedule
```

You can drag-and-drop the entire folder structure into the GitHub web UI, or use GitHub Desktop if you prefer.

### 2.3 Add your secrets

1. In your repo, go to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret** and add:

| Name | Value |
|------|-------|
| `INSTAGRAM_ACCESS_TOKEN` | The system user token from Step 1.3 |
| `INSTAGRAM_USER_ID` | The numeric ID from Step 1.4 |

### 2.4 Test it manually

1. Go to the **Actions** tab in your repo.
2. Click **Post to Instagram** in the left sidebar.
3. Click **Run workflow → Run workflow**.
4. Watch the logs. If today has no post scheduled you'll see "No post scheduled for [date]. Nothing to do." — that's correct.
5. To test an actual post, temporarily change one entry in `schedule.json` to today's date, run the workflow, then change it back.

---

## Part 3 — Monthly update (5 min per month)

Each month, Cowork generates a new batch:
- New image folders under `the-safe-house/images/`
- A new `schedule.json` (replaces the old one)

You just commit those files to the repo and you're done. GitHub Actions handles the rest automatically.

---

## Troubleshooting

**"Media upload failed"** — The image URL isn't publicly reachable. Make sure the repo is public and the file paths in `schedule.json` exactly match the actual folder/file names.

**"Invalid OAuth access token"** — The token was entered incorrectly in GitHub Secrets. Copy it again from Meta Business Suite.

**Posts not going out** — Check the Actions tab for failed runs. GitHub will email you if a scheduled workflow fails.

**"User not allowed to publish content"** — Your Instagram account needs to be set to Business or Creator (not personal), and linked to a Facebook Page.

---

## Summary

Once set up:
- Cowork generates the monthly batch (runs automatically on last Friday of each month)
- You commit the new images + schedule.json to GitHub (~5 min)
- GitHub posts everything automatically, on time, every week

Total ongoing time per month: **~5 minutes**.
