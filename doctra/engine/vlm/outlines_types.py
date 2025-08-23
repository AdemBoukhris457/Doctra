from pydantic import BaseModel

class Chart(BaseModel):
    title: str
    headers: list[str]
    rows: list[list[str]]

class Table(BaseModel):
    title: str
    headers: list[str]
    rows: list[list[str]]
