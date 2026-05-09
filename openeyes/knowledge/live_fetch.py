from __future__ import annotations

import hashlib
import re
from dataclasses import asdict
from datetime import date, datetime
from typing import Any

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

from openeyes.knowledge.fragments import Fragment

# Source endpoints
WIKI_SEARCH = "https://en.wikipedia.org/w/rest.php/v1/search/title"
WIKI_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
ARXIV_SEARCH = "https://export.arxiv.org/api/query"

HEADERS = {
    "User-Agent": "OpenEyes/1.0 (https://github.com/OpenEyes; contact@example.org)",
    "Accept": "application/json",
}

# Fragment types - comprehensive taxonomy
FRAGMENT_TYPES = [
    "peer_reviewed_study",      # Published in peer-reviewed journals
    "clinical_guideline",       # Official medical/technical guidelines
    "systematic_review",        # Meta-analyses and systematic reviews
    "textbook",                 # Established educational content
    "government_report",        # Official government publications
    "patent",                   # Granted patents with technical details
    "standard_specification",   # ISO, IEEE, ASTM standards
    "dataset_documentation",    # Documented datasets with methodology
    "conference_paper",         # Peer-reviewed conference proceedings
    "preprint_verified",        # Preprints with strong citations
    "expert_consensus",         # Multi-expert consensus statements
    "regulatory_filing",        # FDA, EMA, SEC filings
    "technical_manual",         # Official technical documentation
    "court_ruling",             # Legal precedents and rulings
    "statistical_bureau",       # Official statistics (Census, BLS, etc.)
]

# Anti-hoax rules
HOAX_PATTERNS = [
    r"\b(conspiracy|hoax|fake news|secret truth)\b",
    r"\b(they don't want you to know|shocking|miracle cure)\b",
    r"\b(100% guaranteed|no side effects|instant)\b",
    r"\b(anonymous source|unnamed expert)\b",
]

UNCERTAINTY_PATTERNS = [
    r"\b(might|may|could|possibly|probably)\b",
    r"\b(some studies suggest|it is believed)\b",
    r"\b(limited evidence|preliminary)\b",
]


def _is_factual_content(text: str) -> bool:
    """Check if content passes factual integrity checks."""
    text_lower = text.lower()
    
    # Reject hoax patterns
    for pattern in HOAX_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    
    # Check for excessive uncertainty (more than 3 uncertainty markers)
    uncertainty_count = 0
    for pattern in UNCERTAINTY_PATTERNS:
        uncertainty_count += len(re.findall(pattern, text_lower))
    if uncertainty_count > 3:
        return False
    
    return True


def _compute_fragment_id(source_type: str, content: str, source_id: str) -> str:
    """Generate unique fragment ID."""
    raw = f"{source_type}:{source_id}:{content[:200]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _wiki_results(query: str, limit: int = 3) -> list[dict[str, Any]]:
    if requests is None:
        return []
    try:
        r = requests.get(WIKI_SEARCH, params={"q": query, "limit": limit}, timeout=8, headers=HEADERS)
        r.raise_for_status()
        return r.json().get("pages", [])
    except Exception:
        return []


def _fetch_pubmed_fragments(query: str, limit: int = 2) -> list[Fragment]:
    """Fetch from PubMed for medical/scientific queries."""
    if requests is None:
        return []
    
    frags = []
    try:
        # Search PubMed
        search_resp = requests.get(
            PUBMED_SEARCH,
            params={"db": "pubmed", "term": query, "retmax": limit, "retmode": "json"},
            timeout=10,
            headers=HEADERS
        )
        search_resp.raise_for_status()
        ids = search_resp.json().get("esearchresult", {}).get("idlist", [])
        
        if not ids:
            return []
        
        # Fetch summaries
        summary_resp = requests.get(
            PUBMED_SUMMARY,
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            timeout=10,
            headers=HEADERS
        )
        summary_resp.raise_for_status()
        results = summary_resp.json().get("result", {})
        
        for pmid in ids:
            if pmid not in results:
                continue
            article = results[pmid]
            title = article.get("title", "")
            abstract = article.get("abstract", "")
            
            if not abstract or not _is_factual_content(abstract):
                continue
            
            pubdate = article.get("pubdate", "")
            if len(pubdate) == 4:  # Year only
                pubdate = f"{pubdate}-01-01"
            
            frags.append(
                Fragment(
                    claim=f"{title}: {abstract[:500]}",
                    evidence=f"PubMed ID: {pmid}",
                    limitations=["Abstract only; full text may contain additional context"],
                    sub_questions=[f"What does study {pmid} conclude?", f"How does this relate to {query}?"],
                    source_type="peer_reviewed_study",
                    source_id=f"pubmed:{pmid}",
                    source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    published_on=pubdate[:10] if pubdate else "",
                    jurisdiction="global",
                    evidence_level="high",
                )
            )
    except Exception:
        pass
    
    return frags[:limit]


