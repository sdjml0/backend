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
    async def get_user_products(userid: UUID, limit: int = 50, offset: int = 0) -> ProductListResponse:
        records = await ProductRepository.get_products_by_user(userid, limit=limit, offset=offset)
        items = [ProductResponse(**r) for r in records]
        return ProductListResponse(count=len(items), data=items)

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
