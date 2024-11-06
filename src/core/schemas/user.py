from pydantic import BaseModel


class BaseUser(BaseModel):
    name: str


class UserInDb(BaseUser):
    id: int

    class Config:
        orm_mode = True
