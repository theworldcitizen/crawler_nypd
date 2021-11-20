from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    fullname: str
    description: Optional[str]
    link: str
    appearance: str


# class Info(BaseModel):
#     fullname: str
#
#     pass
#
#
# class Complaint(BaseModel):
#     pass


# class Result(BaseModel):
#     platform_id = 'nypd'
#     url: str
#     info: Info
#     complaint: Complaint
