import os
import re
import requests
import praw
import openai
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Load environment variables from a .env file
load_dotenv()

# Constants
# Constants
CLOUDINARY_CLOUD_NAME = "dzedpnsqm"
CLOUDINARY_API_KEY = "245762654934129"
CLOUDINARY_API_SECRET = "Sqjs5COkNFic-SZXIimD7_rZmmM" 

REDDIT_CLIENT_ID = '4TZ3gGjdB6VeYunJeql2ew'
REDDIT_CLIENT_SECRET = 'S_R1x63DYTDWVmz8R8kV4oYNA0jgkA'
REDDIT_USER_AGENT = 'praw22'
OPENAI_API_KEY = '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'
DEVTO_API_KEY = 'RkY1WbMwQEUeyib9nuPEaCjv'

class BlogPostGenerator:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    def publish_to_devto(self, title, markdown_content, tags, image_url):
        print("Publishing to Dev.to...")
        headers = {
            'api-key': DEVTO_API_KEY,
            'Content-Type': 'application/json',
        }

        # Prepare the article data, including tags and image URL if provided
        article_data = {
            'article': {
                'title': title,
                'body_markdown': markdown_content,
                'published': False,
                'tags': tags,  # Add tags to the article data
                'main_image': image_url,  # Add the main image URL if provided
            }
        }

        # Endpoint to publish an article
        url = 'https://dev.to/api/articles'

        # Make the POST request to publish the article
        response = requests.post(url, headers=headers, json=article_data)

        # Check the response
        if response.status_code == 201:
            print(f'Successfully created and published article with ID: {response.json()["id"]}')
        else:
            print(f'Failed to create and publish article: {response.json()}')

    def config_cloudinary(self):
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )

    def upload_image_to_cloudinary(self, file_path):
        print("Uploading image to Cloudinary...")
        try:
            response = cloudinary.uploader.upload(file_path)
            return response.get('secure_url')
        except Exception as e:
            print(f"An error occurred while uploading to Cloudinary: {e}")
            return None

    

            
    def fetch_hot_posts_reddit(self):
        print("Fetching hot posts from Reddit...")
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        subreddits = ['python', 'MachineLearning']
        all_titles = []
        try:
            for subreddit_name in subreddits:
                subreddit = reddit.subreddit(subreddit_name)
                for submission in subreddit.hot(limit=10):
                    all_titles.append(submission.title)
            return all_titles
        except Exception as e:
            print(f'Error fetching posts from Reddit: {e}')
            return all_titles
        
    def analyze_topics(self, topics):
            print("Analyzing topics...")
            analysis_prompt = f"Identify the most engaging and current topic for a blog post from the following list: {', '.join(topics)}."
            try:
                analysis_response = openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",  # Ensure this is the correct chat model
                    messages=[{"role": "system", "content": analysis_prompt}],
                )
                topic = analysis_response.choices[0].message['content'].strip()
                # print(f"Selected topic for blog post: {topic}")
                return topic
            except Exception as e:
                print(f'Error analyzing topics with OpenAI: {e}')
                return None
    
    def format_in_markdown(self, content, image_url):
            # Headers
            content = re.sub(r'^(#{1,6}) (.+)$', r'\1 \2', content, flags=re.MULTILINE)

            # Bold & Italic
            content = re.sub(r'\*\*(.+?)\*\*', r'**\1**', content)
            content = re.sub(r'\*(.+?)\*', r'*\1*', content)
            content = re.sub(r'__(.+?)__', r'__\1__', content)
            content = re.sub(r'_(.+?)_', r'_\1_', content)

            # Links
            content = re.sub(r'\[(.+?)\]\((.+?)\)', r'[\1](\2)', content)

            # Inline Images
            content = re.sub(r'!\[(.+?)\]\((.+?)\)', r'![\1](\2)', content)

            # Code and Syntax Highlighting
            content = re.sub(r'```(.+?)```', r'```\1```', content, flags=re.DOTALL)
            content = re.sub(r'`(.+?)`', r'`\1`', content)

            # Lists - assuming spaces are used for indentation
            content = re.sub(r'^( +)([*+-] .+)$', r'\1\2', content, flags=re.MULTILINE)
            content = re.sub(r'^( +)(\d+\. .+)$', r'\1\2', content, flags=re.MULTILINE)

            # Blockquotes
            content = re.sub(r'^> (.+)$', r'> \1', content, flags=re.MULTILINE)

            # Horizontal Rule
            content = re.sub(r'^-{3,}$', r'---', content, flags=re.MULTILINE)
            content = re.sub(r'^\*{3,}$', r'***', content, flags=re.MULTILINE)
            content = re.sub(r'^_{3,}$', r'___', content, flags=re.MULTILINE)
            
            markdown_content = content
         

            return markdown_content

    def format_content_with_openai(self, content):
        print("Formatting content with OpenAI...")
        prompt = (
            "Please format the following content into Markdown. Ensure headers, lists, "
            "bold and italic text, links, and code blocks are correctly formatted.\n\n"
            f"{content}"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",  # Ensure this is the correct chat model
                messages=[{"role": "system", "content": prompt}],
                max_tokens=4096,
                temperature=0.5,
            )
            markdown_formatted_content = response.choices[0].message['content'].strip()
            print("Content formatted successfully.")
            return markdown_formatted_content
        except Exception as e:
            print(f"An error occurred while formatting with OpenAI: {e}")
            return content  # Return original content if formatting fails



    def fetch_cover_image(self, tags):
        topic_str = tags
        prompt = (
            f"Create a visually appealing and conceptual image that synthesizes the essence of these topic: "
            f"{topic_str}."
        )

        try:
            print("Generating image with DALL-E 3...")
            response = openai.Image.create(
                model="dall-e-3",  # Specify the DALL-E 3 model
                prompt=prompt,
                size="1024x1024",  # Choose your desired output size
                # Optionally specify 'quality' and 'style' parameters
                quality="standard",
                style="vivid",
            )
            image_url = response['data'][0]['url']
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # sanitized_tags = ''.join(char for char in tags if char.isalnum())
            image_name = f"cover_image_.png"
            with open(image_name, 'wb') as file:
                file.write(image_response.content)
            print(f"Cover image saved as {image_name}.")
             # First, upload the local image to Cloudinary
            online_image_url = self.upload_image_to_cloudinary(image_name)
            if not online_image_url:
                print("Failed to upload image to Cloudinary.")
                return None
            
            # Now that we have the online image URL, proceed with other operations
            print(f"Cover image available at: {online_image_url}")
            return online_image_url
            # return image_name

        except Exception as e:
            print(f"An error occurred while generating the cover image with DALL-E 3: {e}")
            return None


    def generate_title(self, topic):
        print("Generating title for the blog post...")
        title_prompt = f"Generate a catchy and descriptive title for a blog post on the topic: {topic}."
        try:
            title_response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "system", "content": title_prompt}],
                max_tokens=30
            )
            title = title_response.choices[0].message['content'].strip()

            # Remove any leading 'Title: ' and surrounding quotes
            title = title.replace('Title: ', '').strip('"')

            print(f"Generated title: {title}")
            return title

        except Exception as e:
            print(f"An error occurred while generating the title: {e}")
            return ""


    def generate_blog_post(self, title, topic):
        # Define the main prompt
        main_prompt = (
            f"Title: do not include the title just generate the content\n"
            f"Objective: Craft a compelling and insightful blog post on {topic}, "
            f"ensuring it's both informative and engaging to the readers.\n"
            f"Style: Maintain a conversational tone, and infuse humor or personal anecdotes where appropriate.\n"
            f"Length: Aim for a 3 to 5-minute read.\n"
        )
        
        # Define any additional instructions for the model
        instructions = (
            "Begin with an engaging introduction that entices the reader to continue reading. "
            "Follow with a series of well-organized sections that delve into various aspects of {topic}, "
            "each with its own engaging subheading. Include real-world examples and relevant code snippets to illustrate your points effectively. "
            "Wrap up with a meaningful conclusion that underscores the significance of {topic} and encourages reader interaction. "
            "Utilize Markdown formatting for headings, subheadings, code snippets, and lists. "
            "Please ensure clarity in explaining technical concepts and cite any sources or references used. Thank you!"
        )
        print("Generating blog content ...")
        # Combine the main prompt and additional instructions
        full_prompt = f"{main_prompt}\n{instructions}"

        # Issue the request to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",  # Assuming this is the correct chat model
            messages=[{"role": "system", "content": full_prompt}],  # Wrap the prompt in a message list
            max_tokens=3000,
            temperature=0.6,
            top_p=1.0
        )
        
        # Extract and return the generated text
        return response['choices'][0]['message']['content'].strip()

    def save_markdown_locally(self, formatted_post, filename="blog_post.md"):
        with open(filename, "w") as file:
            file.write(formatted_post)
        print(f"Markdown saved locally at {filename}")
        
    def save_markdown_locally_ai(self, formatted_post):
        file_path = "blog_post_ai.md"
        with open(file_path, "w") as file:
            file.write(formatted_post)
        print(f"Ai Markdown saved locally at {file_path}")
        
    def generate_tags_openai(self, content):
        print("Generating tags using OpenAI...")
        tag_prompt = f"Based on the following content, suggest a maximum of 4 one-word relevant keywords to this {content} that are related to technology and do not prefix the tags with # or use any non-alphanumeric characters, also the generated tag cannot be a number:\n\n{content}"
        
        try:
            tag_response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",  # Update to the latest chat model
                messages=[{"role": "system", "content": tag_prompt}],
            )
            tags_text = tag_response.choices[0].message['content'].strip()

            # Use regular expressions to filter out non-alphanumeric characters and numbers
            tags = re.findall(r'\b[a-zA-Z]+\b', tags_text)

            # Limit to a maximum of 4 tags
            tags = tags[:4]

            print("Generated tags:", tags)
            return tags
        except Exception as e:
            print(f"An error occurred while generating tags: {e}")
            return []


