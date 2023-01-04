from fastapi import APIRouter, Depends

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
