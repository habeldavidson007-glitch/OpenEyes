"""
OpenEyes Dice Table — Würfelspiel Fragment Assembler

Layer 3 of the OpenEyes engine. Given Survivor fragments (post-Monte Carlo),
selects which fragments to include in the final answer and sequences them
into a coherent chain using Musikalisches Würfelspiel (Musical Dice Game) theory.

The Dice Table is a lookup matrix, not a model. It maps:
(score range × domain × philosophy) → fragment selection rules
"""

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DiceTableRow:
    """A single row in the Dice Table."""
    score_range: Tuple[int, int]  # [min, max] inclusive
    fragment_class: str  # e.g., "first_line_treatment", "HALT"
    include_confidence_note: bool = False
    require_source_citation: bool = True
    halt_message: Optional[str] = None
    priority: int = 0  # For ordering within same score range
    
    def matches_score(self, score: float) -> bool:
        """Check if a score falls within this row's range."""
        return self.score_range[0] <= score <= self.score_range[1]


@dataclass
class AssembledOutput:
    """The final assembled output from the Dice Table."""
    answer: str
    confidence: float
    fragments_used: List[Dict[str, Any]]
    philosophy_checks_passed: List[str]
    trace_id: str
    halt: bool = False
    halt_reason: Optional[str] = None
    recommendation: Optional[str] = None
    confidence_note: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "answer": self.answer,
            "confidence": self.confidence,
            "fragments_used": self.fragments_used,
            "philosophy_checks_passed": self.philosophy_checks_passed,
            "trace_id": self.trace_id,
            "halt": self.halt
        }
        if self.halt_reason:
            result["halt_reason"] = self.halt_reason
        if self.recommendation:
            result["recommendation"] = self.recommendation
        if self.confidence_note:
            result["confidence_note"] = self.confidence_note
        return result