def main():
    print("Running main function...")
    generator = BlogPostGenerator()
    generator.config_cloudinary()
    
    # Fetch and analyze topics from Reddit
    reddit_titles = generator.fetch_hot_posts_reddit()
    if not reddit_titles:
        print("No titles were fetched from Reddit.")
        return

    best_topic = generator.analyze_topics(reddit_titles)
    print(f"best topic generated")
    if not best_topic:
        print("No topic was selected for the blog post.")
        return

    # Generate title and blog post content
    title = generator.generate_title(best_topic)
    print(f"Generated title for blog post: {title}")

    blog_post_content = generator.generate_blog_post(title, best_topic)
    print("Generated blog post content: {blog_post_content}")
    
    tags = generator.generate_tags_openai(blog_post_content)
    print(f"Final tags: {tags}\n")

    cover_image_url = generator.fetch_cover_image(best_topic)
    print(f"Generated cover image for blog post: {cover_image_url}")

    markdown_formatted_content = generator.format_in_markdown(blog_post_content, cover_image_url)
    print("Formatted blog post content in Markdown.")
    
    markdown_formatted_content_ai = generator.format_content_with_openai(blog_post_content)
    print("AI Formatted blog post content in Markdown.")

    # Save the markdown content locally
    generator.save_markdown_locally(markdown_formatted_content)
    print("Saved markdown content locally.")
    
     # Save the markdown content locally
    generator.save_markdown_locally_ai(markdown_formatted_content_ai)
    print("Saved ai markdown content locally.")
    
    if cover_image_url:
        print(f"Cover image uploaded successfully. URL: {cover_image_url}")
        markdown_formatted_content = generator.format_in_markdown(blog_post_content, cover_image_url)
        print("Formatted blog post content in Markdown.")
        generator.publish_to_devto(title, markdown_formatted_content, tags, cover_image_url)
    else:
        print("Cover image upload failed. The blog post will not be published without a cover image.")


if __name__ == "__main__":
    main()
