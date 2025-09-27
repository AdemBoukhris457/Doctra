from pydantic import BaseModel, Field

class Chart(BaseModel):
    """
    Structured representation of a chart extracted from an image.
    
    Includes a title, a short description, column headers, and data rows
    identified using VLM (Vision Language Model) processing.

    :param title: Title or caption of the chart (max 31 characters)
    :param description: Short description of the chart (max 300 characters)
    :param headers: Column headers for the chart data
    :param rows: Data rows containing the chart values
    """
    title: str = Field(max_length=31)
    description: str = Field(max_length=300)
    headers: list[str]
    rows: list[list[str]]

class Table(BaseModel):
    """
    Structured representation of a table extracted from an image.
    
    Includes a title, a short description, column headers, and data rows
    identified using VLM (Vision Language Model) processing.

    :param title: Title or caption of the table (max 31 characters)
    :param description: Short description of the table (max 300 characters)
    :param headers: Column headers for the table data
    :param rows: Data rows containing the table values
    """
    title: str = Field(max_length=31)
    description: str = Field(max_length=300)
    headers: list[str]
    rows: list[list[str]]
