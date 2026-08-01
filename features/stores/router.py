from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from core.dependencies import get_current_user
from features.stores.schema import StoreCreate, StoreUpdate, StoreResponse, StoreListResponse
from features.stores.service import StoreService

router = APIRouter(
    prefix="/v1/stores",
    tags=["Store Management CRUD"]
)


@router.post(
    "",
    response_model=StoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Connect / Create a new store"
)
async def create_store(
    store_data: StoreCreate,
    userid: UUID = Depends(get_current_user)
):
    """
    Create/connect a new marketplace store associated with the authenticated user.
    """
    return await StoreService.create_store(userid, store_data)


@router.get(
    "",
    response_model=StoreListResponse,
    summary="List connected stores"
)
async def get_user_stores(
    limit: int = Query(50, ge=1, le=200, description="Max items to retrieve"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieve all stores connected to the authenticated user account.
    """
    return await StoreService.get_user_stores(userid, limit=limit, offset=offset)


@router.get(
    "/{storeid}",
    response_model=StoreResponse,
    summary="Get store details by ID"
)
async def get_store_by_id(
    storeid: UUID,
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieve details of a specific store by its UUID.
    """
    return await StoreService.get_store_by_id(storeid, userid)


@router.put(
    "/{storeid}",
    response_model=StoreResponse,
    summary="Update store details or status"
)
async def update_store(
    storeid: UUID,
    store_data: StoreUpdate,
    userid: UUID = Depends(get_current_user)
):
    """
    Update platform, region, or connection status for an existing store.
    """
    return await StoreService.update_store(storeid, userid, store_data)


@router.delete(
    "/{storeid}",
    summary="Delete / disconnect a store"
)
async def delete_store(
    storeid: UUID,
    userid: UUID = Depends(get_current_user)
):
    """
    Delete a store record by its UUID.
    """
    return await StoreService.delete_store(storeid, userid)
