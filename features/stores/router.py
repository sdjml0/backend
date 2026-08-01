from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from core.dependencies import get_current_user
from features.stores.schema import StoreCreate, StoreUpdate, StoreResponse, StoreListResponse
from features.stores.service import StoreService
from features.products.schema import ProductListResponse
from features.products.service import ProductService


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


@router.get(
    "/{storeid}/products",
    response_model=ProductListResponse,
    summary="List products for a specific store"
)
async def get_products_by_store(
    storeid: UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    limit: Optional[int] = Query(None, ge=1, le=200, description="Max items to retrieve (legacy limit)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of items to skip (legacy offset)"),
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieve paginated products for a specific connected store (e.g., Amazon, Shopify).
    """
    return await ProductService.get_user_products(
        userid,
        storeid=storeid,
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset
    )



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
