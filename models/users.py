from sqlmodel import Field, SQLModel

class UserBase(SQLModel, table=True):
    email: str = Field(description="User's email", index=True)
    name: str = Field(description="User's name", index=True)
    phone: str = Field(description="User's phone number", index=True)

class User(UserBase):
    id: int = Field(primary_key=True)
    password: str = Field(description="User's password")

class UserPublic(UserBase):
    id: int = Field(primary_key=True)

