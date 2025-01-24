

import datetime
import glob
import json
from unidecode import unidecode

# download comments with:
# yt-dlp --write-comments --skip-download -a raw_data/data_youtube_videos_bayern.txt -o "tmp/%(id)s_comments.json"
# where aw_data/data_youtube_videos_bayern.txt contains a link per line to videos

region = "sh"
filepaths = glob.glob("tmp/*comments.json.info.json")


def list_comments_with_author(filepaths: list[str]):
    comments = []
    for filepath in filepaths:
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.loads(file.read())
            if "comments" in content:
                for comment in content["comments"]:
                    author = unidecode(comment["author"])
                    comment_text = unidecode(comment["text"])
                    
                    comments.append((author, comment_text))
    
    with open(f"processed_data/commenters_with_comments_youtube_{region}.json", "w") as file:
        file.write(json.dumps(comments, indent=4))

def find_comments(filepaths: list[str]):
    comments = []
    comments_by_year = {}
    for filepath in filepaths:
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.loads(file.read())
            if "comments" in content:
                for comment in content["comments"]:
                    comment_text = unidecode(comment["text"])
                    
                    date = datetime.datetime.fromtimestamp(comment["timestamp"])
                    year = date.strftime("%Y")
                    
                    if year not in comments_by_year:
                        comments_by_year[year] = []
                    comments_by_year[year].append(comment_text)
                    comments.append(comment_text)

    data = {
        "topic_name": region,
        "posts": filepaths,
        "comments_on_posts": comments,
        "comments_by_year": comments_by_year,
        }


    with open(f"processed_data/comments_youtube_{region}.json", "w") as file:
        file.write(json.dumps(data, indent=4))

def find_commenters(filepaths: list[str]):
    comments_by_author = {}
    for filepath in filepaths:
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.loads(file.read())
            if "comments" in content:
                for comment in content["comments"]:
                    author = unidecode(comment["author"])
                    likes = comment["like_count"]
                    verified = comment["author_is_verified"]
                    if author not in comments_by_author:
                        comments_by_author[author] = {}
                        comments_by_author[author]["num_comments"] = 0
                        comments_by_author[author]["likes"] = 0
                        comments_by_author[author]["verified"] = verified
                    
                    comments_by_author[author]["likes"] += likes
                    comments_by_author[author]["num_comments"] += 1

    comments_by_author_sorted_num_comments = sorted(comments_by_author.items(), key=lambda x: x[1]["num_comments"], reverse=True)
    comments_by_author_sorted_num_likes = sorted(comments_by_author.items(), key=lambda x: x[1]["likes"], reverse=True)
    comments_by_author_sorted_verified = sorted(comments_by_author.items(), key=lambda x: x[1]["verified"], reverse=True)

    # with open(f"processed_data/commenters_youtube_{region}_by_num_comments.json", "w") as file:
    #     file.write(json.dumps(comments_by_author_sorted_num_comments, indent=4))

    with open(f"processed_data/commenters_youtube_{region}_by_num_likes.json", "w") as file:
        file.write(json.dumps(comments_by_author_sorted_num_likes, indent=4))
        
    # with open(f"processed_data/commenters_youtube_{region}_by_verified.json", "w") as file:
    #     file.write(json.dumps(comments_by_author_sorted_verified, indent=4))


find_comments(filepaths)
list_comments_with_author(filepaths)
find_commenters(filepaths)