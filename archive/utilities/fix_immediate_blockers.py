#!/usr/bin/env python3
"""
OpenEyes Production Hardening - Immediate Blocker Fixes

This script addresses the three immediate blockers identified in the production hardening test:

1. Fragment Schema Validation Pipeline - Add pre-flight validation for domain rules
2. Reasoning Role Annotation - Auto-classify fragments missing reasoning_role
3. Semantic Query Understanding - Improve query normalization with negation handling

Additionally fixes:
- Credibility class mapping mismatch (fragments use 'A', rules expect 'peer_reviewed_journal')
- Missing prohibit_source_type rule handler in Philosophy Guard
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


# =============================================================================
# FIX 1: CREDIBILITY CLASS MAPPING
# =============================================================================

CREDIBILITY_MAPPING_HEALTHCARE = {
    # Legacy single-letter grades
    "A": "peer_reviewed_journal",
    "B": "clinical_guideline", 
    "C": "government_agency",
    "D": "medical_association",
    "E": "public_health_organization",
    
    # Existing descriptive classes (keep as-is)
    "peer_reviewed": "peer_reviewed_journal",
    "peer_reviewed_guideline": "clinical_guideline",
    "clinical_guideline": "clinical_guideline",
    "clinical_trial": "academic_research",
    "government_agency": "government_agency",
    "regulatory_agency": "regulatory_agency",
    "medical_association": "medical_association",
    "public_health_organization": "public_health_organization",
    "hospital_system": "hospital_system",
    "academic_research": "academic_research",
    "meta_analysis": "peer_reviewed_journal",
    "review": "peer_reviewed_journal",
    
    # Finance/Economy mappings (for reference)
    "regulatory_filing": "regulatory_agency",
    "earnings_report": "company_disclosure",
    "analyst_report": "financial_institution",
}


def normalize_credibility_class(fragment: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """
    Normalize credibility class to match domain rules expectations.
    
    Args:
        fragment: Fragment dict
        domain: Domain name
        
    Returns:
        Updated fragment dict with normalized credibility_class
    """
    current_class = fragment.get("credibility_class", "")
    
    if not current_class:
        return fragment
    
    # Get domain-specific mapping
    if domain == "healthcare":
        mapping = CREDIBILITY_MAPPING_HEALTHCARE
    else:
        # Default: keep as-is
        mapping = {}
    
    normalized = mapping.get(current_class, current_class)
    
    if normalized != current_class:
        fragment["credibility_class_normalized"] = normalized
        fragment["_original_credibility_class"] = current_class
    
    return fragment


# =============================================================================
# FIX 2: REASONING ROLE AUTO-CLASSIFICATION
# =============================================================================

REASONING_ROLE_KEYWORDS = {
    "definition": [
        "defined as", "refers to", "means", "is a", "are", "definition", 
        "criteria", "diagnostic criteria", "classification", "types of",
        "what is", "understanding", "overview", "introduction"
    ],
    "mechanism": [
        "mechanism", "pathway", "how", "works by", "acts through", 
        "binding", "receptor", "enzyme", "metabolism", "pharmacokinetics"
    ],
    "evidence": [
        "study shows", "trial", "randomized", "cohort", "meta-analysis",
        "systematic review", "evidence", "data from", "results indicate",
        "found that", "observed", "significant", "p-value", "confidence interval"
    ],
    "treatment_protocol": [
        "treatment", "therapy", "dosage", "dose", "administer", "protocol",
        "first-line", "second-line", "recommended", "guideline recommends"
    ],
    "contraindication": [
        "contraindicated", "avoid", "not recommended", "warning", "caution",
        "adverse effect", "side effect", "risk", "complication"
    ],
    "counter_argument": [
        "however", "but", "although", "despite", "in contrast", "on the other hand",
        "alternative view", "controversy", "debate", "uncertainty", "limited evidence"
    ],
    "latest_data": [
        "recent", "latest", "updated", "202", "202", "current", "emerging",
        "new data", "preliminary"
    ],
    "procedural": [
        "procedure", "how to", "steps", "prepare", "during", "after", 
        "recovery", "preparation", "process"
    ]
}


def auto_classify_reasoning_role(fragment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-classify reasoning_role based on content keywords if missing.
    
    Args:
        fragment: Fragment dict
        
    Returns:
        Updated fragment dict with reasoning_role if it was missing
    """
    if fragment.get("reasoning_role"):
        return fragment
    
    content = fragment.get("content", "").lower()
    tags = [t.lower() for t in fragment.get("tags", [])]
    combined = content + " " + " ".join(tags)
    
    best_score = 0
    best_role = "definition"  # Default
    
    for role, keywords in REASONING_ROLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > best_score:
            best_score = score
            best_role = role
    
    fragment["reasoning_role"] = best_role
    fragment["_reasoning_role_auto_classified"] = True
    fragment["_reasoning_role_confidence"] = best_score
    
    return fragment


