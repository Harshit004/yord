"""
PDF Export Generator for YORD.
Generates styled PDF research reports using fpdf2.
RAM Impact: Low (<10MB). Processing stream on memory buffer.
"""

import os
from fpdf import FPDF

class YordPdfReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 168, 255)  # Accent blue (#00A8FF)
        self.cell(0, 10, "YORD Autonomous Research Report", border=False, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(42, 42, 42)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(136, 136, 136)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Local Memory-Bound Engine", align="C")

def generate_pdf_report(title: str, content: str, output_path: str) -> str:
    """
    Generates a PDF document for a given research output.
    """
    pdf = YordPdfReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(224, 224, 224)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Body Content
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    
    lines = content.split("\n")
    for line in lines:
        if line.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, line.replace("### ", ""), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
        elif line.startswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, line.replace("**", ""))
            pdf.set_font("Helvetica", "", 10)
        else:
            pdf.multi_cell(0, 6, line)
            
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return output_path
