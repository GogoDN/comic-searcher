import httpx
import hashlib
import math

from fastapi import HTTPException

from datetime import datetime

from ...config import settings
from ...dependencies import CategoryEnum


class MarvelApiClient:
    COMMON_PARAMS = ["limit", "offset"]
    CHARACTER_PARAMS = COMMON_PARAMS + ["name", "nameStartsWith"]
    COMIC_PARAMS = COMMON_PARAMS + ["title", "titleStartsWith"]

    def __init__(self) -> None:
        self.base_url = "https://gateway.marvel.com/v1/public"
        self.public_key = settings.marvel_public_key
        self.private_key = settings.marvel_private_key
        self.client = httpx.AsyncClient()

    def __get_mandatory_params(self) -> dict:
        now = datetime.now()
        ts = datetime.timestamp(now)
        md5_string = f"{str(ts)}{self.private_key}{self.public_key}".encode()
        md5_hash = hashlib.md5(md5_string).hexdigest()

        return {
            "apikey": self.public_key,
            "ts": ts,
            "hash": md5_hash,
        }

    def __parse_characters(self, collection: dict):
        output = []
        for character in collection:
            output.append(
                {
                    "id": character.get("id"),
                    "name": character.get("name"),
                    "image": character.get("thumbnail").get("path"),
                    "appereances": character.get("comics").get("available"),
                }
            )
        return output

    def __parse_comics(self, collection: dict):
        output = []
        for comic in collection:
            on_sale_date = [
                date
                for date in comic.get("dates")
                if date.get("type") == "onsaleDate"
            ][0]
            output.append(
                {
                    "id": comic.get("id"),
                    "title": comic.get("title"),
                    "image": comic.get("thumbnail").get("path"),
                    "onSaleDate": on_sale_date.get("date"),
                }
            )
        return output

    def __get_category_params(self, params: dict, allowed_param_list: list):
        return {
            k: v
            for k, v in params.items()
            if k in allowed_param_list and v is not None
        }

    def __get_options_by_category(self, category: CategoryEnum):
        if category == CategoryEnum.comics:
            return (
                self.COMIC_PARAMS,
                "comics",
                self.__parse_comics,
                self.base_url + "/comics",
            )
        return (
            self.CHARACTER_PARAMS,
            "characters",
            self.__parse_characters,
            self.base_url + "/characters",
        )

    async def __perform_get(self, url, params):
        try:
            response = await self.client.get(url=url, params=params)
        except Exception:
            raise HTTPException(
                503, detail="Communication with external resources unavailable"
            )

        return response

    async def get_data(self, params: dict):
        (
            allowed_params,
            key,
            parse_function,
            url,
        ) = self.__get_options_by_category(params.get("category"))
        request_params = self.__get_mandatory_params()
        request_params.update(
            self.__get_category_params(params, allowed_params)
        )
        response = await self.__perform_get(url, request_params)
        data = response.json().get("data")
        output = {
            "totalPages": math.ceil(data.get("total") / params.get("limit")),
            "page": params.get("pageIndex"),
            key: parse_function(data.get("results")),
        }
        return output
