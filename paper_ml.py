"""
paper_ml.py  ─  Theory Paper Upload ML Engine
==============================================
Runs 7 ML / NLP pipelines on an uploaded theory paper file.

Pipeline overview
-----------------
1. OCR Model               – extract text from PDF / scanned image
2. Document Classification – subject type & exam category
3. Duplicate Detection     – cosine similarity vs all existing papers
4. Text Similarity         – top similar papers with scores
5. Difficulty Prediction   – easy / medium / hard distribution
6. Error Detection         – formatting, grammar, structure issues
7. Keyword Extraction      – top TF-IDF keywords / topics
"""

import os
import re
import json
import math
import string
from collections import Counter

# ── Optional heavy deps (fallback-safe) ───────────────────────────────────────
try:
    import fitz  # PyMuPDF
    PYMUPDF_OK = True
except ImportError:
    PYMUPDF_OK = False

try:
    from PIL import Image
    import pytesseract
    OCR_OK = True
except ImportError:
    OCR_OK = False

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

STOPWORDS = {
    'a','an','the','is','are','was','were','be','been','being','have','has',
    'had','do','does','did','will','would','could','should','may','might',
    'can','this','that','these','those','to','of','in','on','at','for',
    'with','about','by','from','and','or','but','not','no','it','its',
    'they','them','their','we','our','you','your','i','my','me','he','she',
    'his','her','us','which','who','what','when','where','how','if','as',
    'so','than','then','there','here','each','all','any','both','few','more',
    'most','other','into','through','during','before','after','above','below',
    'between','out','off','over','under','again','further','very','just',
    'also','up','down','such','same','own','too','only','than', 'give'
}

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return [t for t in text.split() if t and t not in STOPWORDS and len(t) > 2]

def _tfidf_vectors(corpus: list[str]) -> tuple[list[dict], dict]:
    """Return TF-IDF vectors for each doc + IDF dict."""
    N = len(corpus)
    if N == 0:
        return [], {}
    tokenized = [_tokenize(doc) for doc in corpus]
    df: dict[str, int] = {}
    for tokens in tokenized:
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log((N + 1) / (freq + 1)) + 1 for t, freq in df.items()}
    vectors = []
    for tokens in tokenized:
        tf: dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        total = max(len(tokens), 1)
        vec = {t: (count / total) * idf.get(t, 1) for t, count in tf.items()}
        vectors.append(vec)
    return vectors, idf

def _cosine(v1: dict, v2: dict) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    mag1 = math.sqrt(sum(x ** 2 for x in v1.values()))
    mag2 = math.sqrt(sum(x ** 2 for x in v2.values()))
    return dot / (mag1 * mag2 + 1e-9)


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 1 – OCR / TEXT EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_text(filepath: str) -> dict:
    """
    Extract readable text from a PDF or image file.
    Returns: {text, method, page_count, char_count, success}
    """
    result = {"text": "", "method": "none", "page_count": 0,
              "char_count": 0, "success": False}
    ext = os.path.splitext(filepath)[1].lower()

    # --- PDF path: try PyMuPDF first (digital PDFs) ---
    if ext == '.pdf' and PYMUPDF_OK:
        try:
            doc = fitz.open(filepath)
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            full_text = "\n".join(pages_text).strip()
            result["page_count"] = len(doc)
            doc.close()
            if len(full_text) > 100:          # likely a digital PDF
                result.update({"text": full_text, "method": "PyMuPDF (digital PDF)",
                                "char_count": len(full_text), "success": True})
                return result
            # Scanned PDF fallback → OCR if available
        except Exception as e:
            result["error"] = str(e)

    # --- Image / scanned PDF: pytesseract ---
    if OCR_OK:
        try:
            if ext == '.pdf' and PYMUPDF_OK:
                doc = fitz.open(filepath)
                page = doc[0]
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                doc.close()
            else:
                img = Image.open(filepath)
            ocr_text = pytesseract.image_to_string(img).strip()
            result.update({"text": ocr_text, "method": "Tesseract OCR",
                           "char_count": len(ocr_text), "success": True,
                           "page_count": result["page_count"] or 1})
        except Exception as e:
            result["error"] = f"OCR failed: {e}"
    else:
        result["error"] = "No OCR/PDF library available. Install PyMuPDF or pytesseract + Pillow."

    return result


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 2 – DOCUMENT CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

