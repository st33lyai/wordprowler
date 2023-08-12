#! /usr/bin/env python3
# Wordprowler - a Python script to extract JS files, words, and URLs from a webpage
# Author: st33lyai
# Date: 12AUG2023
# Version: 1.0.1
# Usage: python3 wordprowler.py <url>
#        python3 wordprowler.py <url> -o <output_file> (output JS files, words, and URLs to a file)
#        python3 wordprowler.py <url> --js-output <js_output_file> --words-output <words_output_file> --urls-output <urls_output_file>


import argparse
import asyncio
import re
import requests
from contextlib import redirect_stdout, redirect_stderr
from playwright.async_api import async_playwright

# Function to check if a URL is live
async def is_url_live(url):
    try:
        response = await asyncio.to_thread(requests.head, url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to write to a file
async def write_to_file(filename, content):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write('\n')
        file.write(content)

# Scrape all words from the URL using Playwright
async def scrape(url, words_output_file, urls_output_file):
    try:
        if not await is_url_live(url):
            print(f"\nEndpoint {url} is not live.")
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)

            # Extract unique words from title
            title = await page.title()
            title_words = re.findall(r'\b\w+\b', title.lower())
            title_words = [word for word in title_words if re.search(r'[a-zA-Z0-9]', word)]

            # Extract unique words from content
            content = await page.evaluate('document.body.textContent')
            words = re.findall(r'\b\w+\b', content.lower())
            words = [word for word in words if re.search(r'[a-zA-Z0-9]', word)]
            
            # Combine unique words from title and content and remove duplicates
            unique_words_list = list(set(title_words + words))
            unique_words_list.sort()
            print("\nUnique words found:\n")
            for word in unique_words_list:
                print(word)


            # Extract URLs from the page
            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                return anchors.map(anchor => anchor.href);
            }''')
            
            base_url = url
            url_list = [link for link in links if link.startswith(base_url)]
            print("\nURLs found:\n")
            # remove duplicates and sort
            url_list = list(set(url_list))
            url_list.sort()
            for new_url in url_list:
                print(new_url)

            if words_output_file:
                with open(words_output_file, 'a', encoding='utf-8') as f:
                    for word in unique_words_list:
                        f.write(word + '\n')

            if urls_output_file:
                with open(urls_output_file, 'a', encoding='utf-8') as f:
                    for new_url in url_list:
                        if new_url not in urls_output_file:
                            f.write(new_url + '\n')

            await browser.close()

    except Exception as e:
        print(f"\nError while scraping {url}: {e}")

# Extract JS files from the URL using requests and regex
async def extract_js_files(url, output_file):
    try:
        response = requests.get(url)
        html_content = response.text
        js_files = re.findall(r'<script\s+src=["\'](.*?)["\']', html_content)
        print("\nJS files found:\n")
        if not js_files:
            print("No JS files found.")
            return

        for js_file in js_files:
            js_file_cleaned = re.sub(r'\?.*', '', js_file)
            if js_file_cleaned.startswith('//'):
                js_file_cleaned = url.split('//')[0] + js_file_cleaned
            print(js_file_cleaned)

        if output_file:
            with open(output_file, 'a', encoding='utf-8') as f:
                for js_file in js_files:
                    js_file_cleaned = re.sub(r'\?.*', '', js_file)
                    f.write(js_file_cleaned + '\n')
    except Exception as e:
        print(f"\nError while extracting JS files from {url}: {e}")

async def main(args):
    url = args.url

    if args.output_all is None:
        await extract_js_files(url, args.js_output)
        await scrape(url, args.words_output, args.urls_output)
    else:
        with open(args.output_all, 'w', encoding='utf-8') as output_file:
            with redirect_stdout(output_file), redirect_stderr(output_file):
                await extract_js_files(url, args.output_all)
                await scrape(url, args.output_all, args.output_all)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract JS files, words, and URLs from a webpage')
    parser.add_argument('url', help='URL of the webpage to scrape')
    parser.add_argument('-o', '--output-all', help='Output file for JS files, words, and URLs')
    parser.add_argument('--js-output', help='Output file for JS files only')
    parser.add_argument('--words-output', help='Output file for unique words only')
    parser.add_argument('--urls-output', help='Output file for URLs only')
    args = parser.parse_args()
    asyncio.run(main(args))
