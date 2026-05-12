"""
OpenEyes Swarm Processors and Archiver — Fragment Processing Pipeline

This module implements the processing and archiving agents for the Signal-Pulse Swarm.
These agents transform harvested evidence into validated fragments and persist them
to the fragment library.

Design Principles:
    - Minimal processing (validation first, enrichment later)
    - Write-first architecture (append-oriented buffering)
    - WAL-mode friendly (batched commits)
    - Memory-efficient operation

Agent Types:
    - FragmentProcessor: Validates and converts evidence to fragments
    - ConsolidationProcessor: Merges duplicate/similar fragments
    - FragmentArchiver: Persists fragments to storage with WAL buffering
"""

from __future__ import annotations

import asyncio
import gc
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openeyes.fragment_library import FragmentLibrary, Fragment
from openeyes.swarm.harvesters import HarvestedEvidence


@dataclass
class ProcessingResult:
    """Result of fragment processing."""
    fragment: Optional[Fragment]
    success: bool
    error_message: Optional[str] = None
    processing_time: float = 0.0
    validation_score: float = 0.0
    source_evidence_id: str = ""


class FragmentProcessor:
    """
    Processes harvested evidence into validated fragments.
    
    Responsibilities:
    - Convert HarvestedEvidence to Fragment objects
    - Validate fragment structure and content
    - Apply domain-specific rules
    - Score fragment quality
    """
    
    def __init__(self, agent_id: str, fragment_library: FragmentLibrary = None):
        self.agent_id = agent_id
        self.fragment_library = fragment_library or FragmentLibrary()
        self.active = False
        self.processed_count = 0
        self.error_count = 0
        
        # Input queue (receives from harvesters)
        self.input_queue: asyncio.Queue = asyncio.Queue()
        
        # Output queue (sends to archiver)
        self.output_queue: asyncio.Queue = asyncio.Queue()
        
        # Metrics
        self.metrics = {
            "evidence_processed": 0,
            "fragments_created": 0,
            "fragments_rejected": 0,
            "errors": 0,
            "avg_processing_time": 0.0,
            "last_process": None,
        }
    
    async def handle_signal(self, signal):
        """Handle incoming signals."""
        from openeyes.swarm.pulse_scheduler import SignalType
        
        if signal.signal_type == SignalType.SIG_WAKE:
            await self._on_wake(signal.payload)
        elif signal.signal_type == SignalType.SIG_PROCESS:
            await self._on_process(signal.payload)
        elif signal.signal_type == SignalType.SIG_HIBERNATE:
            await self._on_hibernate(signal.payload)
        elif signal.signal_type == SignalType.SIG_SHUTDOWN:
            await self._on_shutdown(signal.payload)
    
    async def _on_wake(self, payload: Dict[str, Any]):
        """Activate processor."""
        print(f"  [{self.agent_id}] Waking up...")
        self.active = True
    
    async def _on_process(self, payload: Dict[str, Any]):
        """Execute processing logic."""
        if not self.active:
            print(f"  [{self.agent_id}] Not active, skipping process")
            return
        
        print(f"  [{self.agent_id}] Starting fragment processing...")
        start_time = time.time()
        
        try:
            await self._execute_processing(payload)
            
            elapsed = time.time() - start_time
            self.metrics["last_process"] = datetime.now().isoformat()
            
            print(f"  [{self.agent_id}] Processing complete in {elapsed:.2f}s")
            
        except Exception as e:
            print(f"  [{self.agent_id}] Processing error: {e}")
            self.metrics["errors"] += 1
    
    async def _on_hibernate(self, payload: Dict[str, Any]):
        """Deactivate and cleanup."""
        print(f"  [{self.agent_id}] Entering hibernation...")
        self.active = False
    
    async def _on_shutdown(self, payload: Dict[str, Any]):
        """Final shutdown."""
        print(f"  [{self.agent_id}] Shutting down...")
        self.active = False
    
    async def _execute_processing(self, payload: Dict[str, Any]):
        """Process all evidence in input queue."""
        processing_times = []
        
        while not self.input_queue.empty():
            if not self.active:
                break
            
            try:
                evidence = await asyncio.wait_for(
                    self.input_queue.get(),
                    timeout=0.1
                )
                
                result = await self._process_evidence(evidence)
                processing_times.append(result.processing_time)
                
                if result.success and result.fragment:
                    await self.output_queue.put(result)
                    self.processed_count += 1
                    self.metrics["fragments_created"] += 1
                else:
                    self.metrics["fragments_rejected"] += 1
                
                self.metrics["evidence_processed"] += 1
                
            except asyncio.TimeoutError:
                break
            except Exception as e:
                print(f"  [{self.agent_id}] Error processing evidence: {e}")
                self.metrics["errors"] += 1
        
        # Update average processing time
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            n = self.metrics["evidence_processed"]
            old_avg = self.metrics["avg_processing_time"]
            self.metrics["avg_processing_time"] = ((old_avg * (n - len(processing_times))) + sum(processing_times)) / max(n, 1)
    
    async def _process_evidence(self, evidence: HarvestedEvidence) -> ProcessingResult:
        """Process a single piece of evidence."""
        start_time = time.time()
        
        try:
            # Convert to fragment
            fragment = evidence.to_fragment()
            
            if not fragment:
                return ProcessingResult(
                    fragment=None,
                    success=False,
                    error_message="Failed to convert evidence to fragment",
                    processing_time=time.time() - start_time,
                    source_evidence_id=evidence.evidence_id,
                )
            
            # Validate fragment
            validation_score = self._validate_fragment(fragment)
            
            if validation_score < 0.3:  # Minimum quality threshold
                return ProcessingResult(
                    fragment=fragment,
                    success=False,
                    error_message=f"Low validation score: {validation_score}",
                    processing_time=time.time() - start_time,
                    validation_score=validation_score,
                    source_evidence_id=evidence.evidence_id,
                )
            
            # Add to library if valid
            existing = self.fragment_library.get_fragment(fragment.id)
            if not existing:
                # Register in library
                self.fragment_library._register_fragment(fragment)
            
            return ProcessingResult(
                fragment=fragment,
                success=True,
                processing_time=time.time() - start_time,
                validation_score=validation_score,
                source_evidence_id=evidence.evidence_id,
            )
            
        except Exception as e:
            return ProcessingResult(
                fragment=None,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time,
                source_evidence_id=evidence.evidence_id,
            )
    
    def _validate_fragment(self, fragment: Fragment) -> float:
        """
        Validate fragment quality.
        
        Returns a score from 0.0 to 1.0 based on:
        - Content length (not too short)
        - Has required metadata
        - Domain is recognized
        - Tags are present
        """
        score = 0.0
        
        # Content quality (max 0.4)
        content_len = len(fragment.content.strip())
        if content_len > 50:
            score += 0.2
        if content_len > 100:
            score += 0.2
        
        # Metadata presence (max 0.3)
        if fragment.source:
            score += 0.1
        if fragment.source_url:
            score += 0.1
        if fragment.tags and len(fragment.tags) > 0:
            score += 0.1
        
        # Domain recognition (max 0.2)
        recognized_domains = ["healthcare", "economy", "governance", "general", "unknown"]
        if fragment.domain in recognized_domains:
            score += 0.2
        
        # Credibility class (max 0.1)
        if fragment.credibility_class in FragmentLibrary.CREDIBILITY_CLASSES:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processor metrics."""
        return {
            **self.metrics,
            "agent_id": self.agent_id,
            "active": self.active,
            "input_queue_size": self.input_queue.qsize(),
            "output_queue_size": self.output_queue.qsize(),
        }


class ConsolidationProcessor:
    """
    Consolidates and merges similar fragments.
    
    Responsibilities:
    - Detect duplicate/similar fragments
    - Merge compatible fragments
    - Update compatibility rules
    - Reduce fragment redundancy
    """
    
    def __init__(self, agent_id: str, fragment_library: FragmentLibrary = None):
        self.agent_id = agent_id
        self.fragment_library = fragment_library or FragmentLibrary()
        self.active = False
        
        self.metrics = {
            "fragments_consolidated": 0,
            "duplicates_merged": 0,
            "compatibilities_updated": 0,
            "last_consolidation": None,
        }
    
    async def handle_signal(self, signal):
        """Handle incoming signals."""
        from openeyes.swarm.pulse_scheduler import SignalType
        
        if signal.signal_type == SignalType.SIG_WAKE:
            await self._on_wake(signal.payload)
        elif signal.signal_type == SignalType.SIG_ARCHIVE:
            await self._on_consolidate(signal.payload)
        elif signal.signal_type == SignalType.SIG_HIBERNATE:
            await self._on_hibernate(signal.payload)
    
    async def _on_wake(self, payload: Dict[str, Any]):
        """Activate consolidator."""
        print(f"  [{self.agent_id}] Waking up...")
        self.active = True
    
    async def _on_consolidate(self, payload: Dict[str, Any]):
        """Execute consolidation logic."""
        if not self.active:
            return
        
        print(f"  [{self.agent_id}] Running consolidation...")
        
        # Simple consolidation: count fragments by domain
        domain_counts = defaultdict(int)
        for frag_id, frag in self.fragment_library._fragments.items():
            domain_counts[frag.domain] += 1
        
        print(f"  [{self.agent_id}] Fragment counts by domain:")
        for domain, count in sorted(domain_counts.items()):
            print(f"    - {domain}: {count}")
        
        self.metrics["fragments_consolidated"] = sum(domain_counts.values())
        self.metrics["last_consolidation"] = datetime.now().isoformat()
    
    async def _on_hibernate(self, payload: Dict[str, Any]):
        """Deactivate."""
        print(f"  [{self.agent_id}] Entering hibernation...")
        self.active = False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get consolidator metrics."""
        return {
            **self.metrics,
            "agent_id": self.agent_id,
            "active": self.active,
            "total_fragments": len(self.fragment_library._fragments),
        }


