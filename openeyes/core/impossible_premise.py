"""
Impossible Premise Detection Module

Detects queries based on impossible, guaranteed, or scientifically invalid premises.
Triggers clarification response instead of providing misleading answers.
"""

import re
from typing import Tuple, Optional, List

# Patterns indicating impossible or guaranteed outcomes
IMPOSSIBLE_PATTERNS = [
    # Guaranteed returns/profits
    (r'guaranteed\s+(?:\d+%|\d+\s*percent)\s+(?:return|profit|gain)', 'GUARANTEED_RETURN'),
    (r'guaranteed\s+(?:to\s+)?(?:make\s+money|get\s+rich|profit)', 'GUARANTEED_PROFIT'),
    (r'100%\s+(?:guaranteed|sure\s+thing|certainty)', 'GUARANTEED_100'),
    (r'never\s+loses', 'NEVER_LOSES'),
    (r'risk[- ]?free\s+(?:investment|profit|return)', 'RISK_FREE'),
    (r'can\'t\s+lose', 'CANT_LOSE'),
    (r'always\s+(?:wins|profits|makes\s+money)', 'ALWAYS_WINS'),
    
    # Medical cures/all solutions
    (r'cure\s+(?:for\s+)?(?:all\s+)?(?:diseases?|cancers?|illnesses?)', 'UNIVERSAL_CURE'),
    (r'permanent\s+cure\s+(?:for\s+)?\w+', 'PERMANENT_CURE'),
    (r'100%\s+(?:effective|successful)\s+(?:treatment|cure)', 'PERFECT_TREATMENT'),
    (r'works\s+(?:for\s+)?everyone', 'WORKS_FOR_ALL'),
    (r'one\s+(?:size|solution|treatment)\s+fits\s+all', 'ONE_SIZE_FITS_ALL'),
    (r'miracle\s+(?:cure|treatment|solution)', 'MIRACLE_CURE'),
    
    # Time travel/impossible physics
    (r'time\s+travel', 'TIME_TRAVEL'),
    (r'faster\s+than\s+light\s+(?:travel|communication)', 'FTL_TRAVEL'),
    (r'perpetual\s+motion', 'PERPETUAL_MOTION'),
    (r'free\s+energy', 'FREE_ENERGY'),
    (r'(?:create|make)\s+something\s+from\s+nothing', 'CREATE_NOTHING'),
    
    # Mind reading/psychic abilities
    (r'read\s+minds?', 'MIND_READING'),
    (r'predict\s+(?:the\s+)?future', 'PREDICT_FUTURE'),
    (r'psychic\s+(?:powers?|abilities?)', 'PSYCHIC'),
    (r'telepathy', 'TELEPATHY'),
    
    # Absolute certainty claims
    (r'absolutely\s+certain', 'ABSOLUTE_CERTAINTY'),
    (r'without\s+a\s+doubt', 'NO_DOUBT'),
    (r'proven\s+beyond\s+(?:any\s+)?doubt', 'PROVEN_BEYOND_DOUBT'),
    (r'scientifically\s+proven\s+(?:to\s+)?(?:work|cure|fix)', 'SCIENTIFICALLY_PROVEN'),
    
    # Get rich quick
    (r'get\s+rich\s+quick', 'GET_RICH_QUICK'),
    (r'overnight\s+(?:success|millionaire|rich)', 'OVERNIGHT_SUCCESS'),
    (r'easy\s+money', 'EASY_MONEY'),
    (r'make\s+money\s+fast', 'MAKE_MONEY_FAST'),
    (r'passive\s+income\s+with\s+no\s+effort', 'PASSIVE_NO_EFFORT'),
]

# Weak patterns that suggest uncertainty but not impossible
WEAK_PREMISE_PATTERNS = [
    r'best\s+(?:way|method|solution)\s+(?:to\s+)?\w*',
    r'perfect\s+(?:way|method|solution)',
    r'flawless\s+(?:strategy|approach)',
]


