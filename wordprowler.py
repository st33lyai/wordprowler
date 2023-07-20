import asyncio
import re
import requests

from playwright.async_api import async_playwright

# Function to check if a URL is live
async def is_url_live(url):
    try:
        response = await asyncio.to_thread(requests.head, url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Scrape all words from the URL
async def scrape(url, depth=0):
    try:
        if not await is_url_live(url):
            print(f"\nEndpoint {url} found, but not live.")
            return

        async with async_playwright() as p:
            browser = await p.firefox.launch()
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            text_content = await page.inner_text('body')
            words = text_content.split()
            words = [word.lower() for word in words]

            links = await page.query_selector_all('a')
            url_list = []
            for link in links:
                href = await link.get_attribute('href')
                if href and href.startswith('http'):
                    url_list.append(href)

            await context.close()
            await browser.close()

            cleaned_words = []
            for word in words:
                # Split the word based on non-word characters
                split_parts = re.split(r'\W+', word)
                cleaned_words.extend(split_parts)

                # If the word was split due to special characters, concatenate and add it
                if len(split_parts) > 1:
                    concatenated_word = ''.join(split_parts)
                    cleaned_words.append(concatenated_word)

            # Remove blank values from the cleaned_words list
            cleaned_words = [word for word in cleaned_words if word]

            # Use a set to remove duplicates
            unique_words = set(cleaned_words)

            # Convert the set back to a list for printing the final output
            unique_words_list = list(unique_words)
            unique_words_list.sort()
            
            print("Words found:")
            for word in unique_words_list:
                print(word)
            print(f"\n{len(unique_words_list)} unique words found.\n")
            
            #if url_list isn't empty, print the urls. don't print duplicates
            if url_list:
                print(f"URLs found:")
                for new_url in url_list:
                    if new_url not in url:
                        print(new_url)


    except Exception as e:
        print(f"\nError while scraping {url}: {e}")

url = input('Enter the url to be scraped: ')
asyncio.run(scrape(url))
