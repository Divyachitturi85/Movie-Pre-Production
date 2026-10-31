import os
import io
import json
import zipfile
import logging
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

import docx
from docx.shared import Inches, Pt, RGBColor

logger = logging.getLogger(__name__)

class DocumentService:
    """
    Generates industry-grade film production documents:
    - ReportLab PDF generators (Breakdown, Stripboard, Call Sheets, Callback Letters, Final Pre-Prod Report)
    - OpenPyXL XLSX workbooks (Budget, Scenes, Cast, Locations, Schedule, Elements)
    - Python-docx DOCX documents
    - Complete Pre-Production Package (.ZIP) containing all 11 key artifacts + JSON
    """

    def __init__(self, export_dir: str = "./exports"):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._init_custom_styles()

    def _init_custom_styles(self):
        self.title_style = ParagraphStyle(
            'DocTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1E293B'),
            alignment=TA_CENTER,
            spaceAfter=12
        )
        self.subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#64748B'),
            alignment=TA_CENTER,
            spaceAfter=16
        )
        self.section_heading = ParagraphStyle(
            'SectionHead',
            parent=self.styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=12,
            spaceAfter=8
        )
        self.body_style = ParagraphStyle(
            'DocBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155')
        )
        self.callout_style = ParagraphStyle(
            'DocCallout',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#475569')
        )

    # -------------------------------------------------------------
    # PDF 1: Script Breakdown PDF
    # -------------------------------------------------------------
    def generate_script_breakdown_pdf(self, project: Dict[str, Any], scenes: List[Dict[str, Any]], elements: List[Dict[str, Any]]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []

        story.append(Paragraph(f"{project.get('name', 'Film Production')} - Script Breakdown", self.title_style))
        story.append(Paragraph(f"Director: {project.get('director', 'TBD')} | Total Scenes: {len(scenes)}", self.subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

        # Map elements by scene
        elem_by_scene = {}
        for el in elements:
            sc_id = el.get("scene_id")
            elem_by_scene.setdefault(sc_id, []).append(el)

        for sc in scenes:
            sc_num = sc.get("scene_number", 1)
            heading = sc.get("heading", "")
            loc = sc.get("location_name", "")
            ie = sc.get("interior_exterior", "INT")
            tod = sc.get("time_of_day", "DAY")
            comp = sc.get("complexity_level", "LOW")
            dur = sc.get("estimated_duration_minutes", 60)
            chars = ", ".join(sc.get("characters", [])) or "None"

            # Scene header block
            header_text = f"<b>SCENE {sc_num}: {heading}</b> ({ie} / {tod}) — Complexity: {comp}"
            story.append(Paragraph(header_text, self.section_heading))
            
            info_data = [
                ["Location:", loc, "Duration:", f"{dur} mins"],
                ["Cast Present:", chars, "Complexity:", comp]
            ]
            t_info = Table(info_data, colWidths=[80, 200, 80, 180])
            t_info.setStyle(TableStyle([
                ('FONTSIZE', (0,0), (-1,-1), 8.5),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(t_info)
            story.append(Spacer(1, 6))

            # Elements table
            sc_elems = elem_by_scene.get(sc.get("id"), [])
            if sc_elems:
                elem_table_data = [["Category", "Element Name", "Source / AI Confidence"]]
                for el in sc_elems[:8]:
                    elem_table_data.append([
                        el.get("category", "PROP"),
                        el.get("name", ""),
                        f"{el.get('extraction_source', 'NLP')} ({int(el.get('confidence', 0.85)*100)}%)"
                    ])
                t_elem = Table(elem_table_data, colWidths=[100, 280, 160])
                t_elem.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                ]))
                story.append(t_elem)
            else:
                story.append(Paragraph("<i>No special production elements extracted for this scene.</i>", self.callout_style))

            story.append(Spacer(1, 14))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=10))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------
    # PDF 7: Stripboard PDF
    # -------------------------------------------------------------
    def generate_stripboard_pdf(self, project: Dict[str, Any], scenes: List[Dict[str, Any]]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
        story = []

        story.append(Paragraph(f"{project.get('name', 'Film Production')} - Production Stripboard", self.title_style))
        story.append(Paragraph("Movie Magic Scheduling-compatible production stripboard layout", self.subtitle_style))
        story.append(Spacer(1, 10))

        table_data = [["Sc #", "I/E", "D/N", "Scene Heading", "Location", "Pages", "Cast", "Duration", "Complexity"]]

        # Standard Film Industry Strip Colors:
        # EXT DAY = Yellow (#FEF08A)
        # INT DAY = White/Off-white (#F8FAFC)
        # EXT NIGHT = Green (#BBF7D0)
        # INT NIGHT = Blue (#BFDBFE)
        row_styles = []
        for idx, sc in enumerate(scenes):
            ie = sc.get("interior_exterior", "INT").upper()
            tod = sc.get("time_of_day", "DAY").upper()
            
            if "EXT" in ie and "NIGHT" in tod:
                bg = colors.HexColor('#BBF7D0') # Green
            elif "EXT" in ie:
                bg = colors.HexColor('#FEF08A') # Yellow
            elif "INT" in ie and "NIGHT" in tod:
                bg = colors.HexColor('#BFDBFE') # Blue
            else:
                bg = colors.HexColor('#FFFFFF') # White

            table_data.append([
                str(sc.get("scene_number", idx+1)),
                ie,
                tod,
                sc.get("heading", "")[:28],
                sc.get("location_name", "")[:18],
                f"{sc.get('estimated_pages', 0.5):.2f}",
                ", ".join(sc.get("characters", []))[:18] or "-",
                f"{sc.get('estimated_duration_minutes', 60)}m",
                sc.get("complexity_level", "LOW")
            ])
            row_styles.append(('BACKGROUND', (0, idx+1), (-1, idx+1), bg))

        t = Table(table_data, colWidths=[32, 34, 38, 140, 95, 40, 95, 45, 60])
        base_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('ALIGN', (0,0), (2,-1), 'CENTER'),
            ('ALIGN', (5,0), (5,-1), 'CENTER'),
            ('ALIGN', (7,0), (8,-1), 'CENTER'),
        ]
        t.setStyle(TableStyle(base_style + row_styles))
        story.append(t)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------
    # PDF 9: Call Sheets PDF
    # -------------------------------------------------------------
    def generate_call_sheets_pdf(self, call_sheets: List[Dict[str, Any]]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []

        for idx, cs in enumerate(call_sheets):
            if idx > 0:
                story.append(PageBreak())

            story.append(Paragraph(f"{cs.get('project_name', 'Production')} - OFFICIAL CALL SHEET", self.title_style))
            story.append(Paragraph(f"DAY {cs.get('day_number', 1)} OF PRODUCTION | DATE: {cs.get('shoot_date', 'Shoot Day')}", self.subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=10))

            # Header info table
            info_data = [
                ["GENERAL CALL:", cs.get("general_call_time", "07:00 AM"), "LOCATION:", cs.get("location_name", "Stage 4")],
                ["WEATHER:", cs.get("weather_placeholder", "Sunny, 72°F"), "PARKING:", cs.get("parking_info", "Lot B")],
                ["HOSPITAL:", cs.get("nearest_hospital", "City Emergency"), "EMERGENCY:", cs.get("emergency_contact", "1st AD")]
            ]
            t_info = Table(info_data, colWidths=[90, 180, 90, 180])
            t_info.setStyle(TableStyle([
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
                ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(t_info)
            story.append(Spacer(1, 10))

            # Scenes schedule
            story.append(Paragraph("<b>TODAY'S SHOOTING SCHEDULE:</b>", self.section_heading))
            scenes_data = [["Sc #", "Slugline", "Pages", "Start Time", "Duration", "Complexity"]]
            for sc in cs.get("scenes_summary", []):
                scenes_data.append([
                    str(sc.get("scene_number", 1)),
                    sc.get("heading", "")[:35],
                    str(sc.get("pages", 0.5)),
                    sc.get("start_time", "08:00 AM"),
                    f"{sc.get('duration_mins', 60)} min",
                    sc.get("complexity", "LOW")
                ])
            t_sc = Table(scenes_data, colWidths=[35, 230, 45, 75, 75, 80])
            t_sc.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(t_sc)
            story.append(Spacer(1, 10))

            # Cast calls
            story.append(Paragraph("<b>CAST CALL TIMES:</b>", self.section_heading))
            cast_data = [["Cast ID", "Character", "Actor Name", "Pickup", "H/MU", "On Set", "Status"]]
            for c in cs.get("cast_calls", []):
                cast_data.append([
                    str(c.get("cast_id", 1)),
                    c.get("character_name", ""),
                    c.get("actor_name", "TBD"),
                    c.get("pickup", "06:15 AM"),
                    c.get("hair_makeup", "06:45 AM"),
                    c.get("on_set", "07:45 AM"),
                    c.get("status", "CALLED")
                ])
            t_cast = Table(cast_data, colWidths=[45, 100, 110, 65, 65, 75, 80])
            t_cast.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 3),
            ]))
            story.append(t_cast)
            story.append(Spacer(1, 10))

            # Special instructions
            story.append(Paragraph("<b>SPECIAL INSTRUCTIONS & SAFETY PROTOCOLS:</b>", self.section_heading))
            story.append(Paragraph(cs.get("special_instructions", "Mandatory morning safety briefing."), self.body_style))
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<b>MEAL BREAK:</b> {cs.get('meal_break', '13:00')}", self.body_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------
    # PDF 10: Callback Letters PDF
    # -------------------------------------------------------------
    def generate_callback_letters_pdf(self, letters: List[Dict[str, Any]]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=45, rightMargin=45, topMargin=45, bottomMargin=45)
        story = []

        for idx, letter_item in enumerate(letters):
            if idx > 0:
                story.append(PageBreak())

            story.append(Paragraph("OFFICIAL AUDITION CALLBACK INVITATION", self.title_style))
            story.append(Paragraph(f"Role: <b>{letter_item.get('character_name', '')}</b> ({letter_item.get('role_type', 'LEAD')})", self.subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=15))

            # Render letter body paragraph by paragraph
            raw_body = letter_item.get("letter_body", "")
            paragraphs = raw_body.split('\n\n')
            for p_text in paragraphs:
                p_text_clean = p_text.replace('\n', '<br/>')
                story.append(Paragraph(p_text_clean, self.body_style))
                story.append(Spacer(1, 8))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------
    # PDF 11: Final Pre-Production Report PDF
    # -------------------------------------------------------------
    def generate_pre_production_report_pdf(
        self,
        project: Dict[str, Any],
        stats: Dict[str, Any],
        schedule: Dict[str, Any],
        budget: Dict[str, Any],
        ai_pipeline_info: List[Dict[str, Any]]
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []

        story.append(Paragraph(f"FINAL PRE-PRODUCTION PACKAGE REPORT", self.title_style))
        story.append(Paragraph(f"Project: {project.get('name', 'Movie')} | Executive Production Dossier", self.subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0F172A'), spaceAfter=15))

        # Executive Summary
        story.append(Paragraph("1. Executive Summary & Statistics", self.section_heading))
        summary_text = (
            f"This pre-production package was autonomously generated from the uploaded screenplay using our "
            f"AI/NLP/OCR pipeline. The production consists of <b>{stats.get('scene_count', 0)} scenes</b> across "
            f"<b>{stats.get('location_count', 0)} distinct locations</b>, requiring <b>{stats.get('character_count', 0)} characters</b>. "
            f"The shooting schedule was mathematically optimized using Google OR-Tools CP-SAT, achieving an optimal schedule of "
            f"<b>{schedule.get('total_days', 0)} shooting days</b> with <b>{schedule.get('total_company_moves', 0)} company moves</b>. "
            f"Estimated production budget: <b>INR {budget.get('grand_total', 0.0):,.2f}</b> ({budget.get('disclaimer', '')})."
        )
        story.append(Paragraph(summary_text, self.body_style))
        story.append(Spacer(1, 10))

        # Table of Production Metrics
        metrics_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Scenes", str(stats.get('scene_count', 0)), "Shooting Days", str(schedule.get('total_days', 0))],
            ["Cast Members", str(stats.get('character_count', 0)), "Est. Budget Subtotal", f"INR {budget.get('subtotal', 0.0):,.2f}"],
            ["Locations", str(stats.get('location_count', 0)), "Contingency (10%)", f"INR {budget.get('contingency_amount', 0.0):,.2f}"],
            ["Total Props", str(stats.get('props_count', 0)), "Taxes & Permits (8%)", f"INR {budget.get('tax_amount', 0.0):,.2f}"],
            ["Costumes / Wardrobe", str(stats.get('costumes_count', 0)), "Grand Total Budget", f"INR {budget.get('grand_total', 0.0):,.2f}"]
        ]
        t_metrics = Table(metrics_data, colWidths=[130, 140, 130, 140])
        t_metrics.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_metrics)
        story.append(Spacer(1, 14))

        # Scheduling Optimization Explanation
        story.append(Paragraph("2. Google OR-Tools CP-SAT Scheduling Formulation", self.section_heading))
        sched_text = (
            "<b>Objective Function:</b> Minimize Weighted Sum = 1000 × Shooting Days + 100 × Location Occurrences + 10 × Cast Days.<br/>"
            "<b>Constraints Implemented:</b><br/>"
            "• Every scene must be scheduled on exactly one day.<br/>"
            "• Daily shooting hours cannot exceed configured maximum (10 hours per day).<br/>"
            "• Setup and changeover times (30 min/scene) are accounted for.<br/>"
            "• Location clustering minimizes redundant company moves.<br/>"
            "• Symmetry breaking enforces consecutive active shooting days."
        )
        story.append(Paragraph(sched_text, self.body_style))
        story.append(Spacer(1, 14))

        # AI Tools & Pipeline Methodology
        story.append(Paragraph("3. AI Pipeline & Explainability Audit", self.section_heading))
        ai_data = [["Pipeline Stage", "AI / Optimization Technology", "Function / Role in System"]]
        ai_data.extend([
            ["PDF Ingestion & OCR", "PyMuPDF + PaddleOCR Fallback", "Direct text extraction with automated scanned PDF OCR fallback."],
            ["Linguistic Processing", "spaCy (en_core_web_sm)", "Sentence boundary detection, POS tagging, and noun chunk extraction."],
            ["Named Entity Recognition", "Hugging Face Transformers (BERT-NER)", "Contextual entity classification for characters, locations, and assets."],
            ["Scheduling Optimization", "Google OR-Tools (CP-SAT Solver)", "Constraint Programming optimization minimizing days and company moves."],
            ["Budget & Pre-Production", "Movie Magic & StudioBinder Workflows", "Structured A-T-L/B-T-L accounting, Stripboard, and Call Sheets."]
        ])
        t_ai = Table(ai_data, colWidths=[120, 160, 260])
        t_ai.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F766E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_ai)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------
    # XLSX Generators using OpenPyXL
    # -------------------------------------------------------------
    def generate_excel_workbook(self, title: str, headers: List[str], rows: List[List[Any]]) -> bytes:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title[:30]

        # Header styling
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # Write headers
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border

        # Write data rows
        for row_idx, row_data in enumerate(rows, 2):
            for col_idx, val in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.border = border
                cell.font = Font(name="Calibri", size=10)
                if isinstance(val, (int, float)):
                    cell.alignment = Alignment(horizontal="right")
                else:
                    cell.alignment = Alignment(horizontal="left")

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(12, min(max_len + 4, 50))

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_budget_xlsx(self, budget: Dict[str, Any]) -> bytes:
        headers = ["Category", "Department", "Code", "Description", "Quantity", "Unit", "Rate (INR)", "Days", "Subtotal (INR)", "Notes"]
        rows = []
        for i in budget.get("items", []):
            rows.append([
                i.get("category", ""),
                i.get("department", ""),
                i.get("account_code", ""),
                i.get("description", ""),
                i.get("quantity", 1),
                i.get("unit", ""),
                i.get("unit_rate", 0),
                i.get("days_count", 1),
                i.get("subtotal", 0),
                i.get("notes", "")
            ])
        # Summary rows
        rows.append([])
        rows.append(["", "", "", "SUBTOTAL:", "", "", "", "", budget.get("subtotal", 0), ""])
        rows.append(["", "", "", f"CONTINGENCY ({int(budget.get('contingency_rate', 0.1)*100)}%):", "", "", "", "", budget.get("contingency_amount", 0), ""])
        rows.append(["", "", "", f"TAXES & PERMITS ({int(budget.get('tax_rate', 0.08)*100)}%):", "", "", "", "", budget.get("tax_amount", 0), ""])
        rows.append(["", "", "", "GRAND TOTAL:", "", "", "", "", budget.get("grand_total", 0), budget.get("disclaimer", "")])

        return self.generate_excel_workbook("Production Budget", headers, rows)

    # -------------------------------------------------------------
    # DOCX Generator for Call Sheet / Letters
    # -------------------------------------------------------------
    def generate_call_sheet_docx(self, cs: Dict[str, Any]) -> bytes:
        doc = docx.Document()
        doc.add_heading(f"{cs.get('project_name', 'Production')} - Call Sheet", level=0)
        doc.add_paragraph(f"Day {cs.get('day_number', 1)} | Shoot Date: {cs.get('shoot_date', '')}")
        doc.add_paragraph(f"General Call: {cs.get('general_call_time', '07:00 AM')} | Location: {cs.get('location_name', '')}")
        
        doc.add_heading("Scheduled Scenes", level=1)
        for s in cs.get("scenes_summary", []):
            doc.add_paragraph(f"Scene {s.get('scene_number')}: {s.get('heading')} ({s.get('pages')} pgs) - {s.get('start_time')}")

        doc.add_heading("Cast Calls", level=1)
        for c in cs.get("cast_calls", []):
            doc.add_paragraph(f"{c.get('character_name')} ({c.get('actor_name')}): Pickup {c.get('pickup')}, H/MU {c.get('hair_makeup')}, On Set {c.get('on_set')}")

        doc.add_heading("Special Instructions", level=1)
        doc.add_paragraph(cs.get("special_instructions", "None"))

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    # -------------------------------------------------------------
    # Complete Pre-Production ZIP Package (All 11 Documents)
    # -------------------------------------------------------------
    def build_complete_package_zip(
        self,
        project: Dict[str, Any],
        scenes: List[Dict[str, Any]],
        characters: List[Dict[str, Any]],
        locations: List[Dict[str, Any]],
        elements: List[Dict[str, Any]],
        schedule: Dict[str, Any],
        budget: Dict[str, Any],
        call_sheets: List[Dict[str, Any]],
        callback_letters: List[Dict[str, Any]]
    ) -> bytes:
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 01_Script_Breakdown.pdf
            pdf_breakdown = self.generate_script_breakdown_pdf(project, scenes, elements)
            zip_file.writestr("01_Script_Breakdown.pdf", pdf_breakdown)

            # 02_Scene_Breakdown.xlsx
            sc_rows = [
                [s.get("scene_number"), s.get("heading"), s.get("interior_exterior"), s.get("location_name"),
                 s.get("time_of_day"), s.get("estimated_pages"), s.get("estimated_duration_minutes"), s.get("complexity_level")]
                for s in scenes
            ]
            xlsx_scenes = self.generate_excel_workbook(
                "Scenes",
                ["Scene #", "Heading", "I/E", "Location", "Time", "Pages", "Duration (mins)", "Complexity"],
                sc_rows
            )
            zip_file.writestr("02_Scene_Breakdown.xlsx", xlsx_scenes)

            # 03_Cast_Breakdown.xlsx
            cast_rows = [
                [c.get("name"), c.get("role"), c.get("scene_count"), c.get("dialogue_count"),
                 c.get("estimated_screen_time_minutes"), c.get("required_shooting_days"), c.get("costume_requirements", "")]
                for c in characters
            ]
            xlsx_cast = self.generate_excel_workbook(
                "Cast",
                ["Character Name", "Role", "Scene Count", "Dialogue Count", "Est Screen Time (min)", "Shoot Days", "Costume Notes"],
                cast_rows
            )
            zip_file.writestr("03_Cast_Breakdown.xlsx", xlsx_cast)

            # 04_Location_Breakdown.xlsx
            loc_rows = [
                [l.get("name"), l.get("interior_exterior"), l.get("day_night"), l.get("scene_count"),
                 l.get("required_days"), "Yes" if l.get("company_move_required") else "No", l.get("estimated_cost", 1500)]
                for l in locations
            ]
            xlsx_loc = self.generate_excel_workbook(
                "Locations",
                ["Location Name", "I/E", "D/N", "Scenes Count", "Required Days", "Company Move Required", "Est Cost (INR)"],
                loc_rows
            )
            zip_file.writestr("04_Location_Breakdown.xlsx", xlsx_loc)

            # 05_Production_Elements.xlsx
            elem_rows = [
                [e.get("category"), e.get("name"), e.get("quantity", 1), f"{int(e.get('confidence', 0.85)*100)}%", e.get("extraction_source"), e.get("description", "")]
                for e in elements
            ]
            xlsx_elem = self.generate_excel_workbook(
                "Production Elements",
                ["Category", "Element Name", "Quantity", "Confidence", "Source Engine", "Description"],
                elem_rows
            )
            zip_file.writestr("05_Production_Elements.xlsx", xlsx_elem)

            # 06_Shooting_Schedule.xlsx
            sched_rows = []
            for d in schedule.get("shooting_days", []):
                for s in d.get("scheduled_scenes", []):
                    sched_rows.append([
                        d.get("day_number"), d.get("shoot_date"), s.get("sequence_order"), s.get("scene_number"),
                        s.get("heading"), s.get("location_name"), s.get("estimated_start_time"),
                        s.get("estimated_duration_minutes"), "YES" if s.get("company_move_before") else "NO"
                    ])
            xlsx_sched = self.generate_excel_workbook(
                "Shooting Schedule",
                ["Day #", "Shoot Date", "Order", "Scene #", "Heading", "Location", "Start Time", "Duration (mins)", "Company Move Before"],
                sched_rows
            )
            zip_file.writestr("06_Shooting_Schedule.xlsx", xlsx_sched)

            # 07_Stripboard.pdf
            pdf_strip = self.generate_stripboard_pdf(project, scenes)
            zip_file.writestr("07_Stripboard.pdf", pdf_strip)

            # 08_Budget.xlsx
            xlsx_budget = self.generate_budget_xlsx(budget)
            zip_file.writestr("08_Budget.xlsx", xlsx_budget)

            # 09_Call_Sheets.pdf
            pdf_call = self.generate_call_sheets_pdf(call_sheets)
            zip_file.writestr("09_Call_Sheets.pdf", pdf_call)

            # 10_Callback_Letters.pdf
            pdf_callbacks = self.generate_callback_letters_pdf(callback_letters)
            zip_file.writestr("10_Callback_Letters.pdf", pdf_callbacks)

            # 11_Pre_Production_Report.pdf
            stats = {
                "scene_count": len(scenes),
                "character_count": len(characters),
                "location_count": len(locations),
                "props_count": sum(1 for e in elements if e.get("category") == "PROP"),
                "costumes_count": sum(1 for e in elements if e.get("category") == "COSTUME")
            }
            pdf_report = self.generate_pre_production_report_pdf(project, stats, schedule, budget, [])
            zip_file.writestr("11_Pre_Production_Report.pdf", pdf_report)

            # complete_project.json
            project_dump = {
                "project": project,
                "scenes": scenes,
                "characters": characters,
                "locations": locations,
                "elements": elements,
                "schedule": schedule,
                "budget": budget,
                "call_sheets": call_sheets,
                "callback_letters": callback_letters
            }
            zip_file.writestr("complete_project.json", json.dumps(project_dump, indent=2, default=str))

        zip_buffer.seek(0)
        return zip_buffer.getvalue()
