from uuid import UUID
from fastapi import HTTPException, status

from features.stores.repository import StoreRepository
from features.stores.schema import StoreCreate, StoreUpdate, StoreResponse, StoreListResponse


class StoreService:

    @staticmethod
    async def create_store(userid: UUID, store_data: StoreCreate) -> StoreResponse:
        record = await StoreRepository.create_store(userid, store_data)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create store."
            )
        return StoreResponse(**record)

    @staticmethod
    async def get_store_by_id(storeid: UUID, userid: UUID) -> StoreResponse:
        record = await StoreRepository.get_store_by_id(storeid, userid)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with ID '{storeid}' not found."
            )
        return StoreResponse(**record)

    @staticmethod
    async def get_user_stores(userid: UUID, limit: int = 50, offset: int = 0) -> StoreListResponse:
        records = await StoreRepository.get_stores_by_user(userid, limit=limit, offset=offset)
        items = [StoreResponse(**r) for r in records]
        return StoreListResponse(count=len(items), data=items)

    @staticmethod
    async def update_store(storeid: UUID, userid: UUID, store_data: StoreUpdate) -> StoreResponse:
        existing = await StoreRepository.get_store_by_id(storeid, userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with ID '{storeid}' not found."
            )

        updated_record = await StoreRepository.update_store(storeid, userid, store_data)
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update store."
            )
        return StoreResponse(**updated_record)

    @staticmethod
    async def delete_store(storeid: UUID, userid: UUID) -> dict:
        existing = await StoreRepository.get_store_by_id(storeid, userid)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with ID '{storeid}' not found."
            )

        success = await StoreRepository.delete_store(storeid, userid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete store."
            )
        return {"success": True, "message": f"Store '{storeid}' successfully deleted."}
