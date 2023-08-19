#! /usr/bin/env python3
# Wordprowler - a Python script to extract Javascript files, words, and URLs from a webpage
# Author: st33lyai
# Date: 18AUG2023
# Version: 1.0.2
# Usage: python3 wordprowler.py <url>
#        python3 wordprowler.py <url> -o <output_file> (output Javascript files, words, and URLs to a file)
#        python3 wordprowler.py <url> --js-output <js_output_file> --words-output <words_output_file> --urls-output <urls_output_file>

import argparse
import asyncio
import re
from contextlib import redirect_stdout, redirect_stderr
from playwright.async_api import async_playwright


# Function to write to a file
async def write_to_file(filename, content):
    if filename:
        with open(filename, 'a', encoding='utf-8') as file:
            file.write('\n')
            file.write(content)


# Scrape all words from the URL using Playwright, including following redirects

async def scrape(url, js_output_file, words_output_file, urls_output_file):
    try:  
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(ignore_https_errors=args.insecure)
            
            # Follow redirects and navigate to the final URL
            response = await page.goto(args.url)
            final_url = response.url

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
            print("\nWords scraped:\n")
            for word in unique_words_list:
                print(word)
            await write_to_file(words_output_file, '\n'.join(unique_words_list))
            # Extract URLs from the page
            url_links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                return anchors.map(anchor => anchor.href);
            }''')
            
            # Extract Javascript files from the page
            js_links = await page.evaluate('''() => {
                const scripts = Array.from(document.querySelectorAll('script'));
                return scripts.map(script => script.src);
            }''')
            
            if not js_links:
                print("\nNo Javascript files found.")
                pass
            else:
                js_links = [link.rstrip() for link in js_links if link.strip()]
                print("\nJavascript files found:\n")
                
                js_links = list(set(js_links))
                js_links.sort()
                for js_link in js_links:
                    print(js_link)
                await write_to_file(js_output_file, '\n'.join(js_links))
            
            if not url_links:
                print("\nNo URLs found.")
                pass
            else:
                base_url = final_url
                url_list = [link for link in url_links if link.startswith(base_url)]
                print("\nURLs found:\n")
                url_list = list(set(url_list))
                url_list.sort()
                for new_url in url_list:
                    print(new_url)
                await write_to_file(urls_output_file, '\n'.join(url_list))

            await browser.close()

    except Exception as e:
        print(f"\nError while scraping {args.url}: {e}")
        pass

async def main(args):
    if args.output_all is None:
        await scrape(args.url, args.js_output, args.words_output, args.urls_output)
    else:
        with open(args.output_all, 'w', encoding='utf-8') as output_file:
            with redirect_stdout(output_file), redirect_stderr(output_file):
                await scrape(args.url, args.output_all, args.output_all, args.output_all)
        print(f"\nJavascript files, words, and URLs extracted from {args.url} are saved to {args.output_all}.\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract Javascript files, words, and URLs from a webpage')
    parser.add_argument('url', help='URL of the webpage to scrape')
    parser.add_argument('-o', '--output-all', required=False, help='Output file for Javascript files, words, and URLs')
    parser.add_argument('--js-output', required=False, help='Output file for Javascript files only')
    parser.add_argument('--words-output', required=False, help='Output file for unique words only')
    parser.add_argument('--urls-output', required=False, help='Output file for URLs only')
    parser.add_argument('-k', '--insecure', action='store_true', required=False, help='Disable SSL verification')
    args = parser.parse_args()
    asyncio.run(main(args))
