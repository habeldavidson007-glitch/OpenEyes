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
    def __init__(self, subject: str = "", verb: str = "", object_phrase: str = "", 
                 metric: Optional[str] = None, timeframe: Optional[str] = None,
                 confidence: float = 0.9, domain: str = "general", 
                 original_text: str = "", metric_value: Optional[float] = None,
                 adjective: Optional[str] = None, analogy: Optional[str] = None):
        self.subject = subject
        self.verb = verb
        self.object_phrase = object_phrase
        self.object = object_phrase  # Alias for compatibility
        self.metric = metric
        self.timeframe = timeframe
        self.confidence = confidence
        self.domain = domain
        self.original_text = original_text
        self.metric_value = metric_value
        self.adjective = adjective
        self.analogy = analogy


@dataclass 
class SyntacticToken:
    """Individual token with grammatical properties"""
    def __init__(self, text: str, role: str = "content", pos_tag: str = "NN", weight: float = 1.0, variants: List[str] = None):
        self.text = text
        self.pos_tag = pos_tag
        self.grammatical_role = role
        self.weight = weight
        self.variants = variants if variants else []


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
        
        # P1: Domain-specific vocabulary clusters
        self.domain_vocab = {
            'economy': {
                'volatility': ['volatility', 'fluctuation', 'swing', 'oscillation', 'instability'],
                'growth': ['expansion', 'uptick', 'momentum', 'acceleration', 'surge'],
                'decline': ['contraction', 'downturn', 'slump', 'recession', 'correction'],
                'market': ['marketplace', 'trading floor', 'exchange', 'bourse', 'index']
            },
            'healthcare': {
                'symptom': ['indicator', 'sign', 'manifestation', 'marker', 'signal'],
                'treatment': ['intervention', 'therapy', 'protocol', 'regimen', 'approach'],
                'patient': ['individual', 'person', 'case', 'patient', 'client'],
                'outcome': ['result', 'prognosis', 'trajectory', 'progress', 'recovery']
            },
            'finance': {
                'portfolio': ['holdings', 'investments', 'assets', 'positions', 'book'],
                'risk': ['exposure', 'vulnerability', 'liability', 'peril', 'hazard'],
                'return': ['yield', 'gain', 'profit', 'performance', 'appreciation'],
                'asset': ['holding', 'investment', 'security', 'instrument', 'position']
            },
            'technology': {
                'system': ['platform', 'infrastructure', 'framework', 'architecture', 'stack'],
                'data': ['information', 'metrics', 'analytics', 'insights', 'intelligence'],
                'algorithm': ['model', 'engine', 'processor', 'routine', 'logic'],
                'performance': ['throughput', 'efficiency', 'latency', 'speed', 'capacity']
            },
            'climate': {
                'temperature': ['heat', 'warmth', 'thermal reading', 'degree', 'level'],
                'emissions': ['output', 'discharge', 'release', 'footprint', 'carbon load'],
                'impact': ['effect', 'consequence', 'ramification', 'repercussion', 'influence'],
                'trend': ['pattern', 'trajectory', 'direction', 'movement', 'shift']
            }
        }
        
        # P1: Response length targets by intent
        self.length_targets = {
            'urgent_concern': (30, 60),      # Short, direct for crisis
            'technical_deep_dive': (100, 200), # Detailed for technical
            'casual_query': (50, 100),       # Conversational
            'educational': (80, 150),        # Informative
            'exploratory': (60, 120)         # Balanced
        }
        
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
        # IMPORTANT: Sort by length (longest first) AND use word boundary regex
        verbs_common = [
            "increases", "decreases", "rises", "falls", "shows",
            "causes", "leads", "results", "means", "represents",
            "slows", "accelerates", "grows", "shrinks", "expands",
            "rising", "falling", "growing", "declining", "increasing", "decreasing",
            "eroding", "improving", "worsening", "strengthening", "weakening",
            "is", "are", "was", "were", "has", "have", "had",
            # Add more action verbs that were being missed
            "spikes", "spike", "surges", "surge", "jumps", "jump",
            "climbs", "climb", "peaks", "peak", "plunges", "plunge",
            "drops", "drop", "slides", "slide", "tumbles", "tumble",
            "creates", "create", "generates", "generate", "produces", "produce",
            "continues", "continue", "remains", "remain", "stays", "stay",
            "indicates", "indicate", "suggests", "suggest", "signals", "signal",
            "drives", "drive", "pushes", "push", "pulls", "pull",
            "triggers", "trigger", "sparks", "spark", "fuels", "fuel"
        ]
        
        verb_found = None
        verb_pos = -1
        verb_end_pos = -1
        
        # Sort by length to find longest match first
        verbs_sorted = sorted(verbs_common, key=len, reverse=True)
        
        for verb in verbs_sorted:
            # Use regex with word boundaries to avoid matching "is" inside "rising"
            pattern = r'\b' + re.escape(verb) + r'\b'
            match = re.search(pattern, text, re.IGNORECASE)
            
            if match and match.start() > 0:  # Must not be at position 0 (need a subject before)
                if verb_pos == -1 or match.start() < verb_pos:
                    verb_found = match.group(0)
                    verb_pos = match.start()
                    verb_end_pos = match.end()
        
        if verb_found and verb_pos > 0:
            subject = text[:verb_pos].strip()
            rest = text[verb_end_pos:].strip()
            
            # Clean up leading articles/prepositions from rest
            while rest and rest[0] in ' ':
                rest = rest[1:]
            
            # Special handling for "is/are/was/were" + adjective/noun (predicate construction)
            if verb_found.lower() in ['is', 'are', 'was', 'were']:
                # The rest IS the object/complement - don't try to extract another verb from it
                object_phrase = rest
                metric = None
                timeframe = None
                
                # Look for percentages in the complement
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
            
            # Try to extract object and metrics for non-copula verbs
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
        last_role_added = None
        consecutive_marker_count = 0
        
        # Voice variation (30% passive for variety)
        use_passive = random.random() < 0.3
        
        # Sentence length variation
        length_targets = ["short", "medium", "medium", "long"]
        target_length = random.choice(length_targets)
        
        for step in blueprint:
            role = step["role"]
            probability = step["probability"]
            
            # ANTI-STUTTER: Skip if we just added the same type of marker
            if role in ["discourse_marker", "filler", "opener", "closer"]:
                if last_role_added == role:
                    # 70% chance to skip consecutive similar roles
                    if random.random() < 0.7:
                        continue
                consecutive_marker_count += 1
                if consecutive_marker_count > 2:
                    # Force skip after 3 consecutive markers
                    continue
            else:
                consecutive_marker_count = 0
            
            # CRITICAL: Ensure we always get a complete clause (subject + verb + object/predicate)
            # If we're at the end of the blueprint and haven't completed a clause, force inclusion
            is_last_step = (step == blueprint[-1])
            has_subject = last_role_added == "subject"
            has_verb = last_role_added == "verb"
            needs_object = has_subject and has_verb  # Need object/predicate to complete clause
            
            # Probabilistic inclusion - but ALWAYS include core clause components
            if role in ["subject", "verb"] and not last_role_added:
                # Force include subject and verb if nothing added yet
                pass  # Don't skip
            elif random.random() > probability and not (needs_object and role in ["object", "impact"]):
                continue
            
            if role == "opener":
                opener_options = self.dna["clusters"]["openings"].get("casual", [])
                if opener_options:
                    opener = self._weighted_choice([(o["text"], o["weight"]) for o in opener_options])
                    tokens.append(opener)
                    last_role_added = "opener"
            
            elif role == "subject":
                subj = atomic.subject.strip()
                if not subj:
                    continue
                    
                # Capitalize properly - only first letter, rest as-is unless all caps
                if subj[0].islower():
                    subj = subj[0].upper() + subj[1:]
                
                if subj.lower() not in ['this', 'it', 'that']:
                    tokens.append(subj)
                    last_role_added = "subject"
                elif atomic.object_phrase:
                    # Use first part of object as subject if subject is weak
                    parts = atomic.object_phrase.split(' ', 2)
                    if len(parts) > 0 and parts[0].lower() not in ['increased', 'decreased', 'risen', 'fallen']:
                        subj_candidate = parts[0].capitalize()
                        tokens.append(subj_candidate)
                        last_role_added = "subject"
                    else:
                        # Fall back to atomic subject even if weak
                        tokens.append(atomic.subject.strip().capitalize())
                        last_role_added = "subject"
                else:
                    tokens.append("This")
                    last_role_added = "subject"
            
            elif role == "verb":
                # Get base verb and apply variation
                base_verb = atomic.verb.strip()
                
                # CRITICAL FIX: Handle copula verbs (is/are/was/were) with predicate adjectives
                # The issue is that for "Portfolio volatility is normal", the deconstruction might
                # extract subject="Portfolio volatility", verb="is", object_phrase="normal, but..."
                # We MUST include "is" in the output!
                if base_verb.lower() in ['is', 'are', 'was', 'were']:
                    # ALWAYS add the copula verb - don't skip it!
                    tokens.append(base_verb)
                    last_role_added = "verb"
                    # Continue to let the object role add the predicate adjective
                    continue
                
                # Skip if verb is empty
                if not base_verb:
                    continue
                
                # CRITICAL FIX 2: Prevent adding "is" before action verbs
                # When we have "Market volatility creates opportunities", we should NOT add "is creates"
                # This happens when the blueprint tries to add a connector like "is" before the verb
                
                # Handle compound verbs like "have risen", "has increased"
                aux_verbs = ["have", "has", "had", "is", "are", "was", "were"]
                main_verb = base_verb
                auxiliary = ""
                
                for aux in aux_verbs:
                    if base_verb.lower().startswith(aux + " "):
                        auxiliary = aux
                        main_verb = base_verb[len(aux)+1:].strip()
                        break
                
                # If main_verb is empty after extracting auxiliary, use object_phrase to infer
                if not main_verb or main_verb.lower() in ['is', 'are', 'was', 'were', 'be', 'been', 'being']:
                    # Check if object_phrase contains the actual verb
                    if atomic.object_phrase:
                        obj_lower = atomic.object_phrase.lower()
                        if 'increased' in obj_lower or 'rise' in obj_lower or 'risen' in obj_lower:
                            main_verb = 'increase'
                        elif 'decreased' in obj_lower or 'fall' in obj_lower or 'fallen' in obj_lower:
                            main_verb = 'decrease'
                        elif 'grown' in obj_lower or 'grow' in obj_lower:
                            main_verb = 'grow'
                
                # Get synonym for main verb - handle plural/singular forms
                # CRITICAL: Only add verb variant if it's NOT a copula construction
                if main_verb and main_verb.lower() not in ['is', 'are', 'was', 'were', 'be', 'been', 'being']:
                    verb_variant = self._get_verb_variant(main_verb)
                    
                    # NEVER add "is" before an action verb - only for passive voice
                    if use_passive and auxiliary:
                        tokens.append(f"is {verb_variant}")
                    elif auxiliary and auxiliary.lower() not in ['is', 'are', 'was', 'were']:
                        # Keep the auxiliary with proper form (but not copula auxiliaries)
                        tokens.append(f"{auxiliary} {verb_variant}")
                    elif use_passive:
                        tokens.append(f"is {verb_variant}")
                    else:
                        # Just add the verb variant directly - NO extra "is"
                        tokens.append(verb_variant)
                    last_role_added = "verb"
                elif base_verb.lower() not in ['is', 'are', 'was', 'were']:
                    # Fallback: use the original verb if we couldn't process it
                    # But make sure we're not adding a duplicate copula
                    tokens.append(base_verb)
                    last_role_added = "verb"
            
            elif role == "object":
                obj_text = atomic.object_phrase.strip()
                
                # Skip if object is empty
                if not obj_text:
                    continue
                
                # Remove any leading verb remnants
                for aux in ["have", "has", "had", "is", "are", "was", "were"]:
                    if obj_text.lower().startswith(aux + " "):
                        obj_text = obj_text[len(aux)+1:].strip()
                        break
                
                # CRITICAL FIX: Handle predicate adjectives after copula verbs (is/are/was/were)
                # If the last role was a copula verb and object is a predicate adjective, KEEP IT
                predicate_adjectives = ['normal', 'stable', 'volatile', 'high', 'low', 'critical', 
                                       'dangerous', 'safe', 'healthy', 'weak', 'strong', 'steady']
                
                # ACTION VERBS that should NOT follow a copula "is"
                action_verbs = ['spikes', 'spike', 'surges', 'surge', 'jumps', 'jump', 'creates', 'create',
                               'continue', 'continues', 'generates', 'generate', 'produces', 'produce',
                               'climbs', 'climb', 'peaks', 'peak', 'falls', 'fall', 'rises', 'rise',
                               'drops', 'drop', 'grows', 'grow', 'shrinks', 'shrink', 'declines', 'decline',
                               'persists', 'persist', 'remains', 'remain', 'yields', 'yield']
                
                if last_role_added == 'verb' and atomic.verb.lower() in ['is', 'are', 'was', 'were']:
                    # Check if obj_text IS a predicate adjective or starts with one
                    first_word = obj_text.split()[0].lower() if obj_text.split() else ""
                    if first_word in predicate_adjectives:
                        # This is valid - keep the predicate adjective!
                        pass  # Don't skip, don't modify
                    elif obj_text.lower() in predicate_adjectives:
                        # The entire object is a predicate adjective - keep it
                        pass
                    elif first_word in action_verbs or obj_text.lower().split()[0] in action_verbs:
                        # ERROR: We added "is" but the object starts with an action verb
                        # This means we incorrectly treated an action verb sentence as a copula sentence
                        # Solution: Skip the object entirely and let the sentence end with just subject+is
                        # OR better: don't add the copula in the first place for these cases
                        # For now, skip this object to avoid "is spikes" error
                        continue
                    elif obj_text.lower() in ['increased', 'decreased', 'risen', 'fallen', 'grown', 'shrunk']:
                        # This is actually a verb form that was incorrectly extracted - skip
                        continue
                    elif not obj_text.split():
                        # Empty after split
                        continue
                    # Otherwise continue normally
                
                # Skip if after cleaning, object looks like a verb form (not a predicate adjective scenario)
                if obj_text.lower() in ['increased', 'decreased', 'risen', 'fallen', 'grown', 'shrunk']:
                    # Only skip if we didn't just add a copula verb
                    if atomic.verb.lower() not in ['is', 'are', 'was', 'were']:
                        continue
                
                # If we already added a verb and object looks like a duplicate verb, skip
                if last_role_added == "verb" and obj_text.lower() in ['increased', 'decreased', 'risen', 'fallen']:
                    if atomic.verb.lower() not in ['is', 'are', 'was', 'were']:
                        continue
                
                if atomic.metric and atomic.metric in obj_text:
                    obj_text = obj_text.replace(atomic.metric, f"a notable {atomic.metric}")
                
                if obj_text:
                    tokens.append(obj_text)
                    last_role_added = "object"
            
            elif role == "connector":
                connector_type = "definition_to_mechanism" if mechanism else "fact_to_impact"
                connectors = self.dna["clusters"]["connectors"].get(connector_type, [])
                if connectors:
                    conn = self._weighted_choice([(c["text"], c["weight"]) for c in connectors])
                    tokens.append(conn)
                    last_role_added = "connector"
            
            elif role == "mechanism" and mechanism:
                tokens.append(mechanism.strip())
                last_role_added = "mechanism"
            
            elif role == "impact" and impact:
                tokens.append(impact.strip())
                last_role_added = "impact"
            
            elif role == "analogy_intro" and analogy:
                analogy_intros = self.dna["clusters"]["connectors"].get("analogy_intro", [])
                if analogy_intros:
                    intro = self._weighted_choice([(a["text"], a["weight"]) for a in analogy_intros])
                    tokens.append(intro)
                    last_role_added = "analogy_intro"
            
            elif role == "analogy" and analogy:
                tokens.append(analogy.strip())
                last_role_added = "analogy"
            
            elif role == "discourse_marker":
                marker = self.inject_discourse_marker()
                if marker:
                    tokens.append(f"{marker}, ")
                    last_role_added = "discourse_marker"
            
            elif role == "fact_bridge":
                bridges = ["This is exactly what happens when", "The same principle applies:", "Here's the connection:"]
                tokens.append(f"{random.choice(bridges)} ")
                last_role_added = "fact_bridge"
            
            elif role == "closer":
                closer_options = self.dna["clusters"]["closings"].get("summary", [])
                # Only add closer if we have a complete sentence already (has verb + object or predicate)
                has_complete_clause = (last_role_added in ["object", "impact", "analogy_end"] or 
                                      (last_role_added == "verb" and atomic.verb.lower() in ['is', 'are', 'was', 'were']))
                if closer_options and random.random() > 0.5 and has_complete_clause:
                    closer = self._weighted_choice([(c["text"], c["weight"]) for c in closer_options])
                    # Ensure proper punctuation before closer
                    if tokens and not tokens[-1].endswith(('.', ',', ' ', '?', '!')):
                        tokens.append('. ')
                    elif tokens and not tokens[-1].endswith(' '):
                        tokens.append(' ')
                    tokens.append(closer)
                    last_role_added = "closer"
            
            elif role == "filler":
                if random.random() > 0.6:
                    filler = self._weighted_choice(self.filler_phrases)
                    tokens.append(f"{filler} ")
                    last_role_added = "filler"
        
        # Vary sentence length
        tokens = self.vary_sentence_length(tokens, target_length)
        
        # Assemble with smart spacing
        result = self._assemble_with_spacing(tokens)
        
        # Ensure proper punctuation
        if result and not result.endswith(('.', '?', '!')):
            result += '.'
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
        
        return result
    
    def _assemble_with_spacing(self, tokens: List[SyntacticToken]) -> str:
        """
        Assembles SyntacticTokens with intelligent spacing to prevent robotic artifacts.
        Handles punctuation, double words, and spacing errors.
        """
        import re
        
        if not tokens:
            return ""
        
        # First pass: join with single spaces, being smart about punctuation
        assembled = []
        prev_token = ""
        
        for token_obj in tokens:
            # Extract text from SyntacticToken object
            token = token_obj.text if hasattr(token_obj, 'text') else str(token_obj)
            token = token.strip()
            if not token:
                continue
            
            # Skip if this is a duplicate of the previous word
            if prev_token and token.lower() == prev_token.lower():
                continue
            
            # Check if previous token ends with punctuation that doesn't need space
            needs_space = True
            if prev_token:
                # No space needed after opening parens or before certain punctuation
                if prev_token.endswith(('(', '[', '{')):
                    needs_space = False
                # Already has trailing space handled
                elif prev_token.endswith((' ',)):
                    needs_space = False
            
            if assembled and needs_space and not token.startswith((' ', ',', '.', ';', ':', '!', '?')):
                assembled.append(' ')
            
            assembled.append(token)
            prev_token = token
        
        raw_text = ''.join(assembled)
        
        # Second pass: Regex cleanup for common artifacts
        return self._smooth_output(raw_text)
    
    def _smooth_output(self, text: str) -> str:
        """
        Post-processing cleanup to fix common procedural generation artifacts.
        """
        import re
        
        if not text:
            return text
        
        # Fix "volatilityis" type errors - missing space between words
        text = re.sub(r'([a-zA-Z])([A-Z][a-z])', r'\1 \2', text)
        
        # Fix double/triple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix missing space after punctuation (e.g., "normal,but" -> "normal, but")
        text = re.sub(r'([,.:;!?])([A-Za-z])', r'\1 \2', text)
        
        # Fix repeated words (e.g., "is is" -> "is", "the the" -> "the")
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Fix stuttering discourse markers (e.g., "essentially essentially")
        text = re.sub(r'\b(essentially|basically|fundamentally|in\s+practice|that\s+is)\s*,?\s*\1\b', r'\1', text, flags=re.IGNORECASE)
        
        # Remove space before commas/periods
        text = re.sub(r'\s+([,.:;!?])', r'\1', text)
        
        # Ensure space after commas/colons if missing
        text = re.sub(r'([,:])([A-Za-z])', r'\1 \2', text)
        
        # Fix consecutive connectors (e.g., "Consequently, This is exactly" -> keep only one)
        connector_patterns = [
            (r'\b(Consequently|Therefore|Thus|Hence|Moreover|Furthermore|Additionally),\s*(This is exactly|The same principle|Here\'s the)', r'\1. \2'),
            (r'\b(What this translates to is|That means|In other words):\s*(The same principle|Here\'s the|This is exactly)', r'\1. \2')
        ]
        for pattern, replacement in connector_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Remove trailing punctuation duplicates (e.g., ".." -> ".")
        text = re.sub(r'([,.!?])\1+', r'\1', text)
        
        # Ensure single space before parentheticals if missing
        text = re.sub(r'(\w)(\()', r'\1 \2', text)
        
        # Fix "is iss" type typos
        text = re.sub(r'\b(is|has|have|was|were)\s+(iss|iss?|iis)\b', r'\1', text, flags=re.IGNORECASE)
        
        # Fix mid-sentence capitalization after connectors (optional nouns should be lowercase)
        # But preserve proper nouns and start of quotes
        text = re.sub(r'\b(Portfolio volatility|Market volatility|Economic indicator)\b', 
                     lambda m: m.group(1).lower() if not text.startswith(m.group(1)) else m.group(1), 
                     text)
        
        # Ensure sentence ends with proper punctuation
        text = text.strip()
        
        # Remove trailing fragments that are incomplete (e.g., "The bottom-line impact:", "This cascades into:")
        trailing_fragment_patterns = [
            r'\s+The\s+(bottom-line\s+)?impact:\s*$',
            r'\s+This\s+cascades\s+into:\s*$',
            r'\s+which\s+is\s+worth\s+noting\s*,?\s*$',
            r'\s+as\s+the\s+evidence\s+suggests\s*$',
            r'\s+if\s+we\s+examine\s+this\s+closely\s*$',
            r'\s+from\s+a\s+structural\s+perspective\s*$',
            r'\s+when\s+you\s+look\s+at\s+the\s+data\s*$',
            r'\s+essentially\s*$',
            r'\s+fundamentally\s*$',
            r'\s+in\s+practice\s*$',
            r'\s+This\s+means\s+that\s*$',
            r'\s+The\s+ripple\s+effect\s+is:\s*$',
            r'\s+For\s+everyday\s+people,\s*$',
            r'\s+Make\s+sense\?$',
            r'\s+Let\s+me\s+know\s+if\s+you\s+need\s+more\s+detail\.?$'
        ]
        for pattern in trailing_fragment_patterns:
            text = re.sub(pattern, '.', text, flags=re.IGNORECASE)
        
        # Fix verb stutter from consecutive connectors (e.g., "Consequently. This is exactly" -> "Consequently, this is exactly")
        text = re.sub(r'\b(Consequently|Therefore|Thus|Hence)\.\s+This\s+is\s+exactly', r'\1, this is exactly', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(Consequently|Therefore|Thus|Hence)\.\s+The\s+same\s+principle', r'\1, the same principle', text, flags=re.IGNORECASE)
        
        if text and not text.endswith(('.', '?', '!')):
            # Check if it ends with a discourse marker that shouldn't have a period
            if not text.lower().endswith(('essentially', 'basically', 'practically speaking')):
                text += '.'
        
        return text
    
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
            # Add common verbs that might not be in clusters
            "peaks": ("peak", [("peak", 1.0), ("spike", 0.9), ("surge", 0.8)], 's'),
            "peaked": ("peak", [("peaked", 1.0), ("spiked", 0.9), ("surged", 0.8)], 'ed'),
            "peaking": ("peak", [("peaking", 1.0), ("spiking", 0.9), ("surging", 0.8)], 'ing'),
            "peak": ("peak", [("peak", 1.0)], 'base'),
            "surges": ("surge", [("surge", 1.0), ("spike", 0.9), ("jump", 0.8)], 's'),
            "surged": ("surge", [("surged", 1.0), ("spiked", 0.9), ("jumped", 0.8)], 'ed'),
            "surging": ("surge", [("surging", 1.0), ("spiking", 0.9), ("jumping", 0.8)], 'ing'),
            "surge": ("surge", [("surge", 1.0)], 'base'),
            "spikes": ("spike", [("spike", 1.0), ("surge", 0.9), ("jump", 0.8)], 's'),
            "spiked": ("spike", [("spiked", 1.0), ("surged", 0.9), ("jumped", 0.8)], 'ed'),
            "spiking": ("spike", [("spiking", 1.0), ("surging", 0.9), ("jumping", 0.8)], 'ing'),
            "spike": ("spike", [("spike", 1.0)], 'base'),
            "jumps": ("jump", [("jump", 1.0), ("spike", 0.9), ("surge", 0.8)], 's'),
            "jumped": ("jump", [("jumped", 1.0), ("spiked", 0.9), ("surged", 0.8)], 'ed'),
            "jumping": ("jump", [("jumping", 1.0), ("spiking", 0.9), ("surging", 0.8)], 'ing'),
            "jump": ("jump", [("jump", 1.0)], 'base'),
            "climbs": ("climb", [("climb", 1.0), ("rise", 0.9), ("gain", 0.8)], 's'),
            "climbed": ("climb", [("climbed", 1.0), ("risen", 0.9), ("gained", 0.8)], 'ed'),
            "climbing": ("climb", [("climbing", 1.0), ("rising", 0.9), ("gaining", 0.8)], 'ing'),
            "climb": ("climb", [("climb", 1.0)], 'base'),
            "gains": ("gain", [("gain", 1.0), ("increase", 0.9), ("rise", 0.8)], 's'),
            "gained": ("gain", [("gained", 1.0), ("increased", 0.9), ("risen", 0.8)], 'ed'),
            "gaining": ("gain", [("gaining", 1.0), ("increasing", 0.9), ("rising", 0.8)], 'ing'),
            "gain": ("gain", [("gain", 1.0)], 'base'),
            "escalates": ("escalate", [("escalate", 1.0), ("accelerate", 0.9), ("intensify", 0.8)], 's'),
            "escalated": ("escalate", [("escalated", 1.0), ("accelerated", 0.9), ("intensified", 0.8)], 'ed'),
            "escalating": ("escalate", [("escalating", 1.0), ("accelerating", 0.9), ("intensifying", 0.8)], 'ing'),
            "escalate": ("escalate", [("escalate", 1.0)], 'base'),
            "hikes": ("hike", [("hike", 1.0), ("increase", 0.9), ("raise", 0.8)], 's'),
            "hiked": ("hike", [("hiked", 1.0), ("increased", 0.9), ("raised", 0.8)], 'ed'),
            "hiking": ("hike", [("hiking", 1.0), ("increasing", 0.9), ("raising", 0.8)], 'ing'),
            "hike": ("hike", [("hike", 1.0)], 'base'),
            "plunges": ("plunge", [("plunge", 1.0), ("drop", 0.9), ("fall", 0.8)], 's'),
            "plunged": ("plunge", [("plunged", 1.0), ("dropped", 0.9), ("fallen", 0.8)], 'ed'),
            "plunging": ("plunge", [("plunging", 1.0), ("dropping", 0.9), ("falling", 0.8)], 'ing'),
            "plunge": ("plunge", [("plunge", 1.0)], 'base'),
            "slumps": ("slump", [("slump", 1.0), ("drop", 0.9), ("decline", 0.8)], 's'),
            "slumped": ("slump", [("slumped", 1.0), ("dropped", 0.9), ("declined", 0.8)], 'ed'),
            "slumping": ("slump", [("slumping", 1.0), ("dropping", 0.9), ("declining", 0.8)], 'ing'),
            "slump": ("slump", [("slump", 1.0)], 'base'),
            # Add more common verbs
            "creates": ("create", [("create", 1.0), ("generate", 0.9), ("produce", 0.85), ("yield", 0.8)], 's'),
            "created": ("create", [("created", 1.0), ("generated", 0.9), ("produced", 0.85)], 'ed'),
            "creating": ("create", [("creating", 1.0), ("generating", 0.9), ("producing", 0.85)], 'ing'),
            "create": ("create", [("create", 1.0)], 'base'),
            "continues": ("continue", [("continue", 1.0), ("persist", 0.9), ("remain", 0.85)], 's'),
            "continued": ("continue", [("continued", 1.0), ("persisted", 0.9), ("remained", 0.85)], 'ed'),
            "continuing": ("continue", [("continuing", 1.0), ("persisting", 0.9)], 'ing'),
            "continue": ("continue", [("continue", 1.0)], 'base'),
        }
        
        # Check if we have a mapping for this verb form
        if verb_lower in base_forms:
            base_key, variants, suffix_type = base_forms[verb_lower]
            selected = self._weighted_choice(variants)
            
            # For auxiliary verbs, irregular forms, and base forms, return as-is
            if suffix_type in ['has', 'have', 'had', 'is', 'are', 'was', 'were', 'been', 'being', 
                               'rose', 'fell', 'grew', 'base']:
                return selected
            
            # Strip any existing suffix from selected word before adding new one
            # CRITICAL: Don't strip if it would create nonsense words
            # Words ending in 'on', 'en', 'an' should NOT be stripped
            for suffix in ['s', 'es', 'ed', 'ing', 'en', 'n']:
                if selected.endswith(suffix) and len(selected) > len(suffix) + 2:
                    # Don't strip if it would leave a very short root or break the word
                    root_candidate = selected[:-len(suffix)]
                    # Avoid stripping that creates nonsense (e.g., "balloon" -> "ballo" + "s" = "balloos")
                    if len(root_candidate) > 4 and not root_candidate.endswith(('oo', 'ee', 'aa')):
                        selected = root_candidate
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
        TWO-PHASE GENERATION PROTOCOL (Option B):
        Phase 1: Deterministic Core Construction (Guaranteed Grammatical Completeness)
        Phase 2: Probabilistic Embellishment (Stylistic Variation)
        """
        # Deconstruct fact
        atomic = self.deconstruct_fact(fact_text, domain)
        
        # ==========================================
        # PHASE 1: DETERMINISTIC CORE CONSTRUCTION
        # Rule: Must produce a valid SVO or SVC sentence. No randomness on structure.
        # ==========================================
        core_tokens = self._build_immutable_core(atomic)
        
        # Validation Gate: Reject if core is not grammatically complete
        if not self._validate_core_completeness(core_tokens):
            # Fallback: Force simplest possible SVO if logic fails
            core_tokens = self._force_minimal_core(atomic)
        
        # ==========================================
        # PHASE 2: PROBABILISTIC EMBELLISHMENT
        # Rule: Add style ONLY around the validated core.
        # ==========================================
        final_tokens = self._apply_stylistic_layer(
            core_tokens=core_tokens,
            atomic=atomic,
            analogy=analogy,
            impact=impact,
            mechanism=mechanism,
            intent=intent
        )
        
        # Assemble and smooth
        result = self._assemble_with_spacing(final_tokens)
        result = self._smooth_output(result)
        
        return result

    def _build_immutable_core(self, atomic: AtomicFact) -> List[SyntacticToken]:
        """
        Builds a grammatically complete sentence core.
        Guarantees: Subject + Verb + (Object/Complement).
        """
        tokens = []
        
        # 1. Subject (Required)
        subj_text = atomic.subject if atomic.subject else "This metric"
        tokens.append(SyntacticToken(subj_text, role="subject"))
        
        # 2. Verb (Required - The Critical Fix)
        verb_text = self._resolve_verb(atomic)
        tokens.append(SyntacticToken(verb_text, role="verb"))
        
        # 3. Object / Complement (Required)
        # Handle copula verbs (is/are) specially to ensure adjective/noun follows
        if self._is_copula(verb_text):
            comp_text = self._build_predicate_complement(atomic)
            if comp_text:
                tokens.append(SyntacticToken(comp_text, role="complement"))
        else:
            # Transitive verb needs object
            obj_text = atomic.object if atomic.object else self._infer_object(atomic)
            if obj_text:
                tokens.append(SyntacticToken(obj_text, role="object"))
                
        return tokens

    def _resolve_verb(self, atomic: AtomicFact) -> str:
        """Deterministically selects the correct verb form."""
        if atomic.verb:
            # If user provided a base verb, conjugate it to match subject (simplified)
            return self._conjugate_verb(atomic.verb, atomic.subject)
        
        # Infer verb from metric/trend if missing
        if atomic.metric_value:
            try:
                val = float(str(atomic.metric_value).replace('%', '').replace('$', '').replace(',', ''))
                if val > 0:
                    return "is rising"
                elif val < 0:
                    return "is falling"
                else:
                    return "is stable"
            except ValueError:
                pass
        
        # Default fallback
        return "is changing"

    def _build_predicate_complement(self, atomic: AtomicFact) -> str:
        """Ensures 'is/are' verbs have a following adjective or noun."""
        parts = []
        if atomic.adjective:
            parts.append(atomic.adjective)
        if atomic.object:
            parts.append(atomic.object)
        if atomic.metric_value:
            parts.append(f"at {atomic.metric_value}")
        if atomic.timeframe:
            parts.append(f"over {atomic.timeframe}")
            
        if not parts:
            # Hardcoded fallbacks to prevent "The market is."
            defaults = ["critical", "volatile", "significant", "in flux"]
            return random.choice(defaults)
            
        return " ".join(parts)

    def _validate_core_completeness(self, tokens: List[SyntacticToken]) -> bool:
        """Strict validation: Must have Subject, Verb, and Complement/Object."""
        has_subj = any(t.grammatical_role == "subject" for t in tokens)
        has_verb = any(t.grammatical_role == "verb" for t in tokens)
        has_comp = any(t.grammatical_role in ["object", "complement"] for t in tokens)
        
        return has_subj and has_verb and has_comp

    def _force_minimal_core(self, atomic: AtomicFact) -> List[SyntacticToken]:
        """Emergency fallback: 'Subject is [state]'."""
        subj = atomic.subject if atomic.subject else "The situation"
        state = atomic.adjective if atomic.adjective else "dynamic"
        return [
            SyntacticToken(subj, role="subject"),
            SyntacticToken("is", role="verb"),
            SyntacticToken(state, role="complement")
        ]

    def _is_copula(self, verb: str) -> bool:
        """Check if verb is a copula (linking verb)."""
        if not verb:
            return False
        copulas = ['is', 'are', 'was', 'were', 'be', 'been', 'being', 'am']
        return verb.lower().split()[0] in copulas

    def _conjugate_verb(self, verb: str, subject: Optional[str] = None) -> str:
        """Simple verb conjugation - returns verb as-is or with minimal modification."""
        if not verb:
            return "is changing"
        
        # If already conjugated, return as-is
        lower_verb = verb.lower()
        if any(lower_verb.endswith(s) for s in ['s', 'es', 'ed', 'ing', 'en']):
            return verb
        
        # Simple third-person singular for present tense
        if subject and any(word in subject.lower() for word in ['it', 'he', 'she', 'the', 'a', 'an']):
            if lower_verb in ['have', 'do', 'go']:
                return {'have': 'has', 'do': 'does', 'go': 'goes'}.get(lower_verb, verb + 's')
            return verb + 's'
        
        return verb

    def _infer_object(self, atomic: AtomicFact) -> Optional[str]:
        """Try to infer an object from the fact text if not explicitly parsed."""
        if atomic.original_text:
            # Simple heuristic: everything after the verb might be the object
            parts = atomic.original_text.split(' ', 2)
            if len(parts) > 2:
                return parts[2]
        return None

    def _apply_stylistic_layer(self, 
                               core_tokens: List[SyntacticToken],
                               atomic: AtomicFact,
                               analogy: Optional[str] = None,
                               impact: Optional[str] = None,
                               mechanism: Optional[str] = None,
                               intent: str = "casual") -> List[SyntacticToken]:
        """
        Wraps the validated core with probabilistic stylistic elements.
        This is where the 'human-like' variance happens.
        """
        final_tokens = []
        
        # 1. Probabilistic Opener (Discourse Marker)
        if random.random() < 0.7:  # 70% chance of opener
            opener = self.inject_discourse_marker(position="start")
            if opener:
                final_tokens.append(SyntacticToken(opener, role="opener"))
        
        # 2. Insert Core (Immutable)
        final_tokens.extend(core_tokens)
        
        # 3. Probabilistic Impact/Mechanism Injection
        if impact and random.random() < 0.5:
            final_tokens.append(SyntacticToken(".", role="punctuation"))
            connector = random.choice(["This means", "As a result", "Consequently"])
            final_tokens.append(SyntacticToken(f"{connector}, {impact}", role="elaboration"))
        
        # 4. Probabilistic Analogy Injection (Mid or End)
        if analogy and random.random() < 0.4:  # 40% chance of analogy
            # Decide position: 50% append to core, 50% new sentence
            if random.random() < 0.5:
                final_tokens.append(SyntacticToken(",", role="punctuation"))
                final_tokens.append(SyntacticToken("like", role="connector"))
                # Ensure analogy is a string, not boolean
                analogy_text = str(analogy) if analogy else "this concept"
                final_tokens.append(SyntacticToken(analogy_text, role="analogy"))
            else:
                final_tokens.append(SyntacticToken(".", role="punctuation"))
                analogy_text = str(analogy) if analogy else "this concept"
                final_tokens.append(SyntacticToken(f"Think of it as {analogy_text}", role="elaboration"))
        
        # 5. Probabilistic Closer
        if random.random() < 0.6:  # 60% chance of closer
            closer = self.inject_discourse_marker(position="end")
            if closer:
                # Ensure we don't end with a comma
                final_tokens.append(SyntacticToken(str(closer).rstrip(','), role="closer"))
                
        return final_tokens


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
