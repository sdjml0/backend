import math
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status

from features.products.repository import ProductRepository
from features.products.schema import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse


class ProductService:

    @staticmethod
    async def create_product(userid: UUID, product_data: ProductCreate) -> ProductResponse:
        record = await ProductRepository.create_product(userid, product_data)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create product."
            )
        return ProductResponse(**record)

    @staticmethod
    async def get_product_by_id(productid: UUID, userid: UUID) -> ProductResponse:
        record = await ProductRepository.get_product_by_id(productid, userid)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID '{productid}' not found."
            )
        return ProductResponse(**record)

    @staticmethod
    async def get_user_products(
        userid: UUID,
        storeid: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 10,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> ProductListResponse:
        effective_limit = limit if limit is not None else page_size
        if offset is not None:
            effective_offset = offset
            effective_page = (offset // effective_limit) + 1
        else:
            effective_page = max(1, page)
            effective_offset = (effective_page - 1) * effective_limit

        records, total_records = await ProductRepository.get_products_paginated_by_user(
            userid, storeid=storeid, limit=effective_limit, offset=effective_offset
        )

        items = [ProductResponse(**r) for r in records]

        total_pages = math.ceil(total_records / effective_limit) if total_records > 0 else 0
        has_next = effective_page < total_pages
        has_prev = effective_page > 1

        return ProductListResponse(
            total=total_records,
            page=effective_page,
            page_size=effective_limit,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            count=len(items),
            data=items
        )



    @staticmethod
    async def update_product(productid: UUID, userid: UUID, product_data: ProductUpdate) -> ProductResponse:
        existing = await ProductRepository.get_product_by_id(productid, userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID '{productid}' not found."
            )

        updated_record = await ProductRepository.update_product(productid, userid, product_data)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update product."
            )
        return ProductResponse(**updated_record)

    @staticmethod
    async def delete_product(productid: UUID, userid: UUID) -> dict:
        existing = await ProductRepository.get_product_by_id(productid, userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID '{productid}' not found."
            )

        success = await ProductRepository.delete_product(productid, userid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete product."
            )
        return {"success": True, "message": f"Product '{productid}' successfully deleted."}
