# Wordprowler V1.0.2

Wordprowler is a word scraping tool that can pull unique words and urls from webpages loaded via javascript.

___
## NOTE: I AM NOT A DEVELOPER, JUST LIKE TO BUILD TOOLS THAT DO WHAT I NEED THEM TO DO AND SHARE THEM. WITH THAT BEING SAID, I AM NOT RESPONSIBLE FOR HOW YOU USE THIS TOOL!

# Installation
```
git clone https://github.com/st33lyai/wordprowler.git
cd wordprowler
pip install -r requirements.txt
playwright install 
```

___

# Usage  

```
chmod +x wordprowler.py
./wordprowler.py <url>
```

___

## To do:
```
 - [ ] add a capability to spider discovered urls
 - [ ] add arguments to output words, urls, or both to a file
 - [X] add argument to set parameters for the spider, to include a scope option
 - [ ] add a feature to compare words crawled to a wordlist and only keep the ones not in the wordlist

```

___

### Backstory

Wordprowler is the result of me building a recon script for pentesting and CTFs in python. I wanted to add the functionality to generate a wordlist from a target page to assist in endpoint enumeration, and planned 
on using cewl, but found that cewl doesn't work against pages that are loaded via javascript. I decided to use this as another opportunity to build a different tool, dabble in webscraping, practice more with python,
and potentially offer a tool to help the community. 