def detect_impossible_premise(query: str) -> Tuple[bool, Optional[str], List[str]]:
    """
    Detect if query is based on an impossible or scientifically invalid premise.
    
    Returns:
        (is_impossible, premise_type, matched_patterns)
    """
    query_lower = query.lower()
    matched = []
    premise_types = set()
    
    for pattern, premise_type in IMPOSSIBLE_PATTERNS:
        if re.search(pattern, query_lower):
            matched.append(pattern)
            premise_types.add(premise_type)
    
    if matched:
        return True, ', '.join(sorted(premise_types)), matched
    
    return False, None, []


def get_impossible_premise_message(premise_type: str) -> str:
    """Generate appropriate response for impossible premise."""
    
    messages = {
        'GUARANTEED_RETURN': "No investment can guarantee specific returns. All investments carry risk.",
        'GUARANTEED_PROFIT': "There is no guaranteed way to make money or get rich. Be wary of scams making such claims.",
        'GUARANTEED_100': "Nothing in finance, medicine, or science has 100% certainty. Claims of 100% guarantees are red flags.",
        'NEVER_LOSES': "All strategies and investments have potential downsides. Nothing never loses.",
        'RISK_FREE': "There is no such thing as a completely risk-free investment or profit opportunity.",
        'CANT_LOSE': "Every option carries some risk. Claims that something can't lose are misleading.",
        'ALWAYS_WINS': "No strategy always wins. Markets and outcomes vary.",
        
        'UNIVERSAL_CURE': "There is no single cure for all diseases. Medical treatments are condition-specific.",
        'PERMANENT_CURE': "Medical science rarely offers permanent cures. Be skeptical of such claims.",
        'PERFECT_TREATMENT': "No treatment is 100% effective for everyone. Individual responses vary.",
        'WORKS_FOR_ALL': "What works for one person may not work for another. Individual variation is normal.",
        'ONE_SIZE_FITS_ALL': "Complex problems rarely have one-size-fits-all solutions.",
        'MIRACLE_CURE': "Miracle cures don't exist. Legitimate treatments go through rigorous testing.",
        
        'TIME_TRAVEL': "Time travel is not possible with current or foreseeable technology.",
        'FTL_TRAVEL': "Faster-than-light travel violates known physics.",
        'PERPETUAL_MOTION': "Perpetual motion machines violate thermodynamics and are impossible.",
        'FREE_ENERGY': "Free energy violates conservation of energy. No such device exists.",
        'CREATE_NOTHING': "Creating something from nothing violates fundamental physics.",
        
        'MIND_READING': "Mind reading is not scientifically possible.",
        'PREDICT_FUTURE': "Accurately predicting the future is not possible.",
        'PSYCHIC': "Psychic abilities have no scientific evidence.",
        'TELEPATHY': "Telepathy is not scientifically supported.",
        
        'ABSOLUTE_CERTAINTY': "Absolute certainty is rare in complex domains. Evidence-based confidence is more appropriate.",
        'NO_DOUBT': "In complex domains, some uncertainty almost always exists.",
        'PROVEN_BEYOND_DOUBT': "Scientific knowledge is provisional. Even well-established findings can be refined.",
        'SCIENTIFICALLY_PROVEN': "Science doesn't 'prove' in absolute terms. It provides evidence with varying confidence levels.",
        
        'GET_RICH_QUICK': "Get-rich-quick schemes are almost always scams. Real wealth building takes time.",
        'OVERNIGHT_SUCCESS': "Overnight success stories typically hide years of prior effort. Be skeptical.",
        'EASY_MONEY': "Easy money opportunities are usually too good to be true.",
        'MAKE_MONEY_FAST': "Fast money-making schemes often involve high risk or are scams.",
        'PASSIVE_NO_EFFORT': "Passive income requires initial effort or capital. 'No effort' claims are misleading.",
    }
    
    # Return message for first matching type, or generic
    for ptype, msg in messages.items():
        if ptype in premise_type:
            return msg
    
    return "This query appears to be based on an unrealistic or impossible premise."


