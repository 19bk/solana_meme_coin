import os
import re
import requests
import praw
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
CLOUDINARY_CLOUD_NAME = "dzedpnsqm"
CLOUDINARY_API_KEY = "245762654934129"
CLOUDINARY_API_SECRET = "Sqjs5COkNFic-SZXIimD7_rZmmM" 

REDDIT_CLIENT_ID = '4TZ3gGjdB6VeYunJeql2ew'
REDDIT_CLIENT_SECRET = 'S_R1x63DYTDWVmz8R8kV4oYNA0jgkA'
REDDIT_USER_AGENT = 'praw22'
OPENAI_API_KEY = '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'
DEVTO_API_KEY = 'RkY1WbMwQEUeyib9nuPEaCjv'


class MemeCoinNameAndImageGenerator:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    def fetch_hot_posts_reddit(self, subreddits=['solana', 'cryptocurrency', 'CryptoCurrencyMemes'], limit=10):
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        all_titles = []
        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=limit):
                all_titles.append(submission.title)
        return all_titles

    def generate_meme_coin_names(self, topics):
        prompt = "Generate creative and catchy names for a meme coin project inspired by these topics: " + ", ".join(topics) + ". Provide five suggestions."
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
        )
        meme_coin_names = response.choices[0].text.strip().split("\n")
        return meme_coin_names

    def generate_and_download_image(self, meme_coin_names):
        dynamic_prompt = f"Create an engaging and humorous image representing meme coins with names such as {', '.join(meme_coin_names[:3])}. The image should include elements that reflect the unique and trendy nature of these meme coins, possibly featuring an anthropomorphic dog character in a whimsical setting that relates to the themes of the coins. The image should be colorful, vibrant, and meme-worthy, appealing to both cryptocurrency enthusiasts and the wider internet meme culture."
        response = openai.Image.create(
            prompt=dynamic_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        image_content = requests.get(image_url).content
        with open('meme_coin_inspired_image.png', 'wb') as image_file:
            image_file.write(image_content)
        print("Image downloaded as meme_coin_inspired_image.png")

def main():
    generator = MemeCoinNameAndImageGenerator()
    reddit_titles = generator.fetch_hot_posts_reddit()
    if not reddit_titles:
        print("No titles were fetched from Reddit.")
        return

    print("Fetched Reddit titles:")
    for title in reddit_titles:
        print("- ", title)

    meme_coin_names = generator.generate_meme_coin_names(reddit_titles)
    print("Generated meme coin names inspired by Reddit titles:")
    for name in meme_coin_names:
        print("- ", name)

    # Generate and download an image inspired by the meme coin names
    generator.generate_and_download_image(meme_coin_names)

if __name__ == "__main__":
    main()
