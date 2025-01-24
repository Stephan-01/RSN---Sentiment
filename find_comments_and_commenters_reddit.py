import json
import random
import time
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import pipeline
import matplotlib.pyplot as plt
from reddit_requests import Comment, Post, create_post_from_post_id
from unidecode import unidecode
import json
import unidecode
from reddit_requests import Comment, Post

class PostsAboutTopic():
    def __init__(self, topic_name: str) -> None:
        self.topic_name = topic_name
        self.positive_posts: list[Post] = []
        self.neutral_posts: list[Post] = []
        self.negative_posts: list[Post] = []
        self.comments_on_positive_posts: list[Comment] = []
        self.comments_on_neutral_posts: list[Comment] = []
        self.comments_on_negative_posts: list[Comment] = []
        self.comments_by_year = {}
        
    def add_based_on_sentiment(self, sentiment, post: Post):
        print(sentiment)
        all_comments: list[Comment] = []
        if sentiment == "Neutral":
            self.neutral_posts.append(post)
            # post.load_comments("top")
        if sentiment == "Positive" or sentiment == "Very Positive":
            sentiment = "Positive"
            self.positive_posts.append(post)
            post.load_comments("top")
            for comment in post.comments:
                all_comments.extend(comment.load_all_replies())
            self.comments_on_positive_posts += all_comments
        if sentiment == "Negative" or sentiment == "Very Negative":
            sentiment = "Negative"
            self.negative_posts.append(post)
            post.load_comments("top")
            for comment in post.comments:
                all_comments.extend(comment.load_all_replies())
            self.comments_on_negative_posts += all_comments
            
        for comment in all_comments:
            comment_text = unidecode.unidecode(comment.body)
            year = comment.time_created.strftime("%Y")
            
            if sentiment not in self.comments_by_year:
                self.comments_by_year[sentiment] = {}
            
            if year not in self.comments_by_year[sentiment]:
                self.comments_by_year[sentiment][year] = []
            self.comments_by_year[sentiment][year].append(comment_text)
            
            
    def save_json(self):
        data = {
            "topic_name": self.topic_name,
            "positive_posts": [p.title + "\n" + p.selftext for p in self.positive_posts],
            "neutral_posts": [p.title + "\n" + p.selftext for p in self.neutral_posts],
            "negative_posts": [p.title + "\n" + p.selftext for p in self.negative_posts],
            
            "comments_on_positive_posts": [c.body for c in self.comments_on_positive_posts],
            "comments_on_neutral_posts": [c.body for c in self.comments_on_neutral_posts],
            "comments_on_negative_posts": [c.body for c in self.comments_on_negative_posts],
            "comments_by_year": self.comments_by_year,
            "topic_name": self.topic_name,
            }
        
        with open(f"processed_data/comments_reddit_{self.topic_name}.json", "w") as file:
            file.write(json.dumps(data, indent=4))


relevant_subreddits_bayern_windkraft = ["Energiewirtschaft", "de", "Bavaria", "Klimawandel"]
relevant_subreddits_sh_windkraft = ["Energiewirtschaft", "de", "Klimawandel"]

topics: list[PostsAboutTopic] = []
topic_bayern = PostsAboutTopic("bayern")
topic_sh = PostsAboutTopic("sh")


# model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
model_name = "tabularisai/multilingual-sentiment-analysis"

model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
max_tokens = model.config.max_position_embeddings

with open("raw_data/data_reddit_posts_bayern.txt", "r") as file:
    post_ids_bayern = file.read().splitlines()
    
    
with open("raw_data/data_reddit_posts_sh.txt", "r") as file:
    post_ids_sh = file.read().splitlines()
    
# get comments for bayern
comments_by_author = {}
commenter_with_comment = []
for post_id in post_ids_bayern:
    post = create_post_from_post_id(post_id)
    post_text = post.title + "\n" + post.selftext
    sentiment = sentiment_pipeline(post_text, truncation=True)[0]["label"] # type: ignore
    
    if post_id == "1hsjlfs" or post_id == "15ehljo":
        sentiment = "Negative"
    
    
    topic_bayern.add_based_on_sentiment(sentiment, post)
    topic_bayern.save_json()
    
    comments = post.comments
    for comment in post.comments:
        author = comment.author
        likes = comment.upvotes
        
        commenter_with_comment.append((author, comment.body))
        if author not in comments_by_author:
            comments_by_author[author] = {}
            comments_by_author[author]["num_comments"] = 0
            comments_by_author[author]["likes"] = 0
        comments_by_author[author]["likes"] += likes
        comments_by_author[author]["num_comments"] += 1
    
comments_by_author_sorted_num_comments = sorted(comments_by_author.items(), key=lambda x: x[1]["num_comments"], reverse=True)
comments_by_author_sorted_num_likes = sorted(comments_by_author.items(), key=lambda x: x[1]["likes"], reverse=True)
# with open(f"processed_data/commenters_reddit_bayern_by_num_comments.json", "w") as file:
#     file.write(json.dumps(comments_by_author_sorted_num_comments, indent=4))
with open(f"processed_data/commenters_reddit_bayern_by_num_likes.json", "w") as file:
    file.write(json.dumps(comments_by_author_sorted_num_likes, indent=4))
# with open(f"processed_data/commenters_with_comments_reddit_bayern.json", "w") as file:
#     file.write(json.dumps(commenter_with_comment, indent=4))
    
# get comments for SH
comments_by_author = {}
commenter_with_comment = []
for post_id in post_ids_sh:
    post = create_post_from_post_id(post_id)
    post_text = post.title + "\n" + post.selftext
    sentiment = sentiment_pipeline(post_text, truncation=True)[0]["label"] # type: ignore
    
    topic_sh.add_based_on_sentiment(sentiment, post)
    topic_sh.save_json()
    
    comments = post.comments
    for comment in post.comments:
        author = comment.author
        likes = comment.upvotes
        
        commenter_with_comment.append((author, comment.body))
        if author not in comments_by_author:
            comments_by_author[author] = {}
            comments_by_author[author]["num_comments"] = 0
            comments_by_author[author]["likes"] = 0
        comments_by_author[author]["likes"] += likes
        comments_by_author[author]["num_comments"] += 1
    
comments_by_author_sorted_num_comments = sorted(comments_by_author.items(), key=lambda x: x[1]["num_comments"], reverse=True)
comments_by_author_sorted_num_likes = sorted(comments_by_author.items(), key=lambda x: x[1]["likes"], reverse=True)
# with open(f"processed_data/commenters_reddit_sh_by_num_comments.json", "w") as file:
#     file.write(json.dumps(comments_by_author_sorted_num_comments, indent=4))
with open(f"processed_data/commenters_reddit_sh_by_num_likes.json", "w") as file:
    file.write(json.dumps(comments_by_author_sorted_num_likes, indent=4))
# with open(f"processed_data/commenters_with_comments_reddit_sh.json", "w") as file:
#     file.write(json.dumps(commenter_with_comment, indent=4))