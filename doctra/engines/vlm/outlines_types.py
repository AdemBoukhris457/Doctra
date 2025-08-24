from pydantic import BaseModel

class Chart(BaseModel):
    """
    Structured representation of a chart extracted from an image.
    
    Contains the title, headers, and data rows extracted from a chart
    using VLM (Vision Language Model) processing.

    :param title: Title or caption of the chart
    :param headers: Column headers for the chart data
    :param rows: Data rows containing the chart values
    """
    title: str
    headers: list[str]
    rows: list[list[str]]

class Table(BaseModel):
    """
    Structured representation of a table extracted from an image.
    
    Contains the title, headers, and data rows extracted from a table
    using VLM (Vision Language Model) processing.

    :param title: Title or caption of the table
    :param headers: Column headers for the table data
    :param rows: Data rows containing the table values
    """
    title: str
    headers: list[str]
    rows: list[list[str]]
