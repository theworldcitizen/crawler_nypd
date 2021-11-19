from pydantic import BaseModel


class User(BaseModel):
    fullname: str
    description: str
    link: str
