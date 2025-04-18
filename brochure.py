
# Inspired by Udemy course: LLM Engineering: Master AI, Large Language Models & Agents
# Creation of a brochure from defined company web page
# Scrapes fron page data and links. LLM creates summary of front page and 
# most important linked pages data, producing the company brochure 
# local llama model used directly via ollama Python library

import ollama
import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import urllib.parse
import time
import requests
from urllib.parse import urljoin, urlparse


# model needs to be run in Linux as: ollama run llama3.2:1b
MODEL = "llama3.2:1b" # for weak machines

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# connect local open "weak machine" ollama model
openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

#######################################################################3
class Website:
    """
    A utility class to represent a Website that we have scraped, now with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

#######################################################################################


test=Website("https://edwarddonner.com")

print(f"********* Weppisite **********\n {test.get_contents()}")
print("********* Found Links **************")
for i, link in enumerate(test.links, 1):
    print(f"{i}. {link}")
print (f".........................................................................")

link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""
print (f"-----> Used link_system_prompt")
print(link_system_prompt)
print (f".........................................................................")


def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

print (f"-------> Getting links with get_links_user_prompt(test)")
print(get_links_user_prompt(test))
print (f".........................................................................")



def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)



print (f"------------------> website: https://huggingface.co")
huggingface = Website("https://huggingface.co")
print (f".........................................................................")


print (f"***************https://huggingface.c********************************")
huggingface_links =get_links("https://huggingface.co")
print("******* Filtered Brochure Links *******")
print(json.dumps(huggingface_links, indent=2))
print (f".........................................................................")


# fixes course example problem with url and urls and with not complete urls
def xxxget_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Found links:", links)
    for link in links["links"]:
        if "url" in link:
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()
        elif "urls" in link and isinstance(link["urls"], list):
            for suburl in link["urls"]:
                # Jos linkki on suhteellinen, tee siitä absoluuttinen
                full_url = suburl if suburl.startswith("http") else os.path.join(url, suburl)
                result += f"\n\n{link['type']} (sub)\n"
                result += Website(full_url).get_contents()
    return result

#######################################################################################
# fixes course example problems for not full url etc "not working links"

def is_valid_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme in ("http", "https") and parsed.netloc != ""
    except Exception:
        return False

def clean_url(url):
    # Poistetaan välilyönnit ja korvataan enkoodatut välit
    return url.replace(" ", "").replace("%20", "")

def safe_fetch(url, max_retries=2):
    for attempt in range(max_retries):
        try:
            return Website(url).get_contents()
        except requests.exceptions.RequestException as e:
            print(f"[WARN] Fetch failed ({attempt+1}/{max_retries}) for {url}: {e}")
            time.sleep(1)
    return f"[ERROR] Failed to fetch: {url}\n"

def get_all_details(url):
    result = "Landing page:\n"
    result += safe_fetch(url)
    links = get_links(url)
    print("Found links:", links)

    for link in links.get("links", []):
        # Yksi suora URL
        if "url" in link:
            raw_url = clean_url(link["url"])
            if not is_valid_url(raw_url):
                print(f"[SKIP] Invalid URL: {raw_url}")
                continue
            result += f"\n\n{link['type']}\n"
            result += safe_fetch(raw_url)

        # Lista useammasta URL:sta
        elif "urls" in link and isinstance(link["urls"], list):
            for suburl in link["urls"]:
                suburl = clean_url(suburl)
                full_url = suburl if suburl.startswith("http") else urllib.parse.urljoin(url, suburl)
                if not is_valid_url(full_url):
                    print(f"[SKIP] Invalid sub-URL: {full_url}")
                    continue
                result += f"\n\n{link['type']} (sub)\n"
                result += safe_fetch(full_url)

    return result

##################################################################################################

print (f"-----------> get_all_details https://hugginface.co")
print(get_all_details("https://huggingface.co"))
print (f".........................................................................")


system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."

# use prompt to set creation style...
# system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
# and creates a short humorous, entertaining, jokey brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
# Include details of company culture, customers and careers/jobs if you have the information."


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:1000] # Truncate if more than 1000 chars, bigger value cause my local machine to crash
    return user_prompt

print (f".....get_brochure_user_prompt.............https://anthropic.com.......................................")
get_brochure_user_prompt("Anthropic", "https://anthropic.com")
print (f".........................................................................")

##########################################################################################################
def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
    )
    result = response.choices[0].message.content
    print(f"{result}")

##########################################################################################################


print (f".....create_brochure..................https://huggingface.co................................")
create_brochure("Hugginface", "https://huggingface.co")

###########################################################################################################
# print created brochure line by line
def stream_brochure_print(company_name, url):
    stream = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        stream=True
    )

    for chunk in stream:
        part = chunk.choices[0].delta.content or ''
        print(part, end='', flush=True)
################################################################################################################

print (f".....stream_brochure line by line printing..........https://huggingface.co........................................")
stream_brochure_print("HuggingFace", "https://huggingface.co")