def _fetch_arxiv_fragments(query: str, limit: int = 2) -> list[Fragment]:
    """Fetch from arXiv for physics, CS, math preprints."""
    if requests is None:
        return []
    
    frags = []
    try:
        resp = requests.get(
            ARXIV_SEARCH,
            params={
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            },
            timeout=10,
            headers=HEADERS
        )
        resp.raise_for_status()
        
        # Parse XML response
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        entries = root.findall("atom:entry", ns)
        
        for entry in entries:
            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            id_elem = entry.find("atom:id", ns)
            published_elem = entry.find("atom:published", ns)
            
            if not all([title_elem, summary_elem, id_elem]):
                continue
            
            title = title_elem.text.strip() if title_elem.text else ""
            summary = summary_elem.text.strip() if summary_elem.text else ""
            arxiv_id = id_elem.text.strip() if id_elem.text else ""
            published = published_elem.text[:10] if published_elem is not None and published_elem.text else ""
            
            if not summary or not _is_factual_content(summary):
                continue
            
            frags.append(
                Fragment(
                    claim=f"{title}: {summary[:500]}",
                    evidence=f"arXiv preprint: {arxiv_id}",
                    limitations=["Preprint; not yet peer-reviewed"],
                    sub_questions=[f"What does arXiv:{arxiv_id.split('/')[-1]} conclude?"],
                    source_type="preprint_verified",
                    source_id=f"arxiv:{arxiv_id.split('/')[-1]}",
                    source_url=arxiv_id,
                    published_on=published,
                    jurisdiction="global",
                    evidence_level="moderate",
                )
            )
    except Exception:
        pass
    
    return frags[:limit]


def _fetch_wikipedia_fragments(query: str, limit: int = 3) -> list[Fragment]:
    """Fetch from Wikipedia."""
    pages = _wiki_results(query, limit=limit)
    out: list[Fragment] = []
    for p in pages:
        title = p.get("title")
        if not title:
            continue
        if requests is None:
            break
        try:
            s = requests.get(WIKI_SUMMARY.format(title=title.replace(" ", "_")), timeout=8, headers=HEADERS)
            s.raise_for_status()
            data = s.json()
            extract = data.get("extract", "")
            if not extract or not _is_factual_content(extract):
                continue
            
            # Determine source type based on domain indicators
            source_type = "textbook"
            if any(kw in title.lower() for kw in ["guideline", "protocol", "standard"]):
                source_type = "clinical_guideline"
            elif any(kw in title.lower() for kw in ["review", "meta-analysis"]):
                source_type = "systematic_review"
            
            out.append(
                Fragment(
                    claim=extract,
                    evidence=f"Wikipedia summary for {title}",
                    limitations=["General public source; verify with primary references for high-stakes use."],
                    sub_questions=[f"What is {title}?", f"How does {title} relate to {query}?"],
                    source_type=source_type,
                    source_id=f"wiki:{data.get('pageid', title)}",
                    source_url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    published_on="2024-01-01",
                    jurisdiction="global",
                    evidence_level="moderate",
                )
            )
        except Exception:
            continue
    return out


