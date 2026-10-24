"""
Data collection for a non-commercial academic research project on diagnostic
delay in chronic pelvic pain and recurrent UTIs/yeast infections.

Read-only: searches and reads PUBLIC posts via the official Reddit API (PRAW).
It never posts, comments, votes or messages. No usernames are collected, and
post IDs are one-way hashed.

Output: pilot_posts.csv with post_id (hashed), subreddit, created_utc, title,
selftext, num_comments.
"""

import csv
import hashlib
import time

MODE = "praw"

TARGETS = [
    {"subreddit": "endometriosis", "query": "diagnosed", "limit": 25},
    {"subreddit": "PCOS", "query": "diagnosed", "limit": 25},
    {"subreddit": "UTI", "query": "years", "limit": 25},
    {"subreddit": "vulvodynia", "query": "diagnosed", "limit": 15},
    {"subreddit": "InterstitialCystitis", "query": "diagnosed", "limit": 15},
]

REQUEST_DELAY_SECONDS = 3  # low request rate

# Credentials go here locally only. Never commit real values.
PRAW_CLIENT_ID = "YOUR_CLIENT_ID"
PRAW_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
PRAW_USER_AGENT = "pelvic-pain-dx-delay-research by u/YOUR_USERNAME"

OUTPUT_FILE = "pilot_posts.csv"


def hash_id(reddit_fullname: str) -> str:
    """One-way hash so the raw Reddit post ID is never stored."""
    return hashlib.sha256(reddit_fullname.encode("utf-8")).hexdigest()[:16]


def fetch_praw_search(reddit, subreddit: str, query: str, limit: int):
    posts = []
    for s in reddit.subreddit(subreddit).search(query, limit=limit):
        posts.append(
            {
                "post_id": hash_id(s.fullname),
                "subreddit": subreddit,
                "created_utc": s.created_utc,
                "title": s.title,
                "selftext": s.selftext,
                "num_comments": s.num_comments,
            }
        )
    return posts


def main():
    import praw

    reddit = praw.Reddit(
        client_id=PRAW_CLIENT_ID,
        client_secret=PRAW_CLIENT_SECRET,
        user_agent=PRAW_USER_AGENT,
    )
    all_posts = []
    for t in TARGETS:
        print(f"Fetching r/{t['subreddit']} (query='{t['query']}', limit={t['limit']})...")
        posts = fetch_praw_search(reddit, t["subreddit"], t["query"], t["limit"])
        print(f"  -> got {len(posts)} posts")
        all_posts.extend(posts)
        time.sleep(REQUEST_DELAY_SECONDS)

    if not all_posts:
        print("No posts collected.")
        return

    fields = ["post_id", "subreddit", "created_utc", "title", "selftext", "num_comments"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_posts)
    print(f"Done. {len(all_posts)} posts written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
