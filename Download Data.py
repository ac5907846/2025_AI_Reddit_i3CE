import praw
import json
import os
from datetime import datetime, timezone

# Replace with your own credentials
reddit = praw.Reddit(
    client_id="HIDE FOR SECURITY",
    client_secret="HIDE FOR SECURITY",
    user_agent="HIDE FOR SECURITY"
)

# Specify the subreddit
subreddit_name = "Construction"

# Number of recent posts to retrieve
num_posts = 1000

def extract_comments(comment, depth=0):
    if hasattr(comment, 'body'):
        return {
            "body": comment.body,
            "replies": [extract_comments(reply, depth + 1) for reply in comment.replies if hasattr(reply, 'body')]
        }
    return None

# List to store the extracted data
posts_data = []

# Fetching recent posts
subreddit = reddit.subreddit(subreddit_name)
print(f"Fetching {num_posts} recent posts from r/{subreddit_name}...")

for i, post in enumerate(subreddit.new(limit=num_posts), 1):
    print(f"\rProcessing post {i}/{num_posts}: {post.title[:50]}...", end="", flush=True)
    post_data = {
        "title": post.title,
        "content": post.selftext,
        "score": post.score,
        "upvote_ratio": post.upvote_ratio,
        "num_comments": post.num_comments,
        "created_utc": post.created_utc,
        "url": post.url,
        "author": str(post.author),
        "comments": []
    }
    
    # Extract comments
    post.comments.replace_more(limit=None)
    for comment in post.comments:
        comment_data = extract_comments(comment)
        if comment_data:
            post_data["comments"].append(comment_data)
    
    posts_data.append(post_data)

print(f"\nFetched {len(posts_data)} posts.")

# Function to format comments for better readability
def format_comments(comments, indent=0):
    formatted = []
    for comment in comments:
        comment_str = f"{'  ' * indent}{comment['body']}"
        formatted.append(comment_str)
        if comment['replies']:
            formatted.extend(format_comments(comment['replies'], indent + 1))
    return formatted

# Format the entire posts data for better readability
print("Formatting posts data...")
formatted_posts_data = []
for post in posts_data:
    formatted_post = {
        "Title": post['title'],
        "Content": post['content'],
        "Score": post['score'],
        "Upvote Ratio": post['upvote_ratio'],
        "Number of Comments": post['num_comments'],
        "Created Date": datetime.fromtimestamp(post['created_utc'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        "URL": post['url'],
        "Author": post['author'],
        "Comments": format_comments(post['comments'])
    }
    formatted_posts_data.append(formatted_post)

# Define the path to save the JSON file
current_date = datetime.now(timezone.utc).strftime('%Y%m%d')
json_filename = os.path.join(os.getcwd(), f"{subreddit_name}Posts_Recent{num_posts}_{current_date}.json")

# Save the formatted data to a JSON file
print(f"Saving data to {json_filename}...")
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(formatted_posts_data, f, ensure_ascii=False, indent=2)

print(f"Completed. {len(formatted_posts_data)} posts have been saved to {json_filename}")