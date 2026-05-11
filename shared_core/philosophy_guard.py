"""
Philosophy Guard - Rule-based filter that enforces domain-specific philosophy rules.

The Philosophy Guard is a hard constraint system that rejects any proposal
violating configured domain rules, regardless of its performance score. This
replaces LLM-based criticism with deterministic, reproducible rule checking.

Architecture:
- Fixed enforcement engine (this module)
- Configurable rule sets (live in openeyes/domain_rules/)

For E-AR: Uses built-in E+ design principles (PHIL-001–005)
For OpenEyes: Loads domain-specific rules from JSON config (medical, legal, etc.)
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class PhilosophyGuard:
    """Rule-based filter for domain-specific philosophy compliance."""
    
    # Core E-AR philosophy rules (used when no external config provided)
    DEFAULT_RULES = {
        "cognitive_simplicity": {
            "id": "PHIL-001",
            "name": "Cognitive Simplicity",
            "description": "No construct should increase cognitive load unnecessarily",
            "check_type": "built_in",
            "check_fn": "_check_cognitive_simplicity"
        },
        "determinism": {
            "id": "PHIL-002", 
            "name": "Deterministic Mapping",
            "description": "All constructs must map deterministically to target languages",
            "check_type": "built_in",
            "check_fn": "_check_determinism"
        },
        "no_syntax_bloat": {
            "id": "PHIL-003",
            "name": "No Syntax Bloat", 
            "description": "Avoid adding keywords or operators without strong justification",
            "check_type": "built_in",
            "check_fn": "_check_syntax_bloat"
        },
        "consistency": {
            "id": "PHIL-004",
            "name": "Consistency",
            "description": "New constructs must be consistent with existing patterns",
            "check_type": "built_in",
            "check_fn": "_check_consistency"
        },
        "beginner_first": {
            "id": "PHIL-005",
            "name": "Beginner-First",
            "description": "Readability for learners takes priority over expert convenience",
            "check_type": "built_in",
            "check_fn": "_check_beginner_first"
        }
    }
    
    def __init__(self, rules_config: Optional[str] = None,
                 primitives_path: Optional[str] = None):
        """
        Initialize Philosophy Guard.
        
        Args:
            rules_config: Path to JSON file containing domain-specific rules.
                         If None, uses default E-AR rules.
            primitives_path: Path to directory containing primitive definitions
                            (for E-AR consistency checks). Optional.
        """
        self.rules_config_path = Path(rules_config) if rules_config else None
        self.primitives_path = Path(primitives_path) if primitives_path else None
        self.rules: Dict[str, Any] = {}
        self.existing_primitives: List[Dict] = []
        
        self._load_rules()
        self._load_existing_primitives()
    
    def _load_rules(self) -> None:
        """Load rules from config file or use defaults."""
        if self.rules_config_path and self.rules_config_path.exists():
            try:
                with open(self.rules_config_path, "r") as f:
                    config = json.load(f)
                    self.rules = config.get("rules", [])
                    self.domain = config.get("domain", "unknown")
                    self.version = config.get("version", "0.1")
                print(f"✓ Loaded {len(self.rules)} domain rules from {self.rules_config_path}")
                print(f"  Domain: {self.domain}, Version: {self.version}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠ Failed to load rules config {self.rules_config_path}: {e}")
                print("  Falling back to default E-AR rules")
                self.rules = list(self.DEFAULT_RULES.values())
                self.domain = "e_ar"
        else:
            # Use default E-AR rules
            self.rules = list(self.DEFAULT_RULES.values())
            self.domain = "e_ar"
            if self.rules_config_path:
                print(f"⚠ Rules config not found: {self.rules_config_path}")
                print("  Using default E-AR rules")
            else:
                print(f"✓ Using default E-AR rules ({len(self.rules)} rules)")
    
    def _load_existing_primitives(self) -> None:
        """Load all existing primitives for consistency checks (E-AR only)."""
        if not self.primitives_path or not self.primitives_path.exists():
            return
        
        for file in self.primitives_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    self.existing_primitives.extend(data)
            except (json.JSONDecodeError, IOError):
                pass
    
    def validate_proposal(self, proposal: Dict) -> Dict[str, Any]:
        """
        Validate a single proposal against all philosophy rules.
        
        Args:
            proposal: Proposal dict with keys like 'type', 'content', 'change_description'
                     For OpenEyes: fragment dict with 'id', 'content', 'tags', 'source_url', etc.
        
        Returns:
            Validation result with pass/fail status and detailed feedback
        """
        results = {
            "proposal_id": proposal.get("id", "unknown"),
            "proposal_type": proposal.get("type", proposal.get("domain", "unknown")),
            "domain": self.domain,
            "passed": True,
            "rule_results": [],
            "rejected_by": [],
            "warnings": []
        }
        
        # Run each rule check
        for rule in self.rules:
            rule_result = self._apply_rule(rule, proposal)
            
            results["rule_results"].append({
                "rule_id": rule.get("id", rule.get("check_type", "unknown")),
                "rule_name": rule.get("name", rule.get("check_type", "unknown")),
                "passed": rule_result["passed"],
                "message": rule_result["message"],
                "severity": rule_result.get("severity", "error")
            })
            
            if not rule_result["passed"]:
                results["passed"] = False
                results["rejected_by"].append(rule.get("id", rule.get("check_type", "unknown")))
                
                if rule_result.get("severity") == "warning":
                    results["warnings"].append(rule_result["message"])
        
        return results
    
    def _apply_rule(self, rule: Dict, proposal: Dict) -> Dict[str, Any]:
        """Apply a single rule to a proposal."""
        check_type = rule.get("check_type", "")
        config = rule.get("config", {})
        
        # Built-in E-AR rules
        if check_type == "built_in":
            check_fn = getattr(self, rule.get("check_fn", ""), None)
            if check_fn:
                return check_fn(proposal)
        
        # OpenEyes domain-specific rule types
        elif check_type == "blacklist_tag_conflict":
            return self._check_blacklist_tag(proposal, config)
        elif check_type == "minimum_credibility_class":
            return self._check_minimum_credibility(proposal, config)
        elif check_type == "requires_field":
            return self._check_requires_field(proposal, config)
        elif check_type == "whitelist_domain":
            return self._check_whitelist_domain(proposal, config)
        elif check_type == "max_age_days":
            return self._check_max_age(proposal, config)
        elif check_type == "compatibility_check":
            return self._check_compatibility(proposal, config)
        elif check_type == "recency_cap":
            return self._check_recency_cap(proposal, config)
        elif check_type == "requires_uncertainty_note":
            return self._check_requires_uncertainty_note(proposal, config)
        elif check_type == "prohibit_source_type":
            return self._check_prohibit_source_type(proposal, config)
        
        # Unknown rule type
        return {
            "passed": True,
            "message": f"Unknown rule type: {check_type}",
            "severity": "warning"
        }
    
    def _check_blacklist_tag(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check if proposal contains any blacklisted tags."""
        flag = config.get("flag", "")
        tags = proposal.get("tags", [])
        
        if flag in tags:
            return {
                "passed": False,
                "message": f"Proposal contains forbidden tag: {flag}",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": f"No forbidden tag '{flag}' detected"
        }
    
    def _check_minimum_credibility(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check if proposal meets minimum credibility class."""
        allowed = config.get("allowed", [])
        
        # Support both Fragment objects (credibility_class) and FragmentCandidate objects (credibility_estimate as float)
        credibility = proposal.get("credibility_class", "")
        
        # If no credibility_class, check for credibility_estimate (FragmentCandidate uses float score)
        if not credibility:
            cred_estimate = proposal.get("credibility_estimate")
            if cred_estimate is not None:
                # For FragmentCandidate, convert float score to pass/fail based on threshold
                # A score >= 0.35 is considered acceptable (matches Monte Carlo threshold)
                if cred_estimate >= 0.35:
                    return {
                        "passed": True,
                        "message": f"Credibility estimate {cred_estimate} meets minimum threshold (0.35)"
                    }
                else:
                    return {
                        "passed": False,
                        "message": f"Credibility estimate {cred_estimate} below minimum threshold (0.35)",
                        "severity": "error"
                    }
        
        if not allowed:
            return {
                "passed": True,
                "message": "No credibility requirements defined"
            }
        
        if credibility not in allowed:
            return {
                "passed": False,
                "message": f"Credibility class '{credibility}' not in allowed list: {allowed}",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": f"Credibility class '{credibility}' meets requirements"
        }
    
    def _check_requires_field(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check if proposal has required field."""
        field = config.get("field", "")
        
        if not field:
            return {
                "passed": True,
                "message": "No field requirement defined"
            }
        
        value = proposal.get(field)
        if value is None or value == "":
            return {
                "passed": False,
                "message": f"Required field '{field}' is missing or empty",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": f"Required field '{field}' present"
        }
    
    def _check_whitelist_domain(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check if proposal domain is in whitelist."""
        allowed_domains = config.get("domains", [])
        domain = proposal.get("domain", "")
        
        if not allowed_domains:
            return {
                "passed": True,
                "message": "No domain whitelist defined"
            }
        
        if domain not in allowed_domains:
            return {
                "passed": False,
                "message": f"Domain '{domain}' not in allowed list: {allowed_domains}",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": f"Domain '{domain}' is allowed"
        }
    
    def _check_max_age(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check if proposal content is not too old."""
        from datetime import datetime, timedelta
        
        max_days = config.get("max_days", 365)
        last_verified = proposal.get("last_verified", "")
        
        if not last_verified:
            return {
                "passed": False,
                "message": "No last_verified date available",
                "severity": "error"
            }
        
        try:
            verified_date = datetime.fromisoformat(last_verified.replace("Z", "+00:00"))
            age = datetime.now(verified_date.tzinfo) - verified_date
            if age.days > max_days:
                return {
                    "passed": False,
                    "message": f"Content is {age.days} days old (max {max_days} days)",
                    "severity": "error"
                }
        except (ValueError, TypeError):
            return {
                "passed": False,
                "message": f"Invalid last_verified date format: {last_verified}",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": f"Content verified within {max_days} days"
        }
    
    def _check_compatibility(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """Check compatibility with other fragments (OpenEyes)."""
        incompatible_with = proposal.get("incompatible_with", [])
        context_fragments = config.get("context_fragments", [])
        
        conflicts = [f for f in incompatible_with if f in context_fragments]
        if conflicts:
            return {
                "passed": False,
                "message": f"Incompatible with context fragments: {conflicts}",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": "No compatibility conflicts detected"
        }
    
    def _check_recency_cap(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """
        FIN-003: Fragments older than max_age_years cannot exceed score_cap.
        This is a soft rule - returns warning but doesn't block.
        Actual score capping happens in Monte Carlo engine.
        """
        from datetime import datetime
        
        max_age_years = config.get("max_age_years", 2)
        score_cap = config.get("score_cap", 60)
        
        fragment_year = proposal.get("year", datetime.now().year)
        current_year = datetime.now().year
        age = current_year - fragment_year
        
        if age > max_age_years:
            # Just warn - actual capping is done by Monte Carlo
            return {
                "passed": True,
                "message": f"Fragment is {age} years old (max {max_age_years}). Score will be capped at {score_cap} during evaluation.",
                "severity": "warning"
            }
        
        return {
            "passed": True,
            "message": f"Fragment is {age} years old, within {max_age_years} year limit"
        }
    
    def _check_requires_uncertainty_note(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
        """
        FIN-004 / HC-004: Fragments with price prediction or treatment dosage tags must include uncertainty note.
        Checks if content contains hedging language when trigger tags are present.
        
        FIX 3: Added support for allowed_tags to bypass uncertainty check for treatment_dosage fragments.
        """
        trigger_tags = config.get("trigger_tags", ["price_target", "prediction", "forecast"])
        allowed_tags = config.get("allowed_tags", [])  # FIX 3: Tags that bypass uncertainty requirement
        fragment_tags = proposal.get("tags", [])
        content = proposal.get("content", "").lower()

        # Check if any trigger tag is present
        has_trigger = any(tag in fragment_tags for tag in trigger_tags)
        
        # FIX 3: If fragment has an allowed_tag (like treatment_dosage), skip uncertainty check
        if has_trigger and allowed_tags:
            has_allowed = any(tag in fragment_tags for tag in allowed_tags)
            if has_allowed:
                return {
                    "passed": True,
                    "message": f"Fragment has allowed tag ({allowed_tags}), uncertainty note not required"
                }

        if has_trigger:
            # Look for uncertainty/hedging language
            uncertainty_phrases = [
                "may", "might", "could", "uncertain", "risk", "volatile",
                "not guaranteed", "past performance", "no assurance",
                "speculative", "hypothetical", "illustration only"
            ]

            has_uncertainty = any(phrase in content for phrase in uncertainty_phrases)

            if not has_uncertainty:
                return {
                    "passed": False,
                    "message": "Fragment contains price prediction/forecast content but lacks required uncertainty disclaimer",
                    "severity": "error"
                }

        return {
            "passed": True,
            "message": "Prediction content includes appropriate uncertainty language"
        }

    def _check_prohibit_source_type(self, proposal: Dict, config: Dict) -> Dict[str, Any]:
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

    def _check_cognitive_simplicity(self, proposal: Dict) -> Dict[str, Any]:
        """
        Check if proposal maintains cognitive simplicity.
        
        Rejects proposals that:
        - Add more than 2 new keywords
        - Introduce nested complexity beyond 2 levels
        - Require memorizing arbitrary rules
        """
        change_type = proposal.get("change_type", "")
        
        # Check for keyword additions
        new_keywords = proposal.get("new_keywords", [])
        if len(new_keywords) > 2:
            return {
                "passed": False,
                "message": f"Proposal adds {len(new_keywords)} new keywords (max 2 allowed)",
                "severity": "error"
            }
        
        # Check for complexity increases
        if proposal.get("increases_nesting_depth", False):
            new_depth = proposal.get("new_nesting_depth", 0)
            if new_depth > 2:
                return {
                    "passed": False,
                    "message": f"Proposal allows nesting depth of {new_depth} (max 2 allowed)",
                    "severity": "error"
                }
        
        # Check for special cases / arbitrary rules
        if proposal.get("requires_memorization", False):
            return {
                "passed": False,
                "message": "Proposal requires memorizing arbitrary rules",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": "Maintains cognitive simplicity"
        }
    
    def _check_determinism(self, proposal: Dict) -> Dict[str, Any]:
        """
        Check if proposal maintains deterministic behavior.
        
        Rejects proposals that:
        - Have ambiguous parsing
        - Depend on execution order
        - Produce different outputs for same input
        """
        # Check for ambiguity
        if proposal.get("ambiguous_parsing", False):
            return {
                "passed": False,
                "message": "Proposal introduces ambiguous parsing",
                "severity": "error"
            }
        
        # Check for non-deterministic behavior
        if proposal.get("non_deterministic", False):
            return {
                "passed": False,
                "message": "Proposal exhibits non-deterministic behavior",
                "severity": "error"
            }
        
        # Check for clear target mapping
        if "target_mapping" in proposal:
            mapping = proposal["target_mapping"]
            if not mapping.get("python") or not mapping.get("signal"):
                return {
                    "passed": False,
                    "message": "Proposal lacks clear mapping to both Python and Signal",
                    "severity": "error"
                }
        
        return {
            "passed": True,
            "message": "Maintains deterministic behavior"
        }
    
    def _check_syntax_bloat(self, proposal: Dict) -> Dict[str, Any]:
        """
        Check if proposal avoids syntax bloat.
        
        Rejects proposals that:
        - Add redundant constructs (existing primitive can do the job)
        - Introduce shorthand without clear benefit
        - Duplicate functionality
        """
        # Check for redundancy
        if proposal.get("redundant", False):
            existing_alternative = proposal.get("existing_alternative", "existing primitive")
            return {
                "passed": False,
                "message": f"Proposal is redundant - {existing_alternative} already provides this functionality",
                "severity": "error"
            }
        
        # Check for shorthand without justification
        if proposal.get("is_shorthand", False):
            justification = proposal.get("shorthand_justification", "")
            if not justification or len(justification) < 20:
                return {
                    "passed": False,
                    "message": "Shorthand syntax lacks strong justification",
                    "severity": "warning"
                }
        
        # Check for operator overloading
        if proposal.get("operator_overloading", False):
            return {
                "passed": False,
                "message": "Proposal introduces operator overloading (increases cognitive load)",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": "No syntax bloat detected"
        }
    
    def _check_consistency(self, proposal: Dict) -> Dict[str, Any]:
        """
        Check if proposal is consistent with existing E+ patterns.
        
        Rejects proposals that:
        - Use different naming conventions
        - Break existing composition patterns
        - Are incompatible with core primitives
        """
        # Check naming convention
        if "new_keyword" in proposal:
            new_keyword = proposal["new_keyword"]
            
            # E+ uses lowercase, space-separated keywords
            if not new_keyword.islower() or "_" in new_keyword:
                return {
                    "passed": False,
                    "message": f"Keyword '{new_keyword}' violates E+ naming convention (lowercase, spaces)",
                    "severity": "error"
                }
        
        # Check for incompatibility with existing primitives
        incompatibilities = proposal.get("incompatible_with", [])
        if incompatibilities:
            return {
                "passed": False,
                "message": f"Proposal incompatible with existing primitives: {', '.join(incompatibilities)}",
                "severity": "error"
            }
        
        # Check composition pattern consistency
        if proposal.get("composition_pattern"):
            pattern = proposal["composition_pattern"]
            # Verify pattern matches existing style (simplified check)
            existing_patterns = set()
            for p in self.existing_primitives:
                tags = p.get("tags", [])
                if tags:
                    existing_patterns.add(tuple(sorted(tags)))
            
            # This is a simplified check - real implementation would be more sophisticated
            new_tags = tuple(sorted(proposal.get("tags", [])))
            if new_tags and new_tags not in existing_patterns and len(existing_patterns) > 0:
                return {
                    "passed": False,
                    "message": "Proposal's tag pattern inconsistent with existing primitives",
                    "severity": "warning"
                }
        
        return {
            "passed": True,
            "message": "Consistent with existing E+ patterns"
        }
    
    def _check_beginner_first(self, proposal: Dict) -> Dict[str, Any]:
        """
        Check if proposal prioritizes beginner readability.
        
        Rejects proposals that:
        - Optimize for expert convenience at expense of clarity
        - Use cryptic abbreviations
        - Assume prior programming knowledge
        """
        # Check for cryptic naming
        if "new_keyword" in proposal:
            keyword = proposal["new_keyword"]
            
            # Flag very short keywords (< 3 chars) as potentially cryptic
            if len(keyword.replace(" ", "")) < 3:
                return {
                    "passed": False,
                    "message": f"Keyword '{keyword}' may be too cryptic for beginners",
                    "severity": "warning"
                }
            
            # Flag abbreviations
            common_abbreviations = ["cnt", "num", "idx", "tmp", "val"]
            if any(abbr in keyword.lower() for abbr in common_abbreviations):
                return {
                    "passed": False,
                    "message": f"Keyword '{keyword}' contains abbreviations harmful to beginners",
                    "severity": "warning"
                }
        
        # Check if proposal assumes advanced knowledge
        if proposal.get("assumes_advanced_knowledge", False):
            return {
                "passed": False,
                "message": "Proposal assumes programming knowledge beginners may not have",
                "severity": "error"
            }
        
        # Check readability score if provided
        readability_score = proposal.get("beginner_readability_score", 0)
        if readability_score > 0 and readability_score < 60:
            return {
                "passed": False,
                "message": f"Proposal scores {readability_score} on beginner readability (min 60 required)",
                "severity": "error"
            }
        
        return {
            "passed": True,
            "message": "Prioritizes beginner readability"
        }
    
    def validate_batch(self, proposals: List[Dict]) -> Dict[str, Any]:
        """
        Validate multiple proposals and generate summary report.
        
        Args:
            proposals: List of proposal dicts
        
        Returns:
            Batch validation report with statistics
        """
        results = []
        passed_count = 0
        rejected_count = 0
        rejection_reasons = {}
        
        for proposal in proposals:
            result = self.validate_proposal(proposal)
            results.append(result)
            
            if result["passed"]:
                passed_count += 1
            else:
                rejected_count += 1
                for rule_id in result["rejected_by"]:
                    rejection_reasons[rule_id] = rejection_reasons.get(rule_id, 0) + 1
        
        return {
            "total_proposals": len(proposals),
            "passed": passed_count,
            "rejected": rejected_count,
            "pass_rate": round(passed_count / len(proposals), 2) if proposals else 0,
            "rejection_breakdown": rejection_reasons,
            "detailed_results": results
        }


# Convenience function
def guard_check(proposal: Dict) -> Dict[str, Any]:
    """
    Quick function to validate a single proposal.
    
    Args:
        proposal: Proposal dict to validate
    
    Returns:
        Validation result
    """
    guard = PhilosophyGuard()
    return guard.validate_proposal(proposal)


if __name__ == "__main__":
    print("\n=== PHILOSOPHY GUARD TEST ===\n")
    
    guard = PhilosophyGuard()
    
    # Test cases
    test_proposals = [
        {
            "id": "test_001",
            "type": "new_primitive",
            "change_type": "add_keyword",
            "new_keywords": ["repeat until"],
            "new_keyword": "repeat until",
            "description": "Add 'repeat until' loop construct",
            "target_mapping": {
                "python": "while not condition:",
                "signal": "loop_until"
            },
            "increases_nesting_depth": False,
            "ambiguous_parsing": False,
            "redundant": False,
            "assumes_advanced_knowledge": False
        },
        {
            "id": "test_002",
            "type": "syntax_change",
            "change_type": "add_operator",
            "new_keywords": ["++", "--", "**", "%%"],
            "description": "Add C-style increment/decrement operators",
            "increases_nesting_depth": False,
            "ambiguous_parsing": True,
            "operator_overloading": True,
            "assumes_advanced_knowledge": True
        },
        {
            "id": "test_003",
            "type": "new_primitive",
            "change_type": "add_keyword",
            "new_keywords": ["cnt"],
            "new_keyword": "cnt",
            "description": "Shorthand counter primitive",
            "is_shorthand": True,
            "shorthand_justification": "faster typing",
            "assumes_advanced_knowledge": False
        }
    ]
    
    for proposal in test_proposals:
        print(f"\n--- Testing: {proposal['id']} ---")
        print(f"Description: {proposal.get('description', 'N/A')}")
        
        result = guard.validate_proposal(proposal)
        
        if result["passed"]:
            print(f"✅ PASSED all philosophy checks")
        else:
            print(f"❌ REJECTED by: {', '.join(result['rejected_by'])}")
            for rule_result in result["rule_results"]:
                if not rule_result["passed"]:
                    print(f"   - {rule_result['rule_name']}: {rule_result['message']}")
        
        if result["warnings"]:
            print(f"⚠️  Warnings: {', '.join(result['warnings'])}")
    
    # Batch validation
    print("\n\n=== BATCH VALIDATION SUMMARY ===")
    batch_result = guard.validate_batch(test_proposals)
    print(f"Total: {batch_result['total_proposals']}")
    print(f"Passed: {batch_result['passed']}")
    print(f"Rejected: {batch_result['rejected']}")
    print(f"Pass Rate: {batch_result['pass_rate']:.0%}")
    
    if batch_result["rejection_breakdown"]:
        print("\nRejection breakdown:")
        for rule_id, count in batch_result["rejection_breakdown"].items():
            print(f"  {rule_id}: {count} proposal(s)")