def should_request_clarification(query: str) -> Tuple[bool, Optional[str]]:
    """
    Determine if query is too vague and needs clarification.
    
    Returns:
        (needs_clarification, reason)
    """
    query_lower = query.lower().strip()
    
    # Empty or near-empty queries
    if len(query_lower) < 5:
        return True, "Query is too short"
    
    # Pronouns without context
    vague_patterns = [
        (r'^what\s+is\s+it$', "Unclear what 'it' refers to"),
        (r'^what\s+are\s+they$', "Unclear what 'they' refers to"),
        (r'^how\s+does\s+it\s+work$', "Unclear what 'it' refers to"),
        (r'^tell\s+me\s+about\s+that$', "Unclear what 'that' refers to"),
        (r'^explain\s+this$', "Unclear what 'this' refers to"),
        (r'^the\s+rate$', "Unclear which rate"),
        (r'^the\s+price$', "Unclear which price"),
        (r'^the\s+law$', "Unclear which law"),
        (r'^the\s+treatment$', "Unclear which treatment"),
        (r'^the\s+symptoms$', "Unclear symptoms of what"),
        (r'^the\s+cause$', "Unclear cause of what"),
        (r'^the\s+effect$', "Unclear effect of what"),
        (r'^the\s+result$', "Unclear result of what"),
        (r'^the\s+process$', "Unclear which process"),
        (r'^the\s+system$', "Unclear which system"),
        (r'^the\s+method$', "Unclear which method"),
        (r'^the\s+best\s+one$', "Unclear what category"),
        (r'^which\s+one', "Unclear what options"),
        (r'^how\s+much', "Unclear what quantity"),
        (r'^how\s+many', "Unclear what count"),
        (r'^when\s+is\s+it', "Unclear what event"),
        (r'^where\s+is\s+it', "Unclear what location/object"),
        (r'^who\s+is\s+it', "Unclear who"),
    ]
    
    for pattern, reason in vague_patterns:
        if re.match(pattern, query_lower):
            return True, reason
    
    # Queries with only question words
    if re.match(r'^(what|how|when|where|why|who)\s*$', query_lower):
        return True, "Incomplete question"
    
    return False, None


def get_clarification_message(reason: str, query: str) -> str:
    """Generate clarification request message."""
    
    templates = {
        "Query is too short": "Could you please provide more details about what you're asking?",
        "Incomplete question": "Your question seems incomplete. Could you elaborate on what you'd like to know?",
        "Unclear what 'it' refers to": "Could you clarify what 'it' refers to in your question?",
        "Unclear what 'they' refers to": "Could you clarify what 'they' refers to?",
        "Unclear what 'that' refers to": "Could you specify what 'that' refers to?",
        "Unclear what 'this' refers to": "Could you specify what 'this' refers to?",
        "Unclear which rate": "Which rate are you asking about? (e.g., interest rate, inflation rate, exchange rate)",
        "Unclear which price": "Which price are you asking about?",
        "Unclear which law": "Which law? (e.g., a specific legal law, or a scientific law like Ohm's law)",
        "Unclear which treatment": "Which medical treatment or condition are you asking about?",
        "Unclear symptoms of what": "Symptoms of what condition or disease?",
        "Unclear cause of what": "Cause of what event or condition?",
        "Unclear effect of what": "Effect of what action or phenomenon?",
        "Unclear result of what": "Result of what process or event?",
        "Unclear which process": "Which process are you asking about?",
        "Unclear which system": "Which system? (e.g., economic system, computer system, biological system)",
        "Unclear which method": "Which method or approach are you asking about?",
        "Unclear what category": "What category are you comparing within?",
        "Unclear what options": "What options are you choosing between?",
        "Unclear what quantity": "What quantity are you asking about?",
        "Unclear what count": "What are you trying to count?",
        "Unclear what event": "What event are you asking about?",
        "Unclear what location/object": "What location or object are you asking about?",
        "Unclear who": "Who specifically are you asking about?",
    }
    
    base_msg = templates.get(reason, "Could you please clarify your question?")
    
    return f"{base_msg}\n\nYou asked: \"{query}\""
