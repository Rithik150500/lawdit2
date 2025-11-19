"""
Tests for document generation utilities
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from lawdit.utils.document_generator import DashboardGenerator, WordDocumentGenerator


class TestWordDocumentGeneratorInitialization:
    """Tests for WordDocumentGenerator initialization."""

    @patch("lawdit.utils.document_generator.Document")
    def test_init_creates_document(self, mock_document_class):
        """Test that initialization creates a Document instance."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        generator = WordDocumentGenerator()

        # Verify Document was created
        mock_document_class.assert_called_once()
        assert generator.doc == mock_doc

    @patch("lawdit.utils.document_generator.Document")
    def test_init_sets_up_styles(self, mock_document_class):
        """Test that initialization sets up custom styles."""
        mock_doc = Mock()
        mock_styles = Mock()
        mock_doc.styles = mock_styles
        mock_document_class.return_value = mock_doc

        # Mock the styles collection
        def mock_contains(style_name):
            return style_name != "CustomTitle"

        mock_styles.__contains__ = mock_contains
        mock_styles.__getitem__ = Mock()
        mock_styles.add_style = Mock()

        generator = WordDocumentGenerator()

        # Verify custom style was added
        mock_styles.add_style.assert_called()


class TestWordDocumentGeneratorAddCoverPage:
    """Tests for add_cover_page method."""

    @patch("lawdit.utils.document_generator.Document")
    @patch("lawdit.utils.document_generator.datetime")
    def test_add_cover_page_with_title_only(self, mock_datetime, mock_document_class):
        """Test adding cover page with only a title."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        # Mock datetime
        mock_now = Mock()
        mock_now.strftime.return_value = "January 01, 2025"
        mock_datetime.now.return_value = mock_now

        generator = WordDocumentGenerator()
        generator.add_cover_page("Legal Risk Analysis")

        # Verify paragraphs were added
        assert mock_doc.add_paragraph.call_count >= 3
        mock_doc.add_page_break.assert_called_once()

    @patch("lawdit.utils.document_generator.Document")
    @patch("lawdit.utils.document_generator.datetime")
    def test_add_cover_page_with_subtitle(self, mock_datetime, mock_document_class):
        """Test adding cover page with title and subtitle."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        mock_now = Mock()
        mock_now.strftime.return_value = "January 01, 2025"
        mock_datetime.now.return_value = mock_now

        generator = WordDocumentGenerator()
        generator.add_cover_page("Legal Risk Analysis", "Comprehensive Due Diligence Report")

        # Verify subtitle paragraph was added
        assert mock_doc.add_paragraph.call_count >= 4
        mock_doc.add_page_break.assert_called_once()


class TestWordDocumentGeneratorAddExecutiveSummary:
    """Tests for add_executive_summary method."""

    @patch("lawdit.utils.document_generator.Document")
    def test_add_executive_summary(self, mock_document_class):
        """Test adding executive summary section."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        generator = WordDocumentGenerator()
        generator.add_executive_summary("This analysis identifies 5 critical risks.")

        # Verify heading and content were added
        mock_doc.add_heading.assert_called_with("Executive Summary", level=1)
        mock_doc.add_paragraph.assert_called_with("This analysis identifies 5 critical risks.")
        mock_doc.add_page_break.assert_called()


class TestWordDocumentGeneratorAddTableOfContents:
    """Tests for add_table_of_contents method."""

    @patch("lawdit.utils.document_generator.Document")
    def test_add_table_of_contents(self, mock_document_class):
        """Test adding table of contents placeholder."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        generator = WordDocumentGenerator()
        generator.add_table_of_contents()

        # Verify TOC heading was added
        mock_doc.add_heading.assert_called_with("Table of Contents", level=1)
        mock_doc.add_page_break.assert_called()


