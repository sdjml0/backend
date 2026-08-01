from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    storeid: Optional[UUID] = Field(None, description="Associated store ID")
    units_sold: Optional[int] = Field(0, ge=0, description="Total units sold")
    revenue: Optional[float] = Field(0.0, ge=0.0, description="Total revenue generated")


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated product name")
    storeid: Optional[UUID] = Field(None, description="Updated store ID")
    units_sold: Optional[int] = Field(None, ge=0, description="Updated units sold")
    revenue: Optional[float] = Field(None, ge=0.0, description="Updated revenue")


class ProductResponse(BaseModel):
    productid: UUID
    userid: UUID
    storeid: Optional[UUID] = None
    product_name: str
    units_sold: int
    revenue: float

    model_config = ConfigDict(from_attributes=True)



class ProductListResponse(BaseModel):
    success: bool = True
    total: int = Field(..., description="Total count of products matching query")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages available")
    has_next: bool = Field(..., description="Indicates if a next page exists")
    has_prev: bool = Field(..., description="Indicates if a previous page exists")
    count: int = Field(..., description="Number of items in current payload")
    data: List[ProductResponse]