# =============================================================================
# FIX 3: SEMANTIC QUERY NORMALIZATION
# =============================================================================

NEGATION_PATTERNS = [
    (r"\b(don't|do not|does not|did not|won't|will not|would not|should not|could not|can not)\b", "NOT_"),
    (r"\b(no|without|never|neither|nor)\b", "NOT_"),
    (r"\b(against|contraindicated|avoid|exclude)\b", "NOT_"),
]

URGENCY_PATTERNS = [
    (r"\b(emergency|urgent|immediately|right now|asap|er|hospital|critical|severe)\b", "[URGENT]"),
    (r"\b(when should i|should i go|need to go|must see)\b", "[URGENT]"),
    (r"\b(worst|extreme|intense|unbearable)\b", "[SEVERE]"),
]

ENTITY_PATTERNS = [
    (r"\b(symptom|symptoms|sign|signs)\b", "[SYMPTOM]"),
    (r"\b(medication|drug|medicine|pill|tablet|prescription)\b", "[MEDICATION]"),
    (r"\b(disease|condition|disorder|syndrome|illness)\b", "[CONDITION]"),
    (r"\b(test|scan|x-ray|mri|blood test|lab)\b", "[DIAGNOSTIC]"),
    (r"\b(treatment|therapy|surgery|procedure)\b", "[TREATMENT]"),
    (r"\b(side effect|adverse effect|complication)\b", "[RISK]"),
]


def enhanced_query_normalization(query: str) -> Dict[str, Any]:
    """
    Enhanced query normalization with negation handling, urgency detection, and entity recognition.
    
    Args:
        query: Raw user query
        
    Returns:
        Dict with normalized query and metadata
    """
    result = {
        "original": query,
        "normalized": query.lower(),
        "has_negation": False,
        "negated_concepts": [],
        "urgency_level": "normal",
        "entities": [],
        "query_intent": "informational"
    }
    
    text = query.lower()
    
    # Detect and mark negations
    for pattern, marker in NEGATION_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            result["has_negation"] = True
            result["negated_concepts"].extend(matches)
            # Mark the negation in normalized form
            text = re.sub(pattern, f"{marker}\\1", text)
    
    # Detect urgency
    urgency_count = 0
    severity_count = 0
    for pattern, marker in URGENCY_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            if "[URGENT]" in marker:
                urgency_count += len(matches)
            if "[SEVERE]" in marker:
                severity_count += len(matches)
            text = re.sub(pattern, f"{marker} \\1", text)
    
    if urgency_count > 0 or severity_count > 0:
        result["urgency_level"] = "critical" if urgency_count >= 2 or severity_count > 0 else "urgent"
    
    # Extract entities
    for pattern, entity_type in ENTITY_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            result["entities"].append(entity_type.strip("[]"))
    
    # Determine query intent
    if any(w in text for w in ["how to", "prepare", "steps", "procedure"]):
        result["query_intent"] = "procedural"
    elif any(w in text for w in ["interact", "interaction", "with", "together", "combine"]):
        result["query_intent"] = "drug_interaction"
    elif result["urgency_level"] in ["urgent", "critical"]:
        result["query_intent"] = "emergency_assessment"
    elif any(w in text for w in ["best", "treatment", "therapy", "cure"]):
        result["query_intent"] = "treatment_selection"
    elif result["has_negation"]:
        result["query_intent"] = "contraindication_check"
    
    result["normalized"] = text
    
    return result


# =============================================================================
# FIX 4: ADD MISSING PHILOSOPHY GUARD RULE HANDLER
# =============================================================================

