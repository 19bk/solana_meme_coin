import re
import praw
import openai
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# ConstantsREDDIT_CLIENT_ID = '4TZ3gGjdB6VeYunJeql2ew'
REDDIT_CLIENT_ID = '4TZ3gGjdB6VeYunJeql2ew'
REDDIT_CLIENT_SECRET = 'S_R1x63DYTDWVmz8R8kV4oYNA0jgkA'
REDDIT_USER_AGENT = 'praw22'
OPENAI_API_KEY = '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'

class MemeCoinNameAndImageGenerator:
    def __init__(self):
        self.reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)
        openai.api_key = OPENAI_API_KEY

    def fetch_top_posts_reddit(self, limit=15, time_filter='day'):
        print("Fetching top posts from Reddit...")
        # Combining all specified subreddits for a single query, including the new ones
        subreddits = "movies+television+CryptoMoonShots+CryptoCurrency+popculturechat"
        all_titles = []

        subreddit = self.reddit.subreddit(subreddits)
        for submission in subreddit.top(time_filter=time_filter, limit=limit):
            all_titles.append(submission.title)
        
        return all_titles


    def generate_meme_coin_names(self, topics):
        print("Generating meme coin names...")
        prompt = (
            "Generate creative and catchy names for a meme coin project inspired by these topics: " + ", ".join(topics) +
            ". Ensure the name is memorable and has a unique symbol that can go viral. " +
            "Incorporate humor and creativity to make the meme coin concept engaging and relatable."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        meme_coin_names = [
            re.sub(r'^\d+\.\s*\$', '$', name).strip() 
            for name in response.choices[0].message['content'].strip().split("\n")
        ]
        print(f"Generated meme coin names: {meme_coin_names}")
        return meme_coin_names


    def evaluate_best_meme_coin(self, meme_coin_names):
        print("Evaluating the best meme coin for success...")
        # Enhanced prompt with additional criteria
        prompt = (
            "Evaluate these meme coin names based on their potential to go viral, appeal to the crypto community, " +
            "and embody a memorable theme, unique name and symbol, as well as humor and creativity. " +
            "Which meme coin name is the best choice for a successful launch? Please quote the selected name."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt + "\n" + "\n".join([f"- {name}" for name in meme_coin_names])}
            ]
        )
        response_text = response.choices[0].message['content'].strip()

        # Attempt to extract the name using regex
        match = re.search(r'"([^"]+)"', response_text)
        if match:
            best_choice_name = match.group(1)
        else:
            # Fallback strategy or simply pick the first one if no name is explicitly quoted
            print("No specific name found in the response, selecting a fallback name.")
            best_choice_name = meme_coin_names[0] if meme_coin_names else "NoNameFound"

        # Ensure the selected name follows the desired $memeCoin format and clean if necessary
        best_choice_name = self.format_meme_coin_name(best_choice_name)
        
        return best_choice_name

    
    def format_meme_coin_name(self, name):
        # Example of correcting a name that starts with a number
        cleaned_name = re.sub(r'^\d+', '', name)  # Remove leading digits
        formatted_name = f"${cleaned_name}"
        return formatted_name.strip()



    def generate_slogan(self, meme_coin_name):
        print(f"Generating a catchy slogan for {meme_coin_name}...")
        # Enhanced prompt to encapsulate memorability, uniqueness, humor, and creativity
        prompt = (
            f"Create a fun, witty, and appealing slogan for the cryptocurrency {meme_coin_name}. " +
            "The slogan should embody a memorable theme and reflect a unique symbol that goes viral. " +
            "Incorporate elements of humor and creativity to make the meme coin's concept engaging and stand out. " +
            "Ensure it resonates well with the crypto community, inspiring excitement and a sense of belonging."
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        slogan = response.choices[0].message['content'].strip()
        print(f"Generated slogan: {slogan}")
        return slogan


    def generate_and_download_image(self, meme_coin_name, slogan):
        slogan=slogan
        print(f"Generating and downloading image for: {meme_coin_name}...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_name = re.sub(r'[^\w\-_\.]', '', meme_coin_name)
        filename = f"{sanitized_name}_{timestamp}.png"

        prompt = f"Create a funny image for '{meme_coin_name}', featuring a cute or confused dog."
       
        
        response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
        image_url = response.data[0].url
        image_content = requests.get(image_url).content

        with open(filename, 'wb') as image_file:
            image_file.write(image_content)
        
        print(f"Image downloaded as {filename}")


    


def main():
    generator = MemeCoinNameAndImageGenerator()
    reddit_titles = generator.fetch_top_posts_reddit()
    if not reddit_titles:
        print("No titles were fetched from Reddit.")
        return

    meme_coin_names = generator.generate_meme_coin_names(reddit_titles)
    print("\nGenerated meme coin names:")
    for name in meme_coin_names:
        print(f"- {name}")

    best_choice_raw = generator.evaluate_best_meme_coin(meme_coin_names)
    formatted_best_choice = generator.format_meme_coin_name(best_choice_raw)
    print(f"\nSelected meme coin for success: {formatted_best_choice}")

    slogan = generator.generate_slogan(formatted_best_choice)
    print(f"\nCatchy slogan for {formatted_best_choice}: {slogan}")

    generator.generate_and_download_image(formatted_best_choice, slogan)

if __name__ == "__main__":
    main()