class FragmentArchiver:
    """
    Archives fragments to persistent storage.
    
    Responsibilities:
    - Persist fragments to JSON files
    - Use append-oriented buffering (WAL-friendly)
    - Batch commits for efficiency
    - Maintain fragment indexes
    """
    
    def __init__(
        self,
        agent_id: str,
        fragment_library: FragmentLibrary = None,
        buffer_size: int = 10,
    ):
        self.agent_id = agent_id
        self.fragment_library = fragment_library or FragmentLibrary()
        self.buffer_size = buffer_size
        self.active = False
        
        # Write buffer for batched commits
        self.write_buffer: List[Fragment] = []
        
        # Metrics
        self.metrics = {
            "fragments_archived": 0,
            "batches_written": 0,
            "write_errors": 0,
            "last_archive": None,
        }
    
    async def handle_signal(self, signal):
        """Handle incoming signals."""
        from openeyes.swarm.pulse_scheduler import SignalType
        
        if signal.signal_type == SignalType.SIG_WAKE:
            await self._on_wake(signal.payload)
        elif signal.signal_type == SignalType.SIG_ARCHIVE:
            await self._on_archive(signal.payload)
        elif signal.signal_type == SignalType.SIG_HIBERNATE:
            await self._on_hibernate(signal.payload)
        elif signal.signal_type == SignalType.SIG_SHUTDOWN:
            await self._on_shutdown(signal.payload)
    
    async def _on_wake(self, payload: Dict[str, Any]):
        """Activate archiver."""
        print(f"  [{self.agent_id}] Waking up...")
        self.active = True
    
    async def _on_archive(self, payload: Dict[str, Any]):
        """Execute archiving logic."""
        if not self.active:
            print(f"  [{self.agent_id}] Not active, skipping archive")
            return
        
        print(f"  [{self.agent_id}] Starting archive phase...")
        start_time = time.time()
        
        try:
            await self._execute_archive(payload)
            
            elapsed = time.time() - start_time
            self.metrics["last_archive"] = datetime.now().isoformat()
            
            print(f"  [{self.agent_id}] Archive complete in {elapsed:.2f}s")
            
        except Exception as e:
            print(f"  [{self.agent_id}] Archive error: {e}")
            self.metrics["write_errors"] += 1
    
    async def _on_hibernate(self, payload: Dict[str, Any]):
        """Flush buffer and deactivate."""
        print(f"  [{self.agent_id}] Flushing write buffer before hibernation...")
        await self._flush_buffer()
        self.active = False
    
    async def _on_shutdown(self, payload: Dict[str, Any]):
        """Final flush and shutdown."""
        print(f"  [{self.agent_id}] Final flush and shutdown...")
        await self._flush_buffer()
        self.active = False
    
    async def _execute_archive(self, payload: Dict[str, Any]):
        """Archive all pending fragments."""
        # Flush any buffered fragments
        await self._flush_buffer()
        
        # Also save all fragments from library
        print(f"  [{self.agent_id}] Saving {len(self.fragment_library._fragments)} fragments to storage...")
        
        for frag_id, frag in self.fragment_library._fragments.items():
            try:
                self.fragment_library._save_fragment(frag)
                self.metrics["fragments_archived"] += 1
            except Exception as e:
                print(f"  [{self.agent_id}] Error saving fragment {frag_id}: {e}")
                self.metrics["write_errors"] += 1
        
        self.metrics["batches_written"] += 1
    
    async def _flush_buffer(self):
        """Flush write buffer to storage."""
        if not self.write_buffer:
            return
        
        print(f"  [{self.agent_id}] Flushing buffer ({len(self.write_buffer)} fragments)...")
        
        for fragment in self.write_buffer:
            try:
                self.fragment_library._register_fragment(fragment)
                self.fragment_library._save_fragment(fragment)
                self.metrics["fragments_archived"] += 1
            except Exception as e:
                print(f"  [{self.agent_id}] Error flushing fragment: {e}")
                self.metrics["write_errors"] += 1
        
        self.write_buffer.clear()
        self.metrics["batches_written"] += 1
    
    async def queue_fragment(self, fragment: Fragment):
        """Queue a fragment for batched writing."""
        self.write_buffer.append(fragment)
        
        # Auto-flush if buffer is full
        if len(self.write_buffer) >= self.buffer_size:
            await self._flush_buffer()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get archiver metrics."""
        return {
            **self.metrics,
            "agent_id": self.agent_id,
            "active": self.active,
            "buffer_size": len(self.write_buffer),
            "library_size": len(self.fragment_library._fragments),
        }


def create_processors(fragment_library: FragmentLibrary = None) -> List[FragmentProcessor]:
    """Create default processor agents."""
    return [
        FragmentProcessor("processor_1", fragment_library),
        FragmentProcessor("processor_2", fragment_library),
    ]


def create_archiver(fragment_library: FragmentLibrary = None) -> FragmentArchiver:
    """Create default archiver agent."""
    return FragmentArchiver("archiver_1", fragment_library)


def create_consolidator(fragment_library: FragmentLibrary = None) -> ConsolidationProcessor:
    """Create default consolidator agent."""
    return ConsolidationProcessor("consolidator_1", fragment_library)


if __name__ == "__main__":
    # Demo: Test processor functionality
    async def demo():
        print("Testing FragmentProcessor...")
        
        library = FragmentLibrary()
        processor = FragmentProcessor("test_processor", library)
        archiver = FragmentArchiver("test_archiver", library)
        
        processor.active = True
        archiver.active = True
        
        # Create sample evidence
        evidence = HarvestedEvidence(
            evidence_id="test_001",
            source_path="/test/path/fragment.json",
            content="This is a test fragment about healthcare policy.",
            metadata={
                "domain": "healthcare",
                "topic": "policy",
                "credibility_class": "expert_consensus",
            },
            tags=["healthcare", "policy", "test"],
        )
        
        # Queue evidence
        await processor.input_queue.put(evidence)
        
        # Process
        await processor._execute_processing({})
        
        print(f"\nProcessor metrics: {processor.get_metrics()}")
        print(f"Output queue size: {processor.output_queue.qsize()}")
        
        # Get results
        while not processor.output_queue.empty():
            result = await processor.output_queue.get()
            print(f"\nProcessing result:")
            print(f"  Success: {result.success}")
            print(f"  Validation score: {result.validation_score}")
            if result.fragment:
                print(f"  Fragment ID: {result.fragment.id}")
                print(f"  Domain: {result.fragment.domain}")
                print(f"  Content preview: {result.fragment.content[:80]}...")
        
        # Archive
        await archiver._execute_archive({})
        
        print(f"\nArchiver metrics: {archiver.get_metrics()}")
        print(f"Library size: {len(library._fragments)}")
    
    asyncio.run(demo())
