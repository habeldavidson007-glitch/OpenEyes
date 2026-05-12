"""
Domain Rules Loader — Five-Tier Brain-Inspired Architecture

Inspired by human cognitive processing:
- Sensory Memory → Working Memory → Long-Term Memory → Retrieval
- Attention filtering at each stage (latent inhibition for genius-mode)
- Neural efficiency optimization (parallel processing, pattern recognition)

Five tiers of scrutiny:
- Tier 0 (Critical): Life-or-death decisions — Maximum HALT, Multiple verification required
- Tier 1 (High Stakes): Medical, Law, Nuclear, Aviation — Strict HALT, Primary sources only
- Tier 2 (Medium Stakes): Engineering, Finance, History — Moderate HALT, Mix of sources
- Tier 3 (Low Stakes): Cooking, Travel, Trivia — Low HALT, allows tertiary sources
- Tier 4 (Exploratory): Creative, Hypothetical, Brainstorming — No HALT, Divergent thinking

Each domain maps to a tier and has specific rule configurations.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


# Domain to Tier mapping (5-tier system)
DOMAIN_TIERS = {
    # Tier 0: Critical Stakes - Immediate life-or-death, requires multiple independent verifications
    "emergency_medical": "tier0",
    "crisis_response": "tier0",
    "nuclear_safety": "tier0",
    "aviation_safety": "tier0",
    
    # Tier 1: High Stakes - Strict HALT, Primary sources only
    "healthcare": "tier1",
    "governance": "tier1",
    "medical": "tier1",  # Legacy alias for healthcare
    "law": "tier1", 
    "legal": "tier1",
    "nuclear": "tier1",
    "aviation": "tier1",
    "pharmaceutical": "tier1",
    "clinical_psychology": "tier1",
    
    # Tier 2: Medium Stakes - Moderate HALT, Mix of Primary/Secondary
    "engineering": "tier2",
    "economy": "tier2",
    "finance": "tier2",  # Legacy alias for economy
    "economics": "tier2",  # Legacy alias for economy
    "history": "tier2",
    "technology": "tier2",
    "science": "tier2",
    "business": "tier2",
    "education": "tier2",
    "environmental": "tier2",
    
    # Tier 3: Low Stakes - Low HALT, allows Wikipedia/Blogs (labeled "Unverified")
    "cooking": "tier3",
    "travel": "tier3",
    "trivia": "tier3",
    "entertainment": "tier3",
    "lifestyle": "tier3",
    "hobbies": "tier3",
    "sports": "tier3",
    "fashion": "tier3",
    
    # Tier 4: Exploratory - No HALT, Encourages divergent thinking
    "creative": "tier4",
    "philosophy": "tier4",
    "art": "tier4",
    "literature": "tier4",
    "hypothetical": "tier4",
    "brainstorming": "tier4",
    "speculative": "tier4"
}


# Domain-Specific Credibility Hierarchies
# Maps source_type to base_score per domain, aligned with real-world epistemology
# Higher scores = more credible sources for that domain
CREDIBILITY_HIERARCHIES = {
    # Tier 1: Healthcare - Strict hierarchy, peer-reviewed evidence paramount
    "healthcare": {
        "clinical_guideline": 98,      # Highest: Official clinical guidelines (CDC, WHO, NIH)
        "peer_reviewed_study": 95,     # Peer-reviewed research studies
        "systematic_review": 93,       # Systematic reviews/meta-analyses
        "textbook": 85,                # Medical textbooks
        "government_source": 85,       # Government health agencies
        "expert_consensus": 80,        # Expert panel consensus
        "case_report": 60,             # Individual case reports (lower evidence)
        "news_article": 50,            # Medical news (secondary reporting)
        "forum": 25,                   # Patient forums (anecdotal)
        "anecdotal": 20                # Personal anecdotes
    },
    
    # Legacy alias for healthcare
    "medical": {
        "clinical_guideline": 98,
        "peer_reviewed_study": 95,
        "systematic_review": 93,
        "textbook": 85,
        "government_source": 85,
        "expert_consensus": 80,
        "case_report": 60,
        "news_article": 50,
        "forum": 25,
        "anecdotal": 20
    },
    
    # Tier 1: Legal - Primary authority is everything
    "legal": {
        "statute": 98,                 # Primary: Statutes and regulations
        "case_law": 95,                # Court decisions (precedent)
        "legal_code": 95,              # Codified law (USC, CFR, etc.)
        "government_source": 90,       # Official government legal resources
        "law_review": 75,              # Academic law review articles
        "legal_textbook": 70,          # Legal treatises and textbooks
        "legal_blog": 45,              # Legal commentary blogs
        "news_article": 40,            # Legal news reporting
        "forum": 20                    # Legal forums (low reliability)
    },
    
    # Tier 2: Engineering - Standards and codes are king
    "engineering": {
        "iso_standard": 98,            # ISO standards
        "astm_standard": 98,           # ASTM standards
        "ieee_standard": 98,           # IEEE standards
        "asme_standard": 98,           # ASME standards
        "code": 95,                    # Building/engineering codes
        "manufacturer_data": 85,       # Manufacturer specifications
        "handbook": 80,                # Engineering handbooks (CRC, Marks')
        "peer_reviewed_study": 75,     # Academic research
        "technical_paper": 70,         # Conference papers
        "textbook": 70,                # Engineering textbooks
        "expert_blog": 50,             # Expert practitioner blogs
        "forum": 30                    # Engineering forums (StackExchange, etc.)
    },
    
    # Tier 2: Finance/Economy - Regulatory and primary market data
    "economy": {
        "sec_filing": 98,              # SEC filings (10-K, 10-Q, etc.)
        "regulatory_guidance": 95,     # SEC, FINRA, Fed guidance
        "primary_market_data": 90,     # Direct market data (Bloomberg, Reuters)
        "central_bank_report": 90,     # Federal Reserve, ECB reports
        "audited_statement": 88,       # Audited financial statements
        "energy_agency_report": 88,    # EIA, IEA energy reports
        "commodity_exchange_data": 88, # CME, LME commodity data
        "analyst_report": 70,          # Professional analyst reports
        "financial_news": 55,          # Financial news (WSJ, FT)
        "investment_blog": 40,         # Investment blogs
        "forum": 25                    # Investment forums (Reddit, etc.)
    },
    
    # Tier 2: Finance (Legacy alias for Economy)
    "finance": {
        "sec_filing": 98,
        "regulatory_guidance": 95,
        "primary_market_data": 90,
        "central_bank_report": 90,
        "audited_statement": 88,
        "analyst_report": 70,
        "financial_news": 55,
        "investment_blog": 40,
        "forum": 25
    },
    
    # Tier 3: Cooking - Established institutions > experts > community
    "cooking": {
        "culinary_institution": 95,    # CIA, Le Cordon Bleu, King Arthur Flour
        "established_cookbook": 90,    # Published cookbooks from known authors
        "government_guideline": 85,    # FDA food safety guidelines
        "expert_chef_blog": 75,        # Known chef blogs (Serious Eats, etc.)
        "food_magazine": 70,           # Bon Appétit, Food & Wine, etc.
        "recipe_website": 60,          # AllRecipes, Epicurious, etc.
        "food_blog": 50,               # Personal food blogs
        "forum": 35,                   # Recipe forums, Reddit r/cooking
        "social_media": 25             # Instagram, TikTok recipes
    },
    
    # Tier 3: Travel - Official sources + established guides
    "travel": {
        "government_travel_advisory": 95,  # State Department, CDC travel notices
        "official_tourism_board": 90,      # Official country/city tourism sites
        "established_guidebook": 85,       # Lonely Planet, Fodor's, Rick Steves
        "travel_magazine": 70,             # Condé Nast Traveler, Travel + Leisure
        "expert_travel_blog": 65,          # Well-established travel bloggers
        "review_site": 55,                 # TripAdvisor, Yelp reviews
        "personal_blog": 40,               # Personal travel blogs
        "forum": 35,                       # Travel forums
        "social_media": 25                 # Instagram travel posts
    },
    
    # Tier 2: Technology - Standards + vendor docs + community
    "technology": {
        "rfc_standard": 98,            # RFCs, W3C standards
        "vendor_documentation": 90,    # Official vendor docs (Microsoft, AWS, etc.)
        "iso_standard": 95,            # ISO/IEC standards
        "peer_reviewed_study": 80,     # Academic CS research
        "technical_book": 75,          # O'Reilly, No Starch Press books
        "official_blog": 70,           # Official company engineering blogs
        "community_wiki": 65,          # Stack Overflow, official wikis
        "tech_news": 55,               # Ars Technica, Wired, etc.
        "personal_blog": 45,           # Developer blogs
        "forum": 35                    # Reddit, Discord, etc.
    },
    
    # Tier 2: Science - Peer review is essential
    "science": {
        "peer_reviewed_study": 95,     # Primary research in reputable journals
        "meta_analysis": 93,           # Meta-analyses and systematic reviews
        "government_report": 90,       # NASA, NOAA, NSF reports
        "academic_textbook": 85,       # University-level textbooks
        "preprint": 70,                # arXiv, bioRxiv (not yet peer-reviewed)
        "science_magazine": 65,        # Scientific American, New Scientist
        "science_news": 55,            # Popular science reporting
        "blog": 35,                    # Science blogs
        "forum": 25                    # Science forums
    },
    
    # Tier 4: Creative/Philosophy - More open, diversity valued
    "creative": {
        "published_work": 90,          # Published books, albums, films
        "established_artist": 80,      # Work by recognized artists
        "academic_analysis": 75,       # Scholarly criticism
        "expert_commentary": 65,       # Expert reviews and analysis
        "established_publication": 60, # Major publications
        "independent_creator": 50,     # Independent artists/creators
        "blog": 40,                    # Creative blogs
        "forum": 30,                   # Creative communities
        "social_media": 25             # Social media content
    },
    
    # Default hierarchy for unmapped domains (uses tier2 as baseline)
    "default": {
        "primary": 85,
        "secondary": 65,
        "tertiary": 45,
        "peer_reviewed_study": 90,
        "government_source": 85,
        "textbook": 75,
        "news_article": 55,
        "blog": 40,
        "forum": 30,
        "anecdotal": 20
    }
}


# Embedded domain rules (fallback if JSON files not found)
EMBEDDED_RULES = {
    "healthcare": {
        "domain": "healthcare",
        "tier": "tier1",
        "version": "1.0",
        "rules": [
            {"id": "HC-001", "name": "Do No Harm", "description": "No fragment may recommend a treatment with a known fatal interaction", "check_type": "blacklist_tag_conflict", "config": {"flag": "fatal_interaction"}, "halt_on_failure": True},
            {"id": "HC-002", "name": "Evidence-Based Only", "description": "All treatment fragments must have primary source credibility", "check_type": "minimum_source_type", "config": {"allowed": ["primary"]}, "halt_on_failure": True},
            {"id": "HC-003", "name": "Cite Source", "description": "Every fragment must carry a source URL", "check_type": "requires_field", "config": {"field": "source_url"}, "halt_on_failure": True}
        ]
    },
    "governance": {
        "domain": "governance",
        "tier": "tier1",
        "version": "0.1",
        "rules": [
            {"id": "GOV-001", "name": "Require Source URL", "description": "Every governance fragment must have a source_url", "check_type": "requires_field", "config": {"field": "source_url"}, "halt_on_failure": True},
            {"id": "GOV-002", "name": "Require Year", "description": "Every governance fragment must have a year", "check_type": "requires_field", "config": {"field": "year"}, "halt_on_failure": True},
            {"id": "GOV-003", "name": "Descriptive Only", "description": "Governance answers must describe what is - not advocate for what should be", "check_type": "opinion_language_check", "config": {"forbidden_phrases": ["should be abolished", "must be reformed"]}, "halt_on_failure": False},
            {"id": "GOV-004", "name": "No Electoral Recommendations", "description": "OpenEyes never recommends voting for or against any candidate or party", "check_type": "blacklist_tag_conflict", "config": {"forbidden_tags": ["vote_recommendation", "candidate_endorsement"]}, "halt_on_failure": True},
            {"id": "GOV-006", "name": "Minimum Source Quality", "description": "Governance answers require government_source or peer_reviewed_study credibility", "check_type": "minimum_source_type", "config": {"allowed": ["government_source", "peer_reviewed_study", "primary"]}, "halt_on_failure": True}
        ]
    },
    "legal": {
        "domain": "legal",
        "tier": "tier1",
        "version": "0.2",
        "rules": [
            {"id": "LEG-001", "name": "Jurisdiction Consistency", "description": "All fragments must reference the same jurisdiction", "check_type": "consistent_metadata", "config": {"field": "jurisdiction"}, "halt_on_failure": True},
            {"id": "LEG-002", "name": "Primary Authority Required", "description": "Legal claims must cite statutes, regulations, or case law", "check_type": "minimum_source_type", "config": {"allowed": ["primary"]}, "halt_on_failure": True}
        ]
    },
    "economy": {
        "domain": "economy",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {"id": "ECO-001", "name": "Source Required", "description": "All economic claims must have source attribution", "check_type": "requires_field", "config": {"field": "source"}, "halt_on_failure": False}
        ]
    },
    "engineering": {
        "domain": "engineering",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {"id": "ENG-001", "name": "Safety Standards Compliance", "description": "Must reference applicable safety standards", "check_type": "requires_standard_reference", "config": {"standards": ["ISO", "ASTM", "IEEE"]}, "halt_on_failure": True}
        ]
    },
    "cooking": {
        "domain": "cooking",
        "tier": "tier3",
        "version": "0.2",
        "rules": [
            {"id": "COOK-001", "name": "Allergy Warning", "description": "Must flag common allergens if present", "check_type": "flag_allergens", "config": {"allergens": ["nuts", "dairy", "eggs"]}, "halt_on_failure": False}
        ]
    },
    "technology": {
        "domain": "technology",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {"id": "TECH-001", "name": "Version Specificity", "description": "Technical information must specify versions", "check_type": "requires_field", "config": {"field": "version"}, "halt_on_failure": False}
        ]
    },
    "creative": {
        "domain": "creative",
        "tier": "tier4",
        "version": "0.2",
        "rules": [
            {"id": "CREATE-001", "name": "Divergent Thinking Encouraged", "description": "Multiple perspectives welcomed", "check_type": "prefer_reasoning_diversity", "config": {"min_roles": 1}, "halt_on_failure": False}
        ]
    },
    "general": {
        "domain": "general",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {"id": "GEN-001", "name": "Source Required", "description": "All claims must have some source attribution", "check_type": "requires_field", "config": {"field": "source"}, "halt_on_failure": False}
        ]
    }
}


class DomainRulesLoader:
    """
    Loads and caches domain-specific rules for the Philosophy Guard.
    
    Supports both file-based rules (openeyes/domain_rules/{domain}.json)
    and embedded fallback rules.
    """
    
    def __init__(self, rules_dir: str = "openeyes/domain_rules"):
        self.rules_dir = Path(rules_dir)
        self._cache: Dict[str, Dict] = {}
    
    def get_domain_tier(self, domain: str) -> str:
        """Get the tier for a domain."""
        return DOMAIN_TIERS.get(domain.lower(), "tier2")
    
    def load_rules(self, domain: str) -> Dict[str, Any]:
        """
        Load rules for a domain.
        
        Returns dict with:
        - domain: domain name
        - tier: tier1/tier2/tier3
        - version: rules version
        - rules: list of rule dicts
        """
        domain_lower = domain.lower()
        
        # Check cache first
        if domain_lower in self._cache:
            return self._cache[domain_lower]
        
        # Try to load from file (check both root and subdirectories)
        rules_file = self.rules_dir / f"{domain_lower}.json"
        
        # Also check for subdirectory structure (e.g., healthcare/healthcare.json)
        subdir_rules_file = self.rules_dir / domain_lower / f"{domain_lower}.json"
        
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    rules_config = json.load(f)
                
                # Validate structure
                if "rules" not in rules_config:
                    rules_config["rules"] = []
                if "tier" not in rules_config:
                    rules_config["tier"] = self.get_domain_tier(domain_lower)
                
                self._cache[domain_lower] = rules_config
                return rules_config
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DomainRulesLoader] Error loading {rules_file}: {e}")
                # Fall through to check subdirectory or embedded rules
        
        # Check subdirectory structure
        if subdir_rules_file.exists():
            try:
                with open(subdir_rules_file, 'r') as f:
                    rules_config = json.load(f)
                
                # Validate structure
                if "rules" not in rules_config:
                    rules_config["rules"] = []
                if "tier" not in rules_config:
                    rules_config["tier"] = self.get_domain_tier(domain_lower)
                
                self._cache[domain_lower] = rules_config
                return rules_config
                
            except (json.JSONDecodeError, IOError) as e:
                print(f"[DomainRulesLoader] Error loading {subdir_rules_file}: {e}")
                # Fall through to embedded rules
        
        # Use embedded rules if available
        if domain_lower in EMBEDDED_RULES:
            self._cache[domain_lower] = EMBEDDED_RULES[domain_lower].copy()
            return self._cache[domain_lower]
        
        # Default fallback
        default_rules = {
            "domain": domain_lower,
            "tier": self.get_domain_tier(domain_lower),
            "version": "0.1",
            "rules": EMBEDDED_RULES["general"]["rules"]
        }
        self._cache[domain_lower] = default_rules
        return default_rules
    
    def get_rule_by_id(self, domain: str, rule_id: str) -> Optional[Dict]:
        """Get a specific rule by ID."""
        rules_config = self.load_rules(domain)
        for rule in rules_config.get("rules", []):
            if rule.get("id") == rule_id:
                return rule
        return None
    
    def get_halt_rules(self, domain: str) -> List[Dict]:
        """Get only rules that cause HALT on failure."""
        rules_config = self.load_rules(domain)
        return [r for r in rules_config.get("rules", []) if r.get("halt_on_failure", False)]
    
    def get_warning_rules(self, domain: str) -> List[Dict]:
        """Get rules that only generate warnings (no HALT)."""
        rules_config = self.load_rules(domain)
        return [r for r in rules_config.get("rules", []) if not r.get("halt_on_failure", False)]
    
    def validate_fragment_against_rules(self, domain: str, fragment: Dict) -> List[Dict]:
        """
        Validate a single fragment against all domain rules.
        
        Returns list of violations (empty if fragment passes all rules).
        """
        violations = []
        rules_config = self.load_rules(domain)
        
        for rule in rules_config.get("rules", []):
            check_type = rule.get("check_type")
            config = rule.get("config", {})
            
            violation = self._check_rule(check_type, fragment, config, rule)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_rule(self, check_type: str, fragment: Dict, config: Dict, rule: Dict) -> Optional[Dict]:
        """Execute a single rule check."""
        
        if check_type == "requires_field":
            field = config.get("field")
            if field and not fragment.get(field):
                return {
                    "rule_id": rule.get("id"),
                    "rule_name": rule.get("name"),
                    "violation": f"Missing required field: {field}",
                    "severity": "halt" if rule.get("halt_on_failure") else "warning"
                }
        
        elif check_type == "minimum_source_type":
            allowed = config.get("allowed", [])
            source_type = fragment.get("source_type", "tertiary")
            if source_type not in allowed:
                return {
                    "rule_id": rule.get("id"),
                    "rule_name": rule.get("name"),
                    "violation": f"Source type '{source_type}' not allowed. Must be one of: {allowed}",
                    "severity": "halt" if rule.get("halt_on_failure") else "warning"
                }
        
        elif check_type == "requires_reasoning_role":
            required_role = config.get("role")
            fragment_role = fragment.get("reasoning_role", "unknown")
            if fragment_role != required_role:
                # This is a composition-level check, skip for single fragment
                pass
        
        elif check_type == "minimum_year":
            min_year = config.get("min_year", 0)
            fragment_year = fragment.get("year", 0)
            if fragment_year < min_year:
                return {
                    "rule_id": rule.get("id"),
                    "rule_name": rule.get("name"),
                    "violation": f"Fragment year ({fragment_year}) is before minimum ({min_year})",
                    "severity": "halt" if rule.get("halt_on_failure") else "warning"
                }
        
        elif check_type == "label_tertiary":
            label = config.get("label", "Unverified")
            if fragment.get("source_type") == "tertiary":
                # Add label to fragment metadata
                if "labels" not in fragment:
                    fragment["labels"] = []
                if label not in fragment["labels"]:
                    fragment["labels"].append(label)
        
        return None


def get_domain_rules(domain: str, rules_dir: str = "openeyes/domain_rules") -> Dict[str, Any]:
    """Convenience function to get domain rules."""
    loader = DomainRulesLoader(rules_dir)
    return loader.load_rules(domain)


def get_domain_tier(domain: str) -> str:
    """Convenience function to get domain tier."""
    return DOMAIN_TIERS.get(domain.lower(), "tier2")


def get_credibility_score(domain: str, source_type: str) -> int:
    """
    Get the credibility score for a source type in a specific domain.
    
    Uses domain-specific credibility hierarchies aligned with real-world epistemology.
    Falls back to default hierarchy if domain or source_type not found.
    
    Args:
        domain: The domain name (e.g., 'medical', 'engineering', 'cooking')
        source_type: The type of source (e.g., 'peer_reviewed_study', 'textbook', 'forum')
    
    Returns:
        Integer credibility score (0-100), higher = more credible
    """
    domain_lower = domain.lower()
    
    # Get domain-specific hierarchy, or fall back to default
    hierarchy = CREDIBILITY_HIERARCHIES.get(domain_lower, CREDIBILITY_HIERARCHIES["default"])
    
    # Get score for source_type, or fall back to generic mapping
    score = hierarchy.get(source_type, None)
    
    if score is not None:
        return score
    
    # Fallback: try common mappings
    fallback_mapping = {
        "primary": 85,
        "secondary": 65,
        "tertiary": 45,
        "peer_reviewed": 90,
        "peer_reviewed_study": 90,
        "government": 85,
        "government_source": 85,
        "textbook": 75,
        "news": 55,
        "news_article": 55,
        "blog": 40,
        "forum": 30,
        "anecdotal": 20
    }
    
    return fallback_mapping.get(source_type, 50)  # Default to 50 if unknown
