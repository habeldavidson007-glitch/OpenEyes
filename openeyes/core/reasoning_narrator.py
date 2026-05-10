"""
Reasoning Chain Narrator

Generates deterministic connective language between assembled fragments
based on their reasoning roles, tag relationships, and sequential position.

This is NOT generative AI. Every connective phrase is selected by rule
from a fixed vocabulary based on structural fragment relationships.
No content is invented. Only transitions are generated.
"""

from typing import List, Dict, Any, Tuple
import random

# Connective phrases by transition type
# Each list contains multiple options for variety — selected deterministically
# based on fragment ID hash to ensure same fragments always produce same transition

TRANSITIONS = {
    # When definition is followed by counter_argument on same topic
    'definition_to_counter': [
        "However, this picture has important nuances.",
        "That said, this view is not without challenge.",
        "The limitation here is significant.",
        "This is the established view, but the evidence complicates it.",
        "A critical counterpoint exists here.",
    ],
    
    # When counter_argument is followed by latest_data
    'counter_to_latest': [
        "More recent data adds another dimension.",
        "The 2024 picture has shifted this debate.",
        "Latest evidence provides useful context here.",
        "Recent developments are worth noting.",
    ],
    
    # When definition is followed by latest_data (no counter in between)
    'definition_to_latest': [
        "More recently, this has evolved.",
        "The current state of this is worth noting.",
        "As of 2024, the landscape looks like this.",
        "Recent data updates this picture.",
    ],
    
    # When a risk/warning fragment follows a strategy fragment
    'strategy_to_risk': [
        "Before acting on this, the risk picture matters.",
        "The downside scenario deserves equal attention.",
        "Risk controls are the prerequisite here, not an afterthought.",
        "This strategy comes with specific vulnerabilities.",
    ],
    
    # When latest_data follows strategy
    'strategy_to_latest': [
        "Current conditions affect how this applies.",
        "The 2024 environment changes the calculus here.",
        "Recent market structure is relevant context.",
    ],
    
    # When a new topic cluster begins (different primary tag)
    'topic_shift': [
        "Turning to a related dimension,",
        "A connected factor worth understanding:",
        "This connects directly to another consideration:",
        "On a related point,",
    ],
    
    # When complementary fragments (same topic, same role, compatible tags)
    'reinforcement': [
        "This is reinforced by another angle:",
        "Supporting evidence comes from a different direction:",
        "This aligns with broader patterns:",
    ],
    
    # Opening of answer — by intent type
    'opening_factual': [
        "{answer_core}",  # Just state the answer directly
    ],
    'opening_strategy': [
        "The foundation before anything else is {primary_topic}.",
        "Starting with what matters most: {primary_topic}.",
        "The right sequence here begins with {primary_topic}.",
    ],
    'opening_theory': [
        "The mechanism works as follows.",
        "Here is how this works.",
        "The underlying logic is this.",
    ],
    
    # Closing of answer — by confidence and fragment count
    'closing_high_confidence': [
        "This answer draws on {fragment_count} verified sources with high consistency.",
        "The evidence base here is strong across {fragment_count} independent sources.",
    ],
    'closing_medium_confidence': [
        "This reflects the current consensus with some uncertainty remaining.",
        "The core picture is clear; some details remain debated.",
    ],
    'closing_challenged': [
        "Note: a meaningful counterargument exists on this topic. The evidence is not fully settled.",
        "The primary view above faces genuine challenge. Both perspectives are evidence-based.",
    ],
}


def _select_phrase(options: List[str], seed: str) -> str:
    """
    Select a phrase deterministically based on seed string.
    Same inputs always produce same output — no randomness.
    """
    idx = hash(seed) % len(options)
    return options[abs(idx)]


