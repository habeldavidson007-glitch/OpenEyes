"""
openeyes/pipeline/processor.py

QueryProcessor: Consolidates all query processing and synthesis logic.
Replaces: engine.py, synthesis_engine.py, logical_synthesizer.py, reasoning_engine.py, 
          router.py, intent_router.py, domain_validator.py, graceful_degradation.py
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Intent Classification & Graceful Degradation (migrated from graceful_degradation.py)
# ============================================================================

class QueryIntent(Enum):
    """Classification of user query intents."""
    FACTUAL = "factual"
    DIAGNOSTIC = "diagnostic"
    TREATMENT = "treatment"
    COMPARISON = "comparison"
    URGENCY = "urgency"
    SYMPTOM_CHECK = "symptom_check"
    DRUG_INFO = "drug_info"
    LIFESTYLE = "lifestyle"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence tiers for graded responses."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    INSUFFICIENT = "insufficient"


@dataclass
class IntentClassification:
    """Result of query intent analysis."""
    intent: QueryIntent
    confidence: float
    entities: list[dict[str, Any]] = field(default_factory=list)
    urgency_detected: bool = False
    requires_medical_disclaimer: bool = True
    suggested_routing: str = "general"


# Intent detection patterns (migrated)
INTENT_PATTERNS = {
    QueryIntent.FACTUAL: [
        r'\bwhat is\b', r'\bwhat are\b', r'\bdefine\b', r'\bexplain\b',
        r'\btell me about\b', r'\bdescribe\b',
    ],
    QueryIntent.DIAGNOSTIC: [
        r'\bcould.*cause\b', r'\bmight.*cause\b', r'\bis.*a sign of\b',
        r'\bis.*a symptom of\b', r'\bdoes.*mean\b', r'\bwhy am i\b',
    ],
    QueryIntent.TREATMENT: [
        r'\bhow to treat\b', r'\btreatment for\b', r'\bwhat can i do for\b',
        r'\bmanage\b', r'\bcure\b', r'\brelieve\b',
    ],
    QueryIntent.COMPARISON: [
        r'\bvs\b', r'\bversus\b', r'\bcompare\b', r'\bdifference between\b',
        r'\bbetter.*or\b',
    ],
    QueryIntent.URGENCY: [
        r'\bemergency\b', r'\burgent\b', r'\bimmediately\b', r'\bnow\b',
        r'\bright now\b', r'\bneed help now\b', r'\bcall 911\b', r'\ber\b',
        r'\bemergency room\b', r'\bhospital\b', r'\boverdose\b', r'\bpoison\b',
        r'\btook too much\b', r'\bchest pain\b', r'\bshortness of breath\b',
        r'\bcan\'t breathe\b', r'\bsevere.*headache\b', r'\bheart attack\b', r'\bstroke\b',
    ],
    QueryIntent.SYMPTOM_CHECK: [
        r'\bi have\b', r'\bi\'m experiencing\b', r'\bi feel\b', r'\bmy.*hurts\b',
        r'\bfeeling\b', r'\bsymptoms?\b',
    ],
    QueryIntent.DRUG_INFO: [
        r'\bside effects?\b', r'\bdosage\b', r'\bdose\b', r'\bhow much.*take\b',
        r'\binteractions?\b', r'\bused for\b', r'\bprescribed for\b',
    ],
    QueryIntent.LIFESTYLE: [
        r'\bprevent\b', r'\bavoid\b', r'\breduce risk\b', r'\bhealthy\b',
        r'\bdiet\b', r'\bexercise\b', r'\blifestyle\b',
    ],
}

EMERGENCY_KEYWORDS = [
    'suicide', 'kill myself', 'self-harm', 'cutting',
    'heart attack', 'chest pain', 'can\'t breathe', 'stroke',
    'overdose', 'poisoning', 'severe bleeding', 'unconscious',
    'seizure', 'anaphylaxis', 'severe allergic reaction',
    'er', 'emergency room', 'hospital', 'took too much',
    'shortness of breath', 'severe headache', 'difficulty breathing',
]

CRISIS_RESOURCES = {
    'suicide_prevention': '988 Suicide & Crisis Lifeline (US)',
    'emergency': 'Call 911 or your local emergency number immediately',
    'poison_control': 'Poison Control: 1-800-222-1222 (US)',
    'domestic_violence': 'National Domestic Violence Hotline: 1-800-799-7233',
}

MEDICAL_DISCLAIMERS = [
    "This information is for educational purposes only and is not medical advice.",
    "Always consult with a qualified healthcare professional for diagnosis and treatment.",
    "Do not disregard professional medical advice or delay seeking care based on this information.",
    "In case of emergency, call 911 or your local emergency services immediately.",
]


def classify_intent(query: str) -> IntentClassification:
    """Classify the intent of a user query."""
    query_lower = query.lower()
    scores = {intent: 0.0 for intent in QueryIntent}
    entities = []
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                scores[intent] += 1.0
    
    # Drug-related boost
    drug_indicators = ['drug', 'medication', 'pill', 'prescription', 'pharmacy']
    if any(ind in query_lower for ind in drug_indicators):
        scores[QueryIntent.DRUG_INFO] += 0.5
    
    common_drugs = [
        'metformin', 'warfarin', 'aspirin', 'ibuprofen', 'lisinopril',
        'atorvastatin', 'omeprazole', 'amlodipine', 'metoprolol', 'gabapentin'
    ]
    for drug in common_drugs:
        if drug in query_lower:
            entities.append({'text': drug, 'type': 'drug'})
            scores[QueryIntent.DRUG_INFO] += 0.8
    
    # Symptom indicators
    symptom_words = ['pain', 'fever', 'headache', 'nausea', 'fatigue', 'dizziness',
                     'cough', 'rash', 'swelling', 'bleeding', 'vomiting']
    for symptom in symptom_words:
        if symptom in query_lower:
            entities.append({'text': symptom, 'type': 'symptom'})
            scores[QueryIntent.SYMPTOM_CHECK] += 0.4
    
    # Urgency check
    urgency_detected = False
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in query_lower:
            urgency_detected = True
            scores[QueryIntent.URGENCY] += 2.0
            break
    
    max_score = max(scores.values())
    if max_score == 0:
        best_intent = QueryIntent.UNKNOWN
        confidence = 0.3
    else:
        best_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(0.95, 0.5 + (max_score * 0.15))
    
    requires_disclaimer = best_intent in [
        QueryIntent.DIAGNOSTIC, QueryIntent.TREATMENT,
        QueryIntent.SYMPTOM_CHECK, QueryIntent.DRUG_INFO,
    ]
    
    routing = "general"
    if urgency_detected:
        routing = "emergency"
    elif best_intent == QueryIntent.SYMPTOM_CHECK:
        routing = "triage"
    elif best_intent == QueryIntent.DRUG_INFO:
        routing = "pharmacology"
    
    return IntentClassification(
        intent=best_intent,
        confidence=confidence,
        entities=entities,
        urgency_detected=urgency_detected,
        requires_medical_disclaimer=requires_disclaimer,
        suggested_routing=routing,
    )


def determine_confidence_level(confidence_percent: float) -> ConfidenceLevel:
    """Map numeric confidence to confidence level enum."""
    if confidence_percent >= 80:
        return ConfidenceLevel.HIGH
    elif confidence_percent >= 60:
        return ConfidenceLevel.MEDIUM
    elif confidence_percent >= 40:
        return ConfidenceLevel.LOW
    elif confidence_percent >= 20:
        return ConfidenceLevel.VERY_LOW
    else:
        return ConfidenceLevel.INSUFFICIENT


def check_safety_halt(query: str, intent: IntentClassification, confidence: float) -> tuple[bool, str]:
    """Determine if a query should be halted for safety reasons."""
    query_lower = query.lower()
    
    self_harm_keywords = [
        'suicide', 'kill myself', 'end my life', 'harm myself', 
        'self-harm', 'cutting myself', 'take my own life'
    ]
    if any(kw in query_lower for kw in self_harm_keywords):
        return True, "SELF_HARM_DETECTED"
    
    if intent.urgency_detected and confidence < 0.5:
        return True, "EMERGENCY_REQUIRES_PROFESSIONAL_HELP"
    
    if intent.intent == QueryIntent.DIAGNOSTIC and confidence < 0.3:
        return True, "LOW_CONFIDENCE_DIAGNOSTIC"
    
    if intent.intent == QueryIntent.TREATMENT and confidence < 0.25:
        return True, "LOW_CONFIDENCE_TREATMENT"
    
    return False, ""


def process_query_with_degradation(
    query: str,
    fragments: List[Any],
    base_confidence: float,
) -> Dict[str, Any]:
    """
    Main entry point: Process a query with full intent classification and graceful degradation.
    This is the function that should be called from the main query pipeline.
    """
    # Step 1: Classify intent
    intent = classify_intent(query)
    
    # Step 2: Check for safety halt
    should_halt, halt_reason = check_safety_halt(query, intent, base_confidence)
    
    if should_halt:
        # Return safety response with appropriate resources
        if halt_reason == "SELF_HARM_DETECTED":
            return {
                'status': 'HALT_SAFETY',
                'answer': "I'm deeply concerned about your wellbeing. Please reach out for help right now.",
                'urgent_resources': {
                    'suicide_prevention': CRISIS_RESOURCES['suicide_prevention'],
                    'emergency': CRISIS_RESOURCES['emergency'],
                },
                'message': "You are not alone. Trained counselors are available 24/7.",
            }
        elif halt_reason == "EMERGENCY_REQUIRES_PROFESSIONAL_HELP":
            return {
                'status': 'HALT_SAFETY',
                'answer': "This appears to be an urgent medical situation. Please seek immediate professional help.",
                'urgent_resources': {
                    'emergency': CRISIS_RESOURCES['emergency'],
                },
            }
        else:
            return {
                'status': 'HALT_SAFETY',
                'answer': "I cannot provide a safe, reliable answer to this question with the information available.",
                'suggestion': "Please consult a healthcare professional for personalized medical advice.",
                'halt_reason': halt_reason,
            }
    
    # For non-halted queries, return basic success response
    # (Full graded response generation would go here if needed)
    return {
        'status': 'ANSWER_PROVIDED',
        'intent': intent.intent.value,
        'confidence': base_confidence,
        'requires_disclaimer': intent.requires_medical_disclaimer,
    }


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
