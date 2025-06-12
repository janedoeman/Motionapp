#!/usr/bin/env python3
"""
Create a sample Exhibit A PDF for testing the FSA Motion Builder
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_exhibit_a():
    filename = "sample_exhibit_a.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "UNITED STATES DISTRICT COURT")
    c.drawString(50, height - 70, "WESTERN DISTRICT OF WASHINGTON")
    
    # Case information
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 120, "UNITED STATES OF AMERICA,")
    c.drawString(300, height - 120, "Case No: 2:21-cr-00123-ABC")
    c.drawString(50, height - 140, "                    Plaintiff,")
    c.drawString(50, height - 180, "v.")
    c.drawString(50, height - 220, "JOHN DEFENDANT SMITH,")
    c.drawString(50, height - 240, "                    Defendant.")
    
    # Document title
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 300, "EXHIBIT A - SENTENCING AND CUSTODY INFORMATION")
    
    # Content
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 350, "Defendant Name: John Defendant Smith")
    c.drawString(50, height - 370, "Case Number: 2:21-cr-00123-ABC")
    c.drawString(50, height - 390, "District: Western District of Washington")
    c.drawString(50, height - 410, "Original Sentence: 84 months imprisonment")
    c.drawString(50, height - 430, "Months Served: 36 months")
    c.drawString(50, height - 450, "Credits Lost: 180 days of good time credit")
    c.drawString(50, height - 470, "Original Release Date: 12/15/2028")
    c.drawString(50, height - 490, "New Release Date: 06/15/2029")
    
    # Additional details
    c.drawString(50, height - 530, "The defendant was sentenced to 84 months imprisonment on charges")
    c.drawString(50, height - 550, "of conspiracy to distribute controlled substances. Due to disciplinary")
    c.drawString(50, height - 570, "infractions, the defendant lost 180 days of good time credits,")
    c.drawString(50, height - 590, "extending the projected release date from December 15, 2028 to")
    c.drawString(50, height - 610, "June 15, 2029.")
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_sample_exhibit_a()