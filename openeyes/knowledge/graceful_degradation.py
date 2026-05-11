"""
P1 Implementation: Graceful Degradation & Query Intent Classification

This module implements:
1. Query intent classification (factual, diagnostic, treatment, comparison, urgency)
2. Graceful degradation with confidence-graded responses
3. Medical disclaimers and safety checks
4. Emergency detection and crisis resource routing
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from openeyes.knowledge.fragments import Fragment


class QueryIntent(Enum):
    """Classification of user query intents."""
    FACTUAL = "factual"  # "What is X?"
    DIAGNOSTIC = "diagnostic"  # "Could X cause Y?"
    TREATMENT = "treatment"  # "How to treat X?"
    COMPARISON = "comparison"  # "X vs Y"
    URGENCY = "urgency"  # "Emergency: X"
    SYMPTOM_CHECK = "symptom_check"  # "I have symptom X"
    DRUG_INFO = "drug_info"  # "Side effects of drug X"
    LIFESTYLE = "lifestyle"  # "How to prevent X"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence tiers for graded responses."""
    HIGH = "high"  # >80% - Can answer confidently
    MEDIUM = "medium"  # 60-80% - Answer with caveats
    LOW = "low"  # 40-60% - Limited information available
    VERY_LOW = "very_low"  # <40% - Minimal information, strong disclaimer
    INSUFFICIENT = "insufficient"  # Cannot answer safely


@dataclass
class IntentClassification:
    """Result of query intent analysis."""
    intent: QueryIntent
    confidence: float
    entities: list[dict[str, Any]] = field(default_factory=list)
    urgency_detected: bool = False
    requires_medical_disclaimer: bool = True
    suggested_routing: str = "general"


@dataclass
class GradedResponse:
    """A response with confidence grading and appropriate messaging."""
    status: str  # ANSWER_HIGH_CONFIDENCE, ANSWER_LOW_CONFIDENCE, HALT_SAFETY
    answer: str
    confidence_percent: float
    confidence_level: ConfidenceLevel
    fragments_used: list[Fragment]
    sources: list[dict[str, str]]
    limitations: list[str]
    disclaimers: list[str]
    related_topics: list[str]
    emergency_resources: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# Intent detection patterns
INTENT_PATTERNS = {
    QueryIntent.FACTUAL: [
        r'\bwhat is\b',
        r'\bwhat are\b',
        r'\bdefine\b',
        r'\bexplain\b',
        r'\btell me about\b',
        r'\bdescribe\b',
    ],
    QueryIntent.DIAGNOSTIC: [
        r'\bcould.*cause\b',
        r'\bmight.*cause\b',
        r'\bis.*a sign of\b',
        r'\bis.*a symptom of\b',
        r'\bdoes.*mean\b',
        r'\bwhy am i\b',
    ],
    QueryIntent.TREATMENT: [
        r'\bhow to treat\b',
        r'\btreatment for\b',
        r'\bwhat can i do for\b',
        r'\bmanage\b',
        r'\bcure\b',
        r'\brelieve\b',
    ],
    QueryIntent.COMPARISON: [
        r'\bvs\b',
        r'\bversus\b',
        r'\bcompare\b',
        r'\bdifference between\b',
        r'\bbetter.*or\b',
    ],
    QueryIntent.URGENCY: [
        r'\bemergency\b',
        r'\burgent\b',
        r'\bimmediately\b',
        r'\bnow\b',
        r'\bright now\b',
        r'\bneed help now\b',
        r'\bcall 911\b',
    ],
    QueryIntent.SYMPTOM_CHECK: [
        r'\bi have\b',
        r'\bi\'m experiencing\b',
        r'\bi feel\b',
        r'\bmy.*hurts\b',
        r'\bfeeling\b',
        r'\bsymptoms?\b',
    ],
    QueryIntent.DRUG_INFO: [
        r'\bside effects?\b',
        r'\bdosage\b',
        r'\bdose\b',
        r'\bhow much.*take\b',
        r'\binteractions?\b',
        r'\bused for\b',
        r'\bprescribed for\b',
    ],
    QueryIntent.LIFESTYLE: [
        r'\bprevent\b',
        r'\bavoid\b',
        r'\breduce risk\b',
        r'\bhealthy\b',
        r'\bdiet\b',
        r'\bexercise\b',
        r'\blifestyle\b',
    ],
}

