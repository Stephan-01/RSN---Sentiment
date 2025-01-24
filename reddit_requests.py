import datetime
import html
from random import randrange
import time
from typing import Literal
import requests
from unidecode import unidecode
from itertools import chain

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"

class PostSearch:
    
    #use "after" in json has a value like "t3_18v6czy". 
    # to go to the next page and list another 100 posts add "&after=t3_18v6czy" to the url
    
    def __init__(
        self,
        subreddit: str,
        listing: Literal[
            "controversial", "best", "hot", "new", "random", "rising", "top"
        ],
        timeframe: Literal["day", "week", "month", "year", "all"],
        after: str | None = None
    ) -> None:
        try:
            print(f"Trying to access {listing} posts of {timeframe} from {subreddit}")
            base_url = f"https://www.reddit.com/r/{subreddit}/{listing}.json?sr_detail=1&t={timeframe}&limit={100}"
            
            if after is not None:
                base_url += f"&after={after}"
            
            print(base_url)
            request = requests.get(base_url, headers={"User-agent": useragent})
            posts_listing = request.json()
            
            self.subreddit = subreddit
            self.listing = listing
            self.timeframe = timeframe
            self.posts: list[Post] = []
            self.after = get_parameter(posts_listing, "after")
            for post in get_parameter(posts_listing, "children"):
                self.posts.append(Post(post))
        except:
            print("an error occured while searching for posts")
    
    def next_page(self):
        return PostSearch(self.subreddit, self.listing, self.timeframe, self.after)

class Post:
    def __str__(self) -> str:
        return (
            self.author
            + ' created the post: "'
            + self.title
            + '" which has '
            + str(self.score)
            + " score"
        )

    def load_comments(self, listing):
        try:
            print(f"Trying to access comments of post {self.post_id}")
            base_url = f"https://www.reddit.com/{self.post_id}/.json?sort={listing}"
            request = requests.get(base_url, headers={"User-agent": useragent})
            comments = request.json()[1]["data"]["children"]

            print(f"found {len(comments)} comments")
            for comment in comments:
                self.comments.append(Comment(comment))
            
            time.sleep(1)
        except Exception as e:
            print(
                f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"  # type: ignore
            )
            print("an error cccured while searching for comments")

    def __init__(self, post) -> None:
        self.subreddit: str = get_parameter(post, "subreddit")
        self.title: str = html.unescape(unidecode(get_parameter(post, "title")))
        self.author: str = html.unescape(unidecode(get_parameter(post, "author")))
        self.selftext: str = html.unescape(unidecode(get_parameter(post, "selftext")))
        self.post_id: str = get_parameter(post, "id")
        self.gilded: int = int(get_parameter(post, "gilded"))
        self.upvotes: int = int(get_parameter(post, "ups"))
        self.downvotes: int = int(get_parameter(post, "downs"))
        self.score: int = int(get_parameter(post, "score"))
        self.url: str = get_parameter(post, "url")
        self.num_comments: int = int(get_parameter(post, "num_comments"))
        self.nsfw: bool = bool(get_parameter(post, "over_18"))
        sr_detail = get_parameter(post, "sr_detail")
        self.time_created = datetime.datetime.fromtimestamp(int(get_parameter(post, "created_utc")), tz=datetime.timezone.utc)
        self.subreddit_icon_url: str = sr_detail["icon_img"] # type: ignore
        self.comments: list[Comment] = []

    def get_good_comments(
        self, score_threshold: int = 300, num_chars_to_limit_comments: int | None = None
    ):
        if len(self.comments) == 0:
            self.load_comments("top")

        print(f"There are {len(self.comments)} comments")

        for index, comment in enumerate(self.comments):
            chain_score = calc_chain_score(comment)
            print(
                f"Comment {index} from {comment.author} has {comment.score} score. This comment chain has a combined {chain_score}"
            )

        # TODO filter removed comments

        filtered_comments = list(
            filter(
                lambda comment: comment.body != "[removed]"
                and comment.body != "[deleted]",
                self.comments,
            )
        )
        if len(self.comments) > len(filtered_comments):
            print(
                f"ignoring {len(self.comments) - len(filtered_comments)} comments because they were removed"
            )

        filtered_comments = list(
            filter(
                lambda comment: calc_chain_score(comment) > score_threshold,
                filtered_comments,
            )
        )[:-1]
        print(f"After score filtering there are {len(filtered_comments)} comments left")

        if num_chars_to_limit_comments != None:
            for index, comment in enumerate(filtered_comments):
                if num_chars_to_limit_comments - len(comment.body) < 0:
                    filtered_comments = filtered_comments[:index]
                    break
                num_chars_to_limit_comments -= len(comment.body)
                print(num_chars_to_limit_comments)

        print(f"Limiting to {len(filtered_comments)} comments")
        return filtered_comments


class Comment:
    def __str__(self) -> str:
        return f'{self.author} wrote: "{self.body}"'

    def load_comment_chain(self, depth=0):
        chain: list[Comment] = []
        chain.append(self)
        if depth > 1 and len(self.replies) > 0:
            chain += self.replies[0].load_comment_chain(depth - 1)
        return chain
    
    def load_all_replies(self):
        comments = [self]
        
        for reply in self.replies:
            comments.extend(reply.load_all_replies())
        
        return list(set(comments))
        

    def __init__(self, comment, ignore_replies=False) -> None:
        self.author: str = get_parameter(comment, "author")
        self.body: str = html.unescape(unidecode(get_parameter(comment, "body")))
        if ignore_replies:
            print("ignoring replies")
            self.replies = []
        else:
            self.replies: list[Comment] = handle_replies(
                get_parameter(comment, "replies")
            )
        self.upvotes: int = int(get_parameter(comment, "ups"))
        self.downvotes: int = int(get_parameter(comment, "downs"))
        self.time_created = datetime.datetime.fromtimestamp(int(get_parameter(comment, "created_utc")), tz=datetime.timezone.utc)
        self.score: int = int(get_parameter(comment, "score"))
        self.gilded: int = int(get_parameter(comment, "gilded"))
        self.id: str = str(get_parameter(comment, "id"))


def create_post_from_post_id(post_id: str) -> Post:
    base_url = f"https://www.reddit.com/{post_id}.json?sr_detail=1"
    print(base_url)
    request = requests.get(base_url, headers={"User-agent": useragent})
    post = request.json()[0]
    post = get_parameter(post, "children")[0]
    # print(post)
    return Post(post)


def handle_replies(replies) -> list[Comment]:
    ret = []

    if isinstance(replies, str):
        pass
    else:
        for child in replies["data"]["children"]:
            if "kind" in child and child["kind"] == "more":
                # TODO handle loading more comments
                # print(replies)
                pass
            else:
                ret.append(Comment(child))

    return ret


def get_parameter(data, parameter):
    if "kind" in data and data["kind"] == "more":
        return "0"

    if "data" in data:
        data = data["data"]

    if parameter in data:
        return data[parameter]

    raise Exception("Unknown Parameter")


def calc_chain_score(comment: Comment, skip_first: bool = True) -> int:
    sum = comment.score

    for reply in comment.replies:
        sum += calc_chain_score(reply, False)

    return sum

def create_post_from_post_id(post_id: str) -> Post:
    base_url = f"https://www.reddit.com/{post_id}.json?sr_detail=1"
    print(base_url)
    request = requests.get(base_url, headers={"User-agent": useragent})
    post = request.json()[0]
    post = get_parameter(post, "children")[0]
    # print(post)
    return Post(post)