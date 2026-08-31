import os
from io import BytesIO
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class MedicalPDFReportGenerator:
    def __init__(self):
        pass

    def generate_pdf(self, patient_info, extracted_parameters, disease_risks, health_score, recommendations):
        """
        Generates a PDF byte stream for the medical report analysis.
        """
        if not HAS_REPORTLAB:
            return None

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=10,
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#2D3748")
        )

        # Header
        story.append(Paragraph("MedInsight AI - Clinical Analysis Report", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Confidential Medical Record", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=15))

        # Patient & Summary Details Table
        patient_data = [
            [
                Paragraph(f"<b>Patient Name:</b> {patient_info.get('name', 'N/A')}", normal_style),
                Paragraph(f"<b>Age:</b> {patient_info.get('age', 'N/A')}", normal_style),
                Paragraph(f"<b>Gender:</b> {patient_info.get('gender', 'N/A')}", normal_style)
            ],
            [
                Paragraph(f"<b>Overall Health Score:</b> {health_score.get('overall_score', 'N/A')}/100", normal_style),
                Paragraph(f"<b>Health Rating:</b> {health_score.get('rating', 'N/A')}", normal_style),
                Paragraph(f"<b>Detected Anomalies:</b> {health_score.get('anomalies_count', 0)}", normal_style)
            ]
        ]
        t_patient = Table(patient_data, colWidths=[200, 160, 160])
        t_patient.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0"))
        ]))
        story.append(t_patient)
        story.append(Spacer(1, 15))

        # Extracted Biomarkers Section
        story.append(Paragraph("1. Extracted Clinical Biomarkers", heading_style))
        table_data = [["Biomarker", "Measured Value", "Standard Unit", "Clinical Flag"]]
        for p in extracted_parameters:
            flag = p.get('flag', 'NORMAL')
            table_data.append([
                p.get('canonical_name', p.get('raw_name', '')),
                str(p.get('measured_value', '')),
                str(p.get('unit', '')),
                flag
            ])

        t_params = Table(table_data, colWidths=[200, 100, 100, 120])
        t_params.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t_params)
        story.append(Spacer(1, 15))

        # Disease Risk Predictions
        story.append(Paragraph("2. Multi-Disease AI Risk Assessment", heading_style))
        disease_data = [["Disease Category", "Predicted Risk Level", "Assessment"]]
        for disease, risk in disease_risks.items():
            pct = f"{risk*100:.1f}%"
            status = "Elevated Risk" if risk > 0.6 else "Moderate Risk" if risk > 0.35 else "Low Risk"
            disease_data.append([disease, pct, status])

        t_disease = Table(disease_data, colWidths=[220, 150, 150])
        t_disease.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4A5568")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(t_disease)
        story.append(Spacer(1, 15))

        # Clinical Recommendations
        if recommendations:
            story.append(Paragraph("3. Evidence-Based Clinical Recommendations", heading_style))
            for rec in recommendations:
                story.append(Paragraph(f"<b>• {rec['title']} ({rec['parameter']} - {rec['flag']})</b>", normal_style))
                for diet in rec.get('diet', []):
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Diet:</b> {diet}", normal_style))
                for life in rec.get('lifestyle', []):
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Lifestyle:</b> {life}", normal_style))
                if rec.get('consult'):
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>Medical Consult:</b> {rec['consult']}", normal_style))
                story.append(Spacer(1, 6))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
