from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..clients.external.marvel import MarvelApiClient
from ..dependencies import CommonQueryParams


router = APIRouter(
    prefix="/searchComics",
    tags=["search_comics"],
    responses={404: {"description": "Not Found"}},
)


@router.get("/")
async def find(
    query_params: CommonQueryParams = Depends(CommonQueryParams),
    client: MarvelApiClient = Depends(MarvelApiClient),
):
    return await client.get_data(query_params.get_params())


@router.get("/comics/{comic_id}")
async def find_characters(
    comic_id: int,
    client: MarvelApiClient = Depends(MarvelApiClient),
):
    response = await client.get_comic_by_id(comic_id)
    if not response:
        return JSONResponse({"message": "Not Found"})
    return response
