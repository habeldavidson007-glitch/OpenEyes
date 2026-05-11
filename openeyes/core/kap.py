"""
Knowledge Acquisition Plan (KAP) — Query-Driven Retrieval Strategy

Before the Swarm retrieves anything, the KAP system reasons about
what the query actually needs and builds a structured retrieval plan.

Each plan has layers. Each layer has:
- A purpose (what this layer contributes to the answer)
- Required fragment roles (definition, counter_argument, latest_data)
- Target tags (what to search for in this layer)
- Mandatory flag (if True and layer returns nothing, system halts)
- Max fragments (how many from this layer go into the answer)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from openeyes.core.intent_router import route_intent, IntentResult


@dataclass
class KAPLayer:
    """A single retrieval layer within a Knowledge Acquisition Plan."""
    name: str
    purpose: str
    required_roles: List[str]
    target_tags: List[str]
    mandatory: bool
    max_fragments: int
    priority: int  # Lower = higher priority, retrieved first


@dataclass
class KnowledgeAcquisitionPlan:
    """Complete retrieval plan for a query."""
    query: str
    domain: str
    intent: IntentResult
    layers: List[KAPLayer]
    safety_required: bool  # If True, safety layer must pass or answer halts
    
    def mandatory_layers(self) -> List[KAPLayer]:
        return [l for l in self.layers if l.mandatory]
    
    def optional_layers(self) -> List[KAPLayer]:
        return [l for l in self.layers if not l.mandatory]
    
    def sorted_layers(self) -> List[KAPLayer]:
        return sorted(self.layers, key=lambda l: l.priority)


# KAP Templates by intent type and domain
# These define what every query of a given type needs to be answered properly

KAP_TEMPLATES = {

    # FACTUAL queries — what is X, define X, explain X
    'factual_entity': {
        'default': [
            KAPLayer(
                name='core_definition',
                purpose='Establish what the subject actually is',
                required_roles=['definition'],
                target_tags=[],  # filled from query keywords
                mandatory=True,
                max_fragments=2,
                priority=0
            ),
            KAPLayer(
                name='supporting_context',
                purpose='Provide relevant context and mechanism',
                required_roles=['definition', 'latest_data'],
                target_tags=[],
                mandatory=False,
                max_fragments=2,
                priority=1
            ),
            KAPLayer(
                name='current_state',
                purpose='How this looks right now',
                required_roles=['latest_data'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=2
            ),
            KAPLayer(
                name='known_limitations',
                purpose='What complicates or challenges this',
                required_roles=['counter_argument'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=3
            ),
        ]
    },

    # THEORY queries — how does X work, why does X happen
    'theory': {
        'default': [
            KAPLayer(
                name='mechanism',
                purpose='The causal mechanism or process',
                required_roles=['definition'],
                target_tags=[],
                mandatory=True,
                max_fragments=2,
                priority=0
            ),
            KAPLayer(
                name='evidence_base',
                purpose='What evidence supports the mechanism',
                required_roles=['definition', 'latest_data'],
                target_tags=[],
                mandatory=False,
                max_fragments=2,
                priority=1
            ),
            KAPLayer(
                name='counter_mechanism',
                purpose='Cases where the mechanism breaks down',
                required_roles=['counter_argument'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=2
            ),
            KAPLayer(
                name='recent_developments',
                purpose='How understanding has evolved recently',
                required_roles=['latest_data'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=3
            ),
        ]
    },

    # STRATEGY queries — best approach, roadmap, how should I, plan for
    'strategy': {
        'economy': [
            KAPLayer(
                name='foundational_knowledge',
                purpose='Core concepts the strategy depends on understanding',
                required_roles=['definition'],
                target_tags=['fundamental_analysis', 'risk_management', 'diversification'],
                mandatory=True,
                max_fragments=3,
                priority=0
            ),
            KAPLayer(
                name='current_market_context',
                purpose='Current conditions that affect which strategy applies',
                required_roles=['latest_data'],
                target_tags=['macro', 'monetary_policy', 'market_structure'],
                mandatory=False,
                max_fragments=2,
                priority=1
            ),
            KAPLayer(
                name='methodology',
                purpose='The actual strategic process or framework',
                required_roles=['definition', 'latest_data'],
                target_tags=['strategy', 'portfolio_construction', 'risk_management'],
                mandatory=True,
                max_fragments=3,
                priority=2
            ),
            KAPLayer(
                name='risk_warnings',
                purpose='What this strategy cannot protect against',
                required_roles=['counter_argument'],
                target_tags=['risk_management', 'volatility', 'drawdown'],
                mandatory=True,  # MANDATORY — strategy without risk warnings is incomplete
                max_fragments=2,
                priority=3
            ),
            KAPLayer(
                name='honesty_gaps',
                purpose='What OpenEyes cannot know without user context',
                required_roles=['counter_argument'],
                target_tags=['risk_management', 'diversification'],
                mandatory=False,
                max_fragments=1,
                priority=4
            ),
        ],
        'healthcare': [
            KAPLayer(
                name='clinical_foundation',
                purpose='Evidence-based clinical basis',
                required_roles=['definition'],
                target_tags=['clinical_guideline', 'evidence_based'],
                mandatory=True,
                max_fragments=2,
                priority=0
            ),
            KAPLayer(
                name='treatment_options',
                purpose='Available approaches with evidence quality',
                required_roles=['definition', 'latest_data'],
                target_tags=[],
                mandatory=True,
                max_fragments=3,
                priority=1
            ),
            KAPLayer(
                name='contraindications',
                purpose='Who this does not apply to',
                required_roles=['counter_argument'],
                target_tags=['contraindication', 'risk'],
                mandatory=True,  # MANDATORY for healthcare
                max_fragments=2,
                priority=2
            ),
            KAPLayer(
                name='recent_evidence',
                purpose='Latest clinical evidence or guideline updates',
                required_roles=['latest_data'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=3
            ),
        ],
        'default': [
            KAPLayer(
                name='foundation',
                purpose='Core knowledge required',
                required_roles=['definition'],
                target_tags=[],
                mandatory=True,
                max_fragments=3,
                priority=0
            ),
            KAPLayer(
                name='context',
                purpose='Current relevant context',
                required_roles=['latest_data'],
                target_tags=[],
                mandatory=False,
                max_fragments=2,
                priority=1
            ),
            KAPLayer(
                name='risks',
                purpose='Risks and limitations',
                required_roles=['counter_argument'],
                target_tags=[],
                mandatory=True,
                max_fragments=2,
                priority=2
            ),
        ]
    },

    # CURRENT_EVENTS queries — what is happening now, latest, current
    'current_events': {
        'default': [
            KAPLayer(
                name='background',
                purpose='Context needed to understand the current event',
                required_roles=['definition'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=0
            ),
            KAPLayer(
                name='current_state',
                purpose='What is actually happening now',
                required_roles=['latest_data'],
                target_tags=[],
                mandatory=True,
                max_fragments=3,
                priority=1
            ),
            KAPLayer(
                name='competing_interpretations',
                purpose='How different analysts read the current situation',
                required_roles=['counter_argument'],
                target_tags=[],
                mandatory=False,
                max_fragments=1,
                priority=2
            ),
        ]
    },
}


def build_kap(query: str, domain: str, keywords: List[str]) -> KnowledgeAcquisitionPlan:
    """
    Build a Knowledge Acquisition Plan for this query.
    
    Args:
        query: The original user query
        domain: Detected domain (economy, healthcare, etc.)
        keywords: Keywords extracted from the query
        
    Returns:
        A complete KAP with layers populated with keyword-based tag targets
    """
    import copy
    
    intent = route_intent(query, domain)
    
    # Get the template for this intent type and domain
    template_group = KAP_TEMPLATES.get(intent.intent_type, KAP_TEMPLATES['factual_entity'])
    template = template_group.get(domain, template_group.get('default', []))
    
    # Deep copy template layers and populate target_tags from keywords
    layers = []
    for layer_template in template:
        layer = copy.deepcopy(layer_template)
        # If layer has no pre-defined target_tags, use query keywords
        if not layer.target_tags:
            layer.target_tags = keywords[:5]  # Top 5 keywords as tag targets
        layers.append(layer)
    
    # Strategy queries always require safety layer
    safety_required = intent.intent_type == 'strategy'
    
    return KnowledgeAcquisitionPlan(
        query=query,
        domain=domain,
        intent=intent,
        layers=layers,
        safety_required=safety_required
    )


def kap_to_trace(kap: KnowledgeAcquisitionPlan) -> str:
    """
    Generate a human-readable KAP trace for Obsidian logging.
    """
    lines = [
        f"QUERY: {kap.query}",
        f"DOMAIN: {kap.domain}",
        f"INTENT: {kap.intent.intent_type} ({kap.intent.search_mode})",
        f"SAFETY REQUIRED: {kap.safety_required}",
        "",
        "KNOWLEDGE ACQUISITION PLAN:",
    ]
    for layer in kap.sorted_layers():
        mandatory_flag = "MANDATORY" if layer.mandatory else "optional"
        lines.append(
            f"  Layer {layer.priority} [{mandatory_flag}] {layer.name}: "
            f"{layer.purpose} "
            f"(roles: {layer.required_roles}, max: {layer.max_fragments})"
        )
    return "\n".join(lines)
