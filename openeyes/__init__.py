"""
OpenEyes — Query Engine for High-Stakes Decisions

"The first AI that proves its work before speaking."

OpenEyes answers user questions by:
1. Decomposing queries into atomic sub-questions via Swarm
2. Stress-testing every candidate answer path via Monte Carlo simulation
3. Selecting and assembling only paths that survive simulation
4. Vetoing any assembly that violates domain philosophy rules
5. Returning traceable answers — every fragment carries its survival score, source, and rule set

There is no neural core. No token prediction. No hallucination — the system halts rather than inventing.
"""

__version__ = "0.1"
__status__ = "Active Development"
__engine_language__ = "Python 3.12"
__architecture__ = "Neuro-Symbolic Logic Engine (Harness-Only, No LLM Core)"


from openeyes.query_interface import OpenEyes

__all__ = ["OpenEyes"]