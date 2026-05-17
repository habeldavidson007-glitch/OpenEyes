"""
Linguistic Genome - Advanced Procedural Grammar Construction
Deconstructs facts into atomic data points and assembles sentences token-by-token
at runtime with probabilistic grammatical rules for infinite human-like variations.

Zero templates. Pure construction. Millions of combinations from minimal codebase.
"""

import json
import random
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class AtomicFact:
    """Deconstructed fact into atomic components"""
    subject: str
    verb: str
    object_phrase: str = ""
    metric: Optional[str] = None
    timeframe: Optional[str] = None
    confidence: float = 0.9
    domain: str = "general"


@dataclass 
class SyntacticToken:
    """Individual token with grammatical properties"""
    text: str
    pos_tag: str  # Part of speech
    grammatical_role: str  # subject, verb, object, modifier, etc.
    weight: float = 1.0
    variants: List[str] = field(default_factory=list)


class LinguisticGenome:
    """
    The algorithmic core for procedural sentence construction.
    Defines rules of construction, not sentences themselves.
    """
    
    def __init__(self, dna_file: str = None):
        if dna_file is None:
            dna_file = Path(__file__).parent.parent / "knowledge" / "linguistic_dna.json"
        
        self.dna_file = str(dna_file)
        self.dna = self._load_dna()
        self._build_vocabulary_clusters()
        self._build_syntactic_blueprints()
        
        # Session tracking for anti-repetition
        self.used_patterns = set()
        self.used_vocabulary = set()
        self.session_id = random.randint(10000, 99999)
        self.conversation_history = []
        
    def _load_dna(self) -> Dict:
        """Load linguistic DNA patterns"""
        try:
            with open(self.dna_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return minimal default DNA
            return {
                "version": "3.0",
                "clusters": {
                    "openings": {"casual": [{"text": "So ", "weight": 1.0}]},
                    "connectors": {"default": [{"text": " ", "weight": 1.0}]},
                    "closings": {"default": [{"text": "", "weight": 1.0}]},
                    "sentence_structures": [{"pattern": "{fact}", "weight": 1.0}],
                    "intent_clusters": {"default": ["casual"]}
                }
            }
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in linguistic DNA: {e}")
    
    def _build_vocabulary_clusters(self):
        """Build weighted vocabulary clusters for stochastic injection"""
        
        # Economic terms
        self.vocab_increase = [
            ("increase", 1.0), ("rise", 0.95), ("grow", 0.9), ("climb", 0.85),
            ("surge", 0.8), ("spike", 0.75), ("jump", 0.7), ("leap", 0.65),
            ("escalate", 0.6), ("accelerate", 0.55), ("balloon", 0.5),
            ("skyrocket", 0.45), ("mushroom", 0.4), ("uptick", 0.6),
            ("hike", 0.65), ("advance", 0.5), ("gain", 0.55), ("appreciate", 0.4)
        ]
        
        self.vocab_decrease = [
            ("decrease", 1.0), ("drop", 0.95), ("fall", 0.9), ("decline", 0.85),
            ("dip", 0.8), ("plunge", 0.75), ("slump", 0.7), ("tumble", 0.65),
            ("shrink", 0.6), ("contract", 0.55), ("slide", 0.5),
            ("crater", 0.45), ("erosion", 0.4), ("downtick", 0.6),
            ("cut", 0.65), ("reduce", 0.5), ("diminish", 0.45)
        ]
        
        self.vocab_change = [
            ("change", 1.0), ("shift", 0.9), ("transform", 0.85), ("evolve", 0.8),
            ("morph", 0.7), ("alter", 0.65), ("modify", 0.6), ("adjust", 0.55),
            ("fluctuate", 0.5), ("oscillate", 0.45), ("vary", 0.5),
            ("swing", 0.5), ("pivot", 0.45), ("transition", 0.5)
        ]
        
        self.vocab_cause = [
            ("cause", 1.0), ("drive", 0.95), ("trigger", 0.9), ("spark", 0.85),
            ("fuel", 0.8), ("propel", 0.75), ("stimulate", 0.7), ("prompt", 0.65),
            ("induce", 0.6), ("generate", 0.55), ("produce", 0.5),
            ("engender", 0.45), ("precipitate", 0.4), ("catalyze", 0.5)
        ]
        
        self.vocab_show = [
            ("show", 1.0), ("indicate", 0.95), ("demonstrate", 0.9), ("reveal", 0.85),
            ("suggest", 0.8), ("imply", 0.75), ("point to", 0.7), ("signal", 0.65),
            ("reflect", 0.6), ("highlight", 0.55), ("underscore", 0.5),
            ("illustrate", 0.5), ("exemplify", 0.45), ("manifest", 0.4)
        ]
        
        # Discourse markers for natural flow
        self.discourse_markers = {
            "contrast": [
                ("however", 1.0), ("nevertheless", 0.8), ("nonetheless", 0.75),
                ("that said", 0.9), ("even so", 0.85), ("still", 0.7),
                ("despite this", 0.65), ("on the other hand", 0.6)
            ],
            "addition": [
                ("moreover", 0.9), ("furthermore", 0.85), ("additionally", 0.8),
                ("beyond that", 0.75), ("on top of this", 0.7), ("plus", 0.65),
                ("what's more", 0.6), ("to boot", 0.5)
            ],
            "emphasis": [
                ("crucially", 1.0), ("importantly", 0.95), ("significantly", 0.9),
                ("notably", 0.85), ("key point", 0.8), ("essentially", 0.75),
                ("fundamentally", 0.7), ("at its core", 0.65)
            ],
            "qualification": [
                ("generally", 1.0), ("typically", 0.95), ("usually", 0.9),
                ("in most cases", 0.85), ("as a rule", 0.8), ("more often than not", 0.75),
                ("for the most part", 0.7), ("by and large", 0.65)
            ],
            "clarification": [
                ("in other words", 1.0), ("put differently", 0.9), ("to clarify", 0.85),
                ("simply put", 0.8), ("to be precise", 0.75), ("more specifically", 0.7),
                ("to elaborate", 0.65), ("breaking it down", 0.6)
            ]
        }
        
        # Filler phrases for human-like rhythm
        self.filler_phrases = [
            ("you know", 0.6), ("I mean", 0.55), ("sort of", 0.5),
            ("kind of", 0.5), ("if you will", 0.45), ("so to speak", 0.4),
            ("in a sense", 0.5), ("as it were", 0.35), ("let's say", 0.5),
            ("think about it", 0.45), ("here's the thing", 0.5),
            ("the reality is", 0.55), ("truth be told", 0.4), ("frankly", 0.45)
        ]
        
        # Thoughtful pauses
        self.pauses = [
            ("...", 0.7), ("—", 0.8), (",", 1.0), ("; ", 0.6),
            (" — ", 0.5), ("... well, ", 0.4), ("... you see, ", 0.35)
        ]
        
    def _build_syntactic_blueprints(self):
        """Define logic trees for sentence arrangement"""
        
        # Blueprint: Simple declarative
        self.blueprint_simple = [
            {"role": "opener", "probability": 0.7},
            {"role": "subject", "probability": 1.0},
            {"role": "verb", "probability": 1.0},
            {"role": "object", "probability": 0.9},
            {"role": "modifier", "probability": 0.5},
            {"role": "closer", "probability": 0.6}
        ]
        
        # Blueprint: Complex with mechanism
        self.blueprint_complex = [
            {"role": "opener", "probability": 0.8},
            {"role": "subject", "probability": 1.0},
            {"role": "verb", "probability": 1.0},
            {"role": "object", "probability": 0.95},
            {"role": "connector", "probability": 0.8},
            {"role": "mechanism", "probability": 0.7},
            {"role": "discourse_marker", "probability": 0.5},
            {"role": "impact", "probability": 0.6},
            {"role": "closer", "probability": 0.7}
        ]
        
        # Blueprint: Analogy-first
        self.blueprint_analogy_first = [
            {"role": "opener", "probability": 0.9},
            {"role": "analogy_intro", "probability": 1.0},
            {"role": "analogy", "probability": 1.0},
            {"role": "connector", "probability": 0.9},
            {"role": "fact_bridge", "probability": 0.8},
            {"role": "subject", "probability": 1.0},
            {"role": "verb", "probability": 1.0},
            {"role": "object", "probability": 0.9},
            {"role": "closer", "probability": 0.6}
        ]
        
        # Blueprint: Impact-focused
        self.blueprint_impact = [
            {"role": "opener", "probability": 0.75},
            {"role": "impact_statement", "probability": 1.0},
            {"role": "discourse_marker", "probability": 0.7},
            {"role": "fact_explanation", "probability": 0.9},
            {"role": "subject", "probability": 0.8},
            {"role": "verb", "probability": 0.8},
            {"role": "object", "probability": 0.7},
            {"role": "closer", "probability": 0.65}
        ]
        
    def _weighted_choice(self, items: List[Tuple[str, float]], 
                         exclude_used: bool = True) -> str:
        """Select item based on weights with anti-repetition"""
        if not items:
            return ""
        
        # Filter out recently used if requested
        if exclude_used:
            available = [(text, w) for text, w in items if text not in self.used_vocabulary]
            if not available:
                available = items
                self.used_vocabulary.clear()
        else:
            available = items
        
        total_weight = sum(w for _, w in available)
        if total_weight == 0:
            return random.choice(available)[0]
        
        rand_val = random.uniform(0, total_weight)
        cumulative = 0
        
        for text, weight in available:
            cumulative += weight
            if rand_val <= cumulative:
                self.used_vocabulary.add(text)
                return text
        
        return available[-1][0]
    
    def _select_blueprint(self, components: Dict[str, Any]) -> List[Dict]:
        """Choose syntactic blueprint based on available components"""
        
        blueprints = {
            "simple": (self.blueprint_simple, 0.3),
            "complex": (self.blueprint_complex, 0.35),
            "analogy_first": (self.blueprint_analogy_first, 0.2),
            "impact": (self.blueprint_impact, 0.15)
        }
        
        # Score each blueprint based on available components
        scores = {}
        
        if components.get('analogy'):
            scores['analogy_first'] = 0.5
            scores['complex'] = 0.3
            
        if components.get('impact'):
            scores['impact'] = 0.45
            scores['complex'] = max(scores.get('complex', 0), 0.35)
            
        if components.get('mechanism'):
            scores['complex'] = max(scores.get('complex', 0), 0.4)
        
        # Default to simple if nothing special
        if not scores:
            scores['simple'] = 0.5
        
        # Add base probabilities
        for name, (_, base_prob) in blueprints.items():
            scores[name] = scores.get(name, 0) + base_prob * 0.5
        
        # Select based on scores
        total = sum(scores.values())
        rand_val = random.uniform(0, total)
        cumulative = 0
        
        selected = 'simple'
        for name, score in scores.items():
            cumulative += score
            if rand_val <= cumulative:
                selected = name
                break
        
        blueprint, _ = blueprints[selected]
        return blueprint
    
    def deconstruct_fact(self, text: str, domain: str = "general") -> AtomicFact:
        """
        Deconstruct verified fact into atomic data points.
        Extracts: Subject, Verb, Object, Metric, Timeframe
        """
        # Simple heuristic-based deconstruction
        # In production, this could use NLP parsing
        
        text = text.strip()
        
        # Detect common patterns - look for subject-verb-object structure
        verbs_common = [
            "increases", "decreases", "rises", "falls", "shows",
            "causes", "leads", "results", "means", "represents",
            "slows", "accelerates", "grows", "shrinks", "expands",
            "is", "are", "was", "were", "has", "have", "had"
        ]
        
        verb_found = None
        verb_pos = -1
        
        # Sort by length to find longest match first (e.g., "increases" before "is")
        verbs_sorted = sorted(verbs_common, key=len, reverse=True)
        
        for verb in verbs_sorted:
            # Try to find verb with word boundaries
            patterns = [
                f" {verb} ",  # verb with spaces
                f" {verb}",   # verb at end
                f"{verb} ",   # verb at start of remaining
            ]
            for pattern in patterns:
                pos = text.lower().find(pattern)
                if pos > 0 and (verb_pos == -1 or pos < verb_pos):
                    verb_found = verb
                    verb_pos = pos
                    break
            if verb_found:
                break
        
        if verb_found and verb_pos > 0:
            subject = text[:verb_pos].strip()
            rest = text[verb_pos + len(verb_found):].strip()
            
            # Clean up leading articles/prepositions from rest
            while rest and rest[0] in ' ':
                rest = rest[1:]
            
            # Try to extract object and metrics
            object_phrase = rest
            metric = None
            timeframe = None
            
            # Look for percentages
            pct_match = re.search(r'(\d+\.?\d*)\s*%', rest)
            if pct_match:
                metric = f"{pct_match.group(1)}%"
            
            # Look for timeframes
            time_patterns = [
                r'(annually|yearly|monthly|weekly|daily)',
                r'(over \d+ years?|in \d+ months?|during \d+ weeks?)',
                r'(since \d{4}|from \d{4} to \d{4})',
                r'(recently|lately|currently|traditionally|typically)',
                r'(past \d+ years?|last \d+ months?)'
            ]
            for pattern in time_patterns:
                time_match = re.search(pattern, rest, re.IGNORECASE)
                if time_match:
                    timeframe = time_match.group(0)
                    break
            
            return AtomicFact(
                subject=subject,
                verb=verb_found,
                object_phrase=object_phrase,
                metric=metric,
                timeframe=timeframe,
                domain=domain
            )
        else:
            # Fallback: treat entire text as a statement
            # Try to extract a noun phrase as subject
            words = text.split()
            if len(words) > 3:
                # Assume first few words are subject
                subject = " ".join(words[:min(3, len(words)//2)])
                object_phrase = " ".join(words[min(3, len(words)//2):])
                verb = "refers to"
            else:
                subject = "This"
                verb = "describes"
                object_phrase = text
            
            return AtomicFact(
                subject=subject,
                verb=verb,
                object_phrase=object_phrase,
                domain=domain
            )
    
    def apply_voice_transformation(self, text: str, voice: str = "active") -> str:
        """Transform sentence between active and passive voice"""
        # Simple transformations - in production would use proper NLP
        passive_markers = [
            (r"\b(is|are|was|were)\s+(\w+)(ed|en|ing)?\b", 
             lambda m: f"{m.group(2)}{m.group(3) or ''} is {m.group(1)}"),
        ]
        
        if voice == "passive":
            # Attempt passive conversion
            for pattern, repl in passive_markers:
                if re.search(pattern, text):
                    return re.sub(pattern, repl, text, count=1)
        
        return text  # Return original if no transformation applied
    
    def vary_sentence_length(self, tokens: List[str], target: str = "medium") -> List[str]:
        """Adjust sentence length by adding/removing modifiers"""
        
        short_additions = ["", "."]
        medium_additions = [" essentially", " fundamentally", " in practice", "."]
        long_additions = [
            " when you look at the data",
            " if we examine this closely",
            " from a structural perspective",
            " which is worth noting",
            " as the evidence suggests",
            "."
        ]
        
        if target == "short":
            additions = short_additions
        elif target == "long":
            additions = long_additions
        else:  # medium
            additions = medium_additions
        
        if additions and random.random() > 0.5:
            addition = random.choice(additions[:-1]) if len(additions) > 1 else ""
            if addition and tokens:
                tokens[-1] = tokens[-1] + addition
        
        return tokens
    
    def inject_discourse_marker(self, position: str = "middle") -> Optional[str]:
        """Inject discourse marker for natural flow"""
        marker_type = random.choice(list(self.discourse_markers.keys()))
        markers = self.discourse_markers[marker_type]
        
        if random.random() > 0.6:  # 40% chance to add marker
            return self._weighted_choice(markers)
        
        return None
    
    def assemble_token_by_token(self, atomic: AtomicFact, 
                                analogy: Optional[str] = None,
                                impact: Optional[str] = None,
                                mechanism: Optional[str] = None,
                                intent: str = "casual") -> str:
        """
        Assemble sentence token-by-token at runtime.
        Core construction engine - no templates, pure procedural generation.
        """
        
        components = {
            'analogy': analogy,
            'impact': impact,
            'mechanism': mechanism,
            'atomic': atomic
        }
        
        # Select blueprint
        blueprint = self._select_blueprint(components)
        
        # Build sentence token by token
        tokens = []
        
        # Voice variation (30% passive for variety)
        use_passive = random.random() < 0.3
        
        # Sentence length variation
        length_targets = ["short", "medium", "medium", "long"]
        target_length = random.choice(length_targets)
        
        for step in blueprint:
            role = step["role"]
            probability = step["probability"]
            
            # Probabilistic inclusion
            if random.random() > probability:
                continue
            
            if role == "opener":
                opener_options = self.dna["clusters"]["openings"].get("casual", [])
                if opener_options:
                    opener = self._weighted_choice([(o["text"], o["weight"]) for o in opener_options])
                    tokens.append(opener)
            
            elif role == "subject":
                subj = atomic.subject.strip().capitalize()
                if subj and subj.lower() not in ['this', 'it', 'that']:
                    tokens.append(subj)
                elif atomic.object_phrase:
                    # Use first part of object as subject if subject is weak
                    parts = atomic.object_phrase.split(' ', 2)
                    if len(parts) > 0:
                        tokens.append(parts[0].capitalize())
                else:
                    tokens.append("This")
            
            elif role == "verb":
                # Get base verb and apply variation
                base_verb = atomic.verb.strip()
                
                # Handle compound verbs like "have risen", "has increased"
                aux_verbs = ["have", "has", "had", "is", "are", "was", "were"]
                main_verb = base_verb
                auxiliary = ""
                
                for aux in aux_verbs:
                    if base_verb.lower().startswith(aux + " "):
                        auxiliary = aux
                        main_verb = base_verb[len(aux)+1:].strip()
                        break
                
                # Get synonym for main verb - handle plural/singular forms
                verb_variant = self._get_verb_variant(main_verb)
                
                if use_passive and auxiliary:
                    tokens.append(f"is {verb_variant}")
                elif auxiliary:
                    # Keep the auxiliary with proper form
                    tokens.append(f"{auxiliary} {verb_variant}")
                elif use_passive:
                    tokens.append(f"is {verb_variant}")
                else:
                    tokens.append(verb_variant)
            
            elif role == "object":
                obj_text = atomic.object_phrase.strip()
                # Remove any leading verb remnants
                for aux in ["have", "has", "had", "is", "are", "was", "were"]:
                    if obj_text.lower().startswith(aux + " "):
                        obj_text = obj_text[len(aux)+1:].strip()
                        break
                
                if atomic.metric and atomic.metric in obj_text:
                    obj_text = obj_text.replace(atomic.metric, f"a notable {atomic.metric}")
                
                if obj_text:
                    tokens.append(obj_text)
            
            elif role == "connector":
                connector_type = "definition_to_mechanism" if mechanism else "fact_to_impact"
                connectors = self.dna["clusters"]["connectors"].get(connector_type, [])
                if connectors:
                    conn = self._weighted_choice([(c["text"], c["weight"]) for c in connectors])
                    tokens.append(conn)
            
            elif role == "mechanism" and mechanism:
                tokens.append(mechanism.strip())
            
            elif role == "impact" and impact:
                tokens.append(impact.strip())
            
            elif role == "analogy_intro" and analogy:
                analogy_intros = self.dna["clusters"]["connectors"].get("analogy_intro", [])
                if analogy_intros:
                    intro = self._weighted_choice([(a["text"], a["weight"]) for a in analogy_intros])
                    tokens.append(intro)
            
            elif role == "analogy" and analogy:
                tokens.append(analogy.strip())
            
            elif role == "discourse_marker":
                marker = self.inject_discourse_marker()
                if marker:
                    tokens.append(f"{marker}, ")
            
            elif role == "fact_bridge":
                bridges = ["This is exactly what happens when", "The same principle applies:", "Here's the connection:"]
                tokens.append(f"{random.choice(bridges)} ")
            
            elif role == "closer":
                closer_options = self.dna["clusters"]["closings"].get("summary", [])
                if closer_options and random.random() > 0.5:
                    closer = self._weighted_choice([(c["text"], c["weight"]) for c in closer_options])
                    tokens.append(closer)
            
            elif role == "filler":
                if random.random() > 0.6:
                    filler = self._weighted_choice(self.filler_phrases)
                    tokens.append(f"{filler} ")
        
        # Vary sentence length
        tokens = self.vary_sentence_length(tokens, target_length)
        
        # Assemble and clean
        result = "".join(tokens)
        result = re.sub(r'\s+', ' ', result)  # Clean multiple spaces
        result = result.strip()
        
        # Ensure proper punctuation
        if result and not result.endswith(('.', '?', '!')):
            result += '.'
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
        
        return result
    
    def _get_verb_variant(self, verb: str) -> str:
        """Get synonym variant for verb with proper conjugation"""
        verb_lower = verb.lower().strip()
        
        # Handle different verb forms - map to base form and vocabulary list
        base_forms = {
            "increases": ("increase", self.vocab_increase, 's'),
            "increased": ("increase", self.vocab_increase, 'ed'),
            "increasing": ("increase", self.vocab_increase, 'ing'),
            "decreases": ("decrease", self.vocab_decrease, 's'),
            "decreased": ("decrease", self.vocab_decrease, 'ed'),
            "decreasing": ("decrease", self.vocab_decrease, 'ing'),
            "rises": ("rise", self.vocab_increase, 's'),
            "risen": ("rise", self.vocab_increase, 'n'),
            "rising": ("rise", self.vocab_increase, 'ing'),
            "rose": ("rise", self.vocab_increase, 'rose'),  # irregular
            "falls": ("fall", self.vocab_decrease, 's'),
            "fallen": ("fall", self.vocab_decrease, 'n'),
            "falling": ("fall", self.vocab_decrease, 'ing'),
            "fell": ("fall", self.vocab_decrease, 'fell'),  # irregular
            "grows": ("grow", self.vocab_increase, 's'),
            "grew": ("grow", self.vocab_increase, 'grew'),  # irregular
            "grown": ("grow", self.vocab_increase, 'n'),
            "growing": ("grow", self.vocab_increase, 'ing'),
            "drops": ("drop", self.vocab_decrease, 's'),
            "dropped": ("drop", self.vocab_decrease, 'ped'),  # double p
            "dropping": ("drop", self.vocab_decrease, 'pping'),  # double p
            "slows": ("slow", self.vocab_decrease, 's'),
            "slowed": ("slow", self.vocab_decrease, 'ed'),
            "slowing": ("slow", self.vocab_decrease, 'ing'),
            "accelerates": ("accelerate", self.vocab_increase, 's'),
            "accelerated": ("accelerate", self.vocab_increase, 'ed'),
            "accelerating": ("accelerate", self.vocab_increase, 'ing'),
            "changes": ("change", self.vocab_change, 's'),
            "changed": ("change", self.vocab_change, 'ed'),
            "changing": ("change", self.vocab_change, 'ing'),
            "causes": ("cause", self.vocab_cause, 's'),
            "caused": ("cause", self.vocab_cause, 'ed'),
            "causing": ("cause", self.vocab_cause, 'ing'),
            "shows": ("show", self.vocab_show, 's'),
            "showed": ("show", self.vocab_show, 'ed'),
            "shown": ("show", self.vocab_show, 'n'),
            "showing": ("show", self.vocab_show, 'ing'),
            "has": ("have", [("has", 1.0), ("have", 0.8)], 'has'),
            "have": ("have", [("have", 1.0), ("has", 0.8)], 'have'),
            "had": ("have", [("had", 1.0)], 'had'),
            "is": ("be", [("is", 1.0)], 'is'),
            "are": ("be", [("are", 1.0)], 'are'),
            "was": ("be", [("was", 1.0)], 'was'),
            "were": ("be", [("were", 1.0)], 'were'),
            "been": ("be", [("been", 1.0)], 'been'),
            "being": ("be", [("being", 1.0)], 'being'),
        }
        
        # Check if we have a mapping for this verb form
        if verb_lower in base_forms:
            base_key, variants, suffix_type = base_forms[verb_lower]
            selected = self._weighted_choice(variants)
            
            # For auxiliary verbs and irregular forms, return as-is
            if suffix_type in ['has', 'have', 'had', 'is', 'are', 'was', 'were', 'been', 'being', 
                               'rose', 'fell', 'grew']:
                return selected
            
            # Strip any existing suffix from selected word before adding new one
            for suffix in ['s', 'es', 'ed', 'ing', 'en', 'n']:
                if selected.endswith(suffix) and len(selected) > len(suffix) + 1:
                    # Don't strip if it would leave a very short root
                    if len(selected) > 4:
                        selected = selected[:-len(suffix)]
                        break
            
            # Maintain the original tense/form by applying appropriate suffix
            if suffix_type == 's':
                # Third person singular - ensure it ends with 's'
                if selected.endswith(('s', 'sh', 'ch', 'x', 'z')):
                    selected = selected + 'es'
                elif not selected.endswith('s'):
                    selected = selected + 's'
            elif suffix_type == 'ed':
                # Past tense - ensure it ends with 'ed'
                if not selected.endswith('ed'):
                    if selected.endswith('e'):
                        selected = selected + 'd'
                    else:
                        selected = selected + 'ed'
            elif suffix_type == 'ing':
                # Present participle - ensure it ends with 'ing'
                if not selected.endswith('ing'):
                    if selected.endswith('e'):
                        selected = selected[:-1] + 'ing'
                    else:
                        selected = selected + 'ing'
            elif suffix_type == 'n':
                # Past participle (often -en)
                if not selected.endswith('n') and not selected.endswith('ed'):
                    selected = selected + 'ed'
            elif suffix_type == 'ped':
                # Double consonant + ed
                if len(selected) > 1 and selected[-1] not in 'aeiou':
                    selected = selected + selected[-1] + 'ed'
                else:
                    selected = selected + 'ed'
            elif suffix_type == 'pping':
                # Double consonant + ing
                if len(selected) > 1 and selected[-1] not in 'aeiou':
                    selected = selected + selected[-1] + 'ing'
                else:
                    selected = selected + 'ing'
            
            return selected
        
        # Return original if no match found
        return verb
    
    def reset_session(self):
        """Reset session tracking for fresh variations"""
        self.used_patterns.clear()
        self.used_vocabulary.clear()
        self.session_id = random.randint(10000, 99999)
        self.conversation_history = []
    
    def generate(self, fact_text: str, 
                 analogy: Optional[str] = None,
                 impact: Optional[str] = None,
                 mechanism: Optional[str] = None,
                 intent: str = "casual",
                 domain: str = "general") -> str:
        """
        Main generation interface.
        Takes verified fact, returns procedurally constructed sentence.
        """
        # Deconstruct fact
        atomic = self.deconstruct_fact(fact_text, domain)
        
        # Assemble token-by-token
        result = self.assemble_token_by_token(
            atomic=atomic,
            analogy=analogy,
            impact=impact,
            mechanism=mechanism,
            intent=intent
        )
        
        return result


# Demo
if __name__ == "__main__":
    print("=== Linguistic Genome Demo: Token-by-Token Construction ===\n")
    
    genome = LinguisticGenome()
    
    test_cases = [
        {
            "fact_text": "Inflation increases consumer prices by approximately 2-3% annually",
            "mechanism": "Central banks adjust interest rates to manage money supply",
            "impact": "Purchasing power decreases for fixed-income households",
            "analogy": "Your paycheck stays the same but your grocery cart shrinks"
        },
        {
            "fact_text": "Healthcare costs have risen faster than wages over the past decade",
            "impact": "Families allocate larger budget share to medical expenses",
            "analogy": "It's like running faster just to stay in the same place"
        },
        {
            "fact_text": "Economic growth typically slows during periods of high uncertainty",
            "mechanism": "Businesses delay investment decisions until clarity improves"
        }
    ]
    
    print("Generating 5 variations per fact:\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"--- Fact {i}: '{test['fact_text']}' ---")
        for run in range(5):
            genome.reset_session()
            result = genome.generate(**test)
            print(f"  {run + 1}. {result}")
        print()
    
    print("=== Demo Complete ===")
