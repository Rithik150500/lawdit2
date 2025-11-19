# Mock Company Data Room - India

This directory contains a comprehensive mock data room for **TechVista Solutions Private Limited**, a fictional Indian IT/software company. This mock data room is designed for testing and demonstrating the Lawdit legal due diligence system.

## 📋 Table of Contents

- [Company Overview](#company-overview)
- [Data Room Structure](#data-room-structure)
- [Document Categories](#document-categories)
- [Usage Instructions](#usage-instructions)
- [Document Details](#document-details)
- [Key Information](#key-information)

## 🏢 Company Overview

**Company Name:** TechVista Solutions Private Limited
**CIN:** U72900KA2020PTC135246
**Industry:** Information Technology / Software Development
**Founded:** January 2020
**Headquarters:** Bengaluru, Karnataka, India
**Employees:** 485+ (as of March 2024)
**Annual Revenue:** ₹45.5 Crores (FY 2023-24)
**Business:** Custom software development, IT consulting, cloud solutions, AI/ML services

## 📁 Data Room Structure

```
mock_data_room_india/
├── corporate/                      # Corporate governance documents
│   ├── certificate_of_incorporation.txt
│   ├── memorandum_of_association.txt
│   ├── articles_of_association.txt
│   ├── board_resolution_2024.txt
│   └── shareholding_pattern.txt
│
├── financial/                      # Financial statements and tax documents
│   ├── balance_sheet_2023_24.txt
│   ├── profit_loss_statement_2023_24.txt
│   ├── income_tax_return_2023_24.txt
│   └── gst_annual_return_2023_24.txt
│
├── contracts/                      # Commercial agreements
│   ├── employment_agreement_template.txt
│   ├── vendor_agreement_cloud_services.txt
│   └── master_services_agreement_customer.txt
│
├── regulatory/                     # Licenses and registrations
│   ├── gst_registration_certificate.txt
│   ├── shops_and_establishment_license.txt
│   ├── pan_tan_certificates.txt
│   └── epf_esi_registration.txt
│
├── intellectual_property/          # IP assets
│   └── trademark_registration.txt
│
├── legal/                          # Legal agreements
│   └── office_lease_agreement.txt
│
├── hr/                             # Human resources documents
│   └── employee_handbook_policies.txt
│
└── README.md                       # This file
```

## 📂 Document Categories

### 1. Corporate Documents
Foundation documents establishing the company's legal existence and governance structure.

- **Certificate of Incorporation** - ROC registration certificate
- **Memorandum of Association (MOA)** - Company's constitution and objectives
- **Articles of Association (AOA)** - Internal governance rules
- **Board Resolution** - Minutes from recent board meeting (March 2024)
- **Shareholding Pattern** - Current ownership structure

### 2. Financial Documents
Financial statements and tax compliance documents for FY 2023-24.

- **Balance Sheet** - Assets, liabilities, and equity as of March 31, 2024
- **Profit & Loss Statement** - Income and expenses for FY 2023-24
- **Income Tax Return** - ITR-6 for Assessment Year 2024-25
- **GST Annual Return** - GSTR-9 for FY 2023-24

### 3. Contracts
Key commercial agreements governing business relationships.

- **Employment Agreement** - Standard employment contract template
- **Vendor Agreement** - Cloud infrastructure services contract
- **Master Services Agreement** - Customer engagement framework

### 4. Regulatory Documents
Statutory licenses and registrations required to operate in India.

- **GST Registration** - Goods and Services Tax registration
- **Shops & Establishment License** - Karnataka labor law compliance
- **PAN/TAN Certificates** - Income tax registrations
- **EPF/ESI Registration** - Employee benefits registrations

### 5. Intellectual Property
Company's IP assets and registrations.

- **Trademark Registration** - "TechVista" brand protection

### 6. Legal Documents
Property and facility agreements.

- **Office Lease Agreement** - Commercial property lease (5-year term)

### 7. HR Documents
Employee policies and procedures.

- **Employee Handbook** - Comprehensive HR policies and code of conduct

## 🚀 Usage Instructions

### For Testing Lawdit

1. **Indexing Test:**
   ```bash
   # Copy files to a test Google Drive folder
   # Run Lawdit indexer on the folder
   lawdit-index --credentials ./credentials.json \
                --folder-id YOUR_TEST_FOLDER_ID \
                --output ./test_index.txt
   ```

2. **Analysis Test:**
   ```bash
   # Run legal analysis on the indexed data room
   lawdit-analyze --index ./test_index.txt \
                  --focus contracts compliance financial
   ```

3. **Risk Assessment:**
   The data room includes various scenarios for testing risk detection:
   - Related party transactions (property lease from director's entity)
   - Regulatory compliance status
   - Financial health indicators
   - Contractual obligations and commitments

### For Development

- Use as reference for document structures in Indian legal context
- Test document parsing and extraction capabilities
- Validate vision AI summarization accuracy
- Benchmark analysis agent performance

## 📊 Document Details

### Corporate Structure

**Promoters:**
- Rahul Sharma (Managing Director) - 30% stake
- Priya Mehta (Director) - 25% stake
- Sharma Family Trust - 10% stake

**Investors:**
- Accel India Ventures II - 15% stake
- Sequoia Capital India Growth - 10% stake

**Total Shares:** 5,00,000 equity shares of ₹100 each

### Financial Highlights (FY 2023-24)

| Metric | Value |
|--------|-------|
| Total Revenue | ₹45.5 Crores |
| Net Profit | ₹8.75 Crores |
| Total Assets | ₹35.6 Crores |
| Net Worth | ₹22.4 Crores |
| EBITDA Margin | 22.86% |
| Net Profit Margin | 14.62% |
| Employee Cost | ₹24.5 Crores |

### Key Contracts

1. **Cloud Services Vendor** (CloudTech Infrastructure)
   - Annual value: ₹88.85 lakhs (including GST)
   - Term: 3 years (2024-2026)
   - Services: Cloud hosting, storage, security

2. **Customer MSA** (Indian Retail Corporation)
   - Annual value: ₹5.1 Crores (estimated)
   - Projects: E-commerce platform, inventory system, legacy modernization
   - Team: 26 resources across projects

3. **Office Lease** (Prestige Tech Park)
   - Monthly rent: ₹8.5 lakhs (Year 1, escalating annually)
   - Area: 8,500 sq ft carpet area
   - Term: 5 years (2024-2028) with lock-in

### Compliance Status

✅ All statutory registrations in place:
- GST: 29AABCT1234F1Z5
- PAN: AABCT1234F
- TAN: BANG12345F
- EPF: KRNBL00001234000
- ESI: 29-00-123456-000-0000

✅ All returns filed on time (FY 2023-24)
✅ No pending litigation or notices
✅ Clean compliance record

### Risk Factors (For Testing)

The mock data room includes realistic scenarios for risk analysis:

1. **Related Party Transactions:**
   - Office lease from entity controlled by director
   - Consulting services from director-related firm
   - Properly disclosed in board minutes

2. **Regulatory:**
   - All registrations current and valid
   - Timely filing of all returns
   - No penalties or defaults

3. **Financial:**
   - Healthy profitability and margins
   - Growing revenue (32% YoY)
   - Strong cash position

4. **Contractual:**
   - Lock-in commitments in lease and customer contracts
   - IP ownership clearly defined
   - Non-compete and confidentiality obligations

5. **Employment:**
   - 485 employees with proper PF/ESI coverage
   - POSH policy and ICC in place
   - Standard employment terms

## 🔍 Key Information

### Company Identifiers

- **CIN:** U72900KA2020PTC135246
- **PAN:** AABCT1234F
- **TAN:** BANG12345F
- **GSTIN:** 29AABCT1234F1Z5
- **EPF Code:** KRNBL00001234000
- **ESI Code:** 29-00-123456-000-0000

### Registered Office

No. 42, 3rd Floor, Prestige Tech Park
Outer Ring Road, Marathahalli
Bengaluru - 560037, Karnataka, India
Phone: +91-80-4567-8900
Email: [email protected]

### Key Personnel

- **Rahul Sharma** - Managing Director (DIN: 08234567)
- **Priya Mehta** - Director (DIN: 08234568)
- **Suresh Reddy** - Chief Financial Officer
- **Anjali Nair** - Company Secretary (ACS: 45678)

### Auditors

**Statutory Auditor:** M/s. Srinivasan & Associates
FRN: 012345S
Partner: CA Venkat Srinivasan (M.No.: 123456)

### Bankers

**Primary Banker:** HDFC Bank Limited, Koramangala Branch, Bengaluru

## 📝 Notes

1. **Fictional Data:** All information in this data room is entirely fictional and created for testing purposes only. Any resemblance to real companies, persons, or entities is purely coincidental.

2. **Realistic Structure:** Documents follow actual Indian legal and regulatory formats to provide authentic testing scenarios.

3. **Completeness:** The data room represents a typical mid-sized Indian IT company's due diligence package but is not exhaustive. Real data rooms would include additional documents.

4. **Currency:** All financial figures are in Indian Rupees (₹). Documents are dated as of March 2024.

5. **Legal Accuracy:** While documents follow standard formats, they should not be used as legal templates. Consult legal professionals for actual agreements.

## 🎯 Testing Scenarios

This mock data room supports testing various Lawdit features:

### 1. Document Classification
Test accuracy of categorizing documents into:
- Corporate governance
- Financial statements
- Contracts
- Compliance
- IP assets
- HR policies

### 2. Information Extraction
Extract key data points:
- Company identifiers (CIN, PAN, GST)
- Financial metrics
- Contract values and terms
- Compliance dates and deadlines
- Personnel information

### 3. Risk Analysis
Identify and assess:
- Related party transactions
- Financial health indicators
- Contractual obligations
- Compliance gaps (none in this clean dataset)
- Employment law compliance

### 4. Relationship Mapping
Discover connections between:
- Directors and related entities
- Customers and contracts
- Vendors and service agreements
- Shareholders and ownership structure

### 5. Timeline Analysis
Track important dates:
- Incorporation and registration dates
- Contract commencement and expiry
- Compliance filing deadlines
- Board meeting dates
- License renewal dates

## 🤝 Contributing

To add more documents or improve existing ones:

1. Follow the naming convention: `lowercase_with_underscores.txt`
2. Use realistic Indian legal/business formats
3. Ensure consistency with existing company information
4. Add entries to this README
5. Keep data fictional but realistic

## 📞 Support

For questions about this mock data room or Lawdit:
- Refer to main Lawdit documentation in the repository root
- Check `/examples/` for usage examples
- Review Lawdit's USAGE_GUIDE.md

---

**Version:** 1.0
**Last Updated:** November 2024
**Created for:** Lawdit Legal Due Diligence System Testing