_SUBJECT_KEYWORDS = {
    "Mathematics":    ["equation", "theorem", "matrix", "calculus", "algebra", "integral", "derivative", "vector", "probability", "limit", "function", "trigonometry"],
    "Computer Science": ["algorithm", "program", "software", "database", "network", "array", "loop", "class", "object", "binary", "compiler", "cpu", "memory", "java", "python", "code", "function", "recursion"],
    "Physics":        ["force", "energy", "velocity", "momentum", "electric", "magnetic", "wave", "quantum", "gravity", "acceleration", "circuit", "current", "resistance"],
    "Chemistry":      ["reaction", "atom", "molecule", "bond", "element", "compound", "acid", "base", "organic", "inorganic", "solution", "mole", "oxidation"],
    "Biology":        ["cell", "organism", "dna", "protein", "evolution", "photosynthesis", "ecosystem", "gene", "chromosome", "enzyme", "respiration", "mitosis"],
    "English":        ["grammar", "essay", "literature", "poem", "prose", "comprehension", "synonym", "antonym", "tense", "verb", "noun", "sentence"],
    "History":        ["century", "war", "kingdom", "empire", "revolution", "independence", "dynasty", "civilization", "treaty", "battle", "colonial"],
    "Economics":      ["demand", "supply", "market", "inflation", "gdp", "fiscal", "monetary", "price", "elasticity", "utility", "budget", "trade"],
}

_EXAM_TYPE_PATTERNS = {
    "Internal": ["unit test", "internal", "cia", "class test", "mid sem", "sessional"],
    "External": ["external", "board", "university", "final exam", "semester end", "annual"],
    "Midterm":  ["midterm", "mid-term", "mid term", "halftime"],
    "Final":    ["final", "end semester", "year end", "annual exam"],
}

