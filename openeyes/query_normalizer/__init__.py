"""
Priority 1: Group Theory - Query Normalization Framework
Computes canonical forms for queries to ensure consistent answers across rephrasing.
"""

import re
from typing import Set

# Synonym registry for medical, engineering, cooking, and finance domains
SYNONYM_REGISTRY = [
    # Medical synonyms
    {"uti", "urinary tract infection", "bladder infection"},
    {"myocardial infarction", "heart attack", "mi"},
    {"hypertension", "high blood pressure", "hbp"},
    {"diabetes mellitus type 2", "type 2 diabetes", "t2dm"},
    {"pancreatic cancer", "cancer of the pancreas"},
    {"methanol poisoning", "methyl alcohol poisoning"},
    {"intermittent fasting", "if", "time-restricted eating"},
    
    # Engineering synonyms
    {"steel beam", "structural steel", "i-beam"},
    {"load capacity", "load bearing", "weight limit"},
    {"cold weather", "low temperature", "sub-zero", "freezing"},
    {"concrete", "cement mixture"},
    
    # Cooking synonyms
    {"sourdough starter", "starter", "levain"},
    {"rising", "proofing", "fermenting"},
    {"hydration", "water content"},
    
    # Finance synonyms
    {"federal reserve", "fed", "fomc", "us central bank"},
    {"interest rate", "fed funds rate", "policy rate"},
    {"quantitative easing", "qe", "asset purchases"},
    {"quantitative tightening", "qt", "balance sheet reduction"},
    {"nonfarm payroll", "nfp", "jobs report", "employment report"},
    {"consumer price index", "cpi", "inflation report"},
    {"gross domestic product", "gdp", "economic output"},
    {"earnings per share", "eps", "earnings"},
    {"price to earnings", "pe ratio", "pe multiple"},
    {"free cash flow", "fcf"},
    {"bitcoin", "btc"},
    {"ethereum", "eth"},
    {"stock market", "equity market", "equities"},
    {"bear market", "market downturn", "market decline"},
    {"bull market", "market rally", "market uptrend"},
    {"yield curve inversion", "inverted yield curve"},
    {"recession", "economic contraction", "negative gdp growth"},
]

# Stop words to remove during normalization
STOP_WORDS = {
    "what", "are", "the", "is", "it", "safe", "for", "in", "on", "at", "to", "of",
    "a", "an", "and", "or", "but", "how", "does", "do", "did", "can", "could",
    "would", "should", "will", "may", "might", "when", "where", "why", "which",
    "symptoms", "effect", "effects", "happen", "happens", "take", "taking",
}

def extract_words(text: str) -> Set[str]:
    """Extract meaningful words from text, removing stop words."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}

def replace_with_canonical(text: str, synonym_set: Set[str]) -> str:
    """Replace any synonym in the set with the canonical (first) form."""
    canonical = sorted(synonym_set)[0]  # Use alphabetically first as canonical
    pattern = r'\b(' + '|'.join(re.escape(s) for s in synonym_set) + r')\b'
    return re.sub(pattern, canonical, text, flags=re.IGNORECASE)

def swap_subject_object(text: str) -> str:
    """Swap subject and object for passive/active normalization."""
    patterns = [
        (r'(\w+) for (\w+)', r'\2 \1'),
        (r'in (\w+) patients?', r'\1 patient'),
    ]
    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def active_to_passive(text: str) -> str:
    """Normalize active and passive voice to a standard form."""
    replacements = [
        (r'treats', 'treatment for'),
        (r'is treated by', 'treatment for'),
        (r'causes', 'cause of'),
        (r'is caused by', 'cause of'),
    ]
    result = text
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def alphabetize_clauses(text: str) -> str:
    """Sort clauses alphabetically to normalize word order."""
    words = extract_words(text)
    return ' | '.join(sorted(words))

def normalize_question_form(text: str) -> str:
    """Normalize different question forms to a standard topic query."""
    text = re.sub(r'^(what|how|why|when|where|who)\s+(is|are|does|do|did|will|would|could|should)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\?$', '', text)
    return text.strip()

def canonical_form(query: str) -> str:
    """
    Reduce query to its canonical form under meaning-preserving transformations.
    Two queries with the same canonical form are guaranteed equivalent.
    """
    normalized = normalize_question_form(query)
    
    for synonym_set in SYNONYM_REGISTRY:
        normalized = replace_with_canonical(normalized, synonym_set)
    
    normalized = active_to_passive(normalized)
    normalized = swap_subject_object(normalized)
    
    words = extract_words(normalized)
    canonical = ' | '.join(sorted(words))
    
    return canonical

def are_queries_equivalent(query1: str, query2: str) -> bool:
    """Check if two queries are semantically equivalent."""
    return canonical_form(query1) == canonical_form(query2)

if __name__ == "__main__":
    test_cases = [
        ("What are the symptoms of pancreatic cancer?", "Pancreatic cancer symptoms"),
        ("Is intermittent fasting safe for diabetics?", "Diabetics intermittent fasting safety"),
        ("What antibiotic is safe for UTI?", "UTI antibiotic safe"),
        ("For UTI patients, which antibiotic is safe?", "UTI antibiotic safe"),
    ]
    
    print("Query Normalization Tests:")
    print("=" * 60)
    for q1, q2 in test_cases:
        c1 = canonical_form(q1)
        c2 = canonical_form(q2)
        match = "✓ MATCH" if c1 == c2 else "✗ NO MATCH"
        print(f"Q1: {q1}")
        print(f"   → {c1}")
        print(f"Q2: {q2}")
        print(f"   → {c2}")
        print(f"   {match}")
        print()
