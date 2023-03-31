import json
import requests
from bs4 import BeautifulSoup
import os

# create image folder
os.makedirs("images", exist_ok=True)


def get_image_from_url(url):
    URL = url  # Replace this with the website's URL
    getURL = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(getURL.text, "html.parser")

    images = soup.find_all("img")
    resolvedURLs = []
    for image in images:
        src = image.get("src")
        resolvedURLs.append(requests.compat.urljoin(URL, src))

    for image in resolvedURLs:
        webs = requests.get(image)
        open("images/" + image.split("/")[-1], "wb").write(webs.content)


def get_urls_from_wayback(url):
    urls = requests.get(url).text
    parse_url = json.loads(urls)  # parses the JSON from urls.
    ## Extracts timestamp and original columns from urls and compiles a url list.
    url_list = []
    for i in range(1, len(parse_url)):
        orig_url = parse_url[i][2]
        tstamp = parse_url[i][1]
        waylink = tstamp + "/" + orig_url
        url_list.append(waylink)
    ## Compiles final url pattern.
    final_url_list = []
    for url in url_list:
        final_url = "https://web.archive.org/web/" + url
        final_url_list.append(final_url)
    return final_url_list


if __name__ == "__main__":
    target_urls = os.environ.get("TARGET_URLS", "").split(",")
    all_urls = []
    for tu in target_urls:
        url = f"https://web.archive.org/cdx/search/cdx?url={tu}/*&collapse=digest&output=json"
        urls = get_urls_from_wayback(url)
        all_urls.extend(urls)

    downloaded_urls = []
    # create downloaded.txt if not exists
    if not os.path.exists("downloaded.txt"):
        open("downloaded.txt", "w").close()
    # read downloaded urls from file
    with open("downloaded.txt", "r") as f:
        downloaded_urls = f.readlines()
    downloaded_urls = [url.strip() for url in downloaded_urls]
    # remove downloaded urls
    all_urls = [url for url in all_urls if url not in downloaded_urls]
    for url in all_urls:
        try:
            get_image_from_url(url)
            print(f"Downloaded {url}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # append downloaded url to file
            with open("downloaded.txt", "a") as f:
                f.write(url + "\n")