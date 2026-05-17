"""
Emergency Detection Module - P0 Critical Safety Fix

Detects medical emergencies and safety-critical situations BEFORE answer generation.
Triggers immediate HALT with emergency resources.
"""

import re
from typing import Tuple, List, Dict

# Emergency keyword patterns by category
EMERGENCY_PATTERNS = {
    'chest_pain': [
        r'chest\s+pain', r'chest\s+hurt', r'chest\s+pressure', r'chest\s+tight',
        r'angina', r'heart\s+attack', r'myocardial\s+infarction'
    ],
    'breathing_issues': [
        r'trouble\s+breath', r'difficulty\s+breath', r'can\'t\s+breathe',
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
        r'overdose', r'too\s+many\s+pills', r'overdosed', r'drug\s+overdose',
        r'pill\s+overdose', r'poisoning', r'ingested\s+toxic', r'take\s+all\s+my\s+pills'
    ],
    'suicidal': [
        r'suicide', r'kill\s+myself', r'end\s+my\s+life', r'self[- ]harm',
        r'hurt\s+myself', r'suicidal', r'want\s+to\s+die', r'no\s+reason\s+to\s+live',
        r'should\s+i\s+just\s+end\s+it', r'want\s+to\s+die', r'made\s+me\s+want\s+to\s+die',
        r'thinking\s+of\s+hurting\s+myself', r'how\s+do\s+i\s+end\s+the\s+pain',
        r'drive\s+.*\s+off\s+a\s+bridge', r'stop\s+breathing', r'peaceful\s+way\s+to\s+exit',
        r'escape\s+this\s+financial\s+ruin', r'can\'t\s+fix\s+this\s+debt',
        r'lost\s+everything.*end\s+it', r'bankruptcy.*too\s+much',
        # NEW: Expanded crisis coverage for self-harm and suicidal ideation
        r'ending\s+it\s+all', r'end\s+it\s+all', r'taking\s+my\s+life',
        r'harm\s+myself', r'hurting\s+myself', r'self[- ]injury', r'injure\s+myself',
        r'better\s+off\s+without\s+me', r'everyone.*better\s+off', r'burden\s+to\s+everyone',
        r'i\s+am\s+a\s+burden', r'nothing\s+matters', r'hurt\s+my\s+family',
        r'harming\s+my\s+family', r'attack\s+my\s+family', r'hurt\s+others',
        r'cutting\s+myself', r'cut\s+myself'
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
    ],
    'mental_health_crisis': [
        r'should\s+i\s+just\s+end\s+it', r'want\s+to\s+die', r'ending\s+pain',
        r'can\'t\s+take\s+it\s+anymore', r'no\s+hope', r'give\s+up\s+life',
        r'peaceful\s+way\s+to\s+exit', r'how\s+do\s+i\s+end\s+the\s+pain'
    ]
}

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
