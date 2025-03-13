import requests
from urllib.parse import urlparse
from duckduckgo_search import DDGS
import time

from typing import Tuple, List, Dict

def get_github_data(github_url) -> Dict[str, str | int]:
    # Parse the URL to extract the username
    path = urlparse(github_url).path
    username = path.strip("/").split("/")[0]

    # GitHub API to fetch user details
    api_url = f"https://api.github.com/users/{username}"
    response = requests.get(api_url)

    if response.status_code == 200:
        user_data = response.json()
        return user_data
    else:
        return None

def fetch_github_readme(response: Dict[str, str | int]) -> str:
    # Fetch the README.md file from the user's GitHub repository
    url = f"https://raw.githubusercontent.com/{response["login"]}/{response["login"]}/refs/heads/main/README.md"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return ""


def get_linkedin_name(linkedin_url: str) -> Tuple[str, str]:
    # Use DuckDuckGo to fetch the name from the LinkedIn URL
    if linkedin_url[-1] == "/":
        linkedin_url = linkedin_url[:-1]
    
    res = DDGS().text(f"{linkedin_url}", max_results=2)
    if res is not None:
        for r in res:
            if "LinkedIn" in r.get("title", ""):
                sliced = r["title"].split("-")
                name = sliced[0].strip()
                return name, sliced[1].strip().split(",")[0] if len(sliced) == 3 else ""
    return "", ""

def fetch_pages_from_name(name: str, place: str, debug: bool=False)-> List[str]:
    # Fetch additional web pages from name
    """
    [
        {
        'title': 'Page title',
        'href': 'Page url',
        'body': "Page body"
        },
    ]
    """
    res = DDGS().text(f"{name} {place}", max_results=10)
    if debug:
        print(res)
    return [r["href"] for r in res if "linkedin.com/in" not in r["href"] and (name.lower() in r["body"].lower() or name.lower() in r["title"].lower())]

class SupplementSource:
    def __init__(self, urls: List[str]):
        self.linkedin = None
        self.github = None
        self.li_name = ""
        self.li_place = ""
        self.gh_data = None

        for url in urls:
            if self.linkedin is None and "linkedin.com/in" in url:
                self.linkedin = url
                
            elif self.github is None and "github.com" in url:
                self.github = url
            
            if self.linkedin is not None and self.github is not None:
                break
        
        if self.linkedin is not None:
            self.li_name, self.li_place = get_linkedin_name(self.linkedin)
        if self.github is not None:
            self.gh_data = get_github_data(self.github)
    
    def get(self)-> Tuple[str, List[str]]:
        supplement_text = []
        urls = []
        try:
            if self.gh_data is not None:
                gh_name = self.gh_data.get("name", "")
                if self.li_name != "" and self.li_name.lower() == gh_name.lower():
                    supplement_text.append(f"Both GitHub and LinkedIn source agree the person's name is {self.li_name}.")
                elif gh_name != "":
                    supplement_text.append(f"GitHub source suggests the person's name is {self.li_name}.")
                if self.gh_data["blog"] is not None:
                    urls.append(self.gh_data["blog"])
                if self.gh_data["email"] is not None:
                    supplement_text.append(f"{gh_name}'s GitHub email: {self.gh_data['email']}.")
                readme = fetch_github_readme(self.gh_data)
                if readme != "":
                    supplement_text.append(f"{gh_name}'s GitHub README: {readme}.")
                if self.gh_data["html_url"] is not None:
                    supplement_text.append(f"{gh_name}'s GitHub profile: {self.gh_data['html_url']}.")

            if self.li_name != "":
                if self.gh_data is None or self.gh_data.get("name", "") != self.li_name:
                    supplement_text.append(f"LinkedIn source suggests the person's name is {self.li_name}.")
                time.sleep(1)
                pages = fetch_pages_from_name(self.li_name, self.li_place)
                urls.extend(pages)
        except Exception as e:
            print(f"Error in SupplementSource.get: {e}")

        return "\n".join(supplement_text), urls


if __name__ == "__main__":
    # github_url = "https://github.com/rudra-singh1"
    github_url = "https://github.com/yanful"
    user_data = get_github_data(github_url)
    print(user_data)
    print(user_data.get("name", "Name not available"))
    readme = fetch_github_readme(user_data)
    print(readme)

    # linkedin_url = ["https://www.linkedin.com/in/rudra-p-singh/"]
    # name, place = get_linkedin_name(linkedin_url)
    # print(name)

    # time.sleep(2)

    # pages = fetch_pages_from_name(name, place, debug=True)
    # print(pages)