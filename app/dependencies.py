from enum import Enum

from typing import Union

from fastapi import Query


class CategoryEnum(Enum):
    characters = "characters"
    comics = "comics"


class CommonQueryParams:
    def __init__(
        self,
        category: CategoryEnum = CategoryEnum.characters,
        pageIndex: int = Query(0, ge=0),
        pageSize: int = Query(10, ge=1, le=100),
        startsWith: Union[str, None] = None,
        exactly: Union[str, None] = None,
    ):
        self.category = category
        self.exactly = exactly
        self.pageIndex = pageIndex
        self.pageSize = pageSize
        self.startsWith = startsWith

    def get_params(self):
        return {
            "category": self.category,
            "limit": self.pageSize,
            "name": self.exactly,
            "nameStartsWith": self.startsWith,
            "offset": self.pageSize * self.pageIndex,
            "pageIndex": self.pageIndex,
            "title": self.exactly,
            "titleStartsWith": self.startsWith,
        }