# Emergency keywords that trigger immediate crisis routing
EMERGENCY_KEYWORDS = [
    'suicide', 'kill myself', 'self-harm', 'cutting',
    'heart attack', 'chest pain', 'can\'t breathe', 'stroke',
    'overdose', 'poisoning', 'severe bleeding', 'unconscious',
    'seizure', 'anaphylaxis', 'severe allergic reaction',
]

# Crisis resources
CRISIS_RESOURCES = {
    'suicide_prevention': '988 Suicide & Crisis Lifeline (US)',
    'emergency': 'Call 911 or your local emergency number immediately',
    'poison_control': 'Poison Control: 1-800-222-1222 (US)',
    'domestic_violence': 'National Domestic Violence Hotline: 1-800-799-7233',
}

# Standard medical disclaimers
MEDICAL_DISCLAIMERS = [
    "This information is for educational purposes only and is not medical advice.",
    "Always consult with a qualified healthcare professional for diagnosis and treatment.",
    "Do not disregard professional medical advice or delay seeking care based on this information.",
    "In case of emergency, call 911 or your local emergency services immediately.",
]


def classify_intent(query: str) -> IntentClassification:
    """
    Classify the intent of a user query.
    
    Analyzes the query to determine:
    - Primary intent type
    - Confidence in classification
    - Recognized entities
    - Urgency level
    - Required safety measures
    """
    query_lower = query.lower()
    scores = {intent: 0.0 for intent in QueryIntent}
    entities = []
    
    # Score each intent based on pattern matching
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                scores[intent] += 1.0
    
    # Boost scores based on entity recognition
    # Drug-related queries
    drug_indicators = ['drug', 'medication', 'pill', 'prescription', 'pharmacy']
    if any(ind in query_lower for ind in drug_indicators):
        scores[QueryIntent.DRUG_INFO] += 0.5
    
    # Common drug names (simplified list)
    common_drugs = [
        'metformin', 'warfarin', 'aspirin', 'ibuprofen', 'lisinopril',
        'atorvastatin', 'omeprazole', 'amlodipine', 'metoprolol', 'gabapentin'
    ]
    for drug in common_drugs:
        if drug in query_lower:
            entities.append({'text': drug, 'type': 'drug'})
            scores[QueryIntent.DRUG_INFO] += 0.8
    
    # Condition indicators
    condition_indicators = ['disease', 'disorder', 'condition', 'syndrome', 'cancer']
    if any(ind in query_lower for ind in condition_indicators):
        scores[QueryIntent.FACTUAL] += 0.3
    
    # Symptom indicators
    symptom_words = [
        'pain', 'fever', 'headache', 'nausea', 'fatigue', 'dizziness',
        'cough', 'rash', 'swelling', 'bleeding', 'vomiting'
    ]
    for symptom in symptom_words:
        if symptom in query_lower:
            entities.append({'text': symptom, 'type': 'symptom'})
            scores[QueryIntent.SYMPTOM_CHECK] += 0.4
    
    # Check for urgency/emergency
    urgency_detected = False
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in query_lower:
            urgency_detected = True
            scores[QueryIntent.URGENCY] += 2.0  # Strong boost
            break
    
    # Find best matching intent
    max_score = max(scores.values())
    if max_score == 0:
        best_intent = QueryIntent.UNKNOWN
        confidence = 0.3
    else:
        best_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(0.95, 0.5 + (max_score * 0.15))
    
    # Determine if medical disclaimer is required
    requires_disclaimer = best_intent in [
        QueryIntent.DIAGNOSTIC,
        QueryIntent.TREATMENT,
        QueryIntent.SYMPTOM_CHECK,
        QueryIntent.DRUG_INFO,
    ]
    
    # Suggest routing based on intent
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


