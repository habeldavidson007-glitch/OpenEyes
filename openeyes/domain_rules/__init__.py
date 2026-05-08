"""
Domain Rules — Domain-Specific Philosophy Guard Rule Configs

Provides domain-specific rule sets for the Philosophy Guard. Each domain has 
a JSON config that defines what the guard checks.

Structure:
- medical.json: Medical domain rules (do_no_harm, evidence_based, cite_source)
- legal.json: Legal domain rules
- engineering.json: Engineering domain rules
- ethics.json: Ethics domain rules
- general.json: General purpose rules
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class DomainRulesConfig:
    """
    Domain-specific rule configuration loader.
    
    Loads and validates domain rule configurations for the Philosophy Guard.
    """
    
    def __init__(self, domain: str = "general", rules_dir: Optional[str] = None):
        """
        Initialize Domain Rules Config.
        
        Args:
            domain: Domain type (medical, legal, engineering, ethics, general)
            rules_dir: Optional path to rules directory
        """
        self.domain = domain
        self.rules_dir = Path(rules_dir) if rules_dir else Path(__file__).parent
        self.config: Dict[str, Any] = {}
        self.rules: List[Dict] = []
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load domain rules from JSON file."""
        config_file = self.rules_dir / f"{self.domain}.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
                self.rules = self.config.get("rules", [])
                print(f"✓ Loaded {len(self.rules)} rules for domain '{self.domain}'")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠ Failed to load domain rules: {e}")
                self._load_default_rules()
        else:
            print(f"⚠ No rules file found for domain '{self.domain}', using defaults")
            self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Load default rules based on domain."""
        if self.domain == "medical":
            self.config = {
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
                        "config": {"allowed": ["clinical_guideline", "peer_reviewed_study"]}
                    },
                    {
                        "id": "MED-003",
                        "name": "Cite Source",
                        "description": "Every fragment included in a medical answer must carry a source URL",
                        "check_type": "requires_field",
                        "config": {"field": "source_url"}
                    }
                ]
            }
        else:
            # Generic rules for other domains
            self.config = {
                "domain": self.domain,
                "version": "0.1",
                "rules": [
                    {
                        "id": f"{self.domain.upper()}-001",
                        "name": "Source Required",
                        "description": "All fragments must have a source attribution",
                        "check_type": "requires_field",
                        "config": {"field": "source"}
                    },
                    {
                        "id": f"{self.domain.upper()}-002",
                        "name": "Minimum Credibility",
                        "description": "Fragments must meet minimum credibility threshold",
                        "check_type": "minimum_credibility_score",
                        "config": {"min_score": 0.6}
                    }
                ]
            }
        
        self.rules = self.config.get("rules", [])
    
    def get_rules(self) -> List[Dict]:
        """Get the list of rules for this domain."""
        return self.rules
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict]:
        """Get a specific rule by ID."""
        for rule in self.rules:
            if rule.get("id") == rule_id:
                return rule
        return None
    
    def validate_fragment(self, fragment: Dict) -> Dict[str, Any]:
        """
        Validate a fragment against all domain rules.
        
        Args:
            fragment: Fragment dict to validate
            
        Returns:
            Validation result with pass/fail status and details
        """
        results = {
            "fragment_id": fragment.get("id", "unknown"),
            "passed": True,
            "rule_results": [],
            "rejected_by": [],
            "warnings": []
        }
        
        for rule in self.rules:
            check_type = rule.get("check_type")
            config = rule.get("config", {})
            
            rule_result = self._apply_rule(fragment, check_type, config)
            
            results["rule_results"].append({
                "rule_id": rule.get("id"),
                "rule_name": rule.get("name"),
                "passed": rule_result["passed"],
                "message": rule_result["message"]
            })
            
            if not rule_result["passed"]:
                results["passed"] = False
                results["rejected_by"].append(rule.get("id"))
                
                if rule_result.get("severity") == "warning":
                    results["warnings"].append(rule_result["message"])
        
        return results
    
    def _apply_rule(self, fragment: Dict, check_type: str, config: Dict) -> Dict[str, Any]:
        """Apply a single rule check to a fragment."""
        
        if check_type == "requires_field":
            field = config.get("field")
            if field and field not in fragment:
                return {
                    "passed": False,
                    "message": f"Missing required field: {field}",
                    "severity": "error"
                }
            return {"passed": True, "message": f"Has required field: {field}"}
        
        elif check_type == "minimum_credibility_class":
            allowed = config.get("allowed", [])
            cred_class = fragment.get("credibility_class", "")
            if cred_class not in allowed:
                return {
                    "passed": False,
                    "message": f"Credibility class '{cred_class}' not in allowed list: {allowed}",
                    "severity": "error"
                }
            return {"passed": True, "message": f"Credibility class '{cred_class}' is allowed"}
        
        elif check_type == "blacklist_tag_conflict":
            flag = config.get("flag")
            tags = fragment.get("tags", [])
            if flag and flag in tags:
                return {
                    "passed": False,
                    "message": f"Fragment has blacklisted tag: {flag}",
                    "severity": "error"
                }
            return {"passed": True, "message": f"No blacklisted tag '{flag}' found"}
        
        elif check_type == "minimum_credibility_score":
            min_score = config.get("min_score", 0.5)
            score = fragment.get("credibility_estimate", 0.0)
            if score < min_score:
                return {
                    "passed": False,
                    "message": f"Credibility score {score:.2f} below minimum {min_score}",
                    "severity": "error"
                }
            return {"passed": True, "message": f"Credibility score {score:.2f} meets minimum {min_score}"}
        
        return {"passed": True, "message": "Rule check passed (unknown check type)"}


def get_domain_rules(domain: str = "general") -> DomainRulesConfig:
    """Convenience function to get domain rules config."""
    return DomainRulesConfig(domain=domain)


__all__ = ["DomainRulesConfig", "get_domain_rules"]