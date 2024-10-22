import csv
import re
from playwright.sync_api import sync_playwright

def scrape_linkedin(query, num_posts=10):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False to see the browser
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})

        # Log in to LinkedIn
        page.goto('https://www.linkedin.com/login')
        page.fill('#username', '2000331530035@rkgit.edu.in')  # Replace with your credentials
        page.fill('#password', 'Roy@1234')  # Replace with your password
        page.click('button[type="submit"]')
        page.wait_for_timeout(5000)  # Wait for login to complete

        # Perform search
        search_url = f'https://www.linkedin.com/search/results/content/?keywords={query}'
        page.goto(search_url)

        posts_data = []

        while len(posts_data) < num_posts:
            page.wait_for_timeout(3000)  # Wait for posts to load
            posts = page.query_selector_all('div.update-components-text.relative')

            for post in posts:
                if len(posts_data) >= num_posts:
                    break

                content = post.inner_text().strip()
                hashtags = extract_unique_hashtags(content)
                filtered_content = re.sub(r'#\w+', '', content).replace('hashtag', '').strip()

                author = post.query_selector('span.feed-shared-actor__name') or post.query_selector('.update-components-actor__name')
                author_name = author.inner_text().strip() if author else "Unknown Author"

                image = post.query_selector('img')
                image_url = image.get_attribute('src') if image else "No Image Available"

                post_url_element = post.query_selector('a.app-aware-link')
                post_url = post_url_element.get_attribute('href') if post_url_element else "No URL"

                posts_data.append({
                    'Content': filtered_content,
                    'Hashtags': ', '.join(hashtags),
                    #'Image URL': image_url,
                    #'Author': author_name,
                    'Post URL': post_url
                })

            if len(posts_data) < num_posts:
                page.mouse.wheel(0, 3000)  # Scroll down

        browser.close()
        return posts_data

def extract_unique_hashtags(content):
    return list(set(re.findall(r'#\w+', content)))

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Content', 'Hashtags', 'Image URL', 'Author', 'Post URL'])
        writer.writeheader()
        writer.writerows(data)