def generate_graded_response(
    query: str,
    fragments: list[Fragment],
    intent: IntentClassification,
    raw_confidence: float = 0.0,
) -> GradedResponse:
    """
    Generate a graded response based on available fragments and confidence.
    
    This implements graceful degradation:
    - High confidence: Full answer with sources
    - Medium confidence: Answer with caveats
    - Low confidence: Limited information, strong disclaimers
    - Very low: Minimal info, suggest alternatives
    - Insufficient: Safety halt with helpful guidance
    """
    confidence_level = determine_confidence_level(raw_confidence)
    
    # Build sources list from fragments
    sources = []
    for frag in fragments[:5]:
        if frag.source_id and frag.source_id != 'unknown':
            sources.append({
                'id': frag.source_id,
                'type': frag.source_type,
                'url': frag.source_url,
                'published': frag.published_on,
            })
    
    # Collect limitations
    limitations = []
    for frag in fragments[:3]:
        limitations.extend(frag.limitations)
    limitations = list(set(limitations))[:5]  # Dedupe, limit to 5
    
    # Build answer based on confidence level
    answer_parts = []
    status = "ANSWER_HIGH_CONFIDENCE"
    
    if confidence_level == ConfidenceLevel.HIGH:
        # Full answer
        claims = [f.claim for f in fragments if f.claim]
        answer_parts.extend(claims[:3])
        
    elif confidence_level == ConfidenceLevel.MEDIUM:
        # Answer with mild caveats
        answer_parts.append("Based on available information:")
        claims = [f.claim for f in fragments if f.claim]
        answer_parts.extend(claims[:2])
        if limitations:
            answer_parts.append(f"Note: {limitations[0]}")
            
    elif confidence_level == ConfidenceLevel.LOW:
        status = "ANSWER_LOW_CONFIDENCE"
        answer_parts.append("Limited information is available on this topic. Here's what I found:")
        if fragments:
            claims = [f.claim for f in fragments if f.claim]
            answer_parts.extend(claims[:1])
        answer_parts.append("This information may be incomplete. Please consult additional sources.")
        
    elif confidence_level == ConfidenceLevel.VERY_LOW:
        status = "ANSWER_LOW_CONFIDENCE"
        answer_parts.append("I have very limited information about this topic.")
        if fragments:
            answer_parts.append(fragments[0].claim[:200])
        answer_parts.append("I cannot provide a comprehensive answer. Please consult a healthcare professional or authoritative medical sources.")
        
    else:  # INSUFFICIENT
        status = "HALT_SAFETY"
        answer_parts.append("I don't have sufficient reliable information to answer this question safely.")
        answer_parts.append("For health-related questions, please consult:")
        answer_parts.append("- Your healthcare provider")
        answer_parts.append("- A pharmacist")
        answer_parts.append("- Authoritative medical websites (Mayo Clinic, WebMD, CDC)")
    
    # Add disclaimers
    disclaimers = []
    if intent.requires_medical_disclaimer:
        disclaimers.extend(MEDICAL_DISCLAIMERS[:2])
    
    # Add emergency resources if urgency detected
    emergency_resources = {}
    if intent.urgency_detected:
        emergency_resources['immediate'] = CRISIS_RESOURCES['emergency']
        if any(kw in query.lower() for kw in ['suicide', 'self-harm', 'kill myself']):
            emergency_resources['crisis'] = CRISIS_RESOURCES['suicide_prevention']
        if any(kw in query.lower() for kw in ['overdose', 'poison']):
            emergency_resources['poison'] = CRISIS_RESOURCES['poison_control']
    
    # Suggest related topics
    related_topics = []
    if fragments:
        # Extract from fragment topics
        for frag in fragments[:2]:
            if hasattr(frag, 'topic'):
                related_topics.append(frag.topic)
    
    # Build final answer
    answer = "\n\n".join(answer_parts)
    
    return GradedResponse(
        status=status,
        answer=answer,
        confidence_percent=raw_confidence,
        confidence_level=confidence_level,
        fragments_used=fragments,
        sources=sources,
        limitations=limitations,
        disclaimers=disclaimers,
        related_topics=related_topics,
        emergency_resources=emergency_resources,
        metadata={
            'intent': intent.intent.value,
            'routing': intent.suggested_routing,
            'timestamp': datetime.now().isoformat(),
        }
    )


