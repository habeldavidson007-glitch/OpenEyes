"""
OpenEyes Swarm Harvesters — Lightweight Evidence Collection Agents

This module implements minimal harvester agents for the Signal-Pulse Swarm.
Harvesters are dormant until triggered by SIG_WAKE, then collect evidence
from designated sources during the HARVEST phase.

Design Principles:
    - Dormant until triggered (no persistent workers)
    - Fetch lightweight sources only
    - Detect and avoid duplicate processing
    - Push results into processing queue
    - Minimal memory footprint

Agent Types:
    - FileSystemHarvester: Scans local fragment directories
    - LibraryHarvester: Retrieves from fragment_library index
    - KnowledgeHarvester: Scans knowledge/ domain directories
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openeyes.fragment_library import FragmentLibrary, Fragment


@dataclass
class HarvestedEvidence:
    """Evidence collected by a harvester agent."""
    evidence_id: str
    source_path: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    harvested_at: float = field(default_factory=time.time)
    harvester_id: str = ""
    domain: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_fragment(self) -> Optional[Fragment]:
        """Convert harvested evidence to a Fragment if possible."""
        try:
            # Extract domain from metadata or infer from path
            domain = self.metadata.get("domain", "unknown")
            if not domain and self.source_path:
                path_parts = self.source_path.split(os.sep)
                for part in path_parts:
                    if part in ["hc", "eco", "gov"]:
                        domain_map = {"hc": "healthcare", "eco": "economy", "gov": "governance"}
                        domain = domain_map.get(part, "unknown")
                        break
            
            # Generate stable fragment ID
            fragment_id = FragmentLibrary.generate_fragment_id(self.content, self.source_path)
            
            return Fragment(
                id=fragment_id,
                domain=domain,
                tags=self.tags or [self.metadata.get("topic", "general")],
                content=self.content[:2000],  # Limit content size
                source=self.metadata.get("source", self.source_path),
                source_url=self.metadata.get("source_url", ""),
                credibility_class=self.metadata.get("credibility_class", "expert_consensus"),
                sub_question=self.metadata.get("sub_question"),
                reasoning_role=self.metadata.get("reasoning_role", "definition"),
                source_type=self.metadata.get("source_type", "secondary"),
                year=self.metadata.get("year", datetime.now().year),
            )
        except Exception as e:
            print(f"[HarvestedEvidence] Error converting to fragment: {e}")
            return None


class HarvesterAgent:
    """
    Base class for harvester agents.
    
    Lifecycle:
    1. Dormant (waiting for SIG_WAKE)
    2. Active (processing SIG_HARVEST)
    3. Dormant (after SIG_HIBERNATE)
    """
    
    def __init__(self, agent_id: str, sources: List[str] = None):
        self.agent_id = agent_id
        self.sources = sources or []
        self.active = False
        self.processed_hashes: Set[str] = set()  # Track processed content to avoid duplicates
        self.harvested_count = 0
        self.last_harvest_time: Optional[float] = None
        
        # Queue for harvested evidence
        self.evidence_queue: asyncio.Queue = asyncio.Queue()
        
        # Performance metrics
        self.metrics = {
            "harvests_completed": 0,
            "evidence_collected": 0,
            "duplicates_avoided": 0,
            "errors": 0,
            "last_harvest": None,
        }
    
    async def handle_signal(self, signal):
        """Handle incoming signals from the signal bus."""
        from openeyes.swarm.pulse_scheduler import SignalType
        
        if signal.signal_type == SignalType.SIG_WAKE:
            await self._on_wake(signal.payload)
        elif signal.signal_type == SignalType.SIG_HARVEST:
            await self._on_harvest(signal.payload)
        elif signal.signal_type == SignalType.SIG_HIBERNATE:
            await self._on_hibernate(signal.payload)
        elif signal.signal_type == SignalType.SIG_SHUTDOWN:
            await self._on_shutdown(signal.payload)
    
    async def _on_wake(self, payload: Dict[str, Any]):
        """Activate the harvester."""
        print(f"  [{self.agent_id}] Waking up...")
        self.active = True
        
        # Update sources if provided
        if "sources" in payload:
            self.sources = payload["sources"]
    
    async def _on_harvest(self, payload: Dict[str, Any]):
        """Execute harvesting logic."""
        if not self.active:
            print(f"  [{self.agent_id}] Not active, skipping harvest")
            return
        
        print(f"  [{self.agent_id}] Starting harvest from {len(self.sources)} sources...")
        start_time = time.time()
        
        try:
            await self._execute_harvest(payload)
            
            elapsed = time.time() - start_time
            self.metrics["harvests_completed"] += 1
            self.metrics["last_harvest"] = datetime.now().isoformat()
            
            print(f"  [{self.agent_id}] Harvest complete in {elapsed:.2f}s. Collected {self.harvested_count} items.")
            
        except Exception as e:
            print(f"  [{self.agent_id}] Harvest error: {e}")
            self.metrics["errors"] += 1
    
    async def _on_hibernate(self, payload: Dict[str, Any]):
        """Deactivate and cleanup."""
        print(f"  [{self.agent_id}] Entering hibernation...")
        self.active = False
        self.last_harvest_time = time.time()
        
        # Clear processed hashes periodically to allow re-harvesting of updated content
        # Keep only recent hashes (simple approach: clear all on hibernate)
        self.processed_hashes.clear()
    
    async def _on_shutdown(self, payload: Dict[str, Any]):
        """Final shutdown."""
        print(f"  [{self.agent_id}] Shutting down...")
        self.active = False
    
    async def _execute_harvest(self, payload: Dict[str, Any]):
        """Override this method in subclasses to implement harvesting logic."""
        raise NotImplementedError("Subclasses must implement _execute_harvest")
    
    def _is_duplicate(self, content: str) -> bool:
        """Check if content has already been processed."""
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        if content_hash in self.processed_hashes:
            self.metrics["duplicates_avoided"] += 1
            return True
        self.processed_hashes.add(content_hash)
        return False
    
    async def push_evidence(self, evidence: HarvestedEvidence):
        """Push harvested evidence to the processing queue."""
        evidence.harvester_id = self.agent_id
        await self.evidence_queue.put(evidence)
        self.harvested_count += 1
        self.metrics["evidence_collected"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get harvester metrics."""
        return {
            **self.metrics,
            "agent_id": self.agent_id,
            "active": self.active,
            "queue_size": self.evidence_queue.qsize(),
            "processed_hashes_count": len(self.processed_hashes),
        }