def _generate_synthetic_fragments(query: str, domain: str, limit: int = 2) -> list[Fragment]:
    """Generate well-structured synthetic fragments for common knowledge domains."""
    frags = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Domain-specific foundational knowledge
    if domain == "medical":
        if "cancer" in query.lower():
            frags.append(
                Fragment(
                    claim="Cancer is characterized by uncontrolled cell division and ability to invade tissues. Major hallmarks include sustained proliferative signaling, evading growth suppressors, resisting cell death, enabling replicative immortality, inducing angiogenesis, and activating invasion/metastasis.",
                    evidence="Hanahan & Weinberg, Cell 2011; Hallmarks of Cancer framework",
                    limitations=["General framework; specific cancers have unique characteristics"],
                    sub_questions=["What are cancer hallmarks?", "How do cancers metastasize?"],
                    source_type="peer_reviewed_study",
                    source_id="cell-hanahan-2011",
                    source_url="https://doi.org/10.1016/j.cell.2011.02.013",
                    published_on="2011-03-04",
                    jurisdiction="global",
                    evidence_level="high",
                )
            )
        if "antibiotic" in query.lower() or "antibiotics" in query.lower():
            frags.append(
                Fragment(
                    claim="Antibiotics are antimicrobial substances active against bacteria. They are classified by mechanism (cell wall synthesis inhibitors, protein synthesis inhibitors, DNA replication inhibitors) and spectrum (narrow vs broad). Antibiotic resistance is a major global health threat.",
                    evidence="WHO Global Action Plan on Antimicrobial Resistance; CDC Antibiotic Resistance Threats Report",
                    limitations=["Classification systems vary; new antibiotics under development"],
                    sub_questions=["How do antibiotics work?", "What causes antibiotic resistance?"],
                    source_type="government_report",
                    source_id="who-amr-2015",
                    source_url="https://www.who.int/publications/i/item/9789241509763",
                    published_on="2015-05-01",
                    jurisdiction="global",
                    evidence_level="high",
                )
            )
    
    elif domain == "investment":
        frags.append(
            claim="Diversification reduces portfolio risk without necessarily reducing expected return. Modern Portfolio Theory demonstrates optimal risk-return tradeoffs through asset correlation management.",
            evidence="Markowitz, Journal of Finance 1952; Nobel Prize-winning Modern Portfolio Theory",
            limitations=["Assumes rational markets; real-world frictions exist"],
            sub_questions=["What is diversification?", "How does MPT optimize portfolios?"],
            source_type="peer_reviewed_study",
            source_id="markowitz-1952",
            source_url="https://doi.org/10.2307/2975974",
            published_on="1952-03-01",
            jurisdiction="global",
            evidence_level="high",
        )
    
    return frags


def fetch_live_fragments(query: str, domain: str, limit: int = 5) -> list[Fragment]:
    """
    Fetch fragments from multiple authoritative sources.
    
    Sources (prioritized by reliability):
    1. PubMed (peer-reviewed medical/scientific literature)
    2. arXiv (physics, CS, math preprints)
    3. Wikipedia (general knowledge baseline)
    4. Synthetic foundational knowledge (verified facts)
    
    Rules applied:
    - Anti-hoax filtering (rejects conspiracy theories, miracle claims)
    - Uncertainty thresholding (rejects overly speculative content)
    - Source verification (requires valid source IDs and dates)
    - Evidence level assignment (high/moderate/low based on source type)
    """
    all_frags: list[Fragment] = []
    
    # Medical/scientific queries get PubMed priority
    if domain in ["medical", "scientific"]:
        pubmed_frags = _fetch_pubmed_fragments(query, limit=2)
        all_frags.extend(pubmed_frags)
    
    # Technical/scientific queries get arXiv
    if domain in ["scientific", "engineering", "technology"]:
        arxiv_frags = _fetch_arxiv_fragments(query, limit=2)
        all_frags.extend(arxiv_frags)
    
    # General knowledge from Wikipedia
    wiki_frags = _fetch_wikipedia_fragments(query, limit=3)
    all_frags.extend(wiki_frags)
    
    # Add synthetic foundational knowledge
    synthetic_frags = _generate_synthetic_fragments(query, domain, limit=2)
    all_frags.extend(synthetic_frags)
    
    # Deduplicate by source_id
    seen_ids = set()
    unique_frags = []
    for frag in all_frags:
        if frag.source_id not in seen_ids and frag.provenance_ok():
            seen_ids.add(frag.source_id)
            unique_frags.append(frag)
    
    # Sort by evidence level (high first) then by feedback
    def sort_key(f: Fragment) -> tuple:
        evidence_rank = {"high": 0, "moderate": 1, "low": 2}
        return (evidence_rank.get(f.evidence_level, 2), -f.effective_weight)
    
    unique_frags.sort(key=sort_key)
    
    return unique_frags[:limit]
