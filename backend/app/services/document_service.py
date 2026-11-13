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
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def _set_cell_background(cell, hex_color: str):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color.lstrip("#")}"/>')
    tcPr.append(shd)

def _set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def _set_table_borders(table, color="CBD5E1"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

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
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=28,
            rightMargin=28,
            topMargin=28,
            bottomMargin=28
        )
        story = []

        # High-clarity typography styles
        cs_title_style = ParagraphStyle(
            'CSTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            alignment=TA_CENTER,
            spaceAfter=3
        )
        cs_subtitle_style = ParagraphStyle(
            'CSSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#D97706'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=8
        )
        cs_section_head = ParagraphStyle(
            'CSSectionHead',
            parent=self.styles['Heading2'],
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor('#0F172A'),
            fontName='Helvetica-Bold',
            spaceBefore=8,
            spaceAfter=4
        )
        c_body = ParagraphStyle('CSCellBody', parent=self.styles['Normal'], fontSize=7.5, leading=9.5, textColor=colors.HexColor('#1E293B'))
        c_bold = ParagraphStyle('CSCellBold', parent=c_body, fontName='Helvetica-Bold')
        c_center = ParagraphStyle('CSCellCenter', parent=c_body, alignment=TA_CENTER)
        c_blue = ParagraphStyle('CSCellBlue', parent=c_body, fontName='Helvetica-Bold', textColor=colors.HexColor('#0369A1'))
        c_green = ParagraphStyle('CSCellGreen', parent=c_body, fontName='Helvetica-Bold', textColor=colors.HexColor('#047857'), alignment=TA_CENTER)
        c_th = ParagraphStyle('CSCellTH', parent=c_body, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
        c_log_lbl = ParagraphStyle('CSLogLbl', parent=c_body, fontName='Helvetica-Bold', textColor=colors.HexColor('#334155'))

        for idx, cs in enumerate(call_sheets):
            if idx > 0:
                story.append(PageBreak())

            story.append(Paragraph(f"<b>{cs.get('project_name', 'Film Production').upper()}</b> — OFFICIAL CALL SHEET", cs_title_style))
            story.append(Paragraph(
                f"DAY {cs.get('day_number', 1)} OF PRODUCTION &nbsp;|&nbsp; "
                f"SHOOT DATE: {cs.get('shoot_date', 'Shoot Day')} &nbsp;|&nbsp; "
                f"GENERAL CALL: {cs.get('general_call_time', '07:00 AM')}",
                cs_subtitle_style
            ))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A'), spaceAfter=8))

            # Key Logistics Block (556 pt wide)
            info_data = [
                [
                    Paragraph("SHOOT LOCATION:", c_log_lbl),
                    Paragraph(f"<b>{cs.get('location_name', 'Studio')}</b>", c_body),
                    Paragraph("PARKING / STAGING:", c_log_lbl),
                    Paragraph(cs.get('parking_info', 'Production lot'), c_body)
                ],
                [
                    Paragraph("LOCATION ADDRESS:", c_log_lbl),
                    Paragraph(cs.get('location_address', 'Main Facility'), c_body),
                    Paragraph("WEATHER FORECAST:", c_log_lbl),
                    Paragraph(cs.get('weather_placeholder', 'Clear & Dry'), c_body)
                ],
                [
                    Paragraph("NEAREST HOSPITAL:", c_log_lbl),
                    Paragraph(f"<b>{cs.get('nearest_hospital', 'Emergency Medical')}</b>", c_body),
                    Paragraph("EMERGENCY CONTACT:", c_log_lbl),
                    Paragraph(cs.get('emergency_contact', '1st AD / Production Office'), c_body)
                ]
            ]
            t_info = Table(info_data, colWidths=[100, 178, 105, 173])
            t_info.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 3.5),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(t_info)
            story.append(Spacer(1, 6))

            # Today's Scenes Schedule (556 pt wide)
            story.append(Paragraph("<b>TODAY'S SHOOTING SCHEDULE:</b>", cs_section_head))
            scenes_headers = [
                Paragraph("Sc #", c_th),
                Paragraph("Slugline / Set", c_th),
                Paragraph("Pages", c_th),
                Paragraph("Start Time", c_th),
                Paragraph("Duration", c_th),
                Paragraph("Complexity", c_th)
            ]
            scenes_rows = [scenes_headers]
            for sc in cs.get("scenes_summary", []):
                scenes_rows.append([
                    Paragraph(f"<b>#{sc.get('scene_number', 1)}</b>", c_center),
                    Paragraph(f"<b>{sc.get('heading', '')}</b>", c_body),
                    Paragraph(str(sc.get("pages", 0.5)), c_center),
                    Paragraph(f"<b>{sc.get('start_time', '08:00 AM')}</b>", c_blue),
                    Paragraph(f"{sc.get('duration_mins', 60)} min", c_center),
                    Paragraph(sc.get("complexity", "LOW"), c_center)
                ])

            t_sc = Table(scenes_rows, colWidths=[35, 236, 45, 80, 80, 80])
            sc_table_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 3),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]
            for r_idx in range(1, len(scenes_rows)):
                bg = colors.HexColor('#FFFFFF') if r_idx % 2 != 0 else colors.HexColor('#F8FAFC')
                sc_table_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg))

            t_sc.setStyle(TableStyle(sc_table_style))
            story.append(t_sc)
            story.append(Spacer(1, 6))

            # Cast Call Times & Department Logistics (556 pt wide)
            story.append(Paragraph("<b>CAST CALL TIMES & DEPARTMENT LOGISTICS:</b>", cs_section_head))
            cast_headers = [
                Paragraph("Cast #", c_th),
                Paragraph("Character", c_th),
                Paragraph("Actor Name", c_th),
                Paragraph("Role", c_th),
                Paragraph("Scenes Today", c_th),
                Paragraph("Pickup", c_th),
                Paragraph("H/MU", c_th),
                Paragraph("Wardrobe / Continuity", c_th),
                Paragraph("On Set", c_th),
                Paragraph("Status", c_th)
            ]
            cast_rows = [cast_headers]
            for c in cs.get("cast_calls", []):
                cast_rows.append([
                    Paragraph(f"<b>#{c.get('cast_id', 1)}</b>", c_center),
                    Paragraph(f"<b>{c.get('character_name', '')}</b>", c_bold),
                    Paragraph(c.get("actor_name", "TBD"), c_body),
                    Paragraph(c.get("role", "Lead"), c_body),
                    Paragraph(c.get("scenes_today", "Today's Scenes"), c_blue),
                    Paragraph(c.get("pickup", "06:15 AM"), c_center),
                    Paragraph(c.get("hair_makeup", "06:45 AM"), c_center),
                    Paragraph(c.get("wardrobe") or "Production Wardrobe", c_body),
                    Paragraph(c.get("on_set", "07:45 AM"), c_green),
                    Paragraph(c.get("status", "CALLED"), c_center)
                ])

            t_cast = Table(cast_rows, colWidths=[28, 70, 78, 58, 68, 40, 40, 92, 44, 38])
            cast_table_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 2.5),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]
            for r_idx in range(1, len(cast_rows)):
                bg = colors.HexColor('#FFFFFF') if r_idx % 2 != 0 else colors.HexColor('#F0F9FF')
                cast_table_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg))

            t_cast.setStyle(TableStyle(cast_table_style))
            story.append(t_cast)
            story.append(Spacer(1, 8))

            # Special Instructions & Safety Protocols Box (556 pt wide)
            safety_content = [
                [Paragraph("<b>SPECIAL INSTRUCTIONS & SAFETY PROTOCOLS:</b>", c_bold)],
                [Paragraph(cs.get("special_instructions", "Mandatory morning safety briefing prior to first camera roll."), c_body)],
                [Paragraph(f"<b>MEAL BREAK:</b> {cs.get('meal_break', '13:00 (Catering Staging Area)')} &nbsp;|&nbsp; <b>SAFETY SUPERVISOR / 1st AD:</b> {cs.get('emergency_contact', 'Production Office')}", c_body)]
            ]
            t_safety = Table(safety_content, colWidths=[556])
            t_safety.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_safety)

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
    # DOCX & XLSX Generators for Call Sheet
    # -------------------------------------------------------------
    def generate_call_sheet_docx(self, cs: Dict[str, Any]) -> bytes:
        doc = docx.Document()
        
        # Set narrow margins (0.5 in) so tables fit with high clarity
        for section in doc.sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        # Title & Banner
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_title = p_title.add_run(f"{cs.get('project_name', 'FILM PRODUCTION').upper()} — OFFICIAL CALL SHEET")
        run_title.font.name = 'Calibri'
        run_title.font.size = Pt(17)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(15, 23, 42)

        p_sub = doc.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_sub = p_sub.add_run(
            f"DAY {cs.get('day_number', 1)} OF PRODUCTION  |  "
            f"DATE: {cs.get('shoot_date', 'Shoot Day')}  |  "
            f"GENERAL CREW CALL: {cs.get('general_call_time', '07:00 AM')}"
        )
        run_sub.font.name = 'Calibri'
        run_sub.font.size = Pt(10.5)
        run_sub.font.bold = True
        run_sub.font.color.rgb = RGBColor(217, 119, 6)

        # Section 1: Logistics Table (3 rows x 4 cols, total width = 7.5 in)
        t_info = doc.add_table(rows=3, cols=4)
        t_info.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_info, "CBD5E1")
        
        info_items = [
            ("SHOOT LOCATION:", cs.get("location_name", "Stage / Set"), "PARKING & STAGING:", cs.get("parking_info", "Crew Parking")),
            ("LOCATION ADDRESS:", cs.get("location_address", "Facility Address"), "WEATHER FORECAST:", cs.get("weather_placeholder", "Clear & Dry")),
            ("NEAREST HOSPITAL:", cs.get("nearest_hospital", "Emergency Medical"), "EMERGENCY CONTACT:", cs.get("emergency_contact", "1st AD / Production Office"))
        ]
        
        col_widths_info = [Inches(1.3), Inches(2.45), Inches(1.3), Inches(2.45)]
        for r_idx, (lbl1, val1, lbl2, val2) in enumerate(info_items):
            row = t_info.rows[r_idx]
            
            # Label 1
            row.cells[0].text = lbl1
            row.cells[0].paragraphs[0].runs[0].font.bold = True
            row.cells[0].paragraphs[0].runs[0].font.size = Pt(8.5)
            row.cells[0].paragraphs[0].runs[0].font.name = 'Calibri'
            _set_cell_background(row.cells[0], "F1F5F9")
            _set_cell_margins(row.cells[0], 60, 60, 100, 100)
            row.cells[0].width = col_widths_info[0]
            
            # Value 1
            row.cells[1].text = str(val1)
            row.cells[1].paragraphs[0].runs[0].font.size = Pt(8.5)
            row.cells[1].paragraphs[0].runs[0].font.name = 'Calibri'
            _set_cell_margins(row.cells[1], 60, 60, 100, 100)
            row.cells[1].width = col_widths_info[1]
            
            # Label 2
            row.cells[2].text = lbl2
            row.cells[2].paragraphs[0].runs[0].font.bold = True
            row.cells[2].paragraphs[0].runs[0].font.size = Pt(8.5)
            row.cells[2].paragraphs[0].runs[0].font.name = 'Calibri'
            _set_cell_background(row.cells[2], "F1F5F9")
            _set_cell_margins(row.cells[2], 60, 60, 100, 100)
            row.cells[2].width = col_widths_info[2]
            
            # Value 2
            row.cells[3].text = str(val2)
            row.cells[3].paragraphs[0].runs[0].font.size = Pt(8.5)
            row.cells[3].paragraphs[0].runs[0].font.name = 'Calibri'
            _set_cell_margins(row.cells[3], 60, 60, 100, 100)
            row.cells[3].width = col_widths_info[3]

        doc.add_paragraph()

        # Section 2: Today's Shooting Schedule
        h_sc = doc.add_heading("TODAY'S SHOOTING SCHEDULE", level=2)
        h_sc.paragraph_format.space_before = Pt(4)
        h_sc.paragraph_format.space_after = Pt(4)
        for r in h_sc.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)

        scenes_summary = cs.get("scenes_summary", [])
        t_sc = doc.add_table(rows=len(scenes_summary) + 1, cols=6)
        t_sc.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_sc, "CBD5E1")
        
        sc_headers = ["Sc #", "Slugline / Set", "Pages", "Start Time", "Duration", "Complexity"]
        sc_widths = [Inches(0.6), Inches(3.3), Inches(0.6), Inches(1.0), Inches(1.0), Inches(1.0)]
        
        for c_idx, text in enumerate(sc_headers):
            cell = t_sc.rows[0].cells[c_idx]
            cell.text = text
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.runs[0]
            run.font.bold = True
            run.font.size = Pt(8.5)
            run.font.name = 'Calibri'
            run.font.color.rgb = RGBColor(255, 255, 255)
            _set_cell_background(cell, "1E293B")
            _set_cell_margins(cell, 80, 80, 80, 80)
            cell.width = sc_widths[c_idx]

        for r_idx, sc in enumerate(scenes_summary, 1):
            row = t_sc.rows[r_idx]
            bg_color = "FFFFFF" if r_idx % 2 != 0 else "F8FAFC"
            sc_vals = [
                f"#{sc.get('scene_number', 1)}",
                sc.get("heading", ""),
                str(sc.get("pages", 0.5)),
                sc.get("start_time", "08:00 AM"),
                f"{sc.get('duration_mins', 60)} min",
                sc.get("complexity", "LOW")
            ]
            for c_idx, val in enumerate(sc_vals):
                cell = row.cells[c_idx]
                cell.text = str(val)
                p = cell.paragraphs[0]
                run = p.runs[0]
                run.font.size = Pt(8)
                run.font.name = 'Calibri'
                if c_idx in [0, 2, 3, 4, 5]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if c_idx == 0:
                    run.font.bold = True
                if c_idx == 3:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(3, 105, 161)
                _set_cell_background(cell, bg_color)
                _set_cell_margins(cell, 60, 60, 80, 80)
                cell.width = sc_widths[c_idx]

        doc.add_paragraph()

        # Section 3: Cast Call Times & Department Logistics
        h_cast = doc.add_heading("CAST CALL TIMES & DEPARTMENT LOGISTICS", level=2)
        h_cast.paragraph_format.space_before = Pt(4)
        h_cast.paragraph_format.space_after = Pt(4)
        for r in h_cast.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)

        cast_calls = cs.get("cast_calls", [])
        t_cast = doc.add_table(rows=len(cast_calls) + 1, cols=10)
        t_cast.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_cast, "CBD5E1")
        
        cast_headers = ["Cast #", "Character", "Actor Name", "Role", "Scenes Today", "Pickup", "H/MU", "Wardrobe / Notes", "On Set", "Status"]
        cast_widths = [Inches(0.45), Inches(0.95), Inches(1.05), Inches(0.75), Inches(0.95), Inches(0.55), Inches(0.55), Inches(1.25), Inches(0.55), Inches(0.45)]

        for c_idx, text in enumerate(cast_headers):
            cell = t_cast.rows[0].cells[c_idx]
            cell.text = text
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.runs[0]
            run.font.bold = True
            run.font.size = Pt(8)
            run.font.name = 'Calibri'
            run.font.color.rgb = RGBColor(255, 255, 255)
            _set_cell_background(cell, "0284C7")
            _set_cell_margins(cell, 80, 80, 60, 60)
            cell.width = cast_widths[c_idx]

        for r_idx, c in enumerate(cast_calls, 1):
            row = t_cast.rows[r_idx]
            bg_color = "FFFFFF" if r_idx % 2 != 0 else "F0F9FF"
            cast_vals = [
                f"#{c.get('cast_id', 1)}",
                c.get("character_name", ""),
                c.get("actor_name", "TBD"),
                c.get("role", "Lead"),
                c.get("scenes_today", "Today's Scenes"),
                c.get("pickup", "06:15 AM"),
                c.get("hair_makeup", "06:45 AM"),
                c.get("wardrobe") or "Production Wardrobe",
                c.get("on_set", "07:45 AM"),
                c.get("status", "CALLED")
            ]
            for col_i, val in enumerate(cast_vals):
                cell = row.cells[col_i]
                cell.text = str(val)
                p = cell.paragraphs[0]
                run = p.runs[0]
                run.font.size = Pt(7.5)
                run.font.name = 'Calibri'
                if col_i in [0, 5, 6, 8, 9]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if col_i in [0, 1]:
                    run.font.bold = True
                if col_i == 4:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(3, 105, 161)
                if col_i == 8:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(4, 120, 87)
                if col_i == 9:
                    run.font.bold = True
                    run.font.color.rgb = RGBColor(2, 132, 199)
                _set_cell_background(cell, bg_color)
                _set_cell_margins(cell, 60, 60, 60, 60)
                cell.width = cast_widths[col_i]

        doc.add_paragraph()

        # Section 4: Special Instructions & Safety Protocols
        h_safe = doc.add_heading("SPECIAL INSTRUCTIONS & SAFETY PROTOCOLS", level=2)
        h_safe.paragraph_format.space_before = Pt(4)
        h_safe.paragraph_format.space_after = Pt(4)
        for r in h_safe.runs:
            r.font.name = 'Calibri'
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)

        t_safe = doc.add_table(rows=2, cols=1)
        t_safe.alignment = WD_TABLE_ALIGNMENT.CENTER
        _set_table_borders(t_safe, "E2E8F0")
        
        t_safe.rows[0].cells[0].text = cs.get("special_instructions", "Mandatory morning safety briefing prior to first camera roll.")
        t_safe.rows[0].cells[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        t_safe.rows[0].cells[0].paragraphs[0].runs[0].font.name = 'Calibri'
        _set_cell_background(t_safe.rows[0].cells[0], "F8FAFC")
        _set_cell_margins(t_safe.rows[0].cells[0], 80, 80, 100, 100)
        t_safe.rows[0].cells[0].width = Inches(7.5)

        t_safe.rows[1].cells[0].text = f"MEAL BREAK: {cs.get('meal_break', '13:00 (Catering Staging Area)')}  |  SAFETY SUPERVISOR / 1st AD: {cs.get('emergency_contact', 'Production Office')}"
        t_safe.rows[1].cells[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        t_safe.rows[1].cells[0].paragraphs[0].runs[0].font.bold = True
        t_safe.rows[1].cells[0].paragraphs[0].runs[0].font.name = 'Calibri'
        _set_cell_background(t_safe.rows[1].cells[0], "F1F5F9")
        _set_cell_margins(t_safe.rows[1].cells[0], 80, 80, 100, 100)
        t_safe.rows[1].cells[0].width = Inches(7.5)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_call_sheet_xlsx(self, cs: Dict[str, Any]) -> bytes:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Call Sheet Day {cs.get('day_number', 1)}"
        ws.views.sheetView[0].showGridLines = True

        # Styles definition
        font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
        font_sub = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_sec = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_th = Font(name="Calibri", size=9.5, bold=True, color="FFFFFF")
        font_lbl = Font(name="Calibri", size=9, bold=True, color="334155")
        font_val = Font(name="Calibri", size=9, color="0F172A")
        font_val_bold = Font(name="Calibri", size=9, bold=True, color="0F172A")
        font_blue = Font(name="Calibri", size=9, bold=True, color="0369A1")
        font_green = Font(name="Calibri", size=9.5, bold=True, color="047857")

        fill_title = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        fill_sub = PatternFill(start_color="D97706", end_color="D97706", fill_type="solid")
        fill_sec_sc = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        fill_th_sc = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
        fill_sec_cast = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
        fill_th_cast = PatternFill(start_color="0369A1", end_color="0369A1", fill_type="solid")
        fill_sec_safe = PatternFill(start_color="475569", end_color="475569", fill_type="solid")
        fill_lbl = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        fill_even = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_even_blue = PatternFill(start_color="F0F9FF", end_color="F0F9FF", fill_type="solid")

        border_thin = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Row 1: Merged Title Banner
        ws.merge_cells("A1:J1")
        ws.row_dimensions[1].height = 32
        cell_t = ws.cell(row=1, column=1, value=f"{cs.get('project_name', 'FILM PRODUCTION').upper()} — OFFICIAL CALL SHEET")
        cell_t.font = font_title
        cell_t.fill = fill_title
        cell_t.alignment = align_center

        # Row 2: Merged Sub-banner
        ws.merge_cells("A2:J2")
        ws.row_dimensions[2].height = 22
        cell_s = ws.cell(row=2, column=1, value=f"DAY {cs.get('day_number', 1)} OF PRODUCTION  |  DATE: {cs.get('shoot_date', 'Shoot Day')}  |  GENERAL CREW CALL: {cs.get('general_call_time', '07:00 AM')}")
        cell_s.font = font_sub
        cell_s.fill = fill_sub
        cell_s.alignment = align_center

        # Row 3: Blank separator
        ws.row_dimensions[3].height = 8

        # Logistics Grid (Rows 4, 5, 6)
        logistics_rows = [
            ("SHOOT LOCATION", cs.get("location_name", ""), "LOCATION ADDRESS", cs.get("location_address", "")),
            ("PARKING / STAGING", cs.get("parking_info", ""), "WEATHER FORECAST", cs.get("weather_placeholder", "")),
            ("NEAREST HOSPITAL", cs.get("nearest_hospital", ""), "EMERGENCY CONTACT", cs.get("emergency_contact", ""))
        ]

        curr_row = 4
        for lbl1, val1, lbl2, val2 in logistics_rows:
            ws.row_dimensions[curr_row].height = 20
            # A-B: Label 1
            ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=2)
            c1 = ws.cell(row=curr_row, column=1, value=lbl1)
            c1.font = font_lbl
            c1.fill = fill_lbl
            c1.alignment = align_left
            c1.border = border_thin

            # C-E: Value 1
            ws.merge_cells(start_row=curr_row, start_column=3, end_row=curr_row, end_column=5)
            c2 = ws.cell(row=curr_row, column=3, value=val1)
            c2.font = font_val_bold if "LOCATION" in lbl1 or "HOSPITAL" in lbl1 else font_val
            c2.alignment = align_left
            c2.border = border_thin

            # F-G: Label 2
            ws.merge_cells(start_row=curr_row, start_column=6, end_row=curr_row, end_column=7)
            c3 = ws.cell(row=curr_row, column=6, value=lbl2)
            c3.font = font_lbl
            c3.fill = fill_lbl
            c3.alignment = align_left
            c3.border = border_thin

            # H-J: Value 2
            ws.merge_cells(start_row=curr_row, start_column=8, end_row=curr_row, end_column=10)
            c4 = ws.cell(row=curr_row, column=8, value=val2)
            c4.font = font_val
            c4.alignment = align_left
            c4.border = border_thin

            curr_row += 1

        # Separator
        curr_row += 1
        ws.row_dimensions[curr_row].height = 8
        curr_row += 1

        # Section Header: Today's Shooting Schedule
        ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=6)
        ws.row_dimensions[curr_row].height = 22
        c_sec_sc = ws.cell(row=curr_row, column=1, value="TODAY'S SHOOTING SCHEDULE")
        c_sec_sc.font = font_sec
        c_sec_sc.fill = fill_sec_sc
        c_sec_sc.alignment = align_left
        curr_row += 1

        # Scenes Table Headers
        sc_headers = ["Sc #", "Slugline / Set", "Pages", "Start Time", "Duration", "Complexity"]
        ws.row_dimensions[curr_row].height = 20
        for col_idx, h in enumerate(sc_headers, 1):
            cell = ws.cell(row=curr_row, column=col_idx, value=h)
            cell.font = font_th
            cell.fill = fill_th_sc
            cell.alignment = align_center
            cell.border = border_thin
        curr_row += 1

        # Scenes Data Rows
        scenes_summary = cs.get("scenes_summary", [])
        for r_idx, sc in enumerate(scenes_summary):
            ws.row_dimensions[curr_row].height = 20
            row_fill = fill_even if r_idx % 2 == 1 else None
            
            c_sc = ws.cell(row=curr_row, column=1, value=f"#{sc.get('scene_number', 1)}")
            c_sc.alignment = align_center
            c_sc.font = font_val_bold
            
            c_hd = ws.cell(row=curr_row, column=2, value=sc.get("heading", ""))
            c_hd.alignment = align_left
            c_hd.font = font_val_bold
            
            c_pg = ws.cell(row=curr_row, column=3, value=sc.get("pages", 0.5))
            c_pg.alignment = align_center
            c_pg.font = font_val
            
            c_st = ws.cell(row=curr_row, column=4, value=sc.get("start_time", "08:00 AM"))
            c_st.alignment = align_center
            c_st.font = font_blue
            
            c_du = ws.cell(row=curr_row, column=5, value=f"{sc.get('duration_mins', 60)} min")
            c_du.alignment = align_center
            c_du.font = font_val
            
            c_cx = ws.cell(row=curr_row, column=6, value=sc.get("complexity", "LOW"))
            c_cx.alignment = align_center
            c_cx.font = font_val
            
            for col_i in range(1, 7):
                cell = ws.cell(row=curr_row, column=col_i)
                cell.border = border_thin
                if row_fill:
                    cell.fill = row_fill
            curr_row += 1

        # Separator
        curr_row += 1
        ws.row_dimensions[curr_row].height = 8
        curr_row += 1

        # Section Header: Cast Call Times & Department Logistics
        ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=10)
        ws.row_dimensions[curr_row].height = 22
        c_sec_cast = ws.cell(row=curr_row, column=1, value="CAST CALL TIMES & DEPARTMENT LOGISTICS")
        c_sec_cast.font = font_sec
        c_sec_cast.fill = fill_sec_cast
        c_sec_cast.alignment = align_left
        curr_row += 1

        # Cast Table Headers
        cast_headers = ["Cast #", "Character Name", "Actor Name", "Role", "Scenes Scheduled Today", "Pickup Time", "Hair & Makeup", "Wardrobe / Notes", "On Set Call", "Call Status"]
        ws.row_dimensions[curr_row].height = 20
        for col_idx, h in enumerate(cast_headers, 1):
            cell = ws.cell(row=curr_row, column=col_idx, value=h)
            cell.font = font_th
            cell.fill = fill_th_cast
            cell.alignment = align_center
            cell.border = border_thin
        curr_row += 1

        # Cast Data Rows
        cast_calls = cs.get("cast_calls", [])
        for r_idx, c in enumerate(cast_calls):
            ws.row_dimensions[curr_row].height = 24
            row_fill = fill_even_blue if r_idx % 2 == 1 else None
            
            c_id = ws.cell(row=curr_row, column=1, value=f"#{c.get('cast_id', 1)}")
            c_id.alignment = align_center
            c_id.font = font_val_bold
            
            c_char = ws.cell(row=curr_row, column=2, value=c.get("character_name", ""))
            c_char.alignment = align_left
            c_char.font = font_val_bold
            
            c_act = ws.cell(row=curr_row, column=3, value=c.get("actor_name", "TBD"))
            c_act.alignment = align_left
            c_act.font = font_val
            
            c_role = ws.cell(row=curr_row, column=4, value=c.get("role", "Lead"))
            c_role.alignment = align_left
            c_role.font = font_val
            
            c_sc = ws.cell(row=curr_row, column=5, value=c.get("scenes_today", "Today's Scenes"))
            c_sc.alignment = align_left
            c_sc.font = font_blue
            
            c_pu = ws.cell(row=curr_row, column=6, value=c.get("pickup", "06:15 AM"))
            c_pu.alignment = align_center
            c_pu.font = font_val
            
            c_hm = ws.cell(row=curr_row, column=7, value=c.get("hair_makeup", "06:45 AM"))
            c_hm.alignment = align_center
            c_hm.font = font_val
            
            c_wd = ws.cell(row=curr_row, column=8, value=c.get("wardrobe") or "Production Wardrobe")
            c_wd.alignment = align_left
            c_wd.font = font_val
            
            c_os = ws.cell(row=curr_row, column=9, value=c.get("on_set", "07:45 AM"))
            c_os.alignment = align_center
            c_os.font = font_green
            
            c_st = ws.cell(row=curr_row, column=10, value=c.get("status", "CALLED"))
            c_st.alignment = align_center
            c_st.font = font_blue
            
            for col_i in range(1, 11):
                cell = ws.cell(row=curr_row, column=col_i)
                cell.border = border_thin
                if row_fill:
                    cell.fill = row_fill
            curr_row += 1

        # Separator
        curr_row += 1
        ws.row_dimensions[curr_row].height = 8
        curr_row += 1

        # Section Header: Special Instructions & Safety
        ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=10)
        ws.row_dimensions[curr_row].height = 20
        c_sec_safe = ws.cell(row=curr_row, column=1, value="SPECIAL INSTRUCTIONS, SAFETY PROTOCOLS & MEAL BREAKS")
        c_sec_safe.font = font_sec
        c_sec_safe.fill = fill_sec_safe
        c_sec_safe.alignment = align_left
        curr_row += 1

        # Safety rows
        ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=10)
        c_inst = ws.cell(row=curr_row, column=1, value=f"SPECIAL INSTRUCTIONS: {cs.get('special_instructions', 'Mandatory morning safety briefing prior to first camera roll.')}")
        c_inst.font = font_val
        c_inst.alignment = align_left
        curr_row += 1

        ws.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=10)
        c_mb = ws.cell(row=curr_row, column=1, value=f"MEAL BREAK: {cs.get('meal_break', '13:00 (Catering Staging Area)')}  |  SAFETY SUPERVISOR / 1st AD: {cs.get('emergency_contact', 'Production Office')}")
        c_mb.font = font_val_bold
        c_mb.alignment = align_left

        # Adjust column widths
        col_min_widths = {
            1: 10,  # Cast # / Sc #
            2: 24,  # Character / Slugline
            3: 20,  # Actor / Pages
            4: 16,  # Role / Start Time
            5: 32,  # Scenes Today / Duration
            6: 14,  # Pickup / Complexity
            7: 14,  # H/MU
            8: 38,  # Wardrobe
            9: 14,  # On Set
            10: 12  # Status
        }
        for col_idx, min_w in col_min_widths.items():
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = min_w

        buffer = io.BytesIO()
        wb.save(buffer)
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
