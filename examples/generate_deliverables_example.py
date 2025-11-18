"""
Example: Generating Deliverables Standalone

This example shows how to use the document generation utilities directly.
"""

from pathlib import Path

from lawdit.utils import DashboardGenerator, WordDocumentGenerator


def generate_sample_word_report():
    """Generate a sample Word document report."""

    print("Generating sample Word report...")

    # Create generator
    generator = WordDocumentGenerator()

    # Add cover page
    generator.add_cover_page(
        title="Legal Risk Analysis Report", subtitle="Sample Data Room Due Diligence"
    )

    # Add executive summary
    executive_summary = """This legal risk analysis identifies several critical areas requiring immediate attention.
The review covered 45 documents across contracts, regulatory filings, litigation records, and corporate governance materials.

Key Findings:
- 3 Critical risks requiring immediate remediation
- 7 High-priority risks needing near-term action
- 12 Medium-priority risks for ongoing monitoring
- 8 Low-priority informational items

The most significant concerns relate to contractual liability exposure and regulatory compliance gaps
in data privacy practices."""

    generator.add_executive_summary(executive_summary)

    # Add table of contents placeholder
    generator.add_table_of_contents()

    # Add contractual risks section
    contractual_risks = [
        {
            "title": "Unlimited Indemnification Liability",
            "severity": "Critical",
            "description": "Three major customer contracts contain unlimited indemnification clauses with no cap on liability.",
            "evidence": "Contracts DOC-101, DOC-103, DOC-105 - Section 8.2 in each",
            "impact": "Could expose company to catastrophic financial loss in the event of a claim.",
            "recommendations": "Immediately negotiate amendments to cap indemnification at contract value or add insurance backstop.",
        },
        {
            "title": "Weak IP Protection Clauses",
            "severity": "High",
            "description": "Customer agreements allow creation of derivative works without clear ownership provisions.",
            "evidence": "Master Services Agreement template - Section 6.4",
            "impact": "Risk of losing IP rights or facing disputes over derivative work ownership.",
            "recommendations": "Revise template to clarify IP ownership and restrict derivative work rights.",
        },
    ]

    generator.add_risk_section(
        category="Contractual Risks",
        risks=contractual_risks,
        overview="The contractual risk analysis revealed significant exposure in liability provisions and intellectual property protection.",
    )

    # Add regulatory risks section
    regulatory_risks = [
        {
            "title": "GDPR Compliance Gaps",
            "severity": "Critical",
            "description": "Data processing practices do not fully comply with GDPR requirements for EU customer data.",
            "evidence": "Privacy Policy DOC-203, Data Processing Addendum DOC-204",
            "impact": "Potential fines up to 4% of global revenue and regulatory enforcement action.",
            "recommendations": "Conduct comprehensive GDPR audit and implement required controls within 90 days.",
        }
    ]

    generator.add_risk_section(
        category="Regulatory & Compliance Risks",
        risks=regulatory_risks,
        overview="Regulatory review identified critical compliance gaps requiring immediate attention.",
    )

    # Add risk matrix summary
    all_risks = contractual_risks + regulatory_risks
    generator.add_risk_matrix_table(
        [
            {
                **risk,
                "category": "Contracts" if risk in contractual_risks else "Regulatory",
                "documents": "DOC-101, DOC-103",
            }
            for risk in all_risks
        ]
    )

    # Save the document
    output_path = "./outputs/sample_legal_risk_report.docx"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generator.save(output_path)

    print(f"✓ Word report generated: {output_path}")


def generate_sample_dashboard():
    """Generate a sample HTML dashboard."""

    print("Generating sample HTML dashboard...")

    # Create generator
    generator = DashboardGenerator()

    # Add sample risks
    risks = [
        {
            "title": "Unlimited Indemnification Liability",
            "category": "Contracts",
            "severity": "Critical",
            "description": "Three major customer contracts contain unlimited indemnification clauses with no cap on liability. This could expose the company to catastrophic financial loss.",
        },
        {
            "title": "Weak IP Protection Clauses",
            "category": "Contracts",
            "severity": "High",
            "description": "Customer agreements allow creation of derivative works without clear ownership provisions, risking loss of IP rights.",
        },
        {
            "title": "GDPR Compliance Gaps",
            "category": "Regulatory",
            "severity": "Critical",
            "description": "Data processing practices do not fully comply with GDPR requirements for EU customer data, risking significant fines.",
        },
        {
            "title": "Missing Export Control Documentation",
            "category": "Regulatory",
            "severity": "High",
            "description": "Export control classification for certain products is not properly documented.",
        },
        {
            "title": "Pending Customer Litigation",
            "category": "Litigation",
            "severity": "High",
            "description": "Two active lawsuits from customers regarding service level breaches.",
        },
        {
            "title": "Board Meeting Documentation Gaps",
            "category": "Governance",
            "severity": "Medium",
            "description": "Board minutes for Q2 2023 are incomplete and missing required signatures.",
        },
        {
            "title": "Related Party Transaction Disclosure",
            "category": "Governance",
            "severity": "Medium",
            "description": "Related party transactions not fully disclosed in financial statements.",
        },
        {
            "title": "Employee Handbook Outdated",
            "category": "Compliance",
            "severity": "Low",
            "description": "Employee handbook has not been updated to reflect current employment law changes.",
        },
    ]

    for risk in risks:
        generator.add_risk(risk)

    # Save the dashboard
    output_path = "./outputs/sample_risk_dashboard.html"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    generator.save(output_path)

    print(f"✓ HTML dashboard generated: {output_path}")
    print(f"  Open in browser: file://{Path(output_path).absolute()}")


def main():
    """Generate both sample deliverables."""

    print("=" * 70)
    print("GENERATING SAMPLE DELIVERABLES")
    print("=" * 70)
    print()

    generate_sample_word_report()
    print()
    generate_sample_dashboard()

    print()
    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
