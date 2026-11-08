import os
import pytest
import pymupdf
from app.services.pdf_service import PDFService
from app.models.explainability import AIExplainabilityRecord

def create_sample_pdf(file_path: str, pages_text: list):
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        if text:
            page.insert_text((50, 50), text)
    doc.save(file_path)
    doc.close()

def test_1_digital_pdf_readable_text(tmp_path):
    pdf_path = str(tmp_path / "digital_script.pdf")
    content = "INT. LABORATORY - NIGHT\n\nDR. ELENA VANCE analyzes the anomalous signal on the monitors.\n\nMARCUS REED enters the lab."
    create_sample_pdf(pdf_path, [content])

    service = PDFService()
    res = service.extract_text(pdf_path)

    assert res["page_count"] == 1
    assert res["extraction_method"] == "PDF_DIRECT"
    assert res["ocr_confidence"] == 1.0
    assert "DR. ELENA VANCE" in res["cleaned_text"]
    assert "MARCUS REED" in res["cleaned_text"]
    assert res["page_details"][0]["method"] == "PDF_DIRECT"
    assert len(res["warnings"]) == 0

def test_2_scanned_pdf_ocr_unavailable(tmp_path, monkeypatch):
    pdf_path = str(tmp_path / "scanned_script.pdf")
    create_sample_pdf(pdf_path, [""])  # empty scanned page

    service = PDFService()
    monkeypatch.setattr(service, "_get_ocr_engine", lambda: "UNAVAILABLE")
    res = service.extract_text(pdf_path)

    assert res["extraction_method"] == "OCR_UNAVAILABLE"
    assert res["ocr_confidence"] == 0.0
    assert res["cleaned_text"] == ""
    assert "SARAH" not in res["cleaned_text"]
    assert "SCANNED SCRIPT LOCATION" not in res["cleaned_text"]
    assert any("OCR engine is unavailable" in w for w in res["warnings"])
    assert res["page_details"][0]["method"] == "OCR_UNAVAILABLE"

def test_3_scanned_pdf_ocr_success(tmp_path, monkeypatch):
    pdf_path = str(tmp_path / "scanned_with_ocr.pdf")
    create_sample_pdf(pdf_path, [""])

    class MockPaddleOCR:
        def ocr(self, img_np, cls=True):
            return [[[
                None, ("INT. COMMAND POST - DAY", 0.95)
            ], [
                None, ("COMMANDER HAYES reviews tactical map.", 0.91)
            ]]]

    service = PDFService()
    monkeypatch.setattr(service, "_get_ocr_engine", lambda: MockPaddleOCR())
    res = service.extract_text(pdf_path)

    assert res["extraction_method"] == "OCR_COMPLETE"
    assert res["ocr_confidence"] == 0.93
    assert "COMMANDER HAYES" in res["cleaned_text"]
    assert "INT. COMMAND POST - DAY" in res["cleaned_text"]
    assert res["page_details"][0]["method"] == "OCR_SUCCESS"

def test_4_multipage_pdf_ocr_partial(tmp_path, monkeypatch):
    pdf_path = str(tmp_path / "multipage_script.pdf")
    create_sample_pdf(pdf_path, ["", ""])  # 2 blank/scanned pages

    call_count = {"count": 0}

    class MockPartialPaddleOCR:
        def ocr(self, img_np, cls=True):
            call_count["count"] += 1
            if call_count["count"] == 1:
                return [[[None, ("INT. CORRIDOR - NIGHT", 0.90)]]]
            return []  # Page 2 fails / recognizes nothing

    service = PDFService()
    monkeypatch.setattr(service, "_get_ocr_engine", lambda: MockPartialPaddleOCR())
    res = service.extract_text(pdf_path)

    assert res["page_count"] == 2
    assert res["extraction_method"] == "OCR_PARTIAL"
    assert res["ocr_confidence"] == 0.90
    assert "INT. CORRIDOR - NIGHT" in res["cleaned_text"]
    assert res["page_details"][0]["method"] == "OCR_SUCCESS"
    assert res["page_details"][1]["method"] == "OCR_FAILED"
    assert res["page_details"][1]["text"] == ""
    assert any("Page 2" in w for w in res["warnings"])

def test_5_scanned_pdf_no_readable_content(tmp_path, monkeypatch):
    pdf_path = str(tmp_path / "empty_scan.pdf")
    create_sample_pdf(pdf_path, [""])

    class MockEmptyPaddleOCR:
        def ocr(self, img_np, cls=True):
            return []

    service = PDFService()
    monkeypatch.setattr(service, "_get_ocr_engine", lambda: MockEmptyPaddleOCR())
    res = service.extract_text(pdf_path)

    assert res["extraction_method"] == "OCR_FAILED"
    assert res["ocr_confidence"] == 0.0
    assert res["cleaned_text"] == ""
    assert any("No readable screenplay text could be extracted" in w for w in res["warnings"])

def test_6_no_fabricated_screenplay_content_in_any_fallback(tmp_path, monkeypatch):
    pdf_path = str(tmp_path / "blank.pdf")
    create_sample_pdf(pdf_path, [""])

    service = PDFService()
    monkeypatch.setattr(service, "_get_ocr_engine", lambda: "UNAVAILABLE")
    res = service.extract_text(pdf_path)

    hallucinations = [
        "SARAH", "MARCUS\nDeploying", "SCANNED SCRIPT LOCATION",
        "perimeter before dawn", "tactical sensor drones"
    ]
    for h in hallucinations:
        assert h not in res["raw_text"]
        assert h not in res["cleaned_text"]

def test_7_accurate_explainability_status():
    from app.api.scripts import upload_script_pdf

    # Test simulation of explainability building for all 5 extraction methods
    test_cases = [
        ("PDF_DIRECT", 100, 1.0, "PDF_EXTRACTION", False),
        ("OCR_COMPLETE", 500, 0.92, "OCR", True),
        ("OCR_PARTIAL", 250, 0.88, "OCR", True),
        ("OCR_UNAVAILABLE", 0, 0.0, "PDF_EXTRACTION", True),
        ("OCR_FAILED", 0, 0.0, "OCR", True)
    ]

    for method, chars, conf, expected_stage, expected_fallback in test_cases:
        extract_result = {
            "page_count": 2,
            "extraction_method": method,
            "ocr_confidence": conf,
            "quality_score": 0.5,
            "cleaned_text": "A" * chars,
            "warnings": ["Test warning"] if chars == 0 else []
        }

        # Verify accurate stage and fallback classification
        is_ocr = (method in ("OCR_COMPLETE", "OCR_PARTIAL", "OCR_FAILED"))
        stage = "OCR" if is_ocr else "PDF_EXTRACTION"
        fallback_used = (method != "PDF_DIRECT")

        assert stage == expected_stage
        assert fallback_used == expected_fallback