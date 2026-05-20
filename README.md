# বাংলা ভয়েস | Bangla Voice — Setup Guide / সেটআপ গাইড

A real online newspaper that:
- ✅ Opens every news story **inside your own site** (no redirect to other websites)
- ✅ Has a **big newspaper name pinned at the top**
- ✅ **Auto-updates daily** from free Bangla / Bangladesh news sources

আপনার এই নিউজপেপারটি এখন একটি সত্যিকারের অনলাইন পত্রিকা — খবরে ক্লিক করলে নিজের সাইটেই সম্পূর্ণ খবর খুলবে, এবং প্রতিদিন স্বয়ংক্রিয়ভাবে নতুন খবর আসবে।

---

## 📁 What's in this folder / এই ফোল্ডারে যা আছে

| File | কী কাজ করে |
|------|-----------|
| `index.html` | The newspaper website itself / মূল ওয়েবসাইট |
| `news.json` | The news data the site reads / সাইট যে খবরগুলো দেখায় |
| `update_news.py` | Fetches fresh news and rewrites `news.json` / নতুন খবর এনে দেয় |
| `.github/workflows/update-news.yml` | Free daily automation / বিনামূল্যে প্রতিদিন আপডেট |

> **Important:** `index.html` and `news.json` must always stay in the **same folder**.

---

## ⚠️ One thing to know first / প্রথমে একটি গুরুত্বপূর্ণ কথা

If you just **double-click `index.html`**, your browser blocks it from reading `news.json` (a browser security rule). The page will load but show "news.json পাওয়া যায়নি".

**The fix is easy** — you just need to *serve* the folder. Pick any option below.

---

## ✅ Option 1 — Quick view on your own computer (2 minutes)

This is the fastest way to see it working locally.

1. Install **Python** (if you don't have it): https://www.python.org/downloads/
2. Open a terminal / command prompt **inside this folder**.
3. Run:
   ```
   python -m http.server 8000
   ```
   *(On Mac, you may need `python3` instead of `python`.)*
4. Open your browser and go to: **http://localhost:8000**

That's it — the newspaper loads with full clickable articles. 🎉

---

## 🔄 Option 2 — Update the news yourself (manual)

To pull the latest real news any time:

1. Install the one dependency (only needed once):
   ```
   pip install feedparser
   ```
2. Run the updater:
   ```
   python update_news.py
   ```
3. It rewrites `news.json` with the newest headlines. Refresh the site — done.

**Sources included:** Prothom Alo, bdnews24, Bangla Tribune, Jugantor, Jagonews24, Kaler Kantho, BanglaNews24, Risingbd, BBC Bangla.

**Add or remove sources** by editing the `FEEDS` list near the top of `update_news.py`. Each entry looks like:
```python
{"name": "প্রথম আলো", "en": "Prothom Alo", "category": "জাতীয়", "url": "https://www.prothomalo.com/feed/"},
```
If a feed ever stops working, the script just skips it — the others keep running.

---

## 🌍 Option 3 — Free hosting + automatic daily updates (recommended)

Put it online for free, and let it update itself every day with **zero cost and no server**. Uses GitHub Pages + GitHub Actions.

### Step 1 — Create a free GitHub account
Go to https://github.com and sign up (free).

### Step 2 — Create a new repository
- Click **New repository**
- Name it anything, e.g. `bangla-voice`
- Make it **Public**
- Click **Create repository**

### Step 3 — Upload these files
- On the repo page click **Add file → Upload files**
- Drag in **all** the files from this folder, including the `.github` folder.
  - *(If GitHub hides the `.github` folder when dragging, upload `index.html`, `news.json`, and `update_news.py` first, then create the workflow file manually: **Add file → Create new file**, name it `.github/workflows/update-news.yml`, and paste the contents.)*
- Click **Commit changes**

### Step 4 — Turn on GitHub Pages
- Go to repo **Settings → Pages**
- Under **Build and deployment → Source**, choose **GitHub Actions**

### Step 5 — Let it run
- Go to the **Actions** tab
- Click the **"Update Bangla Voice News Daily"** workflow → **Run workflow** (to do it once now)
- After it finishes, your live site is at:
  **`https://YOUR-USERNAME.github.io/bangla-voice/`**

From now on it **updates by itself** 4 times a day (00:00, 06:00, 12:00, 18:00 UTC). Want a different schedule? Edit the `cron:` lines in `.github/workflows/update-news.yml`.

> **Tip:** To use your own domain (e.g. `banglavoice.com`), go to Settings → Pages → Custom domain.

---

## 🎨 How the site works (for your reference)

- **Click any headline / card / ticker item → full article opens inside the site.** The URL becomes something like `…/#article/abc123`, so articles are shareable and the browser Back button works.
- **Each article shows a link back to the original publisher** (in the "ORIGINAL SOURCE" box) so readers can read the complete report there if they wish. This keeps you compliant — you show a summary + credit, and link to the source.
- **Search** (top right) filters the loaded articles instantly.
- **Images:** if a feed provides an image, it's shown; if not, a clean red "বাংলা ভয়েস" placeholder appears automatically.

---

## 📝 Changing your branding

Open `index.html` in any text editor and search for:
- `বাংলা ভয়েস` — your paper's Bangla name
- `BANGLA VOICE` — English name
- `A Publication of ABC VOICE` — publisher line
- `shamimnyusa@gmail.com` and `347-541-6141` — contact info

Change those and save.

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "news.json পাওয়া যায়নি" | You opened the file directly. Use **Option 1** (serve it) instead of double-clicking. |
| `update_news.py` shows 0 articles | Your network/firewall may be blocking the feeds, or a feed is briefly down. Try again, or rely on GitHub Actions (Option 3). |
| `pip` or `python` not found | Install Python from python.org and reopen your terminal. On Mac/Linux try `python3` / `pip3`. |
| Want more articles per page | In `update_news.py`, raise `MAX_TOTAL` and `MAX_PER_SOURCE`. |

---

*সত্যের পথে, জনতার সাথে — Bangla Voice, A Publication of ABC VOICE.*
