from pydantic import BaseModel
from decimal import Decimal


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str | None = None
    price: Decimal
    supplier_id: int

    class Config:
        from_attributes = True