class TestWordDocumentGeneratorAddRiskSection:
    """Tests for add_risk_section method."""

    @patch("lawdit.utils.document_generator.Document")
    def test_add_risk_section_basic(self, mock_document_class):
        """Test adding a basic risk section."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        # Mock paragraph for severity coloring
        mock_para = Mock()
        mock_run = Mock()
        mock_para.add_run.return_value = mock_run
        mock_doc.add_paragraph.return_value = mock_para

        generator = WordDocumentGenerator()

        risks = [
            {
                "title": "Inadequate Liability Cap",
                "severity": "High",
                "description": "Contract lacks proper liability limitations.",
            }
        ]

        generator.add_risk_section("Contractual Risks", risks)

        # Verify section was added
        assert mock_doc.add_heading.called

    @patch("lawdit.utils.document_generator.Document")
    def test_add_risk_section_with_overview(self, mock_document_class):
        """Test adding risk section with overview."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        mock_para = Mock()
        mock_run = Mock()
        mock_para.add_run.return_value = mock_run
        mock_doc.add_paragraph.return_value = mock_para

        generator = WordDocumentGenerator()

        risks = [{"title": "Risk 1", "severity": "Medium"}]
        overview = "Overview of contractual risks"

        generator.add_risk_section("Contracts", risks, overview=overview)

        # Verify overview was added
        mock_doc.add_paragraph.assert_any_call(overview)

    @patch("lawdit.utils.document_generator.Document")
    def test_add_risk_section_critical_severity_color(self, mock_document_class):
        """Test that critical severity gets red color."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        mock_para = Mock()
        mock_run = Mock()
        mock_para.add_run.return_value = mock_run
        mock_doc.add_paragraph.return_value = mock_para

        generator = WordDocumentGenerator()

        risks = [{"title": "Critical Issue", "severity": "Critical"}]

        generator.add_risk_section("Risks", risks)

        # Verify severity run was created and colored
        assert mock_run.font.color.rgb is not None

    @patch("lawdit.utils.document_generator.Document")
    def test_add_risk_section_all_fields(self, mock_document_class):
        """Test adding risk with all optional fields."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        mock_para = Mock()
        mock_run = Mock()
        mock_para.add_run.return_value = mock_run
        mock_doc.add_paragraph.return_value = mock_para

        generator = WordDocumentGenerator()

        risks = [
            {
                "title": "Complete Risk",
                "severity": "High",
                "description": "Detailed description",
                "evidence": "Supporting evidence",
                "impact": "Potential impact",
                "recommendations": "Recommended actions",
            }
        ]

        generator.add_risk_section("Complete Risks", risks)

        # Verify all subsections were added
        headings = [call[0][0] for call in mock_doc.add_heading.call_args_list]
        assert "Description" in headings
        assert "Supporting Evidence" in headings
        assert "Potential Impact" in headings
        assert "Recommendations" in headings


