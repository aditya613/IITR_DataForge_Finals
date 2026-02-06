from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_medical_guidelines_pdf():
    """Create a sample medical guidelines PDF for testing."""
    pdf = canvas.Canvas("medical_guidelines.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 100, "Medical Guidelines - Type 2 Diabetes")
    
    # Content
    pdf.setFont("Helvetica", 12)
    y_position = height - 150
    
    guidelines = [
        "Type 2 Diabetes is a chronic condition affecting how the body processes blood sugar.",
        "",
        "Treatment Guidelines:",
        "1. First-line medication: Metformin is recommended for most patients.",
        "2. Dosage: Start with 500mg twice daily, increase gradually as tolerated.",
        "3. Monitoring: Check HbA1c levels every 3 months initially.",
        "4. Lifestyle modifications: Diet and exercise are essential components.",
        "",
        "Side Effects of Metformin:",
        "- Gastrointestinal discomfort (nausea, diarrhea)",
        "- Vitamin B12 deficiency with long-term use",
        "- Lactic acidosis (rare but serious)",
        "",
        "Contraindications:",
        "- Severe kidney disease (eGFR < 30 mL/min/1.73 m²)",
        "- Acute or chronic metabolic acidosis",
        "- Hypersensitivity to metformin",
    ]
    
    for line in guidelines:
        pdf.drawString(100, y_position, line)
        y_position -= 20
        if y_position < 100:  # Start new page if needed
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = height - 100
    
    pdf.save()
    print("medical_guidelines.pdf created successfully!")

if __name__ == "__main__":
    create_medical_guidelines_pdf()
