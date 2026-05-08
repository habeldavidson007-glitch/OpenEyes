"""
SEO Trend Harvester for OpenEyes Swarm Training

This tool simulates finding high-volume, complex search queries to stress-test
the Swarm's decomposition and retrieval capabilities.

In production, this would connect to:
- Google Trends API
- SEMRush/Ahrefs APIs  
- AnswerThePublic
- Reddit/Twitter trending topics

For now, it uses a curated list of historically complex, high-stakes queries
that represent the kind of questions OpenEyes should handle (or HALT on).
"""

import json
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime


@dataclass
class TrendingQuery:
    query: str
    category: str
    complexity_score: int  # 1-10, based on ambiguity + stakes
    estimated_monthly_searches: int
    why_complex: str
    expected_subquestions: List[str]


# Curated list of complex, high-stakes queries based on historical search trends
# These represent questions where "mostly right" is worse than silence
TRENDING_QUERIES = [
    TrendingQuery(
        query="What are the early symptoms of pancreatic cancer?",
        category="medical",
        complexity_score=9,
        estimated_monthly_searches=246000,
        why_complex="High stakes (life/death), vague symptoms overlap with benign conditions, requires differential diagnosis knowledge",
        expected_subquestions=[
            "What are specific early symptoms of pancreatic cancer?",
            "How do pancreatic cancer symptoms differ from benign GI conditions?",
            "What risk factors increase pancreatic cancer probability?",
            "When should someone with these symptoms see a doctor?"
        ]
    ),
    TrendingQuery(
        query="Can I take ibuprofen with blood thinners?",
        category="medical",
        complexity_score=8,
        estimated_monthly_searches=165000,
        why_complex="Drug interaction with potentially fatal consequences, depends on specific blood thinner, dosage, patient history",
        expected_subquestions=[
            "What blood thinners interact with ibuprofen?",
            "What is the mechanism of interaction between NSAIDs and anticoagulants?",
            "What are safer alternatives for pain relief on blood thinners?",
            "What symptoms indicate dangerous bleeding?"
        ]
    ),
    TrendingQuery(
        query="Is it legal to record a conversation in California without consent?",
        category="legal",
        complexity_score=7,
        estimated_monthly_searches=89000,
        why_complex="Two-party consent state with exceptions, varies by context (phone/in-person), criminal vs civil implications",
        expected_subquestions=[
            "What is California's two-party consent law?",
            "Are there exceptions to two-party consent in California?",
            "What are the penalties for illegal recording in CA?",
            "Does the law apply to video recordings with audio?"
        ]
    ),
    TrendingQuery(
        query="Should I get a Roth IRA or Traditional IRA?",
        category="financial",
        complexity_score=8,
        estimated_monthly_searches=201000,
        why_complex="Depends on current vs future tax bracket, income limits, age, retirement timeline, contribution limits",
        expected_subquestions=[
            "What are the tax differences between Roth and Traditional IRA?",
            "What are the income limits for Roth IRA contributions?",
            "At what tax bracket does Roth become preferable?",
            "Can you contribute to both Roth and Traditional IRA?"
        ]
    ),
    TrendingQuery(
        query="What happens if you drink methanol?",
        category="medical",
        complexity_score=9,
        estimated_monthly_searches=134000,
        why_complex="Life-threatening emergency, time-sensitive treatment, confusion with ethanol, requires immediate action guidance",
        expected_subquestions=[
            "What are the symptoms of methanol poisoning?",
            "What is the lethal dose of methanol?",
            "What is the antidote for methanol poisoning?",
            "What immediate actions should be taken after methanol ingestion?"
        ]
    ),
    TrendingQuery(
        query="Can ADHD medication cause heart problems?",
        category="medical",
        complexity_score=8,
        estimated_monthly_searches=112000,
        why_complex="Stimulant cardiovascular effects, pre-existing conditions matter, risk/benefit analysis required",
        expected_subquestions=[
            "How do stimulant ADHD medications affect heart rate and blood pressure?",
            "What pre-existing heart conditions contraindicate ADHD stimulants?",
            "What monitoring is recommended for patients on ADHD medication?",
            "Are non-stimulant ADHD medications safer for cardiac patients?"
        ]
    ),
    TrendingQuery(
        query="Is intermittent fasting safe for diabetics?",
        category="medical",
        complexity_score=9,
        estimated_monthly_searches=178000,
        why_complex="Type 1 vs Type 2 distinction critical, medication timing, hypoglycemia risk, individual variation",
        expected_subquestions=[
            "How does intermittent fasting affect blood glucose levels?",
            "What are the risks of fasting for Type 1 diabetics?",
            "What are the risks of fasting for Type 2 diabetics on medication?",
            "What monitoring is required if a diabetic attempts intermittent fasting?"
        ]
    ),
    TrendingQuery(
        query="What is the statute of limitations for medical malpractice in New York?",
        category="legal",
        complexity_score=7,
        estimated_monthly_searches=67000,
        why_complex="Varies by injury type, discovery rule exceptions, minor vs adult, foreign object cases",
        expected_subquestions=[
            "What is the standard statute of limitations for medical malpractice in NY?",
            "When does the clock start for statute of limitations (discovery rule)?",
            "Are there different rules for minors in NY medical malpractice?",
            "What exceptions extend the statute of limitations in NY?"
        ]
    ),
    TrendingQuery(
        query="Can you sue for emotional distress without physical injury?",
        category="legal",
        complexity_score=8,
        estimated_monthly_searches=94000,
        why_complex="Jurisdiction-dependent, intentional vs negligent infliction, evidentiary standards vary",
        expected_subquestions=[
            "What is the difference between IIED and NIED?",
            "Which states allow emotional distress claims without physical injury?",
            "What evidence is required to prove emotional distress?",
            "What are the damage caps for emotional distress claims?"
        ]
    ),
    TrendingQuery(
        query="What antibiotics treat UTI in pregnancy?",
        category="medical",
        complexity_score=9,
        estimated_monthly_searches=89000,
        why_complex="Fetal safety paramount, trimester-specific considerations, resistance patterns, asymptomatic bacteriuria treatment",
        expected_subquestions=[
            "Which antibiotics are safe during each trimester of pregnancy?",
            "Which antibiotics are contraindicated in pregnancy?",
            "Should asymptomatic bacteriuria be treated in pregnancy?",
            "What are the risks of untreated UTI during pregnancy?"
        ]
    )
]


