from sqlmodel import Field, SQLModel

class TravelDestinations(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    city: str
    country: str
    feature: str