def format_response_for_user(response: GradedResponse) -> dict[str, Any]:
    """
    Format a graded response for user-facing output.
    
    Returns a dictionary suitable for API response or display.
    """
    result = {
        'status': response.status,
        'answer': response.answer,
        'confidence': {
            'percent': response.confidence_percent,
            'level': response.confidence_level.value,
        },
        'sources': response.sources,
        'limitations': response.limitations,
    }
    
    # Add disclaimers prominently for medical content
    if response.disclaimers:
        result['important_notice'] = response.disclaimers
    
    # Add emergency resources at top if present
    if response.emergency_resources:
        result['urgent_resources'] = response.emergency_resources
    
    # Add related topics for exploration
    if response.related_topics:
        result['related_topics'] = response.related_topics
    
    # Add metadata
    result['_metadata'] = response.metadata
    
    return result


def check_safety_halt(query: str, intent: IntentClassification, confidence: float) -> tuple[bool, str]:
    """
    Determine if a query should be halted for safety reasons.
    
    Returns (should_halt, reason).
    
    Safety halt conditions:
    - Emergency/urgency detected (route to crisis resources instead)
    - Very low confidence on medical diagnostic/treatment query
    - Self-harm indicators
    - Requests for specific medical advice without proper context
    """
    query_lower = query.lower()
    
    # Immediate halt for self-harm (redirect to crisis resources)
    if any(kw in query_lower for kw in ['suicide', 'kill myself', 'end my life']):
        return True, "SELF_HARM_DETECTED"
    
    # Halt for emergency medical situations (provide crisis resources)
    if intent.urgency_detected and confidence < 0.5:
        return True, "EMERGENCY_REQUIRES_PROFESSIONAL_HELP"
    
    # Halt for diagnostic queries with very low confidence
    if intent.intent == QueryIntent.DIAGNOSTIC and confidence < 0.3:
        return True, "INSUFFICIENT_CONFIDENCE_FOR_DIAGNOSIS"
    
    # Halt for treatment queries with very low confidence
    if intent.intent == QueryIntent.TREATMENT and confidence < 0.25:
        return True, "INSUFFICIENT_CONFIDENCE_FOR_TREATMENT_ADVICE"
    
    return False, ""


# Integration helper function
def process_query_with_degradation(
    query: str,
    fragments: list[Fragment],
    base_confidence: float,
) -> dict[str, Any]:
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
    
    # Step 3: Generate graded response
    response = generate_graded_response(query, fragments, intent, base_confidence)
    
    # Step 4: Format for user
    return format_response_for_user(response)


if __name__ == '__main__':
    # Test the intent classification and graceful degradation
    print("Testing Query Intent Classification & Graceful Degradation...\n")
    
    test_queries = [
        "What is metformin used for?",
        "I have chest pain and can't breathe, what should I do?",
        "Could my headache be a sign of something serious?",
        "How do I treat diabetes naturally?",
        "Warfarin vs aspirin - which is better?",
        "I'm feeling suicidal and don't know what to do",
        "What are the side effects of lisinopril?",
        "Tell me about cancer immunotherapy",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('-'*60)
        
        intent = classify_intent(query)
        print(f"Intent: {intent.intent.value} (confidence: {intent.confidence:.2f})")
        print(f"Urgency detected: {intent.urgency_detected}")
        print(f"Entities: {intent.entities}")
        print(f"Suggested routing: {intent.suggested_routing}")
        
        # Simulate fragments (empty for testing)
        fragments = []
        base_confidence = 0.45  # Simulate medium-low confidence
        
        result = process_query_with_degradation(query, fragments, base_confidence)
        print(f"\nResponse Status: {result['status']}")
        print(f"Answer Preview: {result['answer'][:150]}...")
        
        if 'urgent_resources' in result:
            print(f"⚠️  URGENT RESOURCES: {result['urgent_resources']}")
        if 'important_notice' in result:
            print(f"📋 Disclaimers: {len(result['important_notice'])} notices")
