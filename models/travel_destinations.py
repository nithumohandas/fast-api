from typing import Optional

from pydantic import BaseModel, Field


class TravelDestination:
    id: int
    city: str
    country: str
    feature: str

    def __init__(self, id, city, country, feature):
        self.id = id
        self.city = city
        self.country = country
        self.feature = feature

class TravelDestinationRequest(BaseModel):
    id: Optional[int] = Field(description="Travel Destination ID", default=None)
    city: str = Field(alias="City", min_length=4)
    country: str = Field(alias="Country", min_length=4)
    feature: str = Field(alias="Feature", min_length=10)
