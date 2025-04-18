
# Inspired by Udemy course: LLM Engineering: Master AI, Large Language Models & Agents
# Creation of a brochure from defined company web page
# Scrapes fron page data and links. LLM creates summary of front page and 
# most important linked pages data, producing the company brochure 
# local llama model used directly via ollama Python library
# Fixed course material link fetching issues

import os
import json
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

# Use local LLaMA3-mallia from  Ollama
MODEL = "llama3.2:1b"
openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# to keep web site happy
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
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


link_system_prompt = """
You are provided with a list of links found on a webpage. You are able to decide which of the links would be most relevant to include in a brochure about the company, such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url}.\n"
    user_prompt += "Please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, or email links.\n"
    user_prompt += "\n".join(website.links)
    return user_prompt

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


###########################################################################
# fixes course example erros for not valid url fetches
def is_valid_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme in ("http", "https") and parsed.netloc != ""
    except Exception:
        return False

def clean_url(url):
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
    for link in links.get("links", []):
        if "url" in link:
            raw_url = clean_url(link["url"])
            if not is_valid_url(raw_url):
                print(f"[SKIP] Invalid URL: {raw_url}")
                continue
            result += f"\n\n{link['type']}\n"
            result += safe_fetch(raw_url)
        elif "urls" in link and isinstance(link["urls"], list):
            for suburl in link["urls"]:
                full_url = suburl if suburl.startswith("http") else urllib.parse.urljoin(url, suburl)
                full_url = clean_url(full_url)
                if not is_valid_url(full_url):
                    print(f"[SKIP] Invalid sub-URL: {full_url}")
                    continue
                result += f"\n\n{link['type']} (sub)\n"
                result += safe_fetch(full_url)
    return result

######################################################################################################

system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown. \
Include details of company culture, customers and careers/jobs if you have the information."

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += get_all_details(url)
    return user_prompt[:1000]

def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
    )
    print(response.choices[0].message.content)

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


###############################################################################################
#  
if __name__ == "__main__":
    test_url = "https://huggingface.co"
    company = "HuggingFace"

    print(f"====== Create_brochure: {test_url} ======")
    create_brochure(company, test_url)

    print(f"\n\n====== Create and print brochery line by line: {test_url} ======")
    stream_brochure_print(company, test_url)