def add_prohibit_source_type_handler():
    """
    Add the missing prohibit_source_type rule handler to Philosophy Guard.
    This is done by patching the file directly.
    """
    pg_path = Path("/workspace/shared_core/philosophy_guard.py")
    
    if not pg_path.exists():
        print(f"ERROR: Philosophy Guard not found at {pg_path}")
        return False
    
    content = pg_path.read_text()
    
    # Check if handler already exists
    if "_check_prohibit_source_type" in content:
        print("✓ _check_prohibit_source_type already exists")
        return True
    
    # Find the location to insert (after _check_requires_uncertainty_note)
    insert_marker = "def _check_cognitive_simplicity"
    insert_pos = content.find(insert_marker)
    
    if insert_pos == -1:
        print("ERROR: Could not find insertion point")
        return False
    
    new_handler = '''    def _check_prohibit_source_type(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check if proposal has a prohibited source type."""
        prohibited = config.get("prohibited", [])
        source_type = proposal.get("source_type", "")
        
        # Also check source_url domain for common prohibited types
        source_url = proposal.get("source_url", "")
        
        if not prohibited:
            return {
                "passed": True,
                "message": "No source type restrictions defined"
            }
        
        if source_type in prohibited:
            return {
                "passed": False,
                "message": f"Source type '{source_type}' is prohibited",
                "severity": "error"
            }
        
        # Check for prohibited domains in URL
        prohibited_domains = {
            "anecdotal": [],
            "personal_blog": ["blogspot", "wordpress.com", "medium.com", "substack"],
            "social_media": ["twitter.com", "facebook.com", "instagram.com", "tiktok.com", "reddit.com"]
        }
        
        for ptype in prohibited:
            domains = prohibited_domains.get(ptype, [])
            for domain in domains:
                if domain in source_url.lower():
                    return {
                        "passed": False,
                        "message": f"Source URL contains prohibited domain '{domain}' ({ptype})",
                        "severity": "error"
                    }
        
        return {
            "passed": True,
            "message": "Source type is acceptable"
        }
    
'''
    
    # Insert the new handler
    new_content = content[:insert_pos] + new_handler + content[insert_pos:]
    
    # Also need to register the handler in _apply_rule
    rule_handler_marker = 'elif check_type == "requires_uncertainty_note":'
    rule_handler_pos = new_content.find(rule_handler_marker)
    
    if rule_handler_pos != -1:
        # Find end of this elif block
        next_line_pos = new_content.find("\n", rule_handler_pos)
        indent = "        "
        registration_line = f'\n{indent}elif check_type == "prohibit_source_type":\n{indent}    return self._check_prohibit_source_type(proposal, config)'
        
        # Insert after the requires_uncertainty_note line
        end_of_line = new_content.find("\n", next_line_pos)
        new_content = new_content[:end_of_line+1] + registration_line + new_content[end_of_line+1:]
    
    pg_path.write_text(new_content)
    print("✓ Added _check_prohibit_source_type handler to Philosophy Guard")
    return True


# =============================================================================
# FIX 5: FRAGMENT SCHEMA VALIDATION PIPELINE
# =============================================================================

