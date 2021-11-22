from typing import Optional
from array import array

from pydantic import BaseModel


class Info(BaseModel):
    link: str
    fullname: str
    appearance: str
    rank: str
    precinct: str
    units: list #actually array
    total_complaints: int
    total_allegations: int
    substantiated_allegations: int

class Complaints(BaseModel):
    date: list #expected to be string
    rank_at_time: list
    # officer_details: str
    complaint_details: str
    allegations: str
    ccrb_conclusion: str



class Data(BaseModel):
    # platform_id = 'nypd'
    # url: str
    info: Info
    complaint: Complaints
