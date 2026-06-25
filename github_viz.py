"""
github_viz.py — Visualize a GitHub user's repo stats using their PAT
Fetches real data from the GitHub API and plots 3 charts.

Setup:
    1. cp .env.example .env
    2. Fill in GITHUB_PAT and GITHUB_USERNAME in .env
    3. pip install requests matplotlib python-dotenv
    4. python github_viz.py
"""

import os
import sys
import requests
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dotenv import load_dotenv
from collections import Counter

# ── Load credentials from .env ─────────────────────────────────────────────
load_dotenv()

PAT      = os.getenv("GITHUB_PAT")
USERNAME = os.getenv("GITHUB_USERNAME")

if not PAT or PAT == "ghp_your_token_here":
    sys.exit("❌  Set GITHUB_PAT in your .env file first.")
if not USERNAME or USERNAME == "your_username_here":
    sys.exit("❌  Set GITHUB_USERNAME in your .env file first.")

# ── GitHub API helpers ─────────────────────────────────────────────────────
HEADERS = {
    "Authorization": f"Bearer {PAT}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def get_repos():
    """Fetch all public repos for the user (handles pagination)."""
    repos, page = [], 1
    while True:
        resp = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            headers=HEADERS,
            params={"per_page": 100, "page": page, "sort": "updated"},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos

def get_user():
    """Fetch the user's profile info."""
    resp = requests.get(f"https://api.github.com/users/{USERNAME}", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# ── Fetch data ─────────────────────────────────────────────────────────────
print(f"🔍  Fetching data for @{USERNAME}...")
user  = get_user()
repos = get_repos()
print(f"✅  Found {len(repos)} repos")

# ── Crunch numbers ─────────────────────────────────────────────────────────
# Top 10 repos by stars
top_starred = sorted(repos, key=lambda r: r["stargazers_count"], reverse=True)[:10]
star_names  = [r["name"] for r in top_starred]
star_counts = [r["stargazers_count"] for r in top_starred]

# Language breakdown (ignore None)
lang_counts = Counter(r["language"] for r in repos if r["language"])
top_langs   = lang_counts.most_common(8)
lang_names  = [l[0] for l in top_langs]
lang_vals   = [l[1] for l in top_langs]

# Fork vs original breakdown
forked   = sum(1 for r in repos if r["fork"])
original = len(repos) - forked

# ── Plot ───────────────────────────────────────────────────────────────────
DARK    = "#0d1117"   # GitHub dark bg
CARD    = "#161b22"   # card bg
BORDER  = "#30363d"   # subtle border
GREEN   = "#3fb950"   # GitHub green
BLUE    = "#58a6ff"   # GitHub blue
PURPLE  = "#bc8cff"   # accent
MUTED   = "#8b949e"   # secondary text
WHITE   = "#e6edf3"   # primary text

LANG_COLORS = [GREEN, BLUE, PURPLE, "#f78166", "#ffa657", "#79c0ff", "#56d364", "#d2a8ff"]

fig = plt.figure(figsize=(14, 9), facecolor=DARK)
fig.suptitle(
    f"@{USERNAME}  ·  GitHub Stats",
    fontsize=18, fontweight="bold", color=WHITE,
    fontfamily="monospace", y=0.97
)

# Profile line under title
followers = user.get("followers", 0)
following = user.get("following", 0)
pub_repos = user.get("public_repos", len(repos))
fig.text(
    0.5, 0.925,
    f"{pub_repos} repos  ·  {followers} followers  ·  {following} following",
    ha="center", fontsize=10, color=MUTED, fontfamily="monospace"
)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35,
                       left=0.07, right=0.96, top=0.88, bottom=0.08)

# ── Chart 1: Top repos by stars (horizontal bar) ──────────────────────────
ax1 = fig.add_subplot(gs[0, :])   # full top row
ax1.set_facecolor(CARD)
for spine in ax1.spines.values():
    spine.set_edgecolor(BORDER)

bars = ax1.barh(star_names[::-1], star_counts[::-1], color=GREEN, height=0.6)

# Value labels
for bar, val in zip(bars, star_counts[::-1]):
    ax1.text(bar.get_width() + max(star_counts) * 0.01, bar.get_y() + bar.get_height() / 2,
             f"★ {val}", va="center", ha="left", color=GREEN, fontsize=8, fontfamily="monospace")

ax1.set_title("Top Repos by Stars", color=WHITE, fontsize=11,
              fontfamily="monospace", pad=8, loc="left")
ax1.tick_params(colors=MUTED, labelsize=8)
ax1.xaxis.label.set_color(MUTED)
ax1.set_xlabel("Stars", color=MUTED, fontsize=8)
ax1.set_xlim(0, max(star_counts) * 1.18 if star_counts else 1)
plt.setp(ax1.get_yticklabels(), fontfamily="monospace", color=WHITE)
plt.setp(ax1.get_xticklabels(), color=MUTED)
ax1.grid(axis="x", color=BORDER, linewidth=0.5, alpha=0.5)
ax1.set_axisbelow(True)

# ── Chart 2: Language breakdown (bar chart) ───────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor(CARD)
for spine in ax2.spines.values():
    spine.set_edgecolor(BORDER)

if lang_names:
    colors = LANG_COLORS[:len(lang_names)]
    ax2.bar(lang_names, lang_vals, color=colors, width=0.6)
    ax2.set_title("Languages Used", color=WHITE, fontsize=11,
                  fontfamily="monospace", pad=8, loc="left")
    plt.setp(ax2.get_xticklabels(), rotation=30, ha="right",
             fontsize=8, fontfamily="monospace", color=WHITE)
    plt.setp(ax2.get_yticklabels(), color=MUTED, fontsize=8)
    ax2.set_ylabel("Repos", color=MUTED, fontsize=8)
    ax2.grid(axis="y", color=BORDER, linewidth=0.5, alpha=0.5)
    ax2.set_axisbelow(True)
else:
    ax2.text(0.5, 0.5, "No language data", ha="center", va="center",
             color=MUTED, transform=ax2.transAxes)

# ── Chart 3: Original vs Forked (donut) ───────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor(CARD)
for spine in ax3.spines.values():
    spine.set_edgecolor(BORDER)

if original + forked > 0:
    wedges, texts, autotexts = ax3.pie(
        [original, forked],
        labels=["Original", "Forked"],
        colors=[BLUE, PURPLE],
        autopct="%1.0f%%",
        startangle=90,
        wedgeprops={"width": 0.5, "edgecolor": DARK, "linewidth": 2},
        pctdistance=0.75,
    )
    for t in texts:
        t.set_color(WHITE); t.set_fontsize(9); t.set_fontfamily("monospace")
    for at in autotexts:
        at.set_color(DARK); at.set_fontsize(8); at.set_fontweight("bold")

ax3.set_title("Original vs Forked", color=WHITE, fontsize=11,
              fontfamily="monospace", pad=8, loc="left")

# ── Save ───────────────────────────────────────────────────────────────────
out = f"{USERNAME}_github_stats.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK)
print(f"📊  Saved → {out}")
plt.show()