class SEOTrendHarvester:
    """
    Simulates SEO trend discovery to feed complex queries to the Swarm.
    
    In production, this would:
    1. Query Google Trends API for rising searches in high-stakes domains
    2. Filter for queries with question words (what, can, should, how)
    3. Score complexity based on:
       - Search volume volatility (rising fast = emerging uncertainty)
       - SERP diversity (many different answer types = no consensus)
       - Featured snippet absence (Google can't confidently answer = hard question)
    4. Return top N complex queries for Swarm training
    """
    
    def __init__(self):
        self.queries = TRENDING_QUERIES
    
    def get_trending_queries(self, category: str = None, min_complexity: int = 7, limit: int = 5) -> List[TrendingQuery]:
        """
        Get trending complex queries, optionally filtered by category.
        
        Args:
            category: Filter by domain (medical, legal, financial, etc.)
            min_complexity: Minimum complexity score (1-10)
            limit: Maximum number of queries to return
            
        Returns:
            List of TrendingQuery objects sorted by complexity
        """
        filtered = self.queries
        
        if category:
            filtered = [q for q in filtered if q.category == category]
        
        filtered = [q for q in filtered if q.complexity_score >= min_complexity]
        
        # Sort by complexity (descending), then by search volume
        sorted_queries = sorted(filtered, key=lambda x: (-x.complexity_score, -x.estimated_monthly_searches))
        
        return sorted_queries[:limit]
    
    def generate_training_scenario(self, query: TrendingQuery) -> dict:
        """
        Convert a trending query into a Night Mode training scenario.
        
        This creates the JSON structure that Scenario Engine expects,
        with the expected subquestions as validation criteria.
        """
        return {
            "id": f"seo_trend_{query.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "category": query.category,
            "domain": query.category,
            "context": f"High-volume search query ({query.estimated_monthly_searches:,} monthly searches)",
            "query_pattern": query.query,
            "expected_fragments": [q.replace(" ", "_").lower() for q in query.expected_subquestions[:3]],
            "pressure_profile": "credibility_heavy",
            "philosophy_checks": ["evidence_based", "cite_source", "no_hallucination"],
            "complexity_tier": query.complexity_score,
            "success_criteria": {
                "must_decompose_into": query.expected_subquestions,
                "source_credibility_threshold": 0.85 if query.category == "medical" else 0.75,
                "requires_source_citation": True,
                "halt_if_confidence_below": 70
            },
            "metadata": {
                "why_complex": query.why_complex,
                "search_volume": query.estimated_monthly_searches,
                "harvested_at": datetime.now().isoformat(),
                "source": "seo_trend_harvester"
            }
        }
    
    def export_for_swarm_training(self, output_path: str = "openeyes/tools/trending_queries.json"):
        """
        Export trending queries as JSON for Swarm agent training.
        """
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "total_queries": len(self.queries),
            "queries": [
                {
                    "query": q.query,
                    "category": q.category,
                    "complexity_score": q.complexity_score,
                    "estimated_monthly_searches": q.estimated_monthly_searches,
                    "why_complex": q.why_complex,
                    "expected_subquestions": q.expected_subquestions
                }
                for q in self.queries
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Exported {len(self.queries)} trending queries to {output_path}")
        return output_path


def main():
    """
    Demo: Find trending complex queries and generate training scenarios.
    """
    harvester = SEOTrendHarvester()
    
    print("=" * 80)
    print("OpenEyes SEO Trend Harvester")
    print("Finding high-complexity, high-stakes queries for Swarm training")
    print("=" * 80)
    print()
    
    # Get top complex medical queries
    print("🔍 Top complex MEDICAL queries:")
    print("-" * 80)
    medical_queries = harvester.get_trending_queries(category="medical", min_complexity=8, limit=5)
    
    for i, q in enumerate(medical_queries, 1):
        print(f"\n{i}. {q.query}")
        print(f"   Complexity: {q.complexity_score}/10 | Searches: {q.estimated_monthly_searches:,}/month")
        print(f"   Why complex: {q.why_complex}")
        print(f"   Expected decomposition:")
        for subq in q.expected_subquestions:
            print(f"     • {subq}")
    
    print("\n" + "=" * 80)
    print("📝 Generating training scenario for top query...")
    print("-" * 80)
    
    top_query = medical_queries[0]
    scenario = harvester.generate_training_scenario(top_query)
    
    print(json.dumps(scenario, indent=2))
    
    print("\n" + "=" * 80)
    print("💾 Exporting all queries for Swarm training...")
    print("-" * 80)
    
    output_file = harvester.export_for_swarm_training()
    
    print(f"\n✅ Done! Use these queries to:")
    print("   1. Test Swarm decomposition accuracy")
    print("   2. Identify knowledge gaps in fragment library")
    print("   3. Prioritize Night Mode simulation targets")
    print("   4. Measure improvement over time (decomposition → retrieval → survival rate)")


if __name__ == "__main__":
    main()
