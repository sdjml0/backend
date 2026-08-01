from __future__ import annotations
from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class StoreCreate(BaseModel):
    platform: str = Field(..., min_length=2, max_length=100, description="Store platform (e.g. Shopify, Amazon, eBay)")
    country: Optional[str] = Field("Global", max_length=100, description="Country or operating region")
    status: Optional[Literal["connected", "disconnected", "syncing"]] = Field("connected", description="Store connection status")


class StoreUpdate(BaseModel):
    platform: Optional[str] = Field(None, min_length=2, max_length=100, description="Updated platform name")
    country: Optional[str] = Field(None, max_length=100, description="Updated country")
    status: Optional[Literal["connected", "disconnected", "syncing"]] = Field(None, description="Updated status")


class StoreResponse(BaseModel):
    storeid: UUID
    userid: UUID
    platform: str
    country: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class StoreListResponse(BaseModel):
    success: bool = True
    count: int
    data: List[StoreResponse]
