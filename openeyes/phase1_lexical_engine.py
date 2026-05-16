"""
Phase 1: Lexical Priority Engine
Implements semantic input processing with token prioritization, synonym expansion,
and phonetic normalization for sub-millisecond query processing.
"""

import re
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib


@dataclass
class WeightedToken:
    """A token with semantic weight and metadata."""
    text: str
    weight: float
    token_class: str  # 'core_entity', 'context_modifier', 'filler'
    position: int = 0
    synonyms: List[str] = field(default_factory=list)
    soundex_code: str = ""


class LexicalPriorityEngine:
    """
    Phase 1: Semantic Input & Token Prioritization
    
    Processes raw human language into clean, weighted logical components
    without neural network matrix math.
    """
    
    # Token class weights (Section 1.1)
    TOKEN_WEIGHTS = {
        'core_entity': 2.0,      # Broad categories, asset classes, system states
        'context_modifier': 1.2, # Critical descriptive properties
        'filler': 0.2,           # Conversational prefixes
    }
    
    # Core entity keywords by domain (extensible)
    CORE_ENTITIES = {
        'economy': {'inflation', 'recession', 'default', 'gdp', 'interest rate', 
                   'unemployment', 'fiscal policy', 'monetary policy', 'debt', 'deficit'},
        'healthcare': {'disease', 'symptom', 'treatment', 'medication', 'diagnosis',
                      'therapy', 'condition', 'disorder', 'syndrome', 'infection'},
        'investment': {'stock', 'bond', 'asset', 'portfolio', 'return', 'risk',
                      'dividend', 'equity', 'security', 'market', 'fund'},
        'governance': {'policy', 'regulation', 'law', 'legislation', 'compliance',
                      'government', 'agency', 'authority', 'mandate', 'statute'},
        'general': {'system', 'process', 'method', 'approach', 'strategy', 'framework'},
    }
    
    # Context modifiers (Section 1.1)
    CONTEXT_MODIFIERS = {'hyper', 'severe', 'acute', 'chronic', 'critical', 'extreme',
                        'rapid', 'gradual', 'significant', 'minor', 'major', 'partial',
                        'global', 'local', 'systemic', 'isolated', 'emerging', 'established'}
    
    # Syntactic fillers to strip (Section 1.1)
    FILLER_PATTERNS = [
        r'^can you explain\s+', r'^please provide\s+', r'^i would like to know\s+',
        r'^what are?\s+', r'^what is\s+', r'^how does?\s+', r'^why does?\s+',
        r'^tell me about\s+', r'^give me details on\s+', r'^i need information about\s+',
        r'^could you tell me\s+', r'^do you know\s+', r'^is it true that\s+',
    ]
    
    def __init__(self):
        self._synonym_cache: Dict[str, List[str]] = {}
        self._soundex_cache: Dict[str, str] = {}
        self._load_synonym_registry()
    
    def _load_synonym_registry(self):
        """Load synonym mappings from query_normalizer module."""
        try:
            from openeyes.query_normalizer import SYNONYM_REGISTRY
            for syn_set in SYNONYM_REGISTRY:
                if isinstance(syn_set, set) and len(syn_set) > 0:
                    canonical = sorted(syn_set)[0]
                    for term in syn_set:
                        self._synonym_cache[term.lower()] = list(syn_set)
                        self._synonym_cache[canonical.lower()] = list(syn_set)
        except ImportError:
            pass  # Use empty registry if not available
    
    def _compute_soundex(self, word: str) -> str:
        """
        Compute Soundex code for phonetic matching.
        Standard American Soundex algorithm.
        """
        if word in self._soundex_cache:
            return self._soundex_cache[word]
        
        if not word:
            return ""
        
        word = word.upper()
        first_letter = word[0]
        
        # Mapping for Soundex codes
        soundex_map = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6',
        }
        
        # Encode remaining letters
        encoded = []
        prev_code = soundex_map.get(first_letter, '0')
        
        for char in word[1:]:
            code = soundex_map.get(char, '0')
            if code != '0' and code != prev_code:
                encoded.append(code)
            prev_code = code if code != '0' else prev_code
        
        # Build final Soundex code
        result = first_letter + ''.join(encoded)
        result = result[:4].ljust(4, '0')
        
        self._soundex_cache[word] = result
        return result
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _strip_fillers(self, query: str) -> str:
        """Remove syntactic filler patterns from query."""
        result = query
        for pattern in self.FILLER_PATTERNS:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        return result.strip()
    
    def _classify_token(self, token: str, domain: str) -> Tuple[str, float]:
        """
        Classify a token and assign weight based on grammatical class.
        Returns (token_class, weight).
        """
        token_lower = token.lower()
        
        # Check for core entities
        domain_entities = self.CORE_ENTITIES.get(domain, set()) | self.CORE_ENTITIES.get('general', set())
        if any(entity in token_lower for entity in domain_entities):
            return 'core_entity', self.TOKEN_WEIGHTS['core_entity']
        
        # Check for context modifiers
        if any(mod in token_lower for mod in self.CONTEXT_MODIFIERS):
            return 'context_modifier', self.TOKEN_WEIGHTS['context_modifier']
        
        # Default to filler
        return 'filler', self.TOKEN_WEIGHTS['filler']
    
    def _expand_synonyms(self, token: str) -> List[str]:
        """Expand a token to include all known synonyms."""
        token_lower = token.lower()
        if token_lower in self._synonym_cache:
            return self._synonym_cache[token_lower]
        return [token]
    
    def _find_phonetic_matches(self, token: str, vocabulary: Set[str], max_distance: int = 2) -> List[str]:
        """
        Find phonetically similar tokens using Soundex and Levenshtein distance.
        Corrects typos dynamically.
        """
        matches = []
        token_soundex = self._compute_soundex(token)
        token_lower = token.lower()
        
        for vocab_word in vocabulary:
            vocab_lower = vocab_word.lower()
            
            # Exact match
            if token_lower == vocab_lower:
                continue
            
            # Soundex match + edit distance check
            vocab_soundex = self._compute_soundex(vocab_lower)
            if token_soundex == vocab_soundex:
                distance = self._levenshtein_distance(token_lower, vocab_lower)
                if distance <= max_distance:
                    matches.append(vocab_word)
        
        return matches
    
    def process_query(self, query: str, domain: str = 'general') -> List[WeightedToken]:
        """
        Process raw query into weighted tokens with synonym expansion
        and phonetic normalization.
        
        Args:
            query: Raw user query string
            domain: Target domain for classification
            
        Returns:
            List of WeightedToken objects sorted by weight (descending)
        """
        # Step 1: Strip fillers
        cleaned_query = self._strip_fillers(query)
        
        # Step 2: Tokenize
        tokens = re.findall(r'\b[a-zA-Z][a-zA-Z\-]+\b', cleaned_query)
        
        # Step 3: Build vocabulary from all sources
        vocabulary = set()
        for domain_entities in self.CORE_ENTITIES.values():
            vocabulary.update(domain_entities)
        vocabulary.update(self.CONTEXT_MODIFIERS)
        for syn_list in self._synonym_cache.values():
            vocabulary.update(syn_list)
        
        # Step 4: Process each token
        weighted_tokens: List[WeightedToken] = []
        
        for position, token in enumerate(tokens):
            # Classify and weight
            token_class, weight = self._classify_token(token, domain)
            
            # Expand synonyms
            synonyms = self._expand_synonyms(token)
            
            # Phonetic correction
            phonetic_matches = self._find_phonetic_matches(token, vocabulary)
            if phonetic_matches:
                # Use first phonetic match as correction
                corrected_token = phonetic_matches[0]
                synonyms.extend(self._expand_synonyms(corrected_token))
            
            # Compute Soundex
            soundex = self._compute_soundex(token)
            
            weighted_tokens.append(WeightedToken(
                text=token,
                weight=weight,
                token_class=token_class,
                position=position,
                synonyms=list(set(synonyms)),  # Deduplicate
                soundex_code=soundex
            ))
        
        # Sort by weight descending (highest priority first)
        weighted_tokens.sort(key=lambda t: t.weight, reverse=True)
        
        return weighted_tokens
    
    def get_priority_keywords(self, query: str, domain: str = 'general', top_n: int = 5) -> List[str]:
        """
        Extract top-N priority keywords from query.
        
        Args:
            query: Raw user query
            domain: Target domain
            top_n: Number of top keywords to return
            
        Returns:
            List of keyword strings (including synonyms)
        """
        weighted_tokens = self.process_query(query, domain)
        
        keywords = []
        for token in weighted_tokens[:top_n]:
            keywords.extend(token.synonyms)
        
        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def normalize_query(self, query: str, domain: str = 'general') -> str:
        """
        Normalize query to canonical form with corrections applied.
        
        Args:
            query: Raw user query
            domain: Target domain
            
        Returns:
            Normalized query string
        """
        weighted_tokens = self.process_query(query, domain)
        
        # Use highest-weight tokens, prefer original if no better synonym
        normalized_parts = []
        for token in weighted_tokens:
            if token.token_class != 'filler':
                # Use first synonym (should be canonical form)
                normalized_parts.append(token.synonyms[0] if token.synonyms else token.text)
        
        return ' '.join(normalized_parts)
    
    def detect_typos(self, query: str, domain: str = 'general') -> List[Dict[str, str]]:
        """
        Detect potential typos in query using phonetic matching.
        
        Args:
            query: Raw user query
            domain: Target domain
            
        Returns:
            List of dicts with 'original', 'correction', 'confidence' keys
        """
        weighted_tokens = self.process_query(query, domain)
        corrections = []
        
        for token in weighted_tokens:
            if token.synonyms and token.text.lower() != token.synonyms[0].lower():
                # Found a correction
                confidence = 1.0 - (self._levenshtein_distance(token.text, token.synonyms[0]) / max(len(token.text), len(token.synonyms[0])))
                corrections.append({
                    'original': token.text,
                    'correction': token.synonyms[0],
                    'confidence': round(confidence, 2)
                })
        
        return corrections


