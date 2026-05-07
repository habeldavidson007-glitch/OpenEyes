"""
Philosophy Guard - Rule-based filter that enforces E+ core design principles.

The Philosophy Guard is a hard constraint system that rejects any proposal
violating E+ fundamental rules, regardless of its performance score. This
replaces LLM-based criticism with deterministic, reproducible rule checking.

Core E+ Philosophy Rules:
1. Cognitive Simplicity - No construct should increase cognitive load unnecessarily
2. Determinism - All constructs must map deterministically to target languages
3. No Syntax Bloat - Avoid adding keywords or operators without strong justification
4. Consistency - New constructs must be consistent with existing E+ patterns
5. Beginner-First - Readability for learners takes priority over expert convenience
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class PhilosophyGuard:
    """Rule-based filter for E+ philosophy compliance."""
    
    # Core philosophy rules with IDs for tracking
    RULES = {
        "cognitive_simplicity": {
            "id": "PHIL-001",
            "name": "Cognitive Simplicity",
            "description": "No construct should increase cognitive load unnecessarily",
            "check_fn": "_check_cognitive_simplicity"
        },
        "determinism": {
            "id": "PHIL-002", 
            "name": "Deterministic Mapping",
            "description": "All constructs must map deterministically to target languages",
            "check_fn": "_check_determinism"
        },
        "no_syntax_bloat": {
            "id": "PHIL-003",
            "name": "No Syntax Bloat", 
            "description": "Avoid adding keywords or operators without strong justification",
            "check_fn": "_check_syntax_bloat"
        },
        "consistency": {
            "id": "PHIL-004",
            "name": "Consistency",
            "description": "New constructs must be consistent with existing E+ patterns",
            "check_fn": "_check_consistency"
        },
        "beginner_first": {
            "id": "PHIL-005",
            "name": "Beginner-First",
            "description": "Readability for learners takes priority over expert convenience",
            "check_fn": "_check_beginner_first"
        }
    }
    
    def __init__(self, primitives_path: str = "evolution/primitives"):
        """
        Initialize Philosophy Guard.
        
        Args:
            primitives_path: Path to directory containing primitive definitions
        """
        self.primitives_path = Path(primitives_path)
        self.existing_primitives: List[Dict] = []
        self.load_existing_primitives()
    
    def load_existing_primitives(self) -> None:
        """Load all existing primitives for consistency checks."""
        if not self.primitives_path.exists():
            print(f"⚠ Primitives directory not found: {self.primitives_path}")
            return
        
        for file in self.primitives_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    self.existing_primitives.extend(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠ Failed to load primitive file {file}: {e}")
        
        print(f"✓ Loaded {len(self.existing_primitives)} existing primitives for consistency checks")
    
    def validate_proposal(self, proposal: Dict) -> Dict[str, Any]:
        """
        Validate a single proposal against all philosophy rules.
        
        Args:
            proposal: Proposal dict with keys like 'type', 'content', 'change_description'
        
        Returns:
            Validation result with pass/fail status and detailed feedback
        """
        results = {
            "proposal_id": proposal.get("id", "unknown"),
            "proposal_type": proposal.get("type", "unknown"),
            "passed": True,
            "rule_results": [],
            "rejected_by": [],
            "warnings": []
        }
        
        # Run each rule check
        for rule_key, rule_def in self.RULES.items():
            check_fn = getattr(self, rule_def["check_fn"])
            rule_result = check_fn(proposal)
            
            results["rule_results"].append({
                "rule_id": rule_def["id"],
                "rule_name": rule_def["name"],
                "passed": rule_result["passed"],
                "message": rule_result["message"],
                "severity": rule_result.get("severity", "error")
            })
            
            if not rule_result["passed"]:
                results["passed"] = False
                results["rejected_by"].append(rule_def["id"])
                
                if rule_result.get("severity") == "warning":
                    results["warnings"].append(rule_result["message"])
        
        return results
    
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