def validate_fragment_schema(fragment: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """
    Pre-flight validation of fragment schema before domain rules check.
    
    Args:
        fragment: Fragment dict
        domain: Domain name
        
    Returns:
        Validation result with errors/warnings
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "auto_fixed": []
    }
    
    # Required fields for all domains
    required_fields = ["id", "content", "domain"]
    for field in required_fields:
        if not fragment.get(field):
            result["errors"].append(f"Missing required field: {field}")
            result["valid"] = False
    
    # Domain-specific requirements
    if domain == "healthcare":
        healthcare_required = ["source_url", "year", "credibility_class"]
        for field in healthcare_required:
            if not fragment.get(field):
                result["errors"].append(f"Healthcare fragment missing required field: {field}")
                result["valid"] = False
    
    # Check credibility class validity
    cred_class = fragment.get("credibility_class", "")
    if cred_class and domain == "healthcare":
        if cred_class not in CREDIBILITY_MAPPING_HEALTHCARE:
            result["warnings"].append(f"Unknown credibility class: {cred_class}")
    
    # Auto-fix: Add reasoning_role if missing
    if not fragment.get("reasoning_role"):
        fixed_fragment = auto_classify_reasoning_role(fragment.copy())
        if fixed_fragment.get("reasoning_role"):
            result["auto_fixed"].append("Added auto-classified reasoning_role")
            fragment["reasoning_role"] = fixed_fragment["reasoning_role"]
    
    # Auto-fix: Normalize credibility class
    if cred_class and domain == "healthcare":
        normalized = CREDIBILITY_MAPPING_HEALTHCARE.get(cred_class, cred_class)
        if normalized != cred_class:
            result["auto_fixed"].append(f"Normalized credibility_class: {cred_class} -> {normalized}")
    
    return result


# =============================================================================
# MAIN: BATCH PROCESS HEALTHCARE FRAGMENTS
# =============================================================================

def batch_fix_healthcare_fragments(dry_run: bool = True) -> Dict[str, Any]:
    """
    Batch process all healthcare fragments to fix schema issues.
    
    Args:
        dry_run: If True, only report issues without modifying files
        
    Returns:
        Summary statistics
    """
    frag_dir = Path("/workspace/openeyes/fragment_library/fragments")
    
    # Find all healthcare fragments
    patterns = ["*HC-*.json", "*health*.json", "*med*.json", "*PH-*.json", "*MH-*.json"]
    health_frags = []
    for pattern in patterns:
        health_frags.extend(frag_dir.glob(pattern))
    
    # Remove duplicates
    health_frags = list(set(health_frags))
    
    stats = {
        "total": len(health_frags),
        "missing_reasoning_role": 0,
        "credibility_mismatch": 0,
        "missing_source_url": 0,
        "missing_year": 0,
        "auto_fixed": 0,
        "files_modified": 0
    }
    
    for fp in health_frags:
        with open(fp) as f:
            fragment = json.load(f)
        
        needs_update = False
        
        # Check reasoning_role
        if not fragment.get("reasoning_role"):
            stats["missing_reasoning_role"] += 1
            fragment = auto_classify_reasoning_role(fragment)
            needs_update = True
            stats["auto_fixed"] += 1
        
        # Check credibility class
        cred_class = fragment.get("credibility_class", "")
        if cred_class in CREDIBILITY_MAPPING_HEALTHCARE:
            normalized = CREDIBILITY_MAPPING_HEALTHCARE[cred_class]
            if normalized != cred_class:
                stats["credibility_mismatch"] += 1
                fragment["credibility_class"] = normalized
                fragment["_original_credibility_class"] = cred_class
                needs_update = True
                stats["auto_fixed"] += 1
        
        # Check required fields
        if not fragment.get("source_url"):
            stats["missing_source_url"] += 1
        
        if not fragment.get("year"):
            stats["missing_year"] += 1
        
        # Write back if updated and not dry run
        if needs_update and not dry_run:
            with open(fp, "w") as f:
                json.dump(fragment, f, indent=2)
            stats["files_modified"] += 1
    
    return stats


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix OpenEyes immediate blockers")
    parser.add_argument("--dry-run", action="store_true", help="Report issues without modifying files")
    parser.add_argument("--add-pg-handler", action="store_true", help="Add prohibit_source_type handler to Philosophy Guard")
    parser.add_argument("--fix-fragments", action="store_true", help="Batch fix healthcare fragments")
    parser.add_argument("--test-query", type=str, help="Test enhanced query normalization")
    
    args = parser.parse_args()
    
    if args.add_pg_handler:
        add_prohibit_source_type_handler()
    
    if args.fix_fragments:
        print("\\n=== Batch Fixing Healthcare Fragments ===")
        stats = batch_fix_healthcare_fragments(dry_run=args.dry_run)
        print(f"Total fragments: {stats['total']}")
        print(f"Missing reasoning_role: {stats['missing_reasoning_role']}")
        print(f"Credibility class mismatch: {stats['credibility_mismatch']}")
        print(f"Missing source_url: {stats['missing_source_url']}")
        print(f"Missing year: {stats['missing_year']}")
        print(f"Auto-fixed: {stats['auto_fixed']}")
        if not args.dry_run:
            print(f"Files modified: {stats['files_modified']}")
    
    if args.test_query:
        print(f"\\n=== Testing Query: '{args.test_query}' ===")
        result = enhanced_query_normalization(args.test_query)
        print(json.dumps(result, indent=2))
    
    if not any([args.add_pg_handler, args.fix_fragments, args.test_query]):
        parser.print_help()
