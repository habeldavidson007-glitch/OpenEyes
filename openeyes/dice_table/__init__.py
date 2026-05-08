"""
Dice Table — Layer 3: Würfel Spiel Fragment Assembler

Named after Mozart's 18th-century compositional game where dice rolls select 
pre-written bars to build a minuet, the Dice Table layer selects Survivor 
fragments and assembles them into a coherent output.

The Dice Table is a lookup matrix, not a model. It maps score ranges, domains, 
and philosophical alignment values to selection rules. It is deterministic 
given the same inputs.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DiceTableRow:
    """A single row in the Dice Table."""
    score_range: Tuple[int, int]  # (min, max) inclusive
    fragment_class: str
    include_confidence_note: bool = False
    require_source_citation: bool = True
    halt_message: Optional[str] = None


class DiceTable:
    """
    Fragment selection and assembly engine.
    
    Given Survivor fragments (post-Monte Carlo), selects which fragments to 
    include in the final answer and sequences them into a coherent chain.
    """
    
    def __init__(self, domain: str = "general", table_path: Optional[str] = None):
        """
        Initialize Dice Table.
        
        Args:
            domain: Domain type (medical, legal, engineering, etc.)
            table_path: Optional path to custom Dice Table JSON file
        """
        self.domain = domain
        self.table_path = Path(table_path) if table_path else None
        self.rows: List[DiceTableRow] = []
        
        if self.table_path and self.table_path.exists():
            self.load_table()
        else:
            self._load_default_table()
    
    def load_table(self) -> None:
        """Load Dice Table from JSON file."""
        try:
            with open(self.table_path, 'r') as f:
                data = json.load(f)
                
            self.rows = []
            for row_data in data.get("rows", []):
                score_range = tuple(row_data.get("score_range", [0, 100]))
                row = DiceTableRow(
                    score_range=score_range,
                    fragment_class=row_data.get("fragment_class", ""),
                    include_confidence_note=row_data.get("include_confidence_note", False),
                    require_source_citation=row_data.get("require_source_citation", True),
                    halt_message=row_data.get("halt_message")
                )
                self.rows.append(row)
            
            print(f"✓ Loaded {len(self.rows)} Dice Table rows from {self.table_path.name}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Failed to load Dice Table: {e}")
            self._load_default_table()
    
    def _load_default_table(self) -> None:
        """Load default Dice Table based on domain."""
        # Default medical domain table per spec
        if self.domain == "medical":
            self.rows = [
                DiceTableRow(
                    score_range=(90, 100),
                    fragment_class="first_line_treatment",
                    include_confidence_note=False,
                    require_source_citation=True
                ),
                DiceTableRow(
                    score_range=(70, 89),
                    fragment_class="second_line_with_caution",
                    include_confidence_note=True,
                    require_source_citation=True
                ),
                DiceTableRow(
                    score_range=(0, 69),
                    fragment_class="HALT",
                    include_confidence_note=False,
                    require_source_citation=False,
                    halt_message="Insufficient confidence. Consult a specialist."
                ),
            ]
        else:
            # Generic table for other domains
            self.rows = [
                DiceTableRow(
                    score_range=(80, 100),
                    fragment_class="high_confidence",
                    include_confidence_note=False,
                    require_source_citation=True
                ),
                DiceTableRow(
                    score_range=(60, 79),
                    fragment_class="medium_confidence",
                    include_confidence_note=True,
                    require_source_citation=True
                ),
                DiceTableRow(
                    score_range=(0, 59),
                    fragment_class="HALT",
                    include_confidence_note=False,
                    require_source_citation=False,
                    halt_message="Insufficient confidence for this domain."
                ),
            ]
    
    def select_fragments(self, survivors: List[Dict]) -> Tuple[List[Dict], bool, Optional[str]]:
        """
        Select fragments from survivors based on Dice Table rules.
        
        Args:
            survivors: List of survivor fragment dicts with 'mean_score' field
            
        Returns:
            Tuple of (selected_fragments, should_halt, halt_message)
        """
        if not survivors:
            return [], True, "No fragments survived Monte Carlo evaluation."
        
        selected = []
        should_halt = False
        halt_message = None
        
        # Sort survivors by score descending
        sorted_survivors = sorted(survivors, key=lambda x: x.get("mean_score", 0), reverse=True)
        
        for survivor in sorted_survivors:
            score = survivor.get("mean_score", 0)
            
            # Find matching row in Dice Table
            matching_row = self._find_matching_row(score)
            
            if not matching_row:
                continue
            
            if matching_row.fragment_class == "HALT":
                should_halt = True
                halt_message = matching_row.halt_message or "Insufficient confidence."
                break
            
            # Add fragment to selection
            selected.append({
                **survivor,
                "fragment_class": matching_row.fragment_class,
                "include_confidence_note": matching_row.include_confidence_note,
                "require_source_citation": matching_row.require_source_citation
            })
        
        # Apply sequencing rules
        if selected:
            selected = self._sequence_fragments(selected)
        
        return selected, should_halt, halt_message
    
    def _find_matching_row(self, score: float) -> Optional[DiceTableRow]:
        """Find the Dice Table row matching a score."""
        for row in self.rows:
            min_score, max_score = row.score_range
            if min_score <= score <= max_score:
                return row
        return None
    
    def _sequence_fragments(self, fragments: List[Dict]) -> List[Dict]:
        """
        Sequence fragments according to domain-specific ordering rules.
        
        Rules (per spec):
        1. Safety/contraindication fragments always appear before treatment fragments
        2. Evidence-base fragments always appear before dosage fragments
        3. Uncertainty notes always appear at the end
        """
        # Priority order for fragment classes
        priority_order = {
            "contraindication": 0,
            "safety": 1,
            "allergy_cross_reactivity": 2,
            "evidence_base": 3,
            "first_line_treatment": 4,
            "second_line_with_caution": 5,
            "dosage_guidance": 6,
            "high_confidence": 4,
            "medium_confidence": 5,
            "uncertainty_note": 99,
        }
        
        def get_priority(fragment: Dict) -> int:
            tags = fragment.get("tags", [])
            fragment_class = fragment.get("fragment_class", "")
            
            # Check tags first
            for tag in tags:
                if tag in priority_order:
                    return priority_order[tag]
            
            # Fall back to fragment class
            return priority_order.get(fragment_class, 50)
        
        # Sort by priority
        sequenced = sorted(fragments, key=get_priority)
        
        return sequenced
    
    def assemble_output(self, selected_fragments: List[Dict]) -> Dict[str, Any]:
        """
        Assemble selected fragments into final output structure.
        
        Args:
            selected_fragments: List of selected and sequenced fragments
            
        Returns:
            Assembled output dict with answer, confidence, traceability info
        """
        if not selected_fragments:
            return {
                "answer": None,
                "confidence": 0.0,
                "fragments_used": [],
                "traceability": None
            }
        
        # Build answer text from fragments
        answer_parts = []
        total_confidence = 0.0
        fragments_trace = []
        
        for frag in selected_fragments:
            content = frag.get("content", "")
            score = frag.get("mean_score", 0)
            source = frag.get("source", "Unknown")
            source_url = frag.get("source_url")
            fragment_id = frag.get("fragment_id", "unknown")
            
            answer_parts.append(content)
            total_confidence += score
            
            # Build trace entry
            trace_entry = {
                "fragment_id": fragment_id,
                "score": score,
                "source": source,
                "fragment_class": frag.get("fragment_class", "unknown")
            }
            if source_url:
                trace_entry["source_url"] = source_url
            
            fragments_trace.append(trace_entry)
            
            # Add confidence note if required
            if frag.get("include_confidence_note"):
                answer_parts.append(f"[Confidence: {score:.1f}%]")
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(selected_fragments) if selected_fragments else 0.0
        
        # Build traceability footer
        traceability = {
            "fragment_ids": [f["fragment_id"] for f in fragments_trace],
            "average_confidence": round(avg_confidence, 2),
            "sources": list(set(f["source"] for f in fragments_trace)),
            "assembly_timestamp": None  # Will be set by caller
        }
        
        # Join answer parts
        answer = "\n\n".join(answer_parts)
        
        return {
            "answer": answer,
            "confidence": round(avg_confidence, 2),
            "fragments_used": fragments_trace,
            "traceability": traceability
        }


__all__ = ["DiceTable", "DiceTableRow"]