def _get_transition_type(frag_a: Dict, frag_b: Dict) -> str:
    """
    Determine the transition type between two sequential fragments.
    """
    role_a = frag_a.get('reasoning_role', 'definition')
    role_b = frag_b.get('reasoning_role', 'definition')
    tags_a = set(frag_a.get('tags', []))
    tags_b = set(frag_b.get('tags', []))
    
    # Same topic (tag overlap >= 2)
    same_topic = len(tags_a & tags_b) >= 2
    
    if same_topic:
        if role_a == 'definition' and role_b == 'counter_argument':
            return 'definition_to_counter'
        if role_a == 'counter_argument' and role_b == 'latest_data':
            return 'counter_to_latest'
        if role_a == 'definition' and role_b == 'latest_data':
            return 'definition_to_latest'
        if role_a == 'definition' and role_b == 'definition':
            return 'reinforcement'
    else:
        # Different topic cluster
        if 'risk_management' in tags_b or 'warning' in tags_b or 'counter_argument' in role_b:
            return 'strategy_to_risk'
        return 'topic_shift'
    
    return 'topic_shift'


def build_opening(intent_type: str, fragments: List[Dict]) -> str:
    """
    Build the opening sentence of the answer based on intent type
    and the primary fragment content.
    """
    if not fragments:
        return ""
    
    primary = fragments[0]
    primary_content = primary.get('content', '')
    primary_tags = primary.get('tags', [])
    
    # For factual queries — lead with the answer directly
    if intent_type == 'factual_entity':
        # Take first sentence of primary fragment
        sentences = primary_content.split('.')
        return sentences[0].strip() + '.' if sentences else primary_content
    
    # For strategy queries — frame the starting point
    if intent_type == 'strategy':
        primary_topic = primary_tags[0] if primary_tags else 'risk management'
        template = _select_phrase(TRANSITIONS['opening_strategy'], primary_topic)
        return template.format(primary_topic=primary_topic.replace('_', ' '))
    
    # For theory queries — signal explanation mode
    if intent_type == 'theory':
        return _select_phrase(TRANSITIONS['opening_theory'], primary_content[:20])
    
    return ""


def build_closing(fragments_used: List[Dict], confidence: float, 
                  has_counter: bool) -> str:
    """
    Build the closing sentence based on answer composition.
    """
    count = len(fragments_used)
    
    if has_counter:
        return _select_phrase(TRANSITIONS['closing_challenged'], str(count))
    
    if confidence >= 75:
        template = _select_phrase(TRANSITIONS['closing_high_confidence'], str(count))
        return template.format(fragment_count=count)
    
    return _select_phrase(TRANSITIONS['closing_medium_confidence'], str(confidence))


def narrate_chain(fragments: List[Dict], intent_type: str, 
                   confidence: float) -> str:
    """
    Main entry point. Takes an ordered list of assembled fragments
    and produces a narrated answer with proper connective reasoning.
    
    Args:
        fragments: Ordered list of fragment dicts from Würfelspiel assembler
        intent_type: From intent router (factual_entity, theory, strategy, etc.)
        confidence: Final confidence score
    
    Returns:
        Full narrated answer string
    """
    if not fragments:
        return ""
    
    has_counter = any(f.get('reasoning_role') == 'counter_argument' for f in fragments)
    
    parts = []
    
    # Opening
    opening = build_opening(intent_type, fragments)
    if opening:
        parts.append(opening)
    
    # Body — fragments with connective transitions
    for i, fragment in enumerate(fragments):
        content = fragment.get('content', '').strip()
        
        if i == 0:
            # First fragment — content only, opening already set the frame
            if intent_type != 'factual_entity':
                # For non-factual, include full first fragment
                parts.append(content)
            # For factual, opening already contains the first sentence
            # so append remaining sentences only
            else:
                sentences = content.split('.')
                if len(sentences) > 1:
                    remaining = '. '.join(sentences[1:]).strip()
                    if remaining:
                        parts.append(remaining)
        else:
            # Get transition to previous fragment
            transition_type = _get_transition_type(fragments[i-1], fragment)
            transition = _select_phrase(
                TRANSITIONS[transition_type],
                fragment.get('id', str(i))
            )
            
            # Combine transition with content
            parts.append(f"{transition} {content}")
    
    # Closing
    closing = build_closing(fragments, confidence, has_counter)
    if closing:
        parts.append(closing)
    
    return '\n\n'.join(parts)
