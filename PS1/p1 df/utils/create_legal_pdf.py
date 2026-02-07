"""
Create a sample legal document for testing domain versatility
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_legal_document():
    pdf = canvas.Canvas("legal_contract.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, height - 100, "Employment Contract - Terms and Conditions")
    
    # Content
    pdf.setFont("Helvetica", 12)
    y_position = height - 150
    
    content = [
        "Employee Rights and Obligations",
        "",
        "1. Working Hours: Standard working hours are 40 hours per week, Monday to Friday.",
        "2. Probation Period: New employees serve a probation period of 3 months.",
        "3. Annual Leave: Employees are entitled to 20 days of paid annual leave per year.",
        "4. Notice Period: Either party may terminate with 30 days written notice.",
        "5. Salary: Base salary is paid monthly on the last working day of each month.",
        "",
        "Confidentiality Obligations:",
        "- Employees must maintain confidentiality of all proprietary information.",
        "- Non-disclosure agreements remain in effect for 2 years post-employment.",
        "- Breach of confidentiality may result in legal action and damages.",
        "",
        "Benefits:",
        "- Health insurance coverage for employee and immediate family.",
        "- Retirement plan with 5% employer contribution after 1 year of service.",
        "- Professional development allowance of $2000 per year.",
    ]
    
    for line in content:
        pdf.drawString(100, y_position, line)
        y_position -= 20
        if y_position < 100:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = height - 100
    
    pdf.save()
    print("legal_contract.pdf created successfully!")

if __name__ == "__main__":
    create_legal_document()
