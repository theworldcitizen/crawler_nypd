from typing import Optional
from array import array

from pydantic import BaseModel


class Info(BaseModel):
    link: str
    fullname: str
    appearance: str
    rank: str
    # precinct: str
    units: list #actually array
    total_complaints: str #actually int
    total_allegations: str #actually int
    substantiated_allegations: str #expected to be int

class Complaints(BaseModel):
    date: str
    # rank_at_time: str
    officer_details: str
    # complaint_details: str
    # allegations: str
    # ccrb_conclusion: str



# class Result(BaseModel):
#     platform_id = 'nypd'
#     url: str
#     info: Info
#     complaint: Complaint
