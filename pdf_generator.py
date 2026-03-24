from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name="CustomTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            textColor="#1f77b4",
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name="CustomHeading",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor="#2ca02c",
            spaceAfter=8,
            spaceBefore=8
        ))

    def generate(self, title: str, url: str, content: str, mode: str) -> bytes:
        """Generate PDF from content"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Header
        story.append(Paragraph("Web Summary Report", self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        story.append(Paragraph(f"<b>Title:</b> {title}", self.styles["Normal"]))
        story.append(Paragraph(f"<b>URL:</b> {url}", self.styles["Normal"]))
        story.append(Paragraph(f"<b>Mode:</b> {mode.upper()}", self.styles["Normal"]))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              self.styles["Normal"]))
        story.append(Spacer(1, 0.3*inch))
        
        # Content
        story.append(Paragraph("Content", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1*inch))
        
        # Split content into paragraphs
        for paragraph in content.split("\n\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), self.styles["Normal"]))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
