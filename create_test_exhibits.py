"""
Create realistic sample PDF exhibits for testing the FSA Motion Builder
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

def create_exhibit_a():
    """Create Exhibit A - Sentencing and Custody Information"""
    filename = "test_exhibit_a.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    story.append(Paragraph("UNITED STATES DISTRICT COURT", styles['Heading1']))
    story.append(Paragraph("EASTERN DISTRICT OF CALIFORNIA", styles['Heading1']))
    story.append(Spacer(1, 24))
    
    # Case caption
    story.append(Paragraph("UNITED STATES OF AMERICA,", styles['Normal']))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Plaintiff,", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("v.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Case No: 1:20-cr-00456-DEF", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("MARIA RODRIGUEZ,", styles['Normal']))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Defendant.", styles['Normal']))
    story.append(Spacer(1, 36))
    
    # Title
    story.append(Paragraph("EXHIBIT A - SENTENCING AND CUSTODY INFORMATION", styles['Heading2']))
    story.append(Spacer(1, 24))
    
    # Information table
    data = [
        ['Defendant Name:', 'Maria Rodriguez'],
        ['Case Number:', '1:20-cr-00456-DEF'],
        ['District:', 'Eastern District of California'],
        ['Original Sentence:', '72 months imprisonment'],
        ['Months Served:', '42 months'],
        ['Credits Lost:', '90 days of good time credit'],
        ['Original Release Date:', '03/15/2026'],
        ['New Release Date:', '06/15/2026'],
        ['Current Institution:', 'FCI Dublin'],
        ['Register Number:', '12345-078']
    ]
    
    table = Table(data, colWidths=[2.5*inch, 3.5*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 24))
    
    # Narrative
    story.append(Paragraph("CASE SUMMARY:", styles['Heading3']))
    story.append(Spacer(1, 12))
    
    narrative = """The defendant was sentenced to 72 months imprisonment on charges of conspiracy to distribute methamphetamine. Due to a disciplinary infraction in 2022, the defendant lost 90 days of good time credits, extending the projected release date from March 15, 2026 to June 15, 2026.

The defendant has served 42 months of the sentence and has completed substance abuse programming, vocational training in computer skills, and has maintained employment in the institution's education department. The defendant has a strong family support system and has secured housing and employment upon release."""
    
    story.append(Paragraph(narrative, styles['Normal']))
    
    doc.build(story)
    print(f"Created {filename}")
    return filename