class FileSystemHarvester(HarvesterAgent):
    """
    Harvests evidence from filesystem directories.
    
    Scans designated directories for JSON fragment files,
    loads them, and pushes to processing queue.
    """
    
    def __init__(self, agent_id: str, sources: List[str] = None):
        super().__init__(agent_id, sources)
        self.base_path = Path(__file__).parent.parent  # openeyes/ root
    
    async def _execute_harvest(self, payload: Dict[str, Any]):
        """Scan filesystem for fragment files."""
        domain_filter = payload.get("domain_filter")
        
        for source_path in self.sources:
            if not self.active:
                break
            
            full_path = self.base_path / source_path
            
            if not full_path.exists():
                print(f"  [{self.agent_id}] Path not found: {full_path}")
                continue
            
            print(f"  [{self.agent_id}] Scanning: {full_path}")
            
            # Find all JSON files
            for json_file in full_path.rglob("*.json"):
                if not self.active:
                    break
                
                try:
                    await self._process_file(json_file, domain_filter)
                except Exception as e:
                    print(f"  [{self.agent_id}] Error processing {json_file}: {e}")
                    self.metrics["errors"] += 1
    
    async def _process_file(self, filepath: Path, domain_filter: Optional[str]):
        """Process a single JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different fragment formats
            content = self._extract_content(data, filepath)
            if not content:
                return
            
            # Check for duplicates
            if self._is_duplicate(content):
                return
            
            # Infer metadata from path
            path_parts = filepath.parts
            domain = self._infer_domain(path_parts, data)
            
            # Apply domain filter
            if domain_filter and domain != domain_filter:
                return
            
            # Create harvested evidence
            evidence = HarvestedEvidence(
                evidence_id=f"fs_{filepath.stem}_{int(time.time())}",
                source_path=str(filepath),
                content=content,
                metadata={
                    "domain": domain,
                    "topic": filepath.stem,
                    "source": filepath.name,
                },
                tags=self._extract_tags(data, path_parts),
            )
            
            await self.push_evidence(evidence)
            
        except Exception as e:
            print(f"  [{self.agent_id}] File processing error: {e}")
            self.metrics["errors"] += 1
    
    def _extract_content(self, data: Dict[str, Any], filepath: Path) -> Optional[str]:
        """Extract content from various JSON formats."""
        # Try common content fields
        content_fields = ["content", "claim", "text", "body", "description"]
        
        for field in content_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    return value
                elif isinstance(value, dict):
                    return value.get("text", value.get("content", str(value)))
        
        # Handle fragment array format
        if "fragments" in data and isinstance(data["fragments"], list):
            if data["fragments"]:
                first_frag = data["fragments"][0]
                for field in content_fields:
                    if field in first_frag:
                        return first_frag[field]
        
        return None
    
    def _infer_domain(self, path_parts: tuple, data: Dict[str, Any]) -> str:
        """Infer domain from path or data."""
        # Check data first
        if "domain" in data:
            return data["domain"]
        
        # Check path components
        domain_map = {
            "hc": "healthcare",
            "healthcare": "healthcare",
            "med": "healthcare",
            "phr": "healthcare",
            "mh": "healthcare",
            "ph": "healthcare",
            "eco": "economy",
            "economy": "economy",
            "fin": "economy",
            "com": "economy",
            "enr": "economy",
            "mac": "economy",
            "geo": "economy",
            "reg": "economy",
            "gov": "governance",
            "governance": "governance",
            "leg": "governance",
            "jud": "governance",
            "sec": "governance",
            "sub": "governance",
            "ele": "governance",
            "gel": "governance",
            "int": "governance",
            "ipl": "governance",
        }
        
        for part in path_parts:
            if part.lower() in domain_map:
                return domain_map[part.lower()]
        
        return "unknown"
    
    def _extract_tags(self, data: Dict[str, Any], path_parts: tuple) -> List[str]:
        """Extract tags from data or path."""
        tags = []
        
        # From data
        if "tags" in data and isinstance(data["tags"], list):
            tags.extend(data["tags"])
        
        if "topic" in data:
            tags.append(data["topic"])
        
        # From path
        for part in path_parts:
            if part not in ["knowledge", "fragment_library", "fragments", "openeyes"]:
                tags.append(part)
        
        return list(set(tags))[:10]  # Limit to 10 tags


class LibraryHarvester(HarvesterAgent):
    """
    Harvests evidence from the FragmentLibrary index.
    
    Iterates through existing fragments to ensure they're properly indexed
    and available for retrieval.
    """
    
    def __init__(self, agent_id: str, fragment_library: FragmentLibrary = None):
        super().__init__(agent_id, sources=["fragment_library"])
        self.fragment_library = fragment_library or FragmentLibrary()
    
    async def _execute_harvest(self, payload: Dict[str, Any]):
        """Iterate through fragment library."""
        print(f"  [{self.agent_id}] Scanning fragment library...")
        
        domain_filter = payload.get("domain_filter")
        
        # Get all fragments
        fragments = []
        for domain in self.fragment_library._domain_index.keys():
            if domain_filter and domain != domain_filter:
                continue
            fragments.extend(
                self.fragment_library.get_fragments_by_domain(domain)
            )
        
        print(f"  [{self.agent_id}] Found {len(fragments)} fragments in library")
        
        # Process each fragment
        for frag in fragments:
            if not self.active:
                break
            
            # Check for duplicates using fragment ID
            if self._is_duplicate(frag.id):
                continue
            
            # Create harvested evidence
            evidence = HarvestedEvidence(
                evidence_id=f"lib_{frag.id}",
                source_path=frag.source_url or frag.source,
                content=frag.content,
                metadata={
                    "domain": frag.domain,
                    "credibility_class": frag.credibility_class,
                    "reasoning_role": frag.reasoning_role,
                    "source_type": frag.source_type,
                    "year": frag.year,
                    "fragment_id": frag.id,
                },
                tags=frag.tags,
            )
            
            await self.push_evidence(evidence)
        
        print(f"  [{self.agent_id}] Library harvest complete: {self.harvested_count} items")


class KnowledgeHarvester(HarvesterAgent):
    """
    Specialized harvester for knowledge/ domain directories.
    
    Focuses on the three core domains: healthcare, economy, governance.
    """
    
    def __init__(self, agent_id: str, sources: List[str] = None):
        default_sources = [
            "knowledge/hc",
            "knowledge/eco",
            "knowledge/gov",
        ]
        super().__init__(agent_id, sources=sources or default_sources)
        self.base_path = Path(__file__).parent.parent
    
    async def _execute_harvest(self, payload: Dict[str, Any]):
        """Harvest from knowledge directories."""
        domain_filter = payload.get("domain_filter")
        
        # Map domain names to directory prefixes
        domain_to_dir = {
            "healthcare": "hc",
            "economy": "eco",
            "governance": "gov",
        }
        
        for source_path in self.sources:
            if not self.active:
                break
            
            # Apply domain filter
            if domain_filter:
                dir_prefix = domain_to_dir.get(domain_filter)
                if dir_prefix and dir_prefix not in source_path:
                    continue
            
            full_path = self.base_path / source_path
            
            if not full_path.exists():
                print(f"  [{self.agent_id}] Path not found: {full_path}")
                continue
            
            print(f"  [{self.agent_id}] Harvesting from: {full_path}")
            
            # Use FileSystemHarvester logic
            fs_harvester = FileSystemHarvester(self.agent_id, [source_path])
            fs_harvester.active = True
            fs_harvester.processed_hashes = self.processed_hashes
            fs_harvester.evidence_queue = self.evidence_queue
            
            try:
                await fs_harvester._execute_harvest(payload)
                
                # Merge metrics
                self.harvested_count += fs_harvester.harvested_count
                self.metrics["evidence_collected"] += fs_harvester.metrics["evidence_collected"]
                
            finally:
                fs_harvester.active = False


def create_harvesters(fragment_library: FragmentLibrary = None) -> List[HarvesterAgent]:
    """Create the default set of harvester agents."""
    harvesters = [
        FileSystemHarvester(
            "harvester_fs_1",
            sources=["fragment_library/fragments"]
        ),
        FileSystemHarvester(
            "harvester_fs_2",
            sources=["knowledge/hc/phr", "knowledge/hc/med"]
        ),
        FileSystemHarvester(
            "harvester_fs_3",
            sources=["knowledge/eco/fin", "knowledge/eco/com"]
        ),
        FileSystemHarvester(
            "harvester_fs_4",
            sources=["knowledge/gov/leg", "knowledge/gov/jud"]
        ),
        LibraryHarvester(
            "harvester_lib_1",
            fragment_library=fragment_library
        ),
    ]
    
    return harvesters


if __name__ == "__main__":
    # Demo: Test harvester functionality
    async def demo():
        print("Testing FileSystemHarvester...")
        
        harvester = FileSystemHarvester(
            "test_harvester",
            sources=["fragment_library/fragments"]
        )
        
        harvester.active = True
        
        # Simulate harvest signal
        from openeyes.swarm.pulse_scheduler import PulseSignal, SignalType
        
        harvest_signal = PulseSignal(
            signal_type=SignalType.SIG_HARVEST,
            payload={"domain_filter": None}
        )
        
        await harvester._on_harvest(harvest_signal.payload)
        
        print(f"\nHarvester metrics: {harvester.get_metrics()}")
        print(f"Evidence queue size: {harvester.evidence_queue.qsize()}")
        
        # Show sample evidence
        if not harvester.evidence_queue.empty():
            evidence = await harvester.evidence_queue.get()
            print(f"\nSample evidence:")
            print(f"  ID: {evidence.evidence_id}")
            print(f"  Source: {evidence.source_path}")
            print(f"  Content preview: {evidence.content[:100]}...")
            print(f"  Domain: {evidence.domain}")
            print(f"  Tags: {evidence.tags}")
    
    asyncio.run(demo())
