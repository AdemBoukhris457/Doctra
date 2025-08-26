import pytest
from doctra.parsers.table_chart_extractor import ChartTablePDFParser


class TestChartTablePDFParser:
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.parser = ChartTablePDFParser()

    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser is not None
        assert hasattr(self.parser, 'parse')

    def test_chart_extraction_config(self):
        """Test chart extraction configuration."""
        parser = ChartTablePDFParser(
            extract_charts=True,
            extract_tables=False
        )
        assert parser is not None

    def test_table_extraction_config(self):
        """Test table extraction configuration."""
        parser = ChartTablePDFParser(
            extract_charts=False,
            extract_tables=True
        )
        assert parser is not None