def classify_document(text: str, filename: str = "", subject_hint: str = "") -> dict:
    """
    Classify the paper by academic subject and exam type.
    Returns: {predicted_subject, exam_type, subject_confidence, notes}
    """
    lower_text = (text + " " + filename).lower()

    # Subject scoring
    scores: dict[str, int] = {}
    for subj, keywords in _SUBJECT_KEYWORDS.items():
        scores[subj] = sum(1 for kw in keywords if kw in lower_text)

    if subject_hint and subject_hint in _SUBJECT_KEYWORDS:
        scores[subject_hint] = scores.get(subject_hint, 0) + 5

    best_subj = max(scores, key=scores.get)
    total_hits = sum(scores.values())
    subject_conf = round((scores[best_subj] / max(total_hits, 1)) * 100, 1) if total_hits else 0.0

    # Exam type detection
    predicted_exam_type = "General"
    for etype, patterns in _EXAM_TYPE_PATTERNS.items():
        if any(p in lower_text for p in patterns):
            predicted_exam_type = etype
            break

    return {
        "predicted_subject": best_subj if scores[best_subj] > 0 else (subject_hint or "General"),
        "exam_type": predicted_exam_type,
        "subject_confidence": subject_conf,
        "all_scores": {k: v for k, v in sorted(scores.items(), key=lambda x: -x[1]) if v > 0}
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 3 & 4 – DUPLICATE DETECTION + TEXT SIMILARITY
# ─────────────────────────────────────────────────────────────────────────────

def detect_duplicates_and_similarity(new_text: str, existing_papers: list[dict]) -> dict:
    """
    Compare new_text against existing_papers (list of {id, title, text}).
    Returns:
      {is_duplicate, duplicate_of_id, max_similarity,
       similar_papers: [{id, title, similarity_score}]}
    """
    if not existing_papers:
        return {"is_duplicate": False, "duplicate_of_id": None,
                "max_similarity": 0.0, "similar_papers": []}

    corpus = [new_text] + [p["text"] for p in existing_papers]
    vectors, _ = _tfidf_vectors(corpus)

    if not vectors:
        return {"is_duplicate": False, "duplicate_of_id": None,
                "max_similarity": 0.0, "similar_papers": []}

    new_vec = vectors[0]
    similarities = []
    for i, paper in enumerate(existing_papers):
        score = _cosine(new_vec, vectors[i + 1])
        similarities.append({
            "id": paper["id"],
            "title": paper.get("title", f"Paper #{paper['id']}"),
            "similarity_score": round(score * 100, 1)
        })

    similarities.sort(key=lambda x: -x["similarity_score"])
    top5 = similarities[:5]
    max_sim = top5[0]["similarity_score"] if top5 else 0.0

    IS_DUP_THRESHOLD = 85.0
    is_dup = max_sim >= IS_DUP_THRESHOLD
    dup_id = top5[0]["id"] if is_dup else None

    return {
        "is_duplicate": is_dup,
        "duplicate_of_id": dup_id,
        "max_similarity": max_sim,
        "similar_papers": top5
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 5 – DIFFICULTY PREDICTION
# ─────────────────────────────────────────────────────────────────────────────

_EASY_KW    = {"define","state","list","name","write","what","which","identify","mention","choose","select","recall","fill","true","false","match"}
_MEDIUM_KW  = {"explain","describe","compare","contrast","discuss","calculate","solve","show","draw","illustrate","find","compute","derive","classify","differentiate","summary","summarize","relate","distinguish"}
_HARD_KW    = {"analyze","analyse","evaluate","design","prove","justify","construct","develop","create","formulate","assess","critique","interpret","investigate","synthesize","debate","argue","recommend","propose"}

def predict_difficulty(text: str) -> dict:
    """
    Predict difficulty distribution of the paper.
    Returns: {easy_pct, medium_pct, hard_pct, easy_count, medium_count, hard_count, total_questions}
    """
    # Split into question-like segments
    sentences = re.split(r'(?<=[.?!])\s+|\n', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    easy = medium = hard = 0
    for sent in sentences:
        words = set(sent.lower().translate(str.maketrans('', '', string.punctuation)).split())
        h_score = len(words & _HARD_KW)
        m_score = len(words & _MEDIUM_KW)
        e_score = len(words & _EASY_KW)
        if h_score >= m_score and h_score >= e_score and h_score > 0:
            hard += 1
        elif m_score >= e_score and m_score > 0:
            medium += 1
        elif e_score > 0:
            easy += 1
        else:
            medium += 1  # default to medium if no signal

    total = easy + medium + hard
    if total == 0:
        return {"easy_pct": 33, "medium_pct": 34, "hard_pct": 33,
                "easy_count": 0, "medium_count": 0, "hard_count": 0, "total_questions": 0}

    return {
        "easy_pct": round(easy / total * 100, 1),
        "medium_pct": round(medium / total * 100, 1),
        "hard_pct": round(hard / total * 100, 1),
        "easy_count": easy,
        "medium_count": medium,
        "hard_count": hard,
        "total_questions": total
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 6 – ERROR DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def detect_errors(text: str) -> list[dict]:
    """
    Detect common formatting/structural errors in question papers.
    Returns: list of {issue, severity, detail}
    """
    errors = []
    lines = text.split('\n')

    # 1. Check total character count (too short = likely OCR failure)
    if len(text.strip()) < 200:
        errors.append({"issue": "Very short document", "severity": "High",
                        "detail": f"Only {len(text.strip())} characters extracted. OCR may have failed or paper is empty."})

    # 2. Detect missing marks annotations
    marks_pattern = re.compile(r'\[\s*\d+\s*(marks?|m|pts?)\s*\]|\(\s*\d+\s*(marks?|m|pts?)\s*\)', re.IGNORECASE)
    if not marks_pattern.search(text):
        errors.append({"issue": "No marks annotations found", "severity": "Medium",
                        "detail": "Question marks/points (e.g. [5 marks] or (2)) not detected. Ensure all questions have marks."})

    # 3. Detect repeated question numbers
    q_numbers = re.findall(r'(?:^|\n)\s*(?:Q\.?|Question)?\s*(\d+)[.)]\s', text, re.IGNORECASE)
    if q_numbers:
        seen, dups = set(), []
        for num in q_numbers:
            if num in seen:
                dups.append(num)
            seen.add(num)
        if dups:
            errors.append({"issue": "Repeated question numbers", "severity": "High",
                            "detail": f"Duplicate question number(s) detected: {', '.join(set(dups))}"})

    # 4. Detect very short (likely incomplete) questions
    short_qs = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r'^\d+[.)]\s', stripped) and len(stripped) < 20:
            short_qs.append(f"Line {i}: \"{stripped}\"")
    if short_qs:
        errors.append({"issue": "Potentially incomplete questions", "severity": "Medium",
                        "detail": f"{len(short_qs)} very short question(s) found: " + "; ".join(short_qs[:3])})

    # 5. Check for section headers
    if not re.search(r'section\s+[a-zA-Z]|part\s+[a-zA-Z IVX]+', text, re.IGNORECASE):
        errors.append({"issue": "No section headers detected", "severity": "Low",
                        "detail": "Consider adding Section A, Section B, etc. for better organization."})

    # 6. Check for total marks line
    if not re.search(r'total\s*:?\s*\d+|max(?:imum)?\s+marks?\s*:?\s*\d+|time\s*:', text, re.IGNORECASE):
        errors.append({"issue": "Total marks / Time limit missing", "severity": "Medium",
                        "detail": "No 'Total Marks' or 'Time' header found at the top of the paper."})

    if not errors:
        errors.append({"issue": "No errors detected", "severity": "None",
                        "detail": "The question paper passed all automated checks successfully. ✓"})

    return errors


# ─────────────────────────────────────────────────────────────────────────────
# MODEL 7 – NLP KEYWORD EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_keywords(text: str, top_n: int = 15) -> list[str]:
    """
    Extract top_n subject-relevant keywords using TF-IDF scoring.
    Returns: list of keyword strings
    """
    tokens = _tokenize(text)
    if not tokens:
        return []
    tf: dict[str, int] = Counter(tokens)
    total = len(tokens)
    # Single-doc IDF approximation: reward rare-in-sentence, penalise super-common
    doc_tokens = set(tokens)
    keywords = sorted(tf.keys(), key=lambda t: tf[t] / total, reverse=True)
    # Prefer longer, meaningful terms
    keywords = sorted(keywords, key=lambda t: (tf[t], len(t)), reverse=True)
    return keywords[:top_n]


# ─────────────────────────────────────────────────────────────────────────────
# MASTER ANALYSIS FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def analyze_paper(filepath: str, existing_papers: list[dict],
                  subject_hint: str = "") -> dict:
    """
    Run all 7 ML models on the uploaded paper file.

    Args:
        filepath        : absolute path to saved file
        existing_papers : list of {'id', 'title', 'text'} dicts from DB
        subject_hint    : subject name selected by teacher (optional)

    Returns:
        Full analysis dict with keys: ocr, classification, similarity,
        difficulty, errors, keywords, success
    """
    result: dict = {"success": False, "error": None}

    # Model 1 — OCR
    ocr = extract_text(filepath)
    result["ocr"] = ocr
    text = ocr.get("text", "")

    if not text.strip():
        result["error"] = "Could not extract text from the uploaded file."
        result["ocr"]["success"] = False
        # Still run other models with empty text (they'll give graceful defaults)

    # Model 2 — Classification
    result["classification"] = classify_document(text, os.path.basename(filepath), subject_hint)

    # Model 3 & 4 — Duplicate Detection + Similarity
    result["similarity"] = detect_duplicates_and_similarity(text, existing_papers)

    # Model 5 — Difficulty
    result["difficulty"] = predict_difficulty(text)

    # Model 6 — Error Detection
    result["errors"] = detect_errors(text)

    # Model 7 — Keyword Extraction
    result["keywords"] = extract_keywords(text)

    result["success"] = True
    return result
