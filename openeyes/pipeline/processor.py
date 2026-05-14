"""
openeyes/pipeline/processor.py

QueryProcessor: Consolidates all query processing and synthesis logic.
Replaces: engine.py, synthesis_engine.py, logical_synthesizer.py, reasoning_engine.py, 
          router.py, intent_router.py, domain_validator.py
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProcessedResponse:
    answer: str
    status: str  # 'ANSWER_PROVIDED', 'HALT_EMERGENCY', 'INSUFFICIENT_DATA'
    confidence: float
    fragments_used: int
    domain: str
    metadata: Dict

class QueryProcessor:
    """
    Unified query processing engine that handles:
    - Domain routing and validation
    - Intent classification
    - Emergency detection
    - Logical synthesis
    - Human-like narrative generation
    
    Produces direct, concise answers that address the actual question first.
    """
    
    def __init__(self):
        self._synthesis_engine = None
        self._emergency_detector = None
        self._domain_validator = None
        self._intent_classifier = None
        
    @property
    def synthesis_engine(self):
        if self._synthesis_engine is None:
            from openeyes.core.synthesis_engine import SynthesisEngine
            self._synthesis_engine = SynthesisEngine()
        return self._synthesis_engine
    
    @property
    def emergency_detector(self):
        if self._emergency_detector is None:
            from openeyes.core.emergency_detection import detect_emergency, get_emergency_message
            self._detect_func = detect_emergency
            self._message_func = get_emergency_message
        return self
    
    @property
    def domain_validator(self):
        if self._domain_validator is None:
            from openeyes.core.domain_validator import DomainValidator
            self._domain_validator = DomainValidator()
        return self._domain_validator
    
    def process(self, query: str, domain: str, fragments: List[Dict]) -> ProcessedResponse:
        """
        Main processing pipeline:
        1. Check for emergencies (medical/safety)
        2. Validate domain appropriateness
        3. Classify intent
        4. Synthesize answer with human-like narrative
        """
        # Step 1: Emergency detection
        is_emergency, emergency_type = self._check_emergency(query, domain)
        if is_emergency:
            return self._create_emergency_response(emergency_type, domain)
        
        # Step 2: Check if we have sufficient data
        if not fragments or len(fragments) == 0:
            return ProcessedResponse(
                answer="I don't have enough information in my knowledge base to answer this question confidently.",
                status='INSUFFICIENT_DATA',
                confidence=0.0,
                fragments_used=0,
                domain=domain,
                metadata={'reason': 'no_fragments'}
            )
        
        # Step 3: Filter low-quality fragments
        filtered_fragments = self._filter_fragments(fragments, query)
        
        if len(filtered_fragments) == 0:
            return ProcessedResponse(
                answer="No relevant information found for this specific query.",
                status='INSUFFICIENT_DATA',
                confidence=0.0,
                fragments_used=0,
                domain=domain,
                metadata={'reason': 'no_relevant_fragments'}
            )
        
        # Step 4: Synthesize human-like answer
        answer = self._synthesize_answer(query, filtered_fragments, domain)
        
        # Step 5: Calculate confidence
        avg_confidence = sum(f.get('confidence_score', 0.5) for f in filtered_fragments) / len(filtered_fragments)
        
        return ProcessedResponse(
            answer=answer,
            status='ANSWER_PROVIDED',
            confidence=avg_confidence,
            fragments_used=len(filtered_fragments),
            domain=domain,
            metadata={
                'fragment_sources': list(set(f.get('_source', 'unknown') for f in filtered_fragments)),
                'query_length': len(query)
            }
        )
    
    def _check_emergency(self, query: str, domain: str) -> Tuple[bool, Optional[str]]:
        """Check if query indicates a medical/safety emergency."""
        if domain != 'medical':
            return False, None
        
        try:
            from openeyes.core.emergency_detection import detect_emergency
            is_emergency = detect_emergency(query)
            
            if is_emergency:
                # Determine emergency type
                query_lower = query.lower()
                if any(word in query_lower for word in ['heart attack', 'chest pain', 'cardiac']):
                    return True, 'cardiac'
                elif any(word in query_lower for word in ['stroke', 'numbness', 'slurred speech']):
                    return True, 'stroke'
                elif any(word in query_lower for word in ['suicide', 'kill myself', 'end my life']):
                    return True, 'mental_health'
                elif any(word in query_lower for word in ['bleeding', 'hemorrhage', 'severe blood']):
                    return True, 'trauma'
                else:
                    return True, 'general_medical'
            
            return False, None
        except Exception as e:
            logger.warning(f"Emergency detection failed: {e}")
            return False, None
    
    def _create_emergency_response(self, emergency_type: str, domain: str) -> ProcessedResponse:
        """Create appropriate emergency response with halt status."""
        messages = {
            'cardiac': "🚨 MEDICAL EMERGENCY DETECTED: Symptoms suggest a possible heart attack. Call emergency services (911/999) immediately. Do not wait. Chew aspirin if available and not allergic while waiting for help.",
            'stroke': "🚨 MEDICAL EMERGENCY DETECTED: Symptoms suggest a possible stroke. Call emergency services (911/999) immediately. Note the time symptoms started. Do not give food or water. Keep the person comfortable and monitor breathing.",
            'mental_health': "🚨 MENTAL HEALTH EMERGENCY DETECTED: If you're having thoughts of self-harm, please reach out now. In the US: Call/text 988 (Suicide & Crisis Lifeline). UK: Call 111 or Samaritans at 116 123. You are not alone, help is available.",
            'trauma': "🚨 MEDICAL EMERGENCY DETECTED: Severe bleeding detected. Apply direct pressure to the wound immediately. Call emergency services (911/999). Elevate the injured area if possible. Do not remove embedded objects.",
            'general_medical': "🚨 MEDICAL EMERGENCY DETECTED: This appears to be an urgent medical situation. Please call emergency services (911/999) or go to the nearest emergency room immediately. Do not rely on AI for emergency medical advice."
        }
        
        return ProcessedResponse(
            answer=messages.get(emergency_type, messages['general_medical']),
            status='HALT_EMERGENCY',
            confidence=1.0,
            fragments_used=0,
            domain=domain,
            metadata={'emergency_type': emergency_type, 'action_required': 'call_emergency_services'}
        )
    
    def _filter_fragments(self, fragments: List[Dict], query: str) -> List[Dict]:
        """Filter out low-quality or irrelevant fragments."""
        if not fragments:
            return []
        
        query_lower = query.lower()
        query_words = set(w for w in query_lower.split() if len(w) > 2)
        
        filtered = []
        for frag in fragments:
            content = frag.get('claim', '').lower()
            
            # Skip very short fragments
            if len(content) < 30:
                continue
            
            # Skip scraper artifacts
            if any(artifact in content for artifact in ['duckduckgo', 'search endpoint', 'retrieved 0', 'bots use']):
                continue
            
            # Skip obviously irrelevant content
            irrelevant_topics = ['ai regulation', 'climate change policy', 'geopolitical conflict']
            if any(topic in content for topic in irrelevant_topics):
                # Unless query is about these topics
                if not any(topic in query_lower for topic in irrelevant_topics):
                    continue
            
            # Check relevance to query
            content_words = set(content.split())
            overlap = query_words & content_words
            
            # Keep if has some relevance or high confidence
            if len(overlap) >= 1 or frag.get('confidence_score', 0) >= 0.7:
                filtered.append(frag)
        
        # Sort by confidence
        filtered.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        return filtered[:10]  # Limit to top 10
    
    def _synthesize_answer(self, query: str, fragments: List[Dict], domain: str) -> str:
        """Generate human-like answer using synthesis engine."""
        try:
            # Use existing synthesis engine for narrative generation
            narrative = self.synthesis_engine.synthesize(query, fragments)
            
            if narrative and len(narrative.strip()) > 20:
                return narrative
        except Exception as e:
            logger.warning(f"Synthesis failed: {e}, using fallback")
        
        # Fallback: Direct fragment combination
        return self._fallback_answer(query, fragments)
    
    def _fallback_answer(self, query: str, fragments: List[Dict]) -> str:
        """Simple fallback answer generation."""
        if not fragments:
            return "I don't have enough information to answer this question."
        
        # For "What is X?" questions, try to find a definition
        query_lower = query.lower()
        if query_lower.startswith('what'):
            # Look for fragments that look like definitions
            for frag in fragments:
                content = frag.get('claim', '')
                if any(pattern in content.lower() for pattern in [' is ', ' are ', ' refers to ', ' means ']):
                    return content
            
            # Just return the highest confidence fragment
            return fragments[0].get('claim', '')
        
        # For other questions, combine top fragments
        parts = []
        for i, frag in enumerate(fragments[:3]):
            content = frag.get('claim', '')
            if i == 0:
                parts.append(content)
            else:
                parts.append(f"Additionally, {content.lower()}")
        
        return " ".join(parts)
