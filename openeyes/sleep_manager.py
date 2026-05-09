"""
OpenEyes Sleep/Wake State Manager
Neuro-inspired lifecycle management for knowledge consolidation.

Mimics biological sleep cycles:
- WAKE: Active query processing, temporary buffer storage (Neural Replay)
- SLEEP: Consolidation, pruning, integration (Memory Consolidation & REM)
- TEMPLATE GENERATION: Learn from failed queries to create new axiom templates
"""

import time
import threading
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum

from .binary_lib import BinaryLibraryEngine, NeuralReplayBuffer, SleepModeConsolidator

class SystemState(Enum):
    WAKE = "wake"
    SLEEP = "sleep"
    CONSOLIDATING = "consolidating"

class SleepWakeManager:
    """
    Manages the lifecycle of OpenEyes between active (wake) and consolidation (sleep) states.
    
    Biological Parallels:
    - Wake: Hippocampus stores temporary patterns (Neural Replay buffer)
    - Sleep SWS: Memory consolidation to Neocortex (permanent library)
    - Sleep REM: Creative integration across domains
    - Pruning: Synaptic homeostasis (removing unused connections)
    - Template Generation: Induce new axiom templates from failed queries
    """
    
    def __init__(self, 
                 library_path: str,
                 binary_path: Optional[str] = None,
                 auto_sleep_minutes: int = 5,
                 on_state_change: Optional[Callable[[SystemState], None]] = None):
        """
        Initialize Sleep/Wake Manager.
        
        Args:
            library_path: Path to main fragment library JSON
            binary_path: Path to binary .oelib file (default: library_path + .oelib)
            auto_sleep_minutes: Minutes of inactivity before auto-sleep
            on_state_change: Callback function when state changes
        """
        self.library_path = Path(library_path)
        self.binary_path = Path(binary_path) if binary_path else self.library_path.with_suffix('.oelib')
        self.auto_sleep_minutes = auto_sleep_minutes
        self.on_state_change = on_state_change
        
        self.state = SystemState.WAKE
        self.last_activity = datetime.now()
        self.neural_replay_buffer: List[Dict[str, Any]] = []  # Temporary success patterns
        self.failed_queries_buffer: List[Dict[str, Any]] = []  # Failed queries for template generation
        self.binary_engine = BinaryLibraryEngine()
        
        self._lock = threading.Lock()
        self._sleep_timer: Optional[threading.Timer] = None
        
        # Load library on startup
        self.library_data = self._load_library()
        
    def _load_library(self) -> Dict[str, Any]:
        """Load library from binary if exists, otherwise JSON."""
        if self.binary_path.exists():
            try:
                data = self.binary_engine.load_from_file(str(self.binary_path))
                print(f"[WAKE] Loaded binary library ({self.binary_path.stem}.oelib) instantly")
                return data
            except Exception as e:
                print(f"[WARN] Binary load failed: {e}, falling back to JSON")
        
        if self.library_path.exists():
            with open(self.library_path, 'r') as f:
                data = json.load(f)
            print(f"[WAKE] Loaded JSON library ({len(data.get('fragments', {}))} fragments)")
            return data
        
        return {"fragments": {}, "metadata": {}}
    
    def record_activity(self, query_result: Dict[str, Any]) -> None:
        """
        Record successful query pattern in Neural Replay buffer.
        Called after every successful query during WAKE state.
        
        Args:
            query_result: Dictionary with query, answer, fragments_used, confidence
        """
        with self._lock:
            self.last_activity = datetime.now()
            
            # Only record successful high-confidence results
            if query_result.get('confidence', 0) >= 70:
                replay_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'canonical_query': query_result.get('canonical_form', ''),
                    'domain': query_result.get('domain', 'unknown'),
                    'tier': query_result.get('tier', 3),
                    'fragments_used': query_result.get('fragment_ids', []),
                    'confidence': query_result.get('confidence', 0),
                    'success_pattern': {
                        'had_counter_argument': any('counter' in str(f) for f in query_result.get('fragment_ids', [])),
                        'had_latest_data': any('latest' in str(f) for f in query_result.get('fragment_ids', [])),
                        'grundy_robust': query_result.get('grundy_value', -1) == 0
                    }
                }
                self.neural_replay_buffer.append(replay_entry)
                
                # Keep buffer manageable (last 100 successes)
                if len(self.neural_replay_buffer) > 100:
                    self.neural_replay_buffer = self.neural_replay_buffer[-100:]
            
            # Reset auto-sleep timer
            self._reset_sleep_timer()
    
    def record_failure(self, query: str, domain: str, reason: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record failed query for template generation during sleep.
        
        Args:
            query: The failed query
            domain: The domain of the query
            reason: Why it failed (e.g., "HALT_LOW_EVIDENCE", "no_fragments")
            context: Additional context about the failure
        """
        with self._lock:
            failure_entry = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'domain': domain,
                'failure_reason': reason,
                'context': context or {}
            }
            self.failed_queries_buffer.append(failure_entry)
            
            # Keep buffer manageable (last 50 failures)
            if len(self.failed_queries_buffer) > 50:
                self.failed_queries_buffer = self.failed_queries_buffer[-50:]
    
    def _reset_sleep_timer(self) -> None:
        """Reset or start the auto-sleep timer."""
        if self._sleep_timer:
            self._sleep_timer.cancel()
        
        self._sleep_timer = threading.Timer(
            self.auto_sleep_minutes * 60,
            self.trigger_sleep
        )
        self._sleep_timer.daemon = True
        self._sleep_timer.start()
    
    def trigger_sleep(self) -> Dict[str, Any]:
        """
        Enter SLEEP state: consolidate, prune, integrate, generate templates, and save binary.
        Can be called manually or triggered automatically by inactivity.
        
        Returns:
            Report of consolidation actions taken
        """
        with self._lock:
            if self.state == SystemState.SLEEP:
                return {"status": "already_sleeping"}
            
            old_state = self.state
            self.state = SystemState.CONSOLIDATING
            self._change_state_callback(SystemState.CONSOLIDATING)
            
            report = {
                "started_at": datetime.now().isoformat(),
                "replay_count": len(self.neural_replay_buffer),
                "failed_query_count": len(self.failed_queries_buffer),
                "actions": []
            }
            
            try:
                # Step 1: Memory Consolidation (SWS-like)
                consolidation_report = self._consolidate_patterns()
                report["actions"].append({"phase": "consolidation", **consolidation_report})
                
                # Step 2: Synaptic Pruning
                pruning_report = self._prune_unused_fragments()
                report["actions"].append({"phase": "pruning", **pruning_report})
                
                # Step 3: REM Integration (Cross-domain linking)
                rem_report = self._rem_integration()
                report["actions"].append({"phase": "rem_integration", **rem_report})
                
                # Step 4: Template Generation (Learn from failures)
                template_report = self._generate_axiom_templates()
                report["actions"].append({"phase": "template_generation", **template_report})
                
                # Step 5: Save Binary Library
                self._save_binary_library()
                report["actions"].append({
                    "phase": "binary_save",
                    "status": "success",
                    "path": str(self.binary_path)
                })
                
            finally:
                self.state = SystemState.SLEEP
                self._change_state_callback(SystemState.SLEEP)
                report["completed_at"] = datetime.now().isoformat()
            
            return report
    
    def _change_state_callback(self, new_state: SystemState) -> None:
        """Notify external systems of state change."""
        if self.on_state_change:
            try:
                self.on_state_change(new_state)
            except Exception as e:
                print(f"[ERROR] State change callback failed: {e}")
    
    def _consolidate_patterns(self) -> Dict[str, Any]:
        """
        Convert frequent success patterns from replay buffer into permanent Synapses.
        Mimics hippocampus-to-neocortex transfer.
        """
        if not self.neural_replay_buffer:
            return {"status": "no_patterns_to_consolidate"}
        
        # Analyze patterns
        pattern_frequency: Dict[str, int] = {}
        for entry in self.neural_replay_buffer:
            key = f"{entry['domain']}:{entry['tier']}:{entry['canonical_query']}"
            pattern_frequency[key] = pattern_frequency.get(key, 0) + 1
        
        # Promote frequent patterns to synapses
        consolidated_count = 0
        for pattern_key, count in pattern_frequency.items():
            if count >= 2:  # Seen multiple times
                # In real implementation, this would update Compiled Logic Index
                consolidated_count += 1
        
        self.neural_replay_buffer.clear()  # Clear buffer after consolidation
        
        return {
            "status": "success",
            "patterns_analyzed": len(pattern_frequency),
            "synapses_created": consolidated_count
        }
    
    def _prune_unused_fragments(self) -> Dict[str, Any]:
        """
        Remove or deprioritize fragments not used recently.
        Mimics Synaptic Homeostasis Hypothesis.
        """
        # Track which fragments were used in replay buffer
        used_fragment_ids = set()
        for entry in self.neural_replay_buffer:
            used_fragment_ids.update(entry.get('fragments_used', []))
        
        # In real implementation: decrease weights of unused fragments
        # or mark for removal if unused for N days
        
        total_fragments = len(self.library_data.get('fragments', {}))
        used_count = len(used_fragment_ids)
        
        return {
            "status": "success",
            "total_fragments": total_fragments,
            "recently_used": used_count,
            "unused_candidates_for_pruning": total_fragments - used_count
        }
    
    def _rem_integration(self) -> Dict[str, Any]:
        """
        Attempt cross-domain connections (creative insights).
        Mimics REM sleep integration of disparate memories.
        """
        # In real implementation: use Category Theory functors
        # to find structural similarities between domains
        
        domains = set()
        for entry in self.neural_replay_buffer:
            domains.add(entry.get('domain', 'unknown'))
        
        integration_attempts = 0
        if len(domains) > 1:
            # Multiple domains active: look for connections
            integration_attempts = len(domains) * (len(domains) - 1) // 2
        
        return {
            "status": "success",
            "active_domains": list(domains),
            "cross_domain_integrations_attempted": integration_attempts
        }
    
    def _generate_axiom_templates(self) -> Dict[str, Any]:
        """
        Analyze failed queries and generate new axiom templates.
        This is the key learning mechanism: turn failures into future successes.
        
        Process:
        1. Group failures by domain
        2. Find common patterns in failed queries
        3. Generate template structures that would handle similar queries
        4. Save templates to axioms.py or separate template file
        """
        if not self.failed_queries_buffer:
            return {"status": "no_failures_to_learn_from"}
        
        # Group failures by domain
        domain_failures: Dict[str, List[Dict[str, Any]]] = {}
        for failure in self.failed_queries_buffer:
            domain = failure.get('domain', 'unknown')
            if domain not in domain_failures:
                domain_failures[domain] = []
            domain_failures[domain].append(failure)
        
        generated_templates = []
        
        for domain, failures in domain_failures.items():
            # Analyze patterns in failed queries
            query_keywords = []
            for f in failures:
                query = f.get('query', '').lower()
                # Extract key nouns/verbs (simplified)
                words = [w for w in query.split() if len(w) > 3 and w not in {'what', 'that', 'this', 'which', 'where', 'when', 'why', 'how'}]
                query_keywords.extend(words)
            
            # Find most common keywords
            keyword_freq: Dict[str, int] = {}
            for kw in query_keywords:
                keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
            
            # Generate template for top keywords
            top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for keyword, count in top_keywords:
                if count >= 2:  # Pattern seen multiple times
                    template = self._create_axiom_template(domain, keyword, failures)
                    if template:
                        generated_templates.append(template)
        
        # Save generated templates
        if generated_templates:
            self._save_axiom_templates(generated_templates)
        
        # Clear failure buffer after processing
        self.failed_queries_buffer.clear()
        
        return {
            "status": "success",
            "domains_analyzed": len(domain_failures),
            "templates_generated": len(generated_templates),
            "templates": [t.get('name', 'unknown') for t in generated_templates]
        }
    
    def _create_axiom_template(self, domain: str, keyword: str, failures: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Create an axiom template based on a keyword pattern in failed queries.
        
        This uses first-principles reasoning to generate a template that can
        handle similar queries in the future.
        """
        # Map domains to axiom categories
        domain_to_category = {
            'history': 'CAUSALITY',
            'philosophy': 'GAME_THEORY',
            'economics': 'EQUILIBRIUM',
            'sociology': 'STRUCTURE',
            'psychology': 'OPTIMIZATION',
            'biology': 'EVOLUTION',
            'physics': 'CONSERVATION',
            'chemistry': 'CONSERVATION',
            'political_science': 'GAME_THEORY',
            'linguistics': 'INFORMATION'
        }
        
        category = domain_to_category.get(domain.lower(), 'STRUCTURE')
        
        # Generate template structure
        template_id = f"AUTO_{category}_{keyword.upper()[:8]}"
        
        template = {
            'id': template_id,
            'name': f"Auto-generated {keyword.title()} Template",
            'category': category,
            'domain': domain,
            'trigger_keyword': keyword,
            'description': f"Template for handling {domain} queries about {keyword}",
            'formal_statement': f"Query({keyword}) → ApplyFirstPrinciples({category})",
            'applicable_domains': [domain],
            'derivation_rules': [f"{keyword}_analysis", "first_principles_deduction"],
            'auto_generated': True,
            'generation_timestamp': datetime.now().isoformat(),
            'based_on_failures': len(failures)
        }
        
        return template
    
    def _save_axiom_templates(self, templates: List[Dict[str, Any]]) -> None:
        """
        Save generated axiom templates to a file for loading on next startup.
        """
        template_file = self.library_path.parent / "auto_axiom_templates.json"
        
        # Load existing templates if any
        existing_templates = []
        if template_file.exists():
            try:
                with open(template_file, 'r') as f:
                    existing_templates = json.load(f)
            except Exception:
                existing_templates = []
        
        # Merge with new templates (avoid duplicates)
        existing_ids = {t.get('id') for t in existing_templates}
        new_templates = [t for t in templates if t.get('id') not in existing_ids]
        all_templates = existing_templates + new_templates
        
        # Save
        with open(template_file, 'w') as f:
            json.dump(all_templates, f, indent=2)
        
        print(f"[SLEEP] Saved {len(new_templates)} new axiom templates to {template_file}")
    
    def _save_binary_library(self) -> None:
        """Serialize and save current library to binary format."""
        self.binary_engine.save_to_file(self.library_data, str(self.binary_path))
        stats = self.binary_engine.get_stats(
            self.binary_engine.serialize(self.library_data)
        )
        print(f"[SLEEP] Binary library saved: {stats['compression_ratio']} compression")
    
    def wake_up(self) -> None:
        """
        Exit sleep state, reload library, resume active processing.
        """
        with self._lock:
            self.library_data = self._load_library()
            self.state = SystemState.WAKE
            self.last_activity = datetime.now()
            self._change_state_callback(SystemState.WAKE)
            print("[WAKE] System resumed active state")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "state": self.state.value,
            "last_activity": self.last_activity.isoformat(),
            "replay_buffer_size": len(self.neural_replay_buffer),
            "failed_queries_buffer_size": len(self.failed_queries_buffer),
            "fragment_count": len(self.library_data.get('fragments', {})),
            "binary_exists": self.binary_path.exists(),
            "auto_sleep_in_minutes": self.auto_sleep_minutes
        }


# Convenience function for standalone usage
def run_sleep_cycle(library_path: str, auto_sleep_minutes: int = 5) -> Dict[str, Any]:
    """
    Initialize manager and wait for auto-sleep trigger.
    For testing purposes.
    """
    manager = SleepWakeManager(library_path, auto_sleep_minutes=auto_sleep_minutes)
    print(f"Manager started in {manager.state.value} mode")
    print(f"Will auto-sleep after {auto_sleep_minutes} minutes of inactivity")
    print("Call manager.trigger_sleep() to force sleep now")
    return manager.get_status()
