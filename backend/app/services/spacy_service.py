import re
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

class SpacyService:
    """
    Linguistic processing engine using spaCy for tokenization, sentence segmentation,
    noun chunk extraction, and named entity recognition.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        self.model_name = model_name
        self._nlp = None

    def _get_nlp(self):
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self.model_name)
                logger.info(f"spaCy model '{self.model_name}' loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load spaCy model '{self.model_name}': {e}. Using linguistic rule fallback.")
                self._nlp = "FALLBACK"
        return self._nlp

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Runs spaCy linguistic pipeline over text.
        Extracts entities, noun chunks, and key sentence structures.
        """
        nlp = self._get_nlp()
        if not text or not text.strip():
            return {"entities": [], "noun_chunks": [], "sentences": []}

        if nlp != "FALLBACK":
            doc = nlp(text)
            entities = [
                {
                    "text": ent.text.strip(),
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                }
                for ent in doc.ents
                if len(ent.text.strip()) > 1
            ]
            noun_chunks = [chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 2]
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            return {
                "entities": entities,
                "noun_chunks": list(set(noun_chunks)),
                "sentences": sentences
            }
        else:
            # Rule-based linguistic fallback
            return self._fallback_linguistic_processing(text)

    def extract_entity_candidates(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts candidate entities grouped by semantic category using spaCy entities and noun chunks.
        """
        proc = self.process_text(text)
        persons = set()
        locations = set()
        products = set()

        for ent in proc["entities"]:
            lbl = ent["label"]
            txt = ent["text"].strip()
            if lbl == "PERSON":
                persons.add(txt)
            elif lbl in ["GPE", "LOC", "FAC"]:
                locations.add(txt)
            elif lbl in ["PRODUCT", "WORK_OF_ART", "ORG"]:
                products.add(txt)

        return {
            "persons": sorted(list(persons)),
            "locations": sorted(list(locations)),
            "potential_objects": sorted(list(set(proc["noun_chunks"]) | products))
        }

    def _fallback_linguistic_processing(self, text: str) -> Dict[str, Any]:
        """Heuristic fallback for sentence and entity chunking"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 2]
        # Capitalized words as entity candidates
        capitalized = set(re.findall(r'\b[A-Z][a-z]{2,}\b', text))
        entities = [{"text": word, "label": "PROPN", "start": 0, "end": len(word)} for word in capitalized]
        # Common noun phrases
        noun_phrases = re.findall(r'\b(?:a|an|the|his|her|their)\s+([a-z]+(?:\s+[a-z]+)?)\b', text, re.IGNORECASE)
        
        return {
            "entities": entities,
            "noun_chunks": list(set(noun_phrases)),
            "sentences": sentences
        }
