
import os
import json
import requests
from dotenv import load_dotenv

class OMDB:
    def __init__(self,env_path=".env"):
        load_dotenv(env_path)
        self._api_key = os.environ.get("API_KEY")
        self.data_url = "http://www.omdbapi.com"
        self.poster_url = "http://img.omdbapi.com"

    def get(self,imdbid=None,title=None,type_=None,
            year=None,fullplot=False):
        assert imdbid is not None or title is not None
        assert type_ is None or type_ in ["movie","series","episode"]
        params = {
            "apikey": self._api_key,
            "i": imdbid,
            "t": title,
            "type": type_,
            "y": year,
            "plot": "full" if fullplot else "short",
            "r": "json",  # Hard-coded json response
            "v": 1        # Hard-coded version 1
            }
        params = {k:v for k,v in params.items() if v is not None}
        resp = requests.get(self.data_url,params=params)
        return resp.json()

    def search(self,title_search,type_=None,year=None,npages=1):
        assert type_ in ["movie","series","episode"]
        assert isinstance(page,int) and 0 < year < 101
        params = {
            "s": title_search,
            "type": type_,
            "y": year,
            "page": 1,
            "r": "json", # Always JSON
            "v": 1       # Always version 1
        }
        params = {k:v for k,v in params.items() if v is not None}
        data = []
        for p in range(npages):
            params["page"] = p
            resp = requests.get(self.data_url,params=params)
            data.append(resp.json())
        return data

    def poster(self,imdbid,height=1920):
        resp = requests.get(
            self.poster_url,
            params={
                "i": imdbid,
                "h": height
            }
        )
        return resp.content()