# Singleton instance
_lexical_engine: Optional[LexicalPriorityEngine] = None


def get_lexical_engine() -> LexicalPriorityEngine:
    """Get or create singleton LexicalPriorityEngine instance."""
    global _lexical_engine
    if _lexical_engine is None:
        _lexical_engine = LexicalPriorityEngine()
    return _lexical_engine


def process_query_lexical(query: str, domain: str = 'general') -> List[WeightedToken]:
    """Convenience function to process query through lexical engine."""
    return get_lexical_engine().process_query(query, domain)


def extract_priority_keywords(query: str, domain: str = 'general', top_n: int = 5) -> List[str]:
    """Convenience function to extract priority keywords."""
    return get_lexical_engine().get_priority_keywords(query, domain, top_n)


def normalize_query_lexical(query: str, domain: str = 'general') -> str:
    """Convenience function to normalize query."""
    return get_lexical_engine().normalize_query(query, domain)


if __name__ == "__main__":
    # Test the Lexical Priority Engine
    engine = LexicalPriorityEngine()
    
    test_queries = [
        ("What causes inflation?", "economy"),
        ("Can you explain hyperinflation effects?", "economy"),
        ("Is insulin safe for type 2 diabetes?", "healthcare"),
        ("What are symptoms of acute myocardial infarction?", "healthcare"),
        ("Please provide details on stock market trends", "investment"),
        ("I need information about fiscal policy regulations", "governance"),
        ("How does recipies affect baking bread?", "general"),  # Typo: "recipies" -> "recipes"
    ]
    
    print("=" * 80)
    print("PHASE 1: LEXICAL PRIORITY ENGINE TEST SUITE")
    print("=" * 80)
    
    for query, domain in test_queries:
        print(f"\nQuery: '{query}' (Domain: {domain})")
        print("-" * 60)
        
        # Process query
        tokens = engine.process_query(query, domain)
        print(f"Top weighted tokens:")
        for token in tokens[:5]:
            print(f"  [{token.weight:.1f}] {token.text} ({token.token_class})")
            if token.synonyms and len(token.synonyms) > 1:
                print(f"       Synonyms: {', '.join(token.synonyms[:3])}")
        
        # Get priority keywords
        keywords = engine.get_priority_keywords(query, domain, top_n=3)
        print(f"Priority keywords: {keywords}")
        
        # Normalize
        normalized = engine.normalize_query(query, domain)
        print(f"Normalized: {normalized}")
        
        # Detect typos
        typos = engine.detect_typos(query, domain)
        if typos:
            print(f"Typo corrections:")
            for typo in typos:
                print(f"  '{typo['original']}' -> '{typo['correction']}' (confidence: {typo['confidence']})")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
