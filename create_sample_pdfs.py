#!/usr/bin/env python3
"""
Create sample PDF files for testing the FSA Motion Builder
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_exhibit_b():
    filename = "sample_exhibit_b.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "EXHIBIT B - SUPPORTING DOCUMENTATION")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Medical Records and Health Information")
    c.drawString(50, height - 130, "Defendant has shown significant rehabilitation efforts")
    c.drawString(50, height - 150, "and has maintained exemplary conduct while incarcerated.")
    
    c.save()
    print(f"Created {filename}")

def create_exhibit_c():
    filename = "sample_exhibit_c.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "EXHIBIT C - ADDITIONAL SUPPORTING DOCUMENTATION")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, "Letters of Support and Community Resources")
    c.drawString(50, height - 130, "Employment verification and housing arrangements")
    c.drawString(50, height - 150, "have been secured for post-release supervision.")
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_exhibit_b()
    create_exhibit_c()