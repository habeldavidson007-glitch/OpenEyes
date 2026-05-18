"""
Emergency Detection Module - P0 Critical Safety Fix

Detects medical emergencies and safety-critical situations BEFORE answer generation.
Triggers immediate HALT with emergency resources.
"""

import re
from typing import Tuple, List, Dict

# Emergency keyword patterns by category
# Note: Patterns now include context markers to distinguish informational vs personal distress
EMERGENCY_PATTERNS = {
    'chest_pain': [
        r'(?:i have|i am having|my chest)\s+(?:chest\s+)?pain', r'chest\s+hurt', r'chest\s+pressure', r'chest\s+tight',
        r'angina', r'(?:i think i am having|i might be having)\s+heart\s+attack', r'myocardial\s+infarction'
    ],
    'breathing_issues': [
        r'(?:i can\'t|i cannot|i am)\s+(?:trouble\s+)?breath', r'difficulty\s+breath', r'can\'t\s+breathe',
        r'shortness\s+of\s+breath', r'gasping', r'choking', r'not\s+getting\s+air',
        r'respiratory\s+distress'
    ],
    'stroke_symptoms': [
        r'face\s+droop', r'arm\s+weak', r'speech\s+difficult', r'sudden\s+numb',
        r'sudden\s+weak', r'slurred\s+speech', r'one\s+sided\s+weakness',
        r'FAST\s+symptoms', r'stroke\s+symptom'
    ],
    'severe_bleeding': [
        r'severe\s+bleed', r'uncontrollable\s+bleed', r'gushing\s+blood',
        r'arterial\s+bleed', r'severely\s+cut', r'deep\s+wound\s+bleeding'
    ],
    'overdose': [
        r'(?:i|he|she)\s+overdose', r'too\s+many\s+pills', r'overdosed', r'drug\s+overdose',
        r'pill\s+overdose', r'poisoning', r'ingested\s+toxic', r'take\s+all\s+my\s+pills'
    ],
    'suicidal': [
        # Personal distress markers (first-person, present tense)
        r'i\s+want\s+to\s+(?:kill\s+)?myself', r'i\s+want\s+to\s+end\s+my\s+life', r'i\s+want\s+to\s+die',
        r'i\s+am\s+suicidal', r'i\s+feel\s+suicidal', r'i\s+think\s+about\s+killing\s+myself',
        r'i\s+have\s+a\s+plan\s+to\s+(?:kill\s+)?myself', r'i\s+am\s+going\s+to\s+(?:kill\s+)?myself',
        r'ending\s+it\s+all', r'end\s+it\s+all', r'taking\s+my\s+life',
        r'i\s+want\s+to\s+harm\s+myself', r'i\s+want\s+to\s+hurt\s+myself',
        r'i\s+am\s+cutting\s+myself', r'i\s+have\s+been\s+cutting\s+myself',
        r'better\s+off\s+without\s+me', r'i\s+am\s+a\s+burden', r'i\s+feel\s+like\s+a\s+burden',
        r'nothing\s+matters\s+anymore', r'i\s+give\s+up', r'i\s+can\'t\s+take\s+it\s+anymore',
        r'i\s+want\s+the\s+pain\s+to\s+end', r'how\s+do\s+i\s+end\s+the\s+pain',
        r'i\s+should\s+just\s+end\s+it', r'i\s+might\s+as\s+well\s+end\s+it',
        # Financial distress with self-harm
        r'escape\s+this\s+financial\s+ruin', r'can\'t\s+fix\s+this\s+debt.*end\s+it',
        r'lost\s+everything.*end\s+it', r'bankruptcy.*too\s+much.*end\s+it',
        # Harm to others (personal intent)
        r'i\s+want\s+to\s+hurt\s+others', r'i\s+want\s+to\s+harm\s+my\s+family',
        r'i\s+am\s+thinking\s+of\s+attacking\s+my\s+family', r'i\s+might\s+hurt\s+my\s+family'
    ],
    'anaphylaxis': [
        r'anaphylaxis', r'severe\s+allergic\s+reaction', r'throat\s+swelling',
        r'can\'t\s+breathe\s+after\s+eating', r'allergic\s+shock'
    ],
    'seizure': [
        r'seizure', r'convulsion', r'fitting', r'epileptic\s+attack',
        r'losing\s+consciousness\s+repeated'
    ],
    'unconscious': [
        r'unconscious', r'passed\s+out', r'won\'t\s+wake\s+up', r'lost\s+consciousness',
        r'fainted\s+and\s+won\'t\s+wake'
    ]
}

