from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    units_sold: Optional[int] = Field(0, ge=0, description="Total units sold")
    revenue: Optional[float] = Field(0.0, ge=0.0, description="Total revenue generated")


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated product name")
    units_sold: Optional[int] = Field(None, ge=0, description="Updated units sold")
    revenue: Optional[float] = Field(None, ge=0.0, description="Updated revenue")


class ProductResponse(BaseModel):
    productid: UUID
    userid: UUID
    product_name: str
    units_sold: int
    revenue: float

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    success: bool = True
    count: int
    data: List[ProductResponse]