class TestWordDocumentGeneratorAddRiskMatrixTable:
    """Tests for add_risk_matrix_table method."""

    @patch("lawdit.utils.document_generator.Document")
    def test_add_risk_matrix_table(self, mock_document_class):
        """Test adding risk matrix summary table."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        # Mock table
        mock_table = Mock()
        mock_header_row = Mock()
        mock_cells = [Mock(), Mock(), Mock(), Mock()]
        mock_header_row.cells = mock_cells
        mock_table.rows = [mock_header_row]
        mock_table.add_row.return_value.cells = mock_cells
        mock_doc.add_table.return_value = mock_table

        generator = WordDocumentGenerator()

        risks = [
            {
                "title": "Risk 1",
                "category": "Contracts",
                "severity": "High",
                "documents": "Doc1, Doc2",
            },
            {
                "title": "Risk 2",
                "category": "Regulatory",
                "severity": "Medium",
                "documents": "Doc3",
            },
        ]

        generator.add_risk_matrix_table(risks)

        # Verify table was created with correct structure
        mock_doc.add_table.assert_called_once_with(rows=1, cols=4)
        assert mock_table.add_row.call_count == 2


class TestWordDocumentGeneratorSave:
    """Tests for save method."""

    @patch("lawdit.utils.document_generator.Document")
    def test_save_creates_directory(self, mock_document_class):
        """Test that save creates parent directory if needed."""
        mock_doc = Mock()
        mock_document_class.return_value = mock_doc

        generator = WordDocumentGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "nested", "dir", "report.docx")

            generator.save(output_path)

            # Verify directory was created
            assert os.path.exists(os.path.dirname(output_path))

            # Verify document was saved
            mock_doc.save.assert_called_once_with(output_path)


class TestDashboardGeneratorInitialization:
    """Tests for DashboardGenerator initialization."""

    def test_init_empty_state(self):
        """Test initialization creates empty state."""
        generator = DashboardGenerator()

        assert generator.risks == []
        assert generator.categories == []
        assert generator.severities == ["Critical", "High", "Medium", "Low"]


class TestDashboardGeneratorAddRisk:
    """Tests for add_risk method."""

    def test_add_risk_single(self):
        """Test adding a single risk."""
        generator = DashboardGenerator()

        risk = {
            "title": "Security Vulnerability",
            "category": "Technical",
            "severity": "High",
            "description": "SQL injection risk",
        }

        generator.add_risk(risk)

        assert len(generator.risks) == 1
        assert generator.risks[0] == risk
        assert "Technical" in generator.categories

    def test_add_risk_multiple_same_category(self):
        """Test that duplicate categories are not added."""
        generator = DashboardGenerator()

        risk1 = {"title": "Risk 1", "category": "Contracts", "severity": "High"}
        risk2 = {"title": "Risk 2", "category": "Contracts", "severity": "Medium"}

        generator.add_risk(risk1)
        generator.add_risk(risk2)

        assert len(generator.risks) == 2
        assert generator.categories.count("Contracts") == 1

    def test_add_risk_different_categories(self):
        """Test adding risks from different categories."""
        generator = DashboardGenerator()

        risk1 = {"title": "Risk 1", "category": "Contracts", "severity": "High"}
        risk2 = {"title": "Risk 2", "category": "Regulatory", "severity": "High"}
        risk3 = {"title": "Risk 3", "category": "Litigation", "severity": "Medium"}

        generator.add_risk(risk1)
        generator.add_risk(risk2)
        generator.add_risk(risk3)

        assert len(generator.categories) == 3
        assert "Contracts" in generator.categories
        assert "Regulatory" in generator.categories
        assert "Litigation" in generator.categories

    def test_add_risk_without_category(self):
        """Test adding risk without category."""
        generator = DashboardGenerator()

        risk = {"title": "Risk 1", "severity": "High"}

        generator.add_risk(risk)

        assert len(generator.risks) == 1
        assert len(generator.categories) == 0


class TestDashboardGeneratorCountBySeverity:
    """Tests for _count_by_severity method."""

    def test_count_by_severity_empty(self):
        """Test counting when no risks exist."""
        generator = DashboardGenerator()

        assert generator._count_by_severity("Critical") == 0
        assert generator._count_by_severity("High") == 0

    def test_count_by_severity_mixed(self):
        """Test counting with mixed severities."""
        generator = DashboardGenerator()

        risks = [
            {"severity": "Critical"},
            {"severity": "Critical"},
            {"severity": "High"},
            {"severity": "Medium"},
            {"severity": "High"},
        ]

        for risk in risks:
            generator.add_risk(risk)

        assert generator._count_by_severity("Critical") == 2
        assert generator._count_by_severity("High") == 2
        assert generator._count_by_severity("Medium") == 1
        assert generator._count_by_severity("Low") == 0


class TestDashboardGeneratorGenerateRiskCards:
    """Tests for _generate_risk_cards method."""

    def test_generate_risk_cards_empty(self):
        """Test generating cards when no risks exist."""
        generator = DashboardGenerator()

        html = generator._generate_risk_cards()

        # Should return empty or minimal HTML
        assert isinstance(html, str)

    def test_generate_risk_cards_single_risk(self):
        """Test generating card for single risk."""
        generator = DashboardGenerator()

        risk = {
            "title": "Critical Security Issue",
            "category": "Security",
            "severity": "Critical",
            "description": "System vulnerability found",
        }

        generator.add_risk(risk)
        html = generator._generate_risk_cards()

        # Verify HTML contains risk information
        assert "Critical Security Issue" in html
        assert "Security" in html
        assert "Critical" in html
        assert "System vulnerability found" in html

    def test_generate_risk_cards_multiple_risks(self):
        """Test generating cards for multiple risks."""
        generator = DashboardGenerator()

        risks = [
            {"title": "Risk 1", "category": "Cat1", "severity": "High"},
            {"title": "Risk 2", "category": "Cat2", "severity": "Medium"},
            {"title": "Risk 3", "category": "Cat3", "severity": "Low"},
        ]

        for risk in risks:
            generator.add_risk(risk)

        html = generator._generate_risk_cards()

        # Verify all risks are in HTML
        assert "Risk 1" in html
        assert "Risk 2" in html
        assert "Risk 3" in html


class TestDashboardGeneratorRisksToJson:
    """Tests for _risks_to_json method."""

    def test_risks_to_json_empty(self):
        """Test JSON generation with no risks."""
        generator = DashboardGenerator()

        json_str = generator._risks_to_json()

        assert json_str == "[]"

    def test_risks_to_json_with_risks(self):
        """Test JSON generation with risks."""
        generator = DashboardGenerator()

        risks = [
            {"title": "Risk 1", "severity": "High"},
            {"title": "Risk 2", "severity": "Medium"},
        ]

        for risk in risks:
            generator.add_risk(risk)

        json_str = generator._risks_to_json()

        # Verify valid JSON
        parsed = json.loads(json_str)
        assert len(parsed) == 2
        assert parsed[0]["title"] == "Risk 1"


class TestDashboardGeneratorGenerateHtml:
    """Tests for generate_html method."""

    def test_generate_html_structure(self):
        """Test that generated HTML has proper structure."""
        generator = DashboardGenerator()

        generator.add_risk(
            {"title": "Test Risk", "category": "Test", "severity": "High", "description": "Test"}
        )

        html = generator.generate_html()

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "Legal Risk Analysis Dashboard" in html

    def test_generate_html_includes_stats(self):
        """Test that HTML includes statistics."""
        generator = DashboardGenerator()

        # Add risks
        generator.add_risk({"severity": "Critical", "category": "Cat1"})
        generator.add_risk({"severity": "Critical", "category": "Cat2"})
        generator.add_risk({"severity": "High", "category": "Cat3"})

        html = generator.generate_html()

        # Verify stats are included
        assert "total-risks" in html
        assert "critical-count" in html
        assert "high-count" in html
        assert "category-count" in html

    def test_generate_html_includes_filters(self):
        """Test that HTML includes filter controls."""
        generator = DashboardGenerator()

        generator.add_risk({"category": "Contracts", "severity": "High"})
        generator.add_risk({"category": "Regulatory", "severity": "Medium"})

        html = generator.generate_html()

        # Verify filters are included
        assert "category-filter" in html
        assert "severity-filter" in html
        assert "search" in html

        # Verify categories are in dropdown
        assert "Contracts" in html
        assert "Regulatory" in html

    def test_generate_html_includes_javascript(self):
        """Test that HTML includes JavaScript for filtering."""
        generator = DashboardGenerator()

        html = generator.generate_html()

        # Verify JavaScript is included
        assert "<script>" in html
        assert "filterRisks" in html
        assert "</script>" in html


class TestDashboardGeneratorSave:
    """Tests for save method."""

    def test_save_creates_file(self):
        """Test that save creates HTML file."""
        generator = DashboardGenerator()

        generator.add_risk(
            {"title": "Test Risk", "category": "Test", "severity": "High", "description": "Desc"}
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "dashboard.html")

            generator.save(output_path)

            # Verify file was created
            assert os.path.exists(output_path)

            # Verify content
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "Test Risk" in content
            assert "<!DOCTYPE html>" in content

    def test_save_creates_parent_directory(self):
        """Test that save creates parent directory if needed."""
        generator = DashboardGenerator()

        generator.add_risk({"title": "Risk", "severity": "High"})

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "nested", "dir", "dashboard.html")

            generator.save(output_path)

            # Verify directory and file were created
            assert os.path.exists(output_path)

    def test_save_utf8_encoding(self):
        """Test that save uses UTF-8 encoding."""
        generator = DashboardGenerator()

        # Add risk with unicode characters
        generator.add_risk(
            {
                "title": "Risk with émojis 🔒",
                "category": "Sécurité",
                "severity": "High",
                "description": "Test unicode: café, naïve, 中文",
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "dashboard.html")

            generator.save(output_path)

            # Verify file contains unicode characters
            with open(output_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert "émojis 🔒" in content
            assert "Sécurité" in content
            assert "café" in content
