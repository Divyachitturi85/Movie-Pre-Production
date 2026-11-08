import os
import re
import io
import logging
from typing import Tuple, Dict, Any, List
import pymupdf  # PyMuPDF
from PIL import Image
import numpy as np

# Disable slow/hanging connectivity checks to external hosters in paddlex/paddleocr
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self, ocr_lang: str = "en"):
        self.ocr_lang = ocr_lang
        self._ocr_engine = None

    def _get_ocr_engine(self):
        """Lazy load PaddleOCR engine with graceful unavailable fallback for memory-constrained cloud tiers"""
        if self._ocr_engine is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr_engine = PaddleOCR(use_angle_cls=True, lang=self.ocr_lang, show_log=False)
                logger.info("PaddleOCR engine initialized successfully.")
            except Exception as e:
                logger.warning(f"PaddleOCR engine not available: {e}. Fallback mode active.")
                self._ocr_engine = "UNAVAILABLE"
        return self._ocr_engine

    def assess_text_quality(self, text: str, page_count: int) -> float:
        """
        Assess quality of extracted text (0.0 to 1.0).
        Scanned PDFs typically yield 0 or near-empty text with few alphanumeric words.
        """
        if not text or page_count <= 0:
            return 0.0

        total_chars = len(text.strip())
        chars_per_page = total_chars / max(1, page_count)

        # Count alphanumeric characters vs garbage/symbols
        alphanumeric = sum(1 for c in text if c.isalnum())
        alpha_ratio = alphanumeric / max(1, total_chars)

        # Screenplay headings typically have INT. or EXT. or scene sluglines
        has_sluglines = bool(re.search(r'\b(INT\.|EXT\.|INT\s|EXT\s|SCENE\s|FADE\sIN)\b', text, re.IGNORECASE))

        # Scoring
        score = 0.0
        if chars_per_page > 300:
            score += 0.4
        elif chars_per_page > 100:
            score += 0.2

        if alpha_ratio > 0.65:
            score += 0.4
        elif alpha_ratio > 0.4:
            score += 0.2

        if has_sluglines:
            score += 0.2

        return min(1.0, score)

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Main extraction pipeline:
        1. Inspect each page with PyMuPDF for native direct text.
        2. For pages with low or missing text, attempt PaddleOCR if available.
        3. Track extraction outcome, recognized text, and confidence per page.
        4. Assemble cleaned extracted text from actual recognized content ONLY (no fabricated dialogue/scenes).
        5. Return explicit extraction status, warnings, and per-page metrics.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = pymupdf.open(file_path)
        page_count = len(doc)
        ocr_engine = None

        page_records = []
        warnings = []
        all_ocr_confidences = []

        for page_idx in range(page_count):
            page = doc[page_idx]
            page_num = page_idx + 1
            direct_text = (page.get_text("text") or "").strip()

            page_quality = self.assess_text_quality(direct_text, 1)
            needs_ocr = page_quality < 0.35 or len(direct_text) < 40

            page_extracted_text = ""
            page_method = "PDF_DIRECT"
            page_confidence = 1.0

            if not needs_ocr:
                # High quality native digital text layer on this page
                page_extracted_text = direct_text
                page_method = "PDF_DIRECT"
                page_confidence = 1.0
            else:
                # Page has low or missing digital text: attempt optical recognition if engine available
                if ocr_engine is None:
                    ocr_engine = self._get_ocr_engine()

                if ocr_engine not in (None, "UNAVAILABLE", "FALLBACK"):
                    ocr_lines, confs, ocr_ok = self._ocr_page(page, ocr_engine)
                    if ocr_ok and ocr_lines:
                        page_extracted_text = "\n".join(ocr_lines)
                        page_method = "OCR_SUCCESS"
                        page_confidence = round(sum(confs) / max(1, len(confs)), 3)
                        all_ocr_confidences.extend(confs)
                    else:
                        # OCR engine attempted but recognized no legible text on this page
                        if direct_text:
                            page_extracted_text = direct_text
                            page_method = "PDF_DIRECT"
                            page_confidence = round(page_quality, 2)
                            warnings.append(f"Page {page_num}: OCR recognized no text; retained low-density digital text.")
                        else:
                            page_extracted_text = ""
                            page_method = "OCR_FAILED"
                            page_confidence = 0.0
                            warnings.append(f"Page {page_num}: Scanned page detected, but optical recognition failed to detect text.")
                else:
                    # OCR engine is unavailable in this deployment tier
                    if direct_text:
                        page_extracted_text = direct_text
                        page_method = "PDF_DIRECT"
                        page_confidence = round(page_quality, 2)
                        warnings.append(f"Page {page_num}: Low digital text density detected and OCR engine is unavailable.")
                    else:
                        page_extracted_text = ""
                        page_method = "OCR_UNAVAILABLE"
                        page_confidence = 0.0
                        warnings.append(f"Page {page_num}: Scanned raster image without text layer; OCR engine is unavailable in this deployment tier.")

            page_records.append({
                "page_number": page_num,
                "method": page_method,
                "confidence": page_confidence,
                "text_length": len(page_extracted_text),
                "has_text": bool(page_extracted_text.strip()),
                "text": page_extracted_text
            })

        doc.close()

        # Build document-level text by preserving actual extracted text from all pages (NO fabricated content)
        valid_pages_text = [p["text"] for p in page_records if p["text"]]
        combined_raw = "\n\n".join(valid_pages_text) if valid_pages_text else ""
        cleaned = self.clean_screenplay_text(combined_raw) if combined_raw else ""
        doc_quality = self.assess_text_quality(cleaned, page_count)

        # Determine document-level extraction status
        ocr_success_pages = [p for p in page_records if p["method"] == "OCR_SUCCESS"]
        ocr_failed_pages = [p for p in page_records if p["method"] == "OCR_FAILED"]
        ocr_unavail_pages = [p for p in page_records if p["method"] == "OCR_UNAVAILABLE"]
        direct_pages = [p for p in page_records if p["method"] == "PDF_DIRECT"]
        scanned_pages_count = len(ocr_success_pages) + len(ocr_failed_pages) + len(ocr_unavail_pages)

        if scanned_pages_count == 0:
            doc_method = "PDF_DIRECT"
            doc_confidence = 1.0
        elif len(ocr_success_pages) == page_count:
            doc_method = "OCR_COMPLETE"
            doc_confidence = round(sum(all_ocr_confidences) / max(1, len(all_ocr_confidences)), 3) if all_ocr_confidences else 0.0
        elif len(ocr_success_pages) > 0:
            doc_method = "OCR_PARTIAL"
            doc_confidence = round(sum(all_ocr_confidences) / max(1, len(all_ocr_confidences)), 3) if all_ocr_confidences else 0.0
        elif len(ocr_unavail_pages) > 0:
            doc_method = "OCR_UNAVAILABLE"
            doc_confidence = 0.0
        elif len(ocr_failed_pages) > 0:
            doc_method = "OCR_FAILED"
            doc_confidence = 0.0
        else:
            doc_method = "PDF_DIRECT"
            doc_confidence = 1.0

        if not cleaned:
            warnings.append("No readable screenplay text could be extracted from this document.")

        return {
            "page_count": page_count,
            "extraction_method": doc_method,
            "ocr_confidence": doc_confidence,
            "quality_score": doc_quality,
            "raw_text": combined_raw,
            "cleaned_text": cleaned,
            "warnings": warnings,
            "page_details": page_records
        }

    def _ocr_page(self, page, ocr_engine) -> Tuple[List[str], List[float], bool]:
        """
        Renders a single PDF page to an RGB raster and executes optical recognition.
        Returns: (lines, confidences, success_flag)
        """
        try:
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img_np = np.array(image)

            try:
                result = ocr_engine.ocr(img_np, cls=True)
            except Exception:
                result = ocr_engine.ocr(img_np)

            lines = []
            confs = []
            if result and result[0]:
                for item in result[0]:
                    if item and len(item) >= 2 and item[1]:
                        txt = str(item[1][0]).strip()
                        c = float(item[1][1])
                        if txt:
                            lines.append(txt)
                            confs.append(c)

            return lines, confs, bool(lines)
        except Exception as e:
            logger.warning(f"PaddleOCR recognition failed on page: {e}")
            return [], [], False

    def clean_screenplay_text(self, text: str) -> str:
        """
        Normalizes screenplay text:
        - Normalizes Windows and Unix line breaks
        - Removes excessive whitespace while preserving screenplay indentation
        - Strips header/footer artifacts and standalone page numbers (e.g. 'Page 14', '14.')
        - Normalizes scene headings (e.g., INT. vs INT - vs INT / EXT)
        """
        if not text:
            return ""

        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove standalone page numbers at top/bottom of pages
        text = re.sub(r'^\s*(?:Page\s+)?\d+\s*[\.\)]?\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)

        # Standardize common heading typos
        text = re.sub(r'^\s*(INT|EXT|I/E|INT/EXT)\s*[\.-]?\s*', lambda m: f"{m.group(1).upper().replace('/', '/.')}. ", text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'INT\.\s*/\s*EXT\.', 'INT./EXT.', text)

        # Collapse 3+ consecutive newlines to 2
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()