# Informational query patterns that should NOT trigger emergency halt
INFORMATIONAL_PATTERNS = [
    r'what\s+is\s+(?:a|an)?\s*(?:heart\s+attack|chest\s+pain|stroke|depression|anxiety|diabetes|ptsd)',
    r'symptoms\s+of\s+\w+',
    r'treatment\s+(?:options\s+)?for\s+\w+',
    r'how\s+does\s+\w+\s+work',
    r'causes?\s+of\s+\w+',
    r'signs\s+of\s+\w+',
    r'side\s+effects\s+of\s+\w+',
    r'what\s+are\s+(?:the\s+)?symptoms',
    r'how\s+to\s+treat\s+\w+',
    r'(?:definition|meaning|explain)\s+(?:of|:)\s*\w+',
    r'\w+\s+(?:resources|statistics|information|facts|overview)',
    r'learn\s+about\s+\w+',
    r'tell\s+me\s+about\s+\w+',
    r'(?:describe|list|outline)\s+\w+'
]

EMERGENCY_RESOURCES = {
    'general': {
        'primary': 'Call 911 immediately',
        'secondary': 'Go to nearest emergency room',
        'hotline': None
    },
    'suicidal': {
        'primary': 'Call 988 Suicide & Crisis Lifeline (24/7)',
        'secondary': 'Call 911 or go to nearest ER',
        'hotline': '988'
    },
    'overdose': {
        'primary': 'Call 911 immediately',
        'secondary': 'Poison Control: 1-800-222-1222',
        'hotline': '1-800-222-1222'
    }
}


def detect_emergency(query: str) -> Tuple[bool, str | None, Dict]:
    """
    Detect if query indicates a medical/safety emergency.
    
    Returns:
        (is_emergency, emergency_type, resources_dict)
    """
    query_lower = query.lower()
    
    # First check if this is an informational query (should NOT halt)
    for pattern in INFORMATIONAL_PATTERNS:
        if re.search(pattern, query_lower):
            return False, None, {}
    
    # Then check for emergency patterns
    for emergency_type, patterns in EMERGENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, query_lower):
                # Determine appropriate resources
                if emergency_type == 'suicidal':
                    resources = EMERGENCY_RESOURCES['suicidal']
                elif emergency_type == 'overdose':
                    resources = EMERGENCY_RESOURCES['overdose']
                else:
                    resources = EMERGENCY_RESOURCES['general']
                
                return True, emergency_type, resources
    
    return False, None, {}


def is_safety_critical_intent(intent_class: str) -> bool:
    """Check if intent classification indicates safety-critical query."""
    critical_intents = [
        'emergency', 'urgent_medical', 'crisis', 'self_harm',
        'acute_symptom', 'trauma'
    ]
    return intent_class.lower() in critical_intents


def get_emergency_message(emergency_type: str, resources: Dict) -> str:
    """Generate appropriate emergency response message."""
    messages = {
        'chest_pain': "CHEST PAIN DETECTED - This could be a heart attack.",
        'breathing_issues': "BREATHING DIFFICULTY DETECTED - This is a medical emergency.",
        'stroke_symptoms': "STROKE SYMPTOMS DETECTED - Time is critical.",
        'severe_bleeding': "SEVERE BLEEDING DETECTED - Immediate medical attention required.",
        'overdose': "OVERDOSE DETECTED - This is life-threatening.",
        'suicidal': "SUICIDAL THOUGHTS DETECTED - You are not alone, help is available.",
        'anaphylaxis': "SEVERE ALLERGIC REACTION DETECTED - This is life-threatening.",
        'seizure': "SEIZURE DETECTED - Medical emergency.",
        'unconscious': "UNCONSCIOUS PERSON DETECTED - This is a medical emergency."
    }
    
    base_msg = messages.get(emergency_type, "MEDICAL EMERGENCY DETECTED")
    
    resource_msg = []
    if resources.get('primary'):
        resource_msg.append(resources['primary'])
    if resources.get('secondary'):
        resource_msg.append(resources['secondary'])
    
    return f"{base_msg}\n\n{' '.join(resource_msg)}\n\nDo not wait. Seek immediate medical attention."
