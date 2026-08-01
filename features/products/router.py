from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status

from core.dependencies import get_current_user
from features.products.schema import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from features.products.service import ProductService

router = APIRouter(
    prefix="/v1/products",
    tags=["Product Management CRUD"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
async def create_product(
    product_data: ProductCreate,
    userid: UUID = Depends(get_current_user)
):
    """
    Create a new product record associated with the authenticated user.
    """
    return await ProductService.create_product(userid, product_data)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List user products with pagination and store filtering"
)
async def get_user_products(
    storeid: Optional[UUID] = Query(None, description="Filter products by Store ID"),
    store_id: Optional[UUID] = Query(None, description="Alias for storeid filter"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    limit: Optional[int] = Query(None, ge=1, le=200, description="Max items to retrieve (legacy limit)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of items to skip (legacy offset)"),
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieve products belonging to the authenticated user with store filtering and page-based pagination.
    """
    target_store = storeid or store_id
    return await ProductService.get_user_products(
        userid,
        storeid=target_store,
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset
    )


@router.get(
    "/store/{storeid}",
    response_model=ProductListResponse,
    summary="Get products for a specific store"
)
async def get_store_products(
    storeid: UUID,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    limit: Optional[int] = Query(None, ge=1, le=200, description="Max items to retrieve (legacy limit)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of items to skip (legacy offset)"),
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieve paginated products belonging to a specific store ID (e.g. Amazon, Shopify).
    """
    return await ProductService.get_user_products(
        userid,
        storeid=storeid,
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset
    )



@router.get(
    "/{productid}",
    response_model=ProductResponse,
    summary="Get product details by ID"
)
async def get_product_by_id(
    productid: UUID,
    userid: UUID = Depends(get_current_user)
):
    """
    Retrieve details of a specific product by its UUID.
    """
    return await ProductService.get_product_by_id(productid, userid)


@router.put(
    "/{productid}",
    response_model=ProductResponse,
    summary="Update product details"
)
async def update_product(
    productid: UUID,
    product_data: ProductUpdate,
    userid: UUID = Depends(get_current_user)
):
    """
    Update fields of an existing product by its UUID.
    """
    return await ProductService.update_product(productid, userid, product_data)


@router.delete(
    "/{productid}",
    summary="Delete a product"
)
async def delete_product(
    productid: UUID,
    userid: UUID = Depends(get_current_user)
):
    """
    Delete a product record by its UUID.
    """
    return await ProductService.delete_product(productid, userid)
