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
    "medical": "tier1",
    "law": "tier1", 
    "legal": "tier1",
    "nuclear": "tier1",
    "aviation": "tier1",
    "pharmaceutical": "tier1",
    "clinical_psychology": "tier1",
    
    # Tier 2: Medium Stakes - Moderate HALT, Mix of Primary/Secondary
    "engineering": "tier2",
    "finance": "tier2",
    "history": "tier2",
    "technology": "tier2",
    "science": "tier2",
    "economics": "tier2",
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


# Embedded domain rules (fallback if JSON files not found)
EMBEDDED_RULES = {
    "medical": {
        "domain": "medical",
        "tier": "tier1",
        "version": "0.2",
        "rules": [
            {
                "id": "MED-001",
                "name": "Do No Harm",
                "description": "No fragment may recommend a treatment with a known fatal interaction",
                "check_type": "blacklist_tag_conflict",
                "config": {"flag": "fatal_interaction"},
                "halt_on_failure": True
            },
            {
                "id": "MED-002",
                "name": "Evidence-Based Only",
                "description": "All treatment fragments must have primary source credibility",
                "check_type": "minimum_source_type",
                "config": {"allowed": ["primary"]},
                "halt_on_failure": True
            },
            {
                "id": "MED-003",
                "name": "Cite Source",
                "description": "Every fragment must carry a source URL",
                "check_type": "requires_field",
                "config": {"field": "source_url"},
                "halt_on_failure": True
            },
            {
                "id": "MED-004",
                "name": "Recent Data Required",
                "description": "At least one fragment must have data from 2024 or later",
                "check_type": "requires_recent_data",
                "config": {"min_year": 2024},
                "halt_on_failure": False
            },
            {
                "id": "MED-005",
                "name": "Counter-Arguments Checked",
                "description": "Must include risk/contraindication information",
                "check_type": "requires_reasoning_role",
                "config": {"role": "counter_argument"},
                "halt_on_failure": False
            }
        ]
    },
    
    "legal": {
        "domain": "legal",
        "tier": "tier1",
        "version": "0.2",
        "rules": [
            {
                "id": "LEG-001",
                "name": "Jurisdiction Consistency",
                "description": "All fragments must reference the same jurisdiction",
                "check_type": "consistent_metadata",
                "config": {"field": "jurisdiction"},
                "halt_on_failure": True
            },
            {
                "id": "LEG-002",
                "name": "Primary Authority Required",
                "description": "Legal claims must cite statutes, regulations, or case law",
                "check_type": "minimum_source_type",
                "config": {"allowed": ["primary"]},
                "halt_on_failure": True
            },
            {
                "id": "LEG-003",
                "name": "No Outdated Precedent",
                "description": "Case law must not be overturned or superseded",
                "check_type": "not_overturned",
                "config": {},
                "halt_on_failure": True
            }
        ]
    },
    
    "engineering": {
        "domain": "engineering",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {
                "id": "ENG-001",
                "name": "Safety Standards Compliance",
                "description": "Must reference applicable safety standards (ISO, ASTM, etc.)",
                "check_type": "requires_standard_reference",
                "config": {"standards": ["ISO", "ASTM", "IEEE", "ASME"]},
                "halt_on_failure": True
            },
            {
                "id": "ENG-002",
                "name": "Recent Technical Data",
                "description": "Technical specifications should be from recent sources",
                "check_type": "minimum_year",
                "config": {"min_year": 2020},
                "halt_on_failure": False
            },
            {
                "id": "ENG-003",
                "name": "Peer-Reviewed Sources Preferred",
                "description": "Prefer peer-reviewed journals over manufacturer claims",
                "check_type": "prefer_source_type",
                "config": {"preferred": ["primary", "secondary"], "discouraged": ["tertiary"]},
                "halt_on_failure": False
            }
        ]
    },
    
    "cooking": {
        "domain": "cooking",
        "tier": "tier3",
        "version": "0.2",
        "rules": [
            {
                "id": "COOK-001",
                "name": "Allergy Warning",
                "description": "Must flag common allergens if present",
                "check_type": "flag_allergens",
                "config": {"allergens": ["nuts", "dairy", "eggs", "soy", "gluten", "shellfish"]},
                "halt_on_failure": False
            },
            {
                "id": "COOK-002",
                "name": "Source Attribution",
                "description": "Recipe should have a source (can be blog, book, etc.)",
                "check_type": "requires_field",
                "config": {"field": "source"},
                "halt_on_failure": False
            },
            {
                "id": "COOK-003",
                "name": "Label Unverified Sources",
                "description": "Tertiary sources must be labeled as unverified",
                "check_type": "label_tertiary",
                "config": {"label": "Unverified"},
                "halt_on_failure": False
            }
        ]
    },
    
    "emergency_medical": {
        "domain": "emergency_medical",
        "tier": "tier0",
        "version": "0.3",
        "rules": [
            {
                "id": "EMERG-001",
                "name": "Triple Verification Required",
                "description": "All emergency medical advice must be verified by 3+ independent primary sources",
                "check_type": "minimum_fragment_count",
                "config": {"min_count": 3, "source_type": "primary"},
                "halt_on_failure": True
            },
            {
                "id": "EMERG-002",
                "name": "Cross-Domain Consensus",
                "description": "Must have agreement across multiple medical subdomains",
                "check_type": "requires_consensus",
                "config": {"min_domains": 2},
                "halt_on_failure": True
            },
            {
                "id": "EMERG-003",
                "name": "Real-Time Data Required",
                "description": "Emergency protocols must reference current year guidelines",
                "check_type": "minimum_year",
                "config": {"min_year": 2025},
                "halt_on_failure": True
            },
            {
                "id": "EMERG-004",
                "name": "Counter-Argument Mandatory",
                "description": "Must include contraindications and risk factors",
                "check_type": "requires_reasoning_role",
                "config": {"role": "counter_argument"},
                "halt_on_failure": True
            }
        ]
    },
    
    "technology": {
        "domain": "technology",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {
                "id": "TECH-001",
                "name": "Version Specificity",
                "description": "Technical information must specify software/hardware versions",
                "check_type": "requires_field",
                "config": {"field": "version"},
                "halt_on_failure": False
            },
            {
                "id": "TECH-002",
                "name": "Recent Data Preferred",
                "description": "Technology information should be from last 3 years",
                "check_type": "minimum_year",
                "config": {"min_year": 2022},
                "halt_on_failure": False
            }
        ]
    },
    
    "creative": {
        "domain": "creative",
        "tier": "tier4",
        "version": "0.2",
        "rules": [
            {
                "id": "CREATE-001",
                "name": "Divergent Thinking Encouraged",
                "description": "Multiple perspectives and creative interpretations welcomed",
                "check_type": "prefer_reasoning_diversity",
                "config": {"min_roles": 1},
                "halt_on_failure": False
            },
            {
                "id": "CREATE-002",
                "name": "Source Attribution Optional",
                "description": "Creative works may or may not have formal sources",
                "check_type": "optional_field",
                "config": {"field": "source"},
                "halt_on_failure": False
            }
        ]
    },
    
    "general": {
        "domain": "general",
        "tier": "tier2",
        "version": "0.2",
        "rules": [
            {
                "id": "GEN-001",
                "name": "Source Required",
                "description": "All claims must have some source attribution",
                "check_type": "requires_field",
                "config": {"field": "source"},
                "halt_on_failure": False
            },
            {
                "id": "GEN-002",
                "name": "Reasoning Chain Completeness",
                "description": "Should have definition and at least one other reasoning role",
                "check_type": "requires_reasoning_diversity",
                "config": {"min_roles": 2},
                "halt_on_failure": False
            }
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
        
        # Try to load from file
        rules_file = self.rules_dir / f"{domain_lower}.json"
        
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
