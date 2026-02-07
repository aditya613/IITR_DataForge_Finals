"""
Generate proper test PDFs for Hallucination Hunter
These PDFs will work correctly with pdfplumber for text extraction.

Run: python generate_test_pdfs.py
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
except ImportError:
    print("Installing reportlab...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'reportlab'])
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

import os

def create_climate_pdf():
    """Create climate science reference PDF."""
    doc = SimpleDocTemplate("data/climate_science.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    content = [
        ("CLIMATE SCIENCE REFERENCE DOCUMENT", styles['Heading1']),
        ("", None),
        ("Section 1: Global Temperature Trends", styles['Heading2']),
        ("The global average temperature has increased by approximately 1.1 degrees Celsius since the pre-industrial era. This warming is primarily due to human activities, particularly the burning of fossil fuels and deforestation.", styles['Normal']),
        ("", None),
        ("Section 2: Carbon Dioxide Levels", styles['Heading2']),
        ("Atmospheric CO2 concentration has risen from 280 ppm in pre-industrial times to approximately 420 ppm as of 2024. This represents a 50% increase in atmospheric carbon dioxide.", styles['Normal']),
        ("", None),
        ("Section 3: Sea Level Rise", styles['Heading2']),
        ("Global mean sea level has risen by approximately 21-24 centimeters since 1880. The rate of sea level rise has accelerated to 3.7 mm per year in recent decades.", styles['Normal']),
        ("", None),
        ("Section 4: Arctic Ice", styles['Heading2']),
        ("Arctic sea ice extent has declined by approximately 13% per decade since 1979. The Arctic could experience ice-free summers by 2050 under current trends.", styles['Normal']),
        ("", None),
        ("Section 5: Greenhouse Gases", styles['Heading2']),
        ("The main greenhouse gases are carbon dioxide, methane, nitrous oxide, and fluorinated gases. Methane has 80 times the warming potential of CO2 over a 20-year period.", styles['Normal']),
        ("", None),
        ("Section 6: Renewable Energy", styles['Heading2']),
        ("Solar and wind energy now account for approximately 12% of global electricity generation. The cost of solar photovoltaic panels has dropped by 99% since 1976.", styles['Normal']),
    ]
    
    for text, style in content:
        if text == "":
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    print("[OK] Created: data/climate_science.pdf")


def create_tech_pdf():
    """Create technology specifications reference PDF."""
    doc = SimpleDocTemplate("data/tech_specs.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    content = [
        ("TECHNOLOGY SPECIFICATIONS DOCUMENT", styles['Heading1']),
        ("", None),
        ("Section 1: Large Language Models", styles['Heading2']),
        ("GPT-4 was released in March 2023 by OpenAI. It uses a transformer architecture and has an estimated 1.7 trillion parameters, making it one of the largest language models ever created.", styles['Normal']),
        ("", None),
        ("Section 2: Quantum Computing", styles['Heading2']),
        ("IBM's Condor processor achieved 1,121 qubits in December 2023. Google's Sycamore processor has 53 qubits and demonstrated quantum supremacy in 2019.", styles['Normal']),
        ("", None),
        ("Section 3: GPU Specifications", styles['Heading2']),
        ("NVIDIA H100 GPU has 80GB of HBM3 memory and delivers 3,958 TFLOPS of FP8 performance. The H100 uses TSMC's 4nm process node.", styles['Normal']),
        ("", None),
        ("Section 4: Battery Technology", styles['Heading2']),
        ("Lithium-ion batteries have an energy density of approximately 250-300 Wh/kg. Solid-state batteries promise energy densities exceeding 400 Wh/kg.", styles['Normal']),
        ("", None),
        ("Section 5: Internet Infrastructure", styles['Heading2']),
        ("5G networks offer peak speeds up to 20 Gbps with latency as low as 1 millisecond. Starlink satellites orbit at approximately 550 km altitude.", styles['Normal']),
        ("", None),
        ("Section 6: Semiconductor Manufacturing", styles['Heading2']),
        ("TSMC produces chips at the 3nm process node as of 2024. EUV lithography uses 13.5nm wavelength light for chip manufacturing.", styles['Normal']),
    ]
    
    for text, style in content:
        if text == "":
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    print("[OK] Created: data/tech_specs.pdf")


def create_history_pdf():
    """Create world history reference PDF."""
    doc = SimpleDocTemplate("data/history_facts.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    content = [
        ("WORLD HISTORY REFERENCE DOCUMENT", styles['Heading1']),
        ("", None),
        ("Section 1: Ancient Civilizations", styles['Heading2']),
        ("The Great Pyramid of Giza was built around 2560 BCE for Pharaoh Khufu. The Roman Empire fell in 476 CE when Romulus Augustulus was deposed.", styles['Normal']),
        ("", None),
        ("Section 2: Medieval Period", styles['Heading2']),
        ("The Black Death killed approximately 75-200 million people between 1346-1353. The Magna Carta was signed in 1215 CE by King John of England.", styles['Normal']),
        ("", None),
        ("Section 3: World Wars", styles['Heading2']),
        ("World War I lasted from 1914 to 1918 and resulted in approximately 17 million deaths. World War II lasted from 1939 to 1945 and resulted in 70-85 million deaths. D-Day occurred on June 6, 1944, when Allied forces invaded Normandy, France.", styles['Normal']),
        ("", None),
        ("Section 4: Space Exploration", styles['Heading2']),
        ("The first human in space was Yuri Gagarin on April 12, 1961. Neil Armstrong became the first person to walk on the Moon on July 20, 1969, during the Apollo 11 mission which launched from Kennedy Space Center in Florida.", styles['Normal']),
        ("", None),
        ("Section 5: Modern History", styles['Heading2']),
        ("The Berlin Wall fell on November 9, 1989. The Soviet Union dissolved on December 26, 1991.", styles['Normal']),
    ]
    
    for text, style in content:
        if text == "":
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(text, style))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    print("[OK] Created: data/history_facts.pdf")


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    print("=" * 50)
    print("Generating Test PDFs for Hallucination Hunter")
    print("=" * 50)
    
    create_climate_pdf()
    create_tech_pdf()
    create_history_pdf()
    
    print("\n[SUCCESS] All PDFs generated successfully!")
    print("\nYou can now upload these via the UI:")
    print("  - data/climate_science.pdf")
    print("  - data/tech_specs.pdf")
    print("  - data/history_facts.pdf")
