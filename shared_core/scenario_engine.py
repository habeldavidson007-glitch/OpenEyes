"""
Scenario Engine - Generates and manages usage scenarios for E-AR stress testing.

The Scenario Engine is the missing piece that transforms E-AR from abstract
primitive evolution into real-world language maturation. It provides:
- Diverse usage contexts (beginner, game dev, data, education, production)
- Complexity tiers (5-line script → 200-line program)
- Domain-specific pressure profiles
- Philosophy constraint validation
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Any, Optional


class ScenarioEngine:
    """Manages scenario library and generates test contexts for the swarm."""
    
    def __init__(self, scenarios_dir: str = "scenarios"):
        """
        Initialize Scenario Engine.
        
        Args:
            scenarios_dir: Path to directory containing scenario JSON files
        """
        self.scenarios_dir = Path(scenarios_dir)
        self.scenarios: List[Dict] = []
        self.load_scenarios()
    
    def load_scenarios(self) -> None:
        """Load all scenario files from the scenarios directory."""
        if not self.scenarios_dir.exists():
            print(f"⚠ Scenarios directory not found: {self.scenarios_dir}")
            return
        
        for file in self.scenarios_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    scenario = json.load(f)
                    self.scenarios.append(scenario)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠ Failed to load scenario {file}: {e}")
        
        print(f"✓ Loaded {len(self.scenarios)} scenarios")
    
    def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """Get a specific scenario by ID."""
        for scenario in self.scenarios:
            if scenario.get("id") == scenario_id:
                return scenario
        return None
    
    def get_scenarios_by_category(self, category: str) -> List[Dict]:
        """Get all scenarios matching a category."""
        return [s for s in self.scenarios if s.get("category") == category]
    
    def get_scenarios_by_domain(self, domain: str) -> List[Dict]:
        """Get all scenarios matching a domain."""
        return [s for s in self.scenarios if s.get("domain") == domain]
    
    def get_scenarios_by_complexity(self, tier: int) -> List[Dict]:
        """Get all scenarios matching a complexity tier."""
        return [s for s in self.scenarios if s.get("complexity_tier") == tier]
    
    def select_random_scenario(self, filters: Optional[Dict] = None) -> Optional[Dict]:
        """
        Select a random scenario, optionally filtered.
        
        Args:
            filters: Optional dict with keys like 'category', 'domain', 'complexity_tier'
        
        Returns:
            Random scenario matching filters, or None if no match
        """
        candidates = self.scenarios[:]
        
        if filters:
            for key, value in filters.items():
                if key in ["category", "domain", "complexity_tier"]:
                    candidates = [s for s in candidates if s.get(key) == value]
        
        if not candidates:
            return None
        
        return random.choice(candidates)
    
    def generate_scenario_batch(self, count: int, 
                                diversity: bool = True) -> List[Dict]:
        """
        Generate a batch of scenarios for stress testing.
        
        Args:
            count: Number of scenarios to select
            diversity: If True, ensure diverse categories/domains
        
        Returns:
            List of selected scenarios
        """
        if diversity and len(self.scenarios) >= count:
            # Ensure diversity by picking from different categories
            categories = set(s.get("category") for s in self.scenarios)
            selected = []
            
            # First pass: one from each category
            for category in categories:
                cat_scenarios = self.get_scenarios_by_category(category)
                if cat_scenarios and len(selected) < count:
                    selected.append(random.choice(cat_scenarios))
            
            # Fill remaining with random picks
            while len(selected) < count:
                remaining = [s for s in self.scenarios if s not in selected]
                if not remaining:
                    break
                selected.append(random.choice(remaining))
            
            return selected[:count]
        else:
            # Simple random selection
            return random.choices(self.scenarios, k=min(count, len(self.scenarios)))
    
    def get_all_categories(self) -> List[str]:
        """Get list of all unique categories."""
        return list(set(s.get("category", "unknown") for s in self.scenarios))
    
    def get_all_domains(self) -> List[str]:
        """Get list of all unique domains."""
        return list(set(s.get("domain", "unknown") for s in self.scenarios))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the scenario library."""
        categories = {}
        domains = {}
        tiers = {}
        
        for scenario in self.scenarios:
            cat = scenario.get("category", "unknown")
            dom = scenario.get("domain", "unknown")
            tier = scenario.get("complexity_tier", 0)
            
            categories[cat] = categories.get(cat, 0) + 1
            domains[dom] = domains.get(dom, 0) + 1
            tiers[tier] = tiers.get(tier, 0) + 1
        
        return {
            "total_scenarios": len(self.scenarios),
            "categories": categories,
            "domains": domains,
            "complexity_tiers": tiers
        }
    
    def validate_scenario(self, scenario: Dict) -> List[str]:
        """
        Validate a scenario structure.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        required_fields = ["id", "context", "task"]
        for field in required_fields:
            if field not in scenario:
                errors.append(f"Missing required field: {field}")
        
        if "expected_constructs" in scenario:
            if not isinstance(scenario["expected_constructs"], list):
                errors.append("expected_constructs must be a list")
        
        if "success_criteria" in scenario:
            if not isinstance(scenario["success_criteria"], dict):
                errors.append("success_criteria must be a dict")
        
        return errors


def create_sample_scenario(scenario_id: str, context: str, task: str,
                          category: str = "beginner", domain: str = "general",
                          complexity_tier: int = 1,
                          expected_constructs: Optional[List[str]] = None,
                          pressure_profile: str = "balanced",
                          philosophy_checks: Optional[List[str]] = None,
                          success_criteria: Optional[Dict] = None) -> Dict:
    """
    Helper function to create a new scenario template.
    
    This can be used to programmatically generate scenarios or as a reference
    for manual scenario creation.
    """
    return {
        "id": scenario_id,
        "category": category,
        "context": context,
        "task": task,
        "expected_constructs": expected_constructs or [],
        "pressure_profile": pressure_profile,
        "philosophy_checks": philosophy_checks or [],
        "complexity_tier": complexity_tier,
        "domain": domain,
        "success_criteria": success_criteria or {}
    }


# Convenience functions for direct usage
_default_engine: Optional[ScenarioEngine] = None

def get_engine(scenarios_dir: str = "scenarios") -> ScenarioEngine:
    """Get or create the default scenario engine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = ScenarioEngine(scenarios_dir)
    return _default_engine


def load_scenarios(scenarios_dir: str = "scenarios") -> List[Dict]:
    """Load all scenarios and return them."""
    engine = get_engine(scenarios_dir)
    return engine.scenarios


def select_scenario(filters: Optional[Dict] = None) -> Optional[Dict]:
    """Select a random scenario with optional filters."""
    engine = get_engine()
    return engine.select_random_scenario(filters)


def get_scenario_stats() -> Dict[str, Any]:
    """Get statistics about loaded scenarios."""
    engine = get_engine()
    return engine.get_statistics()


if __name__ == "__main__":
    # Demo: show scenario library statistics
    engine = ScenarioEngine()
    
    print("\n=== SCENARIO ENGINE STATISTICS ===\n")
    stats = engine.get_statistics()
    print(f"Total scenarios: {stats['total_scenarios']}")
    print(f"\nCategories: {stats['categories']}")
    print(f"Domains: {stats['domains']}")
    print(f"Complexity tiers: {stats['complexity_tiers']}")
    
    print("\n=== SAMPLE SCENARIOS ===\n")
    for scenario in engine.scenarios[:3]:
        print(f"ID: {scenario['id']}")
        print(f"Context: {scenario['context']}")
        print(f"Task: {scenario['task']}")
        print(f"Category: {scenario['category']}")
        print("---")
