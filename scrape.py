
import re
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from tqdm import tqdm


START_URL = "https://film-grab.com/movies-a-z"
STILL_ZIP_BASE_PATH = Path("./raw-movie-stills/")
STILL_ZIP_BASE_PATH.mkdir(exist_ok=True)
METADATA_PATH = Path("./filmgrab-metadata.json")

def get_movie_list():
    start_page = requests.get(START_URL)
    soup = BeautifulSoup(start_page.content,"lxml")
    ul = soup.find("ul",attrs={"class":"display-posts-listing"})
    lis = ul.find_all("li")
    return [
        {"title":li.text,"link":li.find("a").attrs.get("href")}
        for li in lis]

def get_download_link(soup):
    return soup.find(
        "div",attrs={
        "class":"bwg_download_gallery"
    }).find("a").attrs.get("href")

def download_zip(fn,link):
    resp = requests.get(link)
    with open(fn,"wb") as f:
        f.write(resp.content)

def get_metadata(soup):
    ec = soup.find("div",attrs={"class":"entry-content"})
    last = None
    dat = []
    for c in ec.find_all(recursive=False):
        if c.name == "p": dat.append(c)
        elif last == "p": break
        last = c.name
    try:
        dat = {k.strip():v.strip() for k, v in [d.text.split(":") for d in dat]}
    except Exception as e:
        print("Error getting metadata",e)
        dat = [d.text for d in dat]
    return dat

def process_movie(name,link,download=True):
    resp = requests.get(link)
    soup = BeautifulSoup(resp.content,"lxml")
    dl_link = get_download_link(soup)
    fn = STILL_ZIP_BASE_PATH / \
        f'stills-{name.lower().replace(" ","_")}.zip'
    if download:
        download_zip(fn,dl_link)
    metadata = get_metadata(soup)
    return {"zip-filename":f"{fn}","metadata":metadata}

def process_movie_eh(name,link,download=True):
    try:
        return process_movie(name,link,download=download)
    except Exception as e:
        # print(f"ERROR: Movie {m} had error {e}")
        return {"error": str(e)}

def main():
    print("Starting up...")
    print("Getting initial list...")
    movie_list = get_movie_list()
    print(f"Found {len(movie_list)} movies")
    movie_data = [
        {**m,**process_movie_eh(m["title"],m["link"])}
        for m in tqdm(movie_list,desc="Movies Processed",ncols=80)
    ]
    print("Done downloading movies.")
    print("Saving metadata...")
    with open(METADATA_PATH,"w") as f:
        json.dump(movie_data,f)
    print("Done.")

if __name__ == "__main__":
    main()

