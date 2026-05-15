"""
Unified System Integration Tests
Tests for the migrated Unified Knowledge Orchestrator and Quality Assessor
"""

import time
import pytest
from openeyes.core.unified_orchestrator import (
    UnifiedKnowledgeOrchestrator, 
    get_orchestrator,
    KnowledgeFragment,
    SourceTier,
    CrossDomainFusionEngine
)
from openeyes.core.quality_assessor import (
    KnowledgeQualityAssessor,
    CredibilityLevel
)


class TestUnifiedOrchestrator:
    """Test cascading retrieval and cross-domain fusion."""
    
    def setup_method(self):
        self.orchestrator = get_orchestrator()
    
    def test_single_domain_retrieval(self):
        """Test basic single-domain query."""
        result = self.orchestrator.retrieve_knowledge(
            "diabetes symptoms",
            domain_hint="Healthcare"
        )
        
        assert result.answer is not None
        assert result.confidence > 0.0
        assert result.strategy_used in ["LOCAL_CACHED", "LIVE_FETCH", "FALLBACK_ESTIMATE"]
        assert len(result.sources) > 0
    
    def test_cross_domain_detection(self):
        """Test automatic detection of multi-domain queries."""
        domains = self.orchestrator.fusion_engine.detect_domains(
            "economic impact of healthcare policy"
        )
        
        assert "Economy" in domains
        assert "Healthcare" in domains
        assert len(domains) >= 2
    
    def test_cross_domain_fusion(self):
        """Test cross-domain answer synthesis."""
        # Create mock fragments from different domains
        fragments = [
            KnowledgeFragment(
                content="Healthcare costs have risen 15% annually",
                source_url="file://health/costs.json",
                confidence_score=0.95,
                tier=SourceTier.LOCAL_HIGH_CONFIDENCE,
                domain="Healthcare"
            ),
            KnowledgeFragment(
                content="GDP growth slowed to 2.1% due to healthcare spending",
                source_url="file://economy/gdp.json",
                confidence_score=0.90,
                tier=SourceTier.LOCAL_HIGH_CONFIDENCE,
                domain="Economy"
            )
        ]
        
        fused_answer = self.orchestrator.fusion_engine.fuse_fragments(
            fragments,
            "economic impact of healthcare costs"
        )
        
        assert "Healthcare" in fused_answer
        assert "Economy" in fused_answer
        assert "Cross-Domain Analysis" in fused_answer
    
    def test_adaptive_confidence_calibration(self):
        """Test ML-based confidence adjustment."""
        base_conf = 0.95
        
        # Calibrate for high-performing domain
        calibrated_hc = self.orchestrator.calibrator.calibrate(
            base_conf, "Healthcare", SourceTier.LOCAL_HIGH_CONFIDENCE
        )
        
        # Calibrate for lower-performing domain
        calibrated_gen = self.orchestrator.calibrator.calibrate(
            base_conf, "General", SourceTier.LIVE_FETCH
        )
        
        # Healthcare should maintain higher confidence
        assert calibrated_hc > calibrated_gen
        assert 0.0 <= calibrated_hc <= 1.0
        assert 0.0 <= calibrated_gen <= 1.0
    
    def test_cascading_fallback(self):
        """Test fallback to live fetch when local cache misses."""
        # Query designed to trigger cache miss
        result = self.orchestrator.retrieve_knowledge(
            "error_trigger_no_local_data",
            domain_hint="Healthcare"
        )
        
        # Should fall back to live fetch or fallback estimate
        assert result.strategy_used in ["LIVE_FETCH", "FALLBACK_ESTIMATE"]


class TestQualityAssessor:
    """Test credibility scoring and integrity validation."""
    
    def setup_method(self):
        self.assessor = KnowledgeQualityAssessor()
    
    def test_trusted_source_credibility(self):
        """Test HIGH credibility for trusted domains."""
        trusted_urls = [
            "https://www.nih.gov/study.pdf",
            "https://www.cdc.gov/research.html",
            "https://www.worldbank.org/data.csv",
            "https://www.nature.com/articles/12345"
        ]
        
        for url in trusted_urls:
            report = self.assessor.assess_source_credibility(url)
            assert report.credibility_level == CredibilityLevel.HIGH
            assert report.score >= 0.9
    
    def test_suspicious_source_credibility(self):
        """Test LOW credibility for suspicious domains."""
        suspicious_urls = [
            "https://randomblog.blogspot.com/post",
            "https://unknown.wordpress.com/article"
        ]
        
        for url in suspicious_urls:
            report = self.assessor.assess_source_credibility(url)
            assert report.credibility_level == CredibilityLevel.LOW
            assert report.score <= 0.5
    
    def test_missing_source_detection(self):
        """Test detection of missing sources (hallucination prevention)."""
        integrity = self.assessor.validate_fragment_integrity(
            content="Some claim without source",
            source_url="",
            timestamp=1234567890
        )
        
        assert not integrity["is_valid"]
        assert "MISSING_SOURCE" in integrity["issues"]
    
    def test_stale_data_detection(self):
        """Test detection of outdated data."""
        old_timestamp = time.time() - (800 * 86400)  # 800 days ago
        
        integrity = self.assessor.validate_fragment_integrity(
            content="Old but valid content",
            source_url="https://example.com/old",
            timestamp=old_timestamp
        )
        
        assert "STALE_DATA" in integrity["issues"]
    
    def test_weighted_confidence_calculation(self):
        """Test combination of base confidence + credibility + integrity."""
        base_conf = 0.9
        cred_score = 0.95  # HIGH credibility
        
        # No integrity issues
        final_conf = self.assessor.calculate_weighted_confidence(
            base_conf, cred_score, []
        )
        
        # With missing source penalty
        final_conf_penalty = self.assessor.calculate_weighted_confidence(
            base_conf, cred_score, ["MISSING_SOURCE"]
        )
        
        # Penalty should reduce confidence
        assert final_conf_penalty < final_conf
        assert 0.0 <= final_conf <= 1.0


class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline_single_domain(self):
        """Test complete query pipeline with quality assessment."""
        orchestrator = get_orchestrator()
        assessor = KnowledgeQualityAssessor()
        
        # Execute query
        result = orchestrator.retrieve_knowledge(
            "medical treatment guidelines",
            domain_hint="Healthcare"
        )
        
        # Assess quality
        credibility_reports = []
        for source_url in result.sources:
            report = assessor.assess_source_credibility(source_url)
            credibility_reports.append(report)
        
        avg_credibility = sum(r.score for r in credibility_reports) / len(credibility_reports)
        final_confidence = assessor.calculate_weighted_confidence(
            result.confidence,
            avg_credibility,
            []
        )
        
        assert result.answer is not None
        assert final_confidence > 0.0
        assert len(credibility_reports) > 0
    
    def test_metrics_collection(self):
        """Test that quality metrics are properly tracked."""
        assessor = KnowledgeQualityAssessor()
        
        # Process multiple sources
        assessor.assess_source_credibility("https://nih.gov/study")
        assessor.assess_source_credibility("https://nih.gov/study2")
        assessor.assess_source_credibility("https://blogspot.com/post")
        
        metrics = assessor.get_metrics_dashboard_data()
        
        assert metrics["total_fragments"] == 3
        assert metrics["credibility_distribution"]["high"] == 2
        assert metrics["credibility_distribution"]["low"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
