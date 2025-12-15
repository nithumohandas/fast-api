from typing import Optional

from pydantic import BaseModel, Field

class TravelDestination(BaseModel):
    id: Optional[int] = Field(description="Travel Destination ID", default=None)
    city: str = Field(min_length=4)
    country: str = Field(min_length=4)
    feature: str = Field(min_length=10)
