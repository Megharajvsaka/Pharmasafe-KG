"""
utils.py
--------
Shared utility functions used across all PharmaSafe-KG pipeline scripts.
Handles: logging, text normalization, progress display, report writing.
"""

import re
import logging
import sys
from pathlib import Path
from datetime import datetime

from config import LOGS_DIR


# ── Logger setup ──────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes to both the terminal AND a dated log file.
    Call this at the top of every script:
        log = get_logger(__name__)
    """
    log_file = LOGS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Terminal handler — INFO level and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S"
    ))

    # File handler — DEBUG level (captures everything)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s"
    ))

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


# ── Text normalisation ────────────────────────────────────────────────────────
def normalize_name(text: str) -> str:
    """
    Lowercase, strip extra whitespace, remove common salt/form suffixes.
    Used before fuzzy matching to improve accuracy.

    Examples:
        "Ibuprofen (400mg)"  →  "ibuprofen"
        "Aspirin sodium 75mg Tablet"  →  "aspirin sodium"
        "PARACETAMOL  "  →  "paracetamol"
    """
    if not isinstance(text, str):
        return ""

    name = text.lower().strip()

    # Remove dosage patterns: (400mg), 400mg, 400 mg, 0.5%, etc.
    name = re.sub(r'\(?\d+\.?\d*\s*(mg|mcg|g|ml|iu|%|units?|mmol).*?\)?', '', name, flags=re.IGNORECASE)

    # Remove route/form words
    form_words = [
        r'\btablet\b', r'\btab\b', r'\bcapsule\b', r'\bcap\b', r'\bsyrup\b',
        r'\binjection\b', r'\binj\b', r'\bdrop\b', r'\bsolution\b', r'\bcream\b',
        r'\bointment\b', r'\bgel\b', r'\bsuspension\b', r'\bpowder\b',
        r'\binfusion\b', r'\bpatch\b', r'\binhaler\b', r'\bspray\b',
    ]
    for word in form_words:
        name = re.sub(word, '', name, flags=re.IGNORECASE)

    # Remove parentheses, brackets
    name = re.sub(r'[\(\)\[\]\{\}]', ' ', name)

    # Remove trailing qualifiers like "as", "hcl", "sodium", "hydrochloride", etc.
    qualifier_suffixes = [
        r'\bas\s+\w+$', r'\bhydrochloride$', r'\bsodium$', r'\bpotassium$',
        r'\bcalcium$', r'\bmaleate$', r'\btartrate$', r'\bphosphate$',
        r'\bsuccinate$', r'\besters?$', r'\bsalt$',
    ]
    for q in qualifier_suffixes:
        name = re.sub(q, '', name, flags=re.IGNORECASE)

    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()

    return name


def extract_generics_from_composition(composition: str) -> list[str]:
    """
    Parses the composition column from the Indian medicine dataset.

    Handles multiple formats:
        "Ibuprofen (400mg) + Paracetamol (325mg)"
        "Amoxicillin 500mg"
        "Metformin Hydrochloride 500 mg | Glibenclamide 5 mg"
        "Atorvastatin (10mg)"

    Returns a list of cleaned generic names:
        ["ibuprofen", "paracetamol"]
    """
    if not isinstance(composition, str) or not composition.strip():
        return []

    # Split on common delimiters: +, |, /
    parts = re.split(r'[+|/]', composition)

    generics = []
    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Strategy 1: text before the first opening parenthesis
        match = re.match(r'^([A-Za-z][A-Za-z\s\-]+?)(?:\s*\(|\s*\d)', part)
        if match:
            candidate = normalize_name(match.group(1))
        else:
            # Strategy 2: just normalize the whole part
            candidate = normalize_name(part)

        # Filter out noise: must be at least 3 chars and contain a letter
        if len(candidate) >= 3 and re.search(r'[a-z]', candidate):
            generics.append(candidate)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for g in generics:
        if g not in seen:
            seen.add(g)
            unique.append(g)

    return unique


def clean_severity(raw: str) -> str:
    """
    Normalises DrugBank severity strings.
    'Major' → 'MAJOR', '' → 'UNKNOWN', etc.
    """
    from config import SEVERITY_MAP
    if not isinstance(raw, str):
        return "UNKNOWN"
    return SEVERITY_MAP.get(raw.strip().lower(), "UNKNOWN")


def write_report(lines: list[str], path: Path) -> None:
    """Writes a plain-text pipeline report to disk."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"PharmaSafe-KG Pipeline Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write("\n".join(lines))
    print(f"\n  Report saved → {path}")


def print_section(title: str) -> None:
    """Prints a visible section header to the terminal."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def count_chars(text: str) -> int:
    """Returns character count including spaces — useful for VTU portal validation."""
    return len(text) if isinstance(text, str) else 0