def create_exhibit_b():
    """Create Exhibit B - Medical Records"""
    filename = "test_exhibit_b.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    story.append(Paragraph("FEDERAL BUREAU OF PRISONS", styles['Heading1']))
    story.append(Paragraph("MEDICAL SERVICES", styles['Heading2']))
    story.append(Spacer(1, 24))
    
    # Title
    story.append(Paragraph("EXHIBIT B - MEDICAL RECORDS SUMMARY", styles['Heading2']))
    story.append(Spacer(1, 24))
    
    # Patient info
    story.append(Paragraph("Patient: Rodriguez, Maria", styles['Normal']))
    story.append(Paragraph("Register Number: 12345-078", styles['Normal']))
    story.append(Paragraph("Institution: FCI Dublin", styles['Normal']))
    story.append(Paragraph("Date of Report: December 1, 2024", styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Medical summary
    story.append(Paragraph("MEDICAL SUMMARY:", styles['Heading3']))
    story.append(Spacer(1, 12))
    
    medical_text = """CHRONIC CONDITIONS:
- Type 2 Diabetes Mellitus (diagnosed 2019)
- Hypertension (diagnosed 2020)
- Chronic kidney disease, stage 3 (diagnosed 2023)

CURRENT MEDICATIONS:
- Metformin 1000mg twice daily
- Lisinopril 10mg daily
- Insulin glargine 25 units at bedtime

RECENT LABORATORY RESULTS:
- HbA1c: 8.2% (elevated, poor glycemic control)
- eGFR: 45 mL/min/1.73m² (stage 3 CKD)
- Blood pressure: consistently 150/95 despite medication

TREATMENT CHALLENGES:
The institutional environment presents significant challenges for optimal diabetes management. Limited access to fresh foods, irregular meal timing due to institutional schedules, and stress-related factors have contributed to poor glycemic control. The patient would benefit from closer monitoring and dietary modifications that are difficult to achieve in the current setting.

RECOMMENDATIONS:
Continued medical management with potential for improved outcomes in a community setting with access to endocrinology specialty care, diabetes education, and appropriate dietary resources."""
    
    story.append(Paragraph(medical_text, styles['Normal']))
    
    doc.build(story)
    print(f"Created {filename}")
    return filename

def create_exhibit_c():
    """Create Exhibit C - Release Plan"""
    filename = "test_exhibit_c.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    story.append(Paragraph("EXHIBIT C - COMPREHENSIVE RELEASE PLAN", styles['Heading1']))
    story.append(Spacer(1, 24))
    
    # Defendant info
    story.append(Paragraph("Defendant: Maria Rodriguez", styles['Normal']))
    story.append(Paragraph("Case: 1:20-cr-00456-DEF", styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Housing section
    story.append(Paragraph("I. HOUSING ARRANGEMENT", styles['Heading3']))
    story.append(Spacer(1, 12))
    
    housing_text = """The defendant will reside with her sister, Carmen Rodriguez, at 1234 Oak Street, Sacramento, CA 95814. Carmen Rodriguez is a registered nurse employed at UC Davis Medical Center and owns her home. She has provided a notarized letter of support confirming housing arrangements and financial support during the defendant's reintegration period.

The residence is located in a stable residential neighborhood with access to public transportation, medical facilities, and employment opportunities."""
    
    story.append(Paragraph(housing_text, styles['Normal']))
    story.append(Spacer(1, 18))
    
    # Employment section
    story.append(Paragraph("II. EMPLOYMENT PLAN", styles['Heading3']))
    story.append(Spacer(1, 12))
    
    employment_text = """The defendant has secured conditional employment with Sacramento Community College as a part-time administrative assistant in their continuing education department. The position offers flexible scheduling to accommodate medical appointments and supervision requirements.

Additionally, the defendant plans to complete certification in medical coding through the college's professional development program, leveraging skills gained during incarceration."""
    
    story.append(Paragraph(employment_text, styles['Normal']))
    story.append(Spacer(1, 18))
    
    # Medical care section
    story.append(Paragraph("III. MEDICAL CARE PLAN", styles['Heading3']))
    story.append(Spacer(1, 12))
    
    medical_care_text = """The defendant will receive ongoing medical care through the UC Davis Health system, which has an established endocrinology clinic experienced in diabetes management. An appointment has been scheduled within one week of release.

The comprehensive care plan includes:
- Endocrinology consultation for diabetes management
- Nephrology follow-up for chronic kidney disease
- Regular primary care visits
- Access to diabetes education and nutritional counseling
- Prescription assistance program for medications"""
    
    story.append(Paragraph(medical_care_text, styles['Normal']))
    story.append(Spacer(1, 18))
    
    # Support system
    story.append(Paragraph("IV. FAMILY AND COMMUNITY SUPPORT", styles['Heading3']))
    story.append(Spacer(1, 12))
    
    support_text = """The defendant has maintained strong family relationships throughout incarceration. Her support system includes:

- Sister Carmen Rodriguez (primary support/housing)
- Mother Elena Rodriguez (emotional support)
- Two adult children who have expressed commitment to maintaining relationships
- Participation in St. Mary's Catholic Church community
- Connection with local re-entry support services through the Sacramento Reentry Program"""
    
    story.append(Paragraph(support_text, styles['Normal']))
    
    doc.build(story)
    print(f"Created {filename}")
    return filename

if __name__ == "__main__":
    # Create all three exhibits
    exhibit_a = create_exhibit_a()
    exhibit_b = create_exhibit_b()
    exhibit_c = create_exhibit_c()
    
    print(f"\nCreated three test exhibits:")
    print(f"- {exhibit_a}")
    print(f"- {exhibit_b}")
    print(f"- {exhibit_c}")
    print(f"\nThese files are ready for testing the FSA Motion Builder.")