class DiceTable:
    """
    The Dice Table lookup matrix for fragment selection.
    
    Maps (Monte Carlo score range × domain × philosophy) to fragment
    selection rules. Deterministic given the same inputs.
    """
    
    DEFAULT_SCORE_RANGES = [
        (90, 100),   # High confidence
        (70, 89),    # Medium confidence  
        (60, 69),    # Low confidence (borderline)
        (0, 59),     # Insufficient confidence → HALT
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the Dice Table.
        
        Args:
            config_path: Path to Dice Table JSON configuration.
                        If None, uses default medical table.
        """
        self.config_path = config_path
        self.tables: Dict[str, Dict[str, Any]] = {}  # domain → philosophy → config
        
        # Load default tables
        self._load_default_tables()
        
        # Load custom config if provided
        if config_path and config_path.exists():
            self._load_config(config_path)
    
    def _load_default_tables(self):
        """Load built-in default Dice Tables."""
        
        # Default medical domain table
        self.tables["medical"] = {
            "do_no_harm": {
                "domain": "medical",
                "philosophy": "do_no_harm",
                "rows": [
                    {
                        "score_range": [90, 100],
                        "fragment_class": "first_line_treatment",
                        "include_confidence_note": False,
                        "require_source_citation": True,
                        "priority": 1
                    },
                    {
                        "score_range": [70, 89],
                        "fragment_class": "second_line_with_caution",
                        "include_confidence_note": True,
                        "require_source_citation": True,
                        "priority": 2
                    },
                    {
                        "score_range": [60, 69],
                        "fragment_class": "third_line_specialist_referral",
                        "include_confidence_note": True,
                        "require_source_citation": True,
                        "priority": 3
                    },
                    {
                        "score_range": [0, 59],
                        "fragment_class": "HALT",
                        "halt_message": "Insufficient confidence. Consult a specialist.",
                        "require_source_citation": False,
                        "priority": 4
                    }
                ]
            }
        }
        
        # Default legal domain table
        self.tables["legal"] = {
            "jurisdiction_consistency": {
                "domain": "legal",
                "philosophy": "jurisdiction_consistency",
                "rows": [
                    {
                        "score_range": [90, 100],
                        "fragment_class": "binding_precedent",
                        "include_confidence_note": False,
                        "require_source_citation": True,
                        "priority": 1
                    },
                    {
                        "score_range": [70, 89],
                        "fragment_class": "persuasive_authority",
                        "include_confidence_note": True,
                        "require_source_citation": True,
                        "priority": 2
                    },
                    {
                        "score_range": [0, 69],
                        "fragment_class": "HALT",
                        "halt_message": "Insufficient legal authority. Consult an attorney.",
                        "require_source_citation": False,
                        "priority": 3
                    }
                ]
            }
        }
        
        # Default general domain table
        self.tables["general"] = {
            "evidence_based": {
                "domain": "general",
                "philosophy": "evidence_based",
                "rows": [
                    {
                        "score_range": [90, 100],
                        "fragment_class": "verified_fact",
                        "include_confidence_note": False,
                        "require_source_citation": True,
                        "priority": 1
                    },
                    {
                        "score_range": [70, 89],
                        "fragment_class": "well_supported_claim",
                        "include_confidence_note": False,
                        "require_source_citation": True,
                        "priority": 2
                    },
                    {
                        "score_range": [60, 69],
                        "fragment_class": "tentative_claim",
                        "include_confidence_note": True,
                        "require_source_citation": True,
                        "priority": 3
                    },
                    {
                        "score_range": [0, 59],
                        "fragment_class": "HALT",
                        "halt_message": "Insufficient evidence to provide an answer.",
                        "require_source_citation": False,
                        "priority": 4
                    }
                ]
            }
        }
    
    def _load_config(self, config_path: Path):
        """Load custom Dice Table configuration from JSON."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Config can contain multiple domain tables
            if isinstance(config, list):
                for table_config in config:
                    self._register_table(table_config)
            elif isinstance(config, dict):
                self._register_table(config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load Dice Table config: {e}")
    
    def _register_table(self, table_config: Dict[str, Any]):
        """Register a single Dice Table configuration."""
        domain = table_config.get("domain", "general")
        philosophy = table_config.get("philosophy", "evidence_based")
        
        if domain not in self.tables:
            self.tables[domain] = {}
        
        self.tables[domain][philosophy] = table_config
    
    def lookup(
        self,
        score: float,
        domain: str = "general",
        philosophy: str = "evidence_based"
    ) -> Optional[DiceTableRow]:
        """
        Look up the Dice Table for a given score, domain, and philosophy.
        
        Args:
            score: Monte Carlo survival score (0-100)
            domain: Domain name (e.g., "medical", "legal")
            philosophy: Philosophy alignment (e.g., "do_no_harm")
            
        Returns:
            Matching DiceTableRow, or None if no match found
        """
        # Get table for domain/philosophy
        domain_table = self.tables.get(domain, {})
        table_config = domain_table.get(philosophy)
        
        if not table_config:
            # Fall back to general domain
            domain_table = self.tables.get("general", {})
            table_config = domain_table.get(philosophy)
        
        if not table_config:
            # Fall back to default general/evidence_based
            table_config = self.tables.get("general", {}).get("evidence_based")
        
        if not table_config:
            return None
        
        # Parse rows and find matching score range
        rows = table_config.get("rows", [])
        matching_rows = []
        
        for row_data in rows:
            score_range = tuple(row_data.get("score_range", [0, 100]))
            row = DiceTableRow(
                score_range=score_range,
                fragment_class=row_data.get("fragment_class", "unknown"),
                include_confidence_note=row_data.get("include_confidence_note", False),
                require_source_citation=row_data.get("require_source_citation", True),
                halt_message=row_data.get("halt_message"),
                priority=row_data.get("priority", 0)
            )
            
            if row.matches_score(score):
                matching_rows.append(row)
        
        if not matching_rows:
            return None
        
        # Return highest priority match (lowest priority number)
        matching_rows.sort(key=lambda r: r.priority)
        return matching_rows[0]
    
    def get_all_tables(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered Dice Tables."""
        return self.tables.copy()


class WurfelspielAssembler:
    """
    Assembles Survivor fragments into coherent output using the Dice Table.
    
    Implements fragment sequencing rules:
    1. Safety/contraindication fragments always appear before treatment fragments
    2. Evidence-base fragments always appear before dosage fragments
    3. Uncertainty notes always appear at the end
    4. Every output includes a traceability footer
    """
    
    # Fragment class ordering priorities (lower = earlier in output)
    SEQUENCE_PRIORITY = {
        "safety_warning": 1,
        "contraindication": 2,
        "allergy_cross_reactivity": 3,
        "evidence_base": 4,
        "first_line_treatment": 5,
        "second_line_with_caution": 6,
        "third_line_specialist_referral": 7,
        "dosage_guidance": 8,
        "monitoring_requirements": 9,
        "uncertainty_note": 10,
        "confidence_note": 11,
        # Default for unknown classes
        "unknown": 5
    }
    
    def __init__(self, dice_table: Optional[DiceTable] = None):
        """
        Initialize the assembler.
        
        Args:
            dice_table: DiceTable instance. Creates default if None.
        """
        self.dice_table = dice_table or DiceTable()
    
    def assemble(
        self,
        survivors: List[Dict[str, Any]],
        domain: str = "general",
        philosophy: str = "evidence_based",
        trace_id: Optional[str] = None,
        original_query: Optional[str] = None  # NEW: Added original query parameter
    ) -> AssembledOutput:
        """
        Assemble survivor fragments into final output.
        
        Args:
            survivors: List of survivor fragments with scores
            domain: Domain for Dice Table lookup
            philosophy: Philosophy alignment for Dice Table lookup
            trace_id: Unique identifier for this query trace
            original_query: The original user query for relevance filtering
            
        Returns:
            AssembledOutput with answer or HALT
        """
        import uuid
        from datetime import datetime
        
        if trace_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_id = f"oe_{timestamp}_{uuid.uuid4().hex[:4]}"
        
        if not survivors:
            return AssembledOutput(
                answer=None,
                confidence=0.0,
                fragments_used=[],
                philosophy_checks_passed=[],
                trace_id=trace_id,
                halt=True,
                halt_reason="No fragments survived Monte Carlo evaluation.",
                recommendation="Consider reformulating your query or consulting a specialist."
            )
        
        # CRITICAL FIX: Filter fragments by relevance to original query
        if original_query:
            survivors = self._filter_by_query_relevance(survivors, original_query)
        
        if not survivors:
            return AssembledOutput(
                answer=None,
                confidence=0.0,
                fragments_used=[],
                philosophy_checks_passed=[],
                trace_id=trace_id,
                halt=True,
                halt_reason="No fragments relevant to the query survived filtering.",
                recommendation="The system lacks verified knowledge on this specific topic."
            )
        
        # Calculate average confidence
        avg_score = sum(s.get("score", 0) for s in survivors) / len(survivors)
        
        # Look up Dice Table
        dice_row = self.dice_table.lookup(avg_score, domain, philosophy)
        
        if dice_row is None:
            return AssembledOutput(
                answer=None,
                confidence=avg_score,
                fragments_used=[],
                philosophy_checks_passed=[],
                trace_id=trace_id,
                halt=True,
                halt_reason=f"No Dice Table rule found for score {avg_score} in domain '{domain}'.",
                recommendation="System configuration error. Please report this issue."
            )
        
        # Check for HALT
        if dice_row.fragment_class == "HALT":
            return AssembledOutput(
                answer=None,
                confidence=avg_score,
                fragments_used=[],
                philosophy_checks_passed=[],
                trace_id=trace_id,
                halt=True,
                halt_reason=dice_row.halt_message or "Insufficient confidence.",
                recommendation="Consult a certified professional in this domain."
            )
        
        # Sequence fragments according to rules
        sequenced_fragments = self._sequence_fragments(survivors)
        
        # Build answer text with original query context
        answer_text = self._build_answer_text(sequenced_fragments, dice_row, original_query)
        
        # Add confidence note if required
        confidence_note = None
        if dice_row.include_confidence_note:
            confidence_note = (
                f"Note: This answer has moderate confidence ({avg_score:.1f}%). "
                f"Consider seeking additional verification."
            )
        
        # Prepare fragments_used metadata - preserve ALL original fields including reasoning_role
        fragments_metadata = []
        for frag in sequenced_fragments:
            meta = {
                "fragment_id": frag.get("fragment_id", "unknown"),
                "content": frag.get("content", ""),
                "score": frag.get("score", 0),
                "source": frag.get("source", "Unknown"),
                "source_url": frag.get("source_url", ""),
                # CRITICAL: Preserve reasoning_role for final philosophy check
                "reasoning_role": frag.get("reasoning_role", "unknown")
            }
            fragments_metadata.append(meta)
        
        return AssembledOutput(
            answer=answer_text,
            confidence=round(avg_score, 1),
            fragments_used=fragments_metadata,
            philosophy_checks_passed=[f"{domain}_{philosophy}"],
            trace_id=trace_id,
            halt=False,
            confidence_note=confidence_note
        )
    
    def _filter_by_query_relevance(self, fragments: List[Dict[str, Any]], original_query: str) -> List[Dict[str, Any]]:
        """
        Filter fragments to only include those relevant to the original query.
        
        Uses keyword matching between query and fragment's sub_question field.
        This prevents wrong-domain fragments from being used in answers.
        """
        if not fragments:
            return []
        
        # Extract keywords from original query
        query_keywords = self._extract_keywords(original_query)
        
        filtered = []
        for frag in fragments:
            # Get sub_question from fragment (set by LibraryAgent during retrieval)
            sub_question = frag.get("sub_question", "")
            
            if not sub_question:
                # If no sub_question, check content and tags as fallback
                content = frag.get("content", "").lower()
                tags = " ".join(frag.get("domain_tags", [])).lower()
                text_to_check = f"{content} {tags}"
            else:
                text_to_check = sub_question.lower()
            
            # Check if any query keyword appears in sub_question or content/tags
            keyword_match = any(kw in text_to_check for kw in query_keywords)
            
            if keyword_match:
                filtered.append(frag)
        
        # If filtering removed everything, return original list (fallback)
        if not filtered:
            print(f"[DiceTable] Warning: Query relevance filter removed all fragments. Using original list.")
            return fragments
        
        print(f"[DiceTable] Filtered {len(fragments)} → {len(filtered)} fragments based on query relevance")
        return filtered
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        import re
        
        # Remove common stop words
        stop_words = {
            'what', 'are', 'the', 'is', 'it', 'for', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of',
            'a', 'an', 'how', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may',
            'if', 'then', 'else', 'when', 'where', 'why', 'which', 'who', 'whom', 'whose', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they', 'them', 'his', 'her',
            'my', 'your', 'our', 'their', 'its', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again', 'further', 'once', 'here', 'there',
            'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'from', 'with', 'as'
        }
        
        # Extract words (alphanumeric, min 3 chars)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and return unique keywords
        keywords = [w for w in words if w not in stop_words]
        
        # Return unique keywords preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def _sequence_fragments(self, survivors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sequence fragments according to domain rules.
        
        Rules:
        1. Safety/contraindication fragments first
        2. Evidence/treatment fragments middle
        3. Dosage/monitoring fragments later
        4. Uncertainty notes last
        """
        def get_priority(frag: Dict[str, Any]) -> int:
            # Determine fragment class from tags or content
            tags = frag.get("tags", [])
            fragment_class = frag.get("fragment_class", "unknown")
            
            # Infer class from tags if not explicit
            if not fragment_class or fragment_class == "unknown":
                if any(t in tags for t in ["safety", "warning", "contraindication", "fatal_interaction"]):
                    fragment_class = "safety_warning"
                elif any(t in tags for t in ["allergy", "cross_reactivity"]):
                    fragment_class = "allergy_cross_reactivity"
                elif any(t in tags for t in ["evidence", "guideline", "study"]):
                    fragment_class = "evidence_base"
                elif any(t in tags for t in ["first_line", "primary"]):
                    fragment_class = "first_line_treatment"
                elif any(t in tags for t in ["second_line", "alternative"]):
                    fragment_class = "second_line_with_caution"
                elif any(t in tags for t in ["dosage", "dose", "mg"]):
                    fragment_class = "dosage_guidance"
                elif any(t in tags for t in ["monitoring", "follow_up"]):
                    fragment_class = "monitoring_requirements"
            
            return self.SEQUENCE_PRIORITY.get(fragment_class, 5)
        
        # Sort by priority
        sorted_fragments = sorted(survivors, key=get_priority)
        return sorted_fragments
    
    def _build_answer_text(
        self,
        fragments: List[Dict[str, Any]],
        dice_row: DiceTableRow,
        original_query: Optional[str] = None  # NEW parameter
    ) -> str:
        """Build the final answer text from sequenced fragments."""
        parts = []
        
        for i, frag in enumerate(fragments):
            content = frag.get("content", "")
            source = frag.get("source", "Unknown")
            
            # Add fragment content
            parts.append(content)
            
            # Add citation if required
            if dice_row.require_source_citation:
                source_url = frag.get("source_url", "")
                if source_url:
                    parts[-1] += f" [Source: {source}]({source_url})"
                else:
                    parts[-1] += f" [Source: {source}]"
        
        # Join with newlines
        answer = "\n\n".join(parts)
        
        # Add traceability footer
        fragment_ids = [f.get("fragment_id", "?") for f in fragments]
        scores = [f.get("score", 0) for f in fragments]
        
        footer_parts = [
            "---",
            f"**Trace ID:** {{trace_id_placeholder}}",
            f"**Fragments:** {', '.join(fragment_ids)}",
            f"**Scores:** {', '.join(f'{s:.1f}' for s in scores)}"
        ]
        answer += "\n\n" + "\n".join(footer_parts)
        
        return answer
