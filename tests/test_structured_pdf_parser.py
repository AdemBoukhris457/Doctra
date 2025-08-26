import pytest
import os
from doctra.parsers.structured_pdf_parser import StructuredPDFParser


class TestStructuredPDFParser:
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.parser = StructuredPDFParser()

    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser is not None
        assert hasattr(self.parser, 'parse')

    def test_parser_with_vlm_config(self):
        """Test parser with VLM configuration."""
        parser = StructuredPDFParser(
            use_vlm=True,
            vlm_provider="openai",
            vlm_api_key="test-key"
        )
        assert parser is not None

    # Add more tests based on your parser's functionality
    @pytest.mark.skipif(not os.path.exists("test_document.pdf"),
                        reason="Test PDF not available")
    def test_parse_document(self):
        """Test parsing a document (requires test PDF)."""
        # This test would need a sample PDF file
        pass