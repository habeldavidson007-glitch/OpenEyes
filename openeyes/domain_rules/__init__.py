"""
OpenEyes Domain Rules — Philosophy Guard Rule Configurations

Provides domain-specific rule sets for the Philosophy Guard.
Each domain has a JSON config that defines what the guard checks.

Target structure:
- medical.json
- legal.json
- engineering.json
- ethics.json
- general.json
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


# Default rule configurations embedded in code
DEFAULT_RULES = {
    "medical": {
        "domain": "medical",
        "version": "0.1",
        "rules": [
            {
                "id": "MED-001",
                "name": "Do No Harm",
                "description": "No fragment may recommend a treatment with a known fatal interaction in the current patient context",
                "check_type": "blacklist_tag_conflict",
                "config": {"flag": "fatal_interaction"}
            },
            {
                "id": "MED-002",
                "name": "Evidence-Based Only",
                "description": "All treatment fragments must have credibility_class of clinical_guideline or peer_reviewed_study",
                "check_type": "minimum_credibility_class",
                "config": {
                    "allowed": ["clinical_guideline", "peer_reviewed_study"]
                }
            },
            {
                "id": "MED-003",
                "name": "Cite Source",
                "description": "Every fragment included in a medical answer must carry a source URL",
                "check_type": "requires_field",
                "config": {"field": "source_url"}
            },
            {
                "id": "MED-004",
                "name": "Recent Verification",
                "description": "Medical fragments must be verified within the last 5 years",
                "check_type": "max_verification_age",
                "config": {"max_years": 5}
            },
            {
                "id": "MED-005",
                "name": "Contraindication Check",
                "description": "Fragments with contraindication tags must be flagged",
                "check_type": "require_warning_if_tagged",
                "config": {"tags": ["contraindication", "black_box_warning"]}
            }
        ]
    },
    
    "legal": {
        "domain": "legal",
        "version": "0.1",
        "rules": [
            {
                "id": "LEG-001",
                "name": "Jurisdiction Consistency",
                "description": "All fragments must reference the same jurisdiction",
                "check_type": "consistent_metadata",
                "config": {"field": "jurisdiction"}
            },
            {
                "id": "LEG-002",
                "name": "Binding Authority Required",
                "description": "Legal claims must come from binding precedent or statute",
                "check_type": "minimum_credibility_class",
                "config": {
                    "allowed": ["binding_precedent", "statute", "regulation"]
                }
            },
            {
                "id": "LEG-003",
                "name": "Cite Source",
                "description": "Every legal fragment must include a citation",
                "check_type": "requires_field",
                "config": {"field": "citation"}
            },
            {
                "id": "LEG-004",
                "name": "No Expired Law",
                "description": "Fragments must not reference repealed or expired laws",
                "check_type": "blacklist_tag_conflict",
                "config": {"flag": "repealed"}
            }
        ]
    },
    
    "engineering": {
        "domain": "engineering",
        "version": "0.1",
        "rules": [
            {
                "id": "ENG-001",
                "name": "Safety Factor Compliance",
                "description": "Engineering recommendations must meet minimum safety factors",
                "check_type": "minimum_threshold",
                "config": {"field": "safety_factor", "min_value": 1.5}
            },
            {
                "id": "ENG-002",
                "name": "Code Compliance",
                "description": "Must reference applicable building/engineering codes",
                "check_type": "requires_field",
                "config": {"field": "code_reference"}
            },
            {
                "id": "ENG-003",
                "name": "Peer Review",
                "description": "Engineering calculations must be peer-reviewed",
                "check_type": "minimum_credibility_class",
                "config": {
                    "allowed": ["peer_reviewed", "code_specification", "standard"]
                }
            }
        ]
    },
    
    "ethics": {
        "domain": "ethics",
        "version": "0.1",
        "rules": [
            {
                "id": "ETH-001",
                "name": "Stakeholder Consideration",
                "description": "Ethical analysis must consider all affected stakeholders",
                "check_type": "requires_tags",
                "config": {"min_tags": ["stakeholder_analysis"]}
            },
            {
                "id": "ETH-002",
                "name": "Principle Alignment",
                "description": "Recommendations must align with established ethical principles",
                "check_type": "whitelist_tag_only",
                "config": {"allowed": ["beneficence", "non_maleficence", "autonomy", "justice"]}
            }
        ]
    },
    
    "general": {
        "domain": "general",
        "version": "0.1",
        "rules": [
            {
                "id": "GEN-001",
                "name": "Source Required",
                "description": "All claims must have a source",
                "check_type": "requires_field",
                "config": {"field": "source"}
            },
            {
                "id": "GEN-002",
                "name": "No Contradictions",
                "description": "Fragments must not contradict each other",
                "check_type": "consistency_check",
                "config": {}
            }
        ]
    }
}


class DomainRulesLoader:
    """
    Loads and manages domain-specific Philosophy Guard rules.
    
    Rules can be loaded from:
    1. Embedded defaults (in this module)
    2. JSON files in openeyes/domain_rules/
    3. Custom paths provided at runtime
    """
    
    def __init__(self, rules_dir: Optional[Path] = None):
        """
        Initialize the rules loader.
        
        Args:
            rules_dir: Directory containing domain rule JSON files.
                      If None, uses default location.
        """
        self.rules_dir = rules_dir or Path(__file__).parent
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get_rules(self, domain: str) -> Dict[str, Any]:
        """
        Get rules for a specific domain.
        
        Args:
            domain: Domain name (e.g., "medical", "legal")
            
        Returns:
            Rule configuration dict
        """
        # Check cache first
        if domain in self._cache:
            return self._cache[domain]
        
        # Try to load from file
        rules_config = self._load_from_file(domain)
        
        # Fall back to defaults
        if rules_config is None:
            rules_config = DEFAULT_RULES.get(domain, DEFAULT_RULES["general"])
        
        # Cache and return
        self._cache[domain] = rules_config
        return rules_config
    
    def _load_from_file(self, domain: str) -> Optional[Dict[str, Any]]:
        """Load rules from a JSON file."""
        config_file = self.rules_dir / f"{domain}.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load rules from {config_file}: {e}")
            return None
    
    def register_rules(self, domain: str, rules_config: Dict[str, Any]):
        """
        Register custom rules for a domain.
        
        Args:
            domain: Domain name
            rules_config: Rule configuration dict
        """
        self._cache[domain] = rules_config
    
    def save_rules_to_file(self, domain: str, rules_config: Dict[str, Any]):
        """
        Save rules to a JSON file.
        
        Args:
            domain: Domain name
            rules_config: Rule configuration dict
        """
        config_file = self.rules_dir / f"{domain}.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(rules_config, f, indent=2)
        
        # Update cache
        self._cache[domain] = rules_config
    
    def list_available_domains(self) -> List[str]:
        """List all domains with available rules."""
        domains = set(DEFAULT_RULES.keys())
        
        # Add domains from files
        if self.rules_dir.exists():
            for config_file in self.rules_dir.glob("*.json"):
                domain = config_file.stem
                if domain != "__init__":
                    domains.add(domain)
        
        return sorted(list(domains))
    
    def validate_rule_config(self, rules_config: Dict[str, Any]) -> bool:
        """
        Validate a rule configuration structure.
        
        Returns True if valid, raises ValueError if invalid.
        """
        if "domain" not in rules_config:
            raise ValueError("Rule config must have 'domain' field")
        
        if "rules" not in rules_config:
            raise ValueError("Rule config must have 'rules' list")
        
        if not isinstance(rules_config["rules"], list):
            raise ValueError("'rules' must be a list")
        
        for i, rule in enumerate(rules_config["rules"]):
            if "id" not in rule:
                raise ValueError(f"Rule {i} missing 'id' field")
            if "check_type" not in rule:
                raise ValueError(f"Rule {rule.get('id', i)} missing 'check_type' field")
        
        return True


# Convenience functions
_default_loader: Optional[DomainRulesLoader] = None


def get_loader(rules_dir: Optional[Path] = None) -> DomainRulesLoader:
    """Get or create the default rules loader."""
    global _default_loader
    if _default_loader is None:
        _default_loader = DomainRulesLoader(rules_dir)
    return _default_loader


def get_domain_rules(domain: str) -> Dict[str, Any]:
    """Get rules for a specific domain."""
    loader = get_loader()
    return loader.get_rules(domain)


def reset_loader():
    """Reset the default loader (for testing)."""
    global _default_loader
    _default_loader = None
