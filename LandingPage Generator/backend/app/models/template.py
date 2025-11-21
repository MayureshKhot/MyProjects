from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InvoiceTemplate(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: str
    style: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True