"""
OpenEyes Signal-Pulse Swarm — Autonomous Cyclic Evidence Circulation

This module implements the MINIMUM VIABLE AUTONOMOUS PULSE LOOP for OpenEyes.
It transforms the system from query-triggered retrieval to continuously 
hydrated autonomous evidence circulation.

Architecture:
    1. WAKE → 2. HARVEST → 3. PROCESS → 4. ARCHIVE → 5. HIBERNATE → REPEAT

Design Principles:
    - Event-driven, not thread-spam (asyncio + queues)
    - Minimal agent count (1 scheduler, 3-5 harvesters, 2 processors, 1 archiver)
    - Staggered activation to reduce CPU/network spikes
    - Fragment hydration FIRST (write-first architecture)
    - Mandatory hibernation phase for low-resource hardware (4GB RAM)

Signal Types:
    - SIG_WAKE: Trigger agent activation
    - SIG_HARVEST: Begin evidence collection
    - SIG_PROCESS: Begin fragment processing
    - SIG_ARCHIVE: Persist fragments
    - SIG_HIBERNATE: Cooldown and memory release

Pulse States:
    - SLEEPING: System dormant
    - WAKING: Initializing agents
    - HARVESTING: Collecting evidence
    - PROCESSING: Validating fragments
    - ARCHIVING: Persisting to storage
    - HIBERNATING: Cleanup and memory release
"""

from __future__ import annotations

import asyncio
import gc
import time
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from openeyes.fragment_library import FragmentLibrary


class PulseState(Enum):
    """System pulse states for lifecycle management."""
    SLEEPING = auto()
    WAKING = auto()
    HARVESTING = auto()
    PROCESSING = auto()
    ARCHIVING = auto()
    HIBERNATING = auto()


class SignalType(Enum):
    """Internal signal types for event-driven communication."""
    SIG_WAKE = auto()
    SIG_HARVEST = auto()
    SIG_PROCESS = auto()
    SIG_ARCHIVE = auto()
    SIG_HIBERNATE = auto()
    SIG_SHUTDOWN = auto()


@dataclass
class PulseSignal:
    """A signal emitted on the internal signal bus."""
    signal_type: SignalType
    timestamp: float = field(default_factory=time.time)
    payload: Optional[Dict[str, Any]] = None
    source: str = "scheduler"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type.name,
            "timestamp": self.timestamp,
            "payload": self.payload or {},
            "source": self.source
        }


class SignalBus:
    """
    Lightweight in-memory async signal bus for internal communication.
    
    Avoids complex message brokers. Uses asyncio queues for event signaling.
    Supports publish/subscribe pattern with topic-based routing.
    """
    
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._global_queue: asyncio.Queue = asyncio.Queue()
        
    def subscribe(self, topic: str, callback: Callable):
        """Subscribe a callback to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
        
        # Create queue for topic if not exists
        if topic not in self._queues:
            self._queues[topic] = asyncio.Queue()
    
    def unsubscribe(self, topic: str, callback: Callable):
        """Unsubscribe a callback from a topic."""
        if topic in self._subscribers:
            self._subscribers[topic].remove(callback)
    
    async def publish(self, topic: str, signal: PulseSignal):
        """Publish a signal to a topic."""
        # Queue the signal
        if topic in self._queues:
            await self._queues[topic].put(signal)
        
        # Call subscribers directly
        if topic in self._subscribers:
            for callback in self._subscribers[topic]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(signal)
                    else:
                        callback(signal)
                except Exception as e:
                    print(f"[SignalBus] Error in subscriber callback: {e}")
        
        # Also publish to global queue
        await self._global_queue.put(signal)
    
    async def get_signal(self, topic: str, timeout: Optional[float] = None) -> Optional[PulseSignal]:
        """Get a signal from a topic queue."""
        if topic not in self._queues:
            return None
        
        try:
            if timeout:
                return await asyncio.wait_for(
                    self._queues[topic].get(),
                    timeout=timeout
                )
            else:
                return await self._queues[topic].get()
        except asyncio.TimeoutError:
            return None
    
    async def get_global_signal(self, timeout: Optional[float] = None) -> Optional[PulseSignal]:
        """Get a signal from the global queue."""
        try:
            if timeout:
                return await asyncio.wait_for(
                    self._global_queue.get(),
                    timeout=timeout
                )
            else:
                return await self._global_queue.get()
        except asyncio.TimeoutError:
            return None
    
    def clear_topic(self, topic: str):
        """Clear all pending signals for a topic."""
        if topic in self._queues:
            while not self._queues[topic].empty():
                try:
                    self._queues[topic].get_nowait()
                except asyncio.QueueEmpty:
                    break
    
    def clear_all(self):
        """Clear all pending signals."""
        for queue in self._queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        while not self._global_queue.empty():
            try:
                self._global_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


@dataclass
class AgentConfig:
    """Configuration for a swarm agent."""
    agent_id: str
    agent_type: str  # "harvester", "processor", "archiver", "consolidator"
    wake_delay: float = 0.0  # Staggered activation delay in seconds
    active_duration: float = 300.0  # How long to stay active (seconds)
    sources: List[str] = field(default_factory=list)  # Sources to harvest
    domain_filter: Optional[str] = None  # Domain restriction


class PulseScheduler:
    """
    Global Pulse Scheduler for autonomous cyclic operation.
    
    Responsibilities:
    - Timed wake cycle
    - Staggered activation of agents
    - Pulse state transitions
    - Hibernation trigger
    - Cycle logging
    
    This is the heart of the Signal-Pulse Swarm architecture.
    """
    
    def __init__(
        self,
        fragment_library: Optional[FragmentLibrary] = None,
        cycle_duration: float = 600.0,  # 10 minutes per cycle
        harvest_duration: float = 180.0,  # 3 minutes harvesting
        process_duration: float = 120.0,  # 2 minutes processing
        archive_duration: float = 60.0,  # 1 minute archiving
        hibernation_duration: float = 240.0,  # 4 minutes hibernation
        stagger_delay: float = 0.5,  # Seconds between agent activations
    ):
        self.fragment_library = fragment_library or FragmentLibrary()
        self.cycle_duration = cycle_duration
        self.harvest_duration = harvest_duration
        self.process_duration = process_duration
        self.archive_duration = archive_duration
        self.hibernation_duration = hibernation_duration
        self.stagger_delay = stagger_delay
        
        self.current_state = PulseState.SLEEPING
        self.signal_bus = SignalBus()
        self.agents: Dict[str, AgentConfig] = {}
        self.active_agents: set = set()
        self.cycle_count = 0
        self.running = False
        self._current_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.metrics = {
            "cycles_completed": 0,
            "fragments_harvested": 0,
            "fragments_processed": 0,
            "fragments_archived": 0,
            "total_hibernations": 0,
            "avg_cycle_time": 0.0,
            "last_cycle_start": None,
            "last_cycle_end": None,
        }
        
        # Register default agents
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register minimal set of agents for validation."""
        # Harvesters (3-5 as specified)
        harvester_sources = [
            ["knowledge/hc", "knowledge/hc/phr", "knowledge/hc/med"],
            ["knowledge/eco", "knowledge/eco/fin", "knowledge/eco/com"],
            ["knowledge/gov", "knowledge/gov/leg", "knowledge/gov/jud"],
            ["fragment_library/fragments"],
            ["knowledge/hc/mh", "knowledge/hc/ph"],
        ]
        
        for i, sources in enumerate(harvester_sources[:5]):
            agent_id = f"harvester_{i+1}"
            self.agents[agent_id] = AgentConfig(
                agent_id=agent_id,
                agent_type="harvester",
                wake_delay=i * self.stagger_delay,  # Staggered activation
                sources=sources,
            )
        
        # Processors (2 as specified)
        for i in range(2):
            agent_id = f"processor_{i+1}"
            self.agents[agent_id] = AgentConfig(
                agent_id=agent_id,
                agent_type="processor",
                wake_delay=(5 + i) * self.stagger_delay,
            )
        
        # Archiver (1 as specified)
        self.agents["archiver_1"] = AgentConfig(
            agent_id="archiver_1",
            agent_type="archiver",
            wake_delay=7 * self.stagger_delay,
        )
        
        # Consolidator (1 as specified)
        self.agents["consolidator_1"] = AgentConfig(
            agent_id="consolidator_1",
            agent_type="consolidator",
            wake_delay=8 * self.stagger_delay,
        )
    
    @property
    def state(self) -> PulseState:
        """Get current pulse state."""
        return self.current_state
    
    def transition_to(self, new_state: PulseState):
        """Transition to a new state with logging."""
        old_state = self.current_state
        self.current_state = new_state
        print(f"[PulseScheduler] State transition: {old_state.name} → {new_state.name}")
    
    async def run_cycle(self):
        """Execute one complete pulse cycle."""
        cycle_start = time.time()
        self.metrics["last_cycle_start"] = datetime.now().isoformat()
        self.cycle_count += 1
        
        print(f"\n{'='*60}")
        print(f"[PulseScheduler] Starting cycle #{self.cycle_count}")
        print(f"{'='*60}")
        
        try:
            # Phase 1: WAKE
            await self._wake_phase()
            
            # Phase 2: HARVEST
            await self._harvest_phase()
            
            # Phase 3: PROCESS
            await self._process_phase()
            
            # Phase 4: ARCHIVE
            await self._archive_phase()
            
            # Phase 5: HIBERNATE
            await self._hibernate_phase()
            
            # Update metrics
            cycle_end = time.time()
            cycle_time = cycle_end - cycle_start
            self.metrics["cycles_completed"] += 1
            self.metrics["last_cycle_end"] = datetime.now().isoformat()
            
            # Running average of cycle time
            n = self.metrics["cycles_completed"]
            avg = self.metrics["avg_cycle_time"]
            self.metrics["avg_cycle_time"] = ((avg * (n - 1)) + cycle_time) / n
            
            print(f"[PulseScheduler] Cycle #{self.cycle_count} completed in {cycle_time:.2f}s")
            
        except asyncio.CancelledError:
            print("[PulseScheduler] Cycle cancelled")
            raise
        except Exception as e:
            print(f"[PulseScheduler] Error in cycle: {e}")
            # Attempt recovery via hibernation
            await self._hibernate_phase()
    
    async def _wake_phase(self):
        """Wake phase: activate agents gradually."""
        self.transition_to(PulseState.WAKING)
        print("[PulseScheduler] WAKE phase: Activating agents...")
        
        # Emit wake signal
        wake_signal = PulseSignal(
            signal_type=SignalType.SIG_WAKE,
            payload={"cycle": self.cycle_count}
        )
        await self.signal_bus.publish("system", wake_signal)
        
        # Activate agents with staggered delays
        for agent_id, config in self.agents.items():
            if config.agent_type == "harvester":
                await asyncio.sleep(config.wake_delay)
                self.active_agents.add(agent_id)
                print(f"  [Agent] {agent_id} activated (delay: {config.wake_delay}s)")
                
                # Notify agent
                await self.signal_bus.publish(
                    f"agent:{agent_id}",
                    PulseSignal(
                        signal_type=SignalType.SIG_WAKE,
                        payload={"agent_id": agent_id, "sources": config.sources}
                    )
                )
        
        print(f"[PulseScheduler] WAKE phase complete. {len(self.active_agents)} agents active.")
    
    async def _harvest_phase(self):
        """Harvest phase: collect evidence from sources."""
        self.transition_to(PulseState.HARVESTING)
        print(f"[PulseScheduler] HARVEST phase: Collecting evidence ({self.harvest_duration}s)...")
        
        # Emit harvest signal
        harvest_signal = PulseSignal(
            signal_type=SignalType.SIG_HARVEST,
            payload={
                "cycle": self.cycle_count,
                "duration": self.harvest_duration,
                "active_agents": list(self.active_agents)
            }
        )
        await self.signal_bus.publish("system", harvest_signal)
        
        # Notify harvesters
        for agent_id, config in self.agents.items():
            if config.agent_type == "harvester" and agent_id in self.active_agents:
                await self.signal_bus.publish(
                    f"agent:{agent_id}",
                    PulseSignal(
                        signal_type=SignalType.SIG_HARVEST,
                        payload={"sources": config.sources, "domain_filter": config.domain_filter}
                    )
                )
        
        # Wait for harvest duration
        await asyncio.sleep(self.harvest_duration)
        
        print("[PulseScheduler] HARVEST phase complete.")
    
    async def _process_phase(self):
        """Process phase: validate and process harvested evidence."""
        self.transition_to(PulseState.PROCESSING)
        print(f"[PulseScheduler] PROCESS phase: Validating fragments ({self.process_duration}s)...")
        
        # Emit process signal
        process_signal = PulseSignal(
            signal_type=SignalType.SIG_PROCESS,
            payload={
                "cycle": self.cycle_count,
                "duration": self.process_duration
            }
        )
        await self.signal_bus.publish("system", process_signal)
        
        # Notify processors
        for agent_id, config in self.agents.items():
            if config.agent_type == "processor":
                await self.signal_bus.publish(
                    f"agent:{agent_id}",
                    PulseSignal(
                        signal_type=SignalType.SIG_PROCESS,
                        payload={}
                    )
                )
        
        # Wait for process duration
        await asyncio.sleep(self.process_duration)
        
        print("[PulseScheduler] PROCESS phase complete.")
    
    async def _archive_phase(self):
        """Archive phase: persist fragments to storage."""
        self.transition_to(PulseState.ARCHIVING)
        print(f"[PulseScheduler] ARCHIVE phase: Persisting fragments ({self.archive_duration}s)...")
        
        # Emit archive signal
        archive_signal = PulseSignal(
            signal_type=SignalType.SIG_ARCHIVE,
            payload={
                "cycle": self.cycle_count,
                "duration": self.archive_duration
            }
        )
        await self.signal_bus.publish("system", archive_signal)
        
        # Notify archiver and consolidator
        for agent_id, config in self.agents.items():
            if config.agent_type in ("archiver", "consolidator"):
                await self.signal_bus.publish(
                    f"agent:{agent_id}",
                    PulseSignal(
                        signal_type=SignalType.SIG_ARCHIVE,
                        payload={}
                    )
                )
        
        # Wait for archive duration
        await asyncio.sleep(self.archive_duration)
        
        print("[PulseScheduler] ARCHIVE phase complete.")
    
    async def _hibernate_phase(self):
        """Hibernate phase: cleanup, release memory, cooldown."""
        self.transition_to(PulseState.HIBERNATING)
        print(f"[PulseScheduler] HIBERNATE phase: Cleanup and memory release ({self.hibernation_duration}s)...")
        
        # Emit hibernate signal
        hibernate_signal = PulseSignal(
            signal_type=SignalType.SIG_HIBERNATE,
            payload={
                "cycle": self.cycle_count,
                "duration": self.hibernation_duration
            }
        )
        await self.signal_bus.publish("system", hibernate_signal)
        
        # Notify all agents to deactivate
        for agent_id in self.active_agents:
            await self.signal_bus.publish(
                f"agent:{agent_id}",
                PulseSignal(
                    signal_type=SignalType.SIG_HIBERNATE,
                    payload={"agent_id": agent_id}
                )
            )
        
        # Clear signal queues
        self.signal_bus.clear_all()
        
        # Deactivate all agents
        deactivated = len(self.active_agents)
        self.active_agents.clear()
        print(f"  [Agent] Deactivated {deactivated} agents")
        
        # Aggressive garbage collection
        print("  [Memory] Running garbage collection...")
        gc.collect()
        
        # Report memory status
        try:
            import tracemalloc
            current, peak = tracemalloc.get_traced_memory()
            print(f"  [Memory] Current: {current / 1024 / 1024:.2f} MB, Peak: {peak / 1024 / 1024:.2f} MB")
        except Exception:
            pass
        
        self.metrics["total_hibernations"] += 1
        
        # Wait for hibernation duration
        await asyncio.sleep(self.hibernation_duration)
        
        self.transition_to(PulseState.SLEEPING)
        print("[PulseScheduler] HIBERNATE phase complete. System entering SLEEPING state.")
    
    async def run_continuous(self, max_cycles: Optional[int] = None):
        """Run continuous pulse cycles."""
        self.running = True
        print(f"[PulseScheduler] Starting continuous pulse loop (max_cycles={max_cycles})")
        
        try:
            while self.running:
                if max_cycles and self.cycle_count >= max_cycles:
                    print(f"[PulseScheduler] Reached max cycles ({max_cycles}), stopping")
                    break
                
                await self.run_cycle()
                
        except asyncio.CancelledError:
            print("[PulseScheduler] Continuous loop cancelled")
        finally:
            self.running = False
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown."""
        print("[PulseScheduler] Shutting down...")
        self.running = False
        
        # Emit shutdown signal
        shutdown_signal = PulseSignal(
            signal_type=SignalType.SIG_SHUTDOWN,
            payload={"cycle_count": self.cycle_count}
        )
        await self.signal_bus.publish("system", shutdown_signal)
        
        # Clear all queues
        self.signal_bus.clear_all()
        
        # Final garbage collection
        gc.collect()
        
        print(f"[PulseScheduler] Shutdown complete. Total cycles: {self.cycle_count}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.metrics,
            "current_state": self.current_state.name,
            "active_agents": len(self.active_agents),
            "total_agents": len(self.agents),
        }


# Convenience function for standalone usage
async def run_pulse_loop(
    cycles: int = 1,
    cycle_duration: float = 600.0,
    fragment_library: Optional[FragmentLibrary] = None
):
    """
    Run the pulse loop for a specified number of cycles.
    
    Args:
        cycles: Number of cycles to run
        cycle_duration: Total duration of each cycle in seconds
        fragment_library: Optional pre-initialized fragment library
    
    Returns:
        The PulseScheduler instance with metrics
    """
    scheduler = PulseScheduler(
        fragment_library=fragment_library,
        cycle_duration=cycle_duration,
    )
    
    await scheduler.run_continuous(max_cycles=cycles)
    
    return scheduler


# Entry point for CLI integration
def start_autonomous_loop(
    cycles: int = 1,
    cycle_duration: float = 600.0,
    blocking: bool = True
):
    """
    Start the autonomous pulse loop.
    
    Args:
        cycles: Number of cycles to run (-1 for infinite)
        cycle_duration: Total duration of each cycle in seconds
        blocking: If True, block until completion
    
    Returns:
        PulseScheduler instance (or None if non-blocking)
    """
    max_cycles = None if cycles == -1 else cycles
    
    if blocking:
        asyncio.run(run_pulse_loop(cycles=max_cycles, cycle_duration=cycle_duration))
    else:
        scheduler = PulseScheduler(cycle_duration=cycle_duration)
        task = asyncio.create_task(scheduler.run_continuous(max_cycles=max_cycles))
        return scheduler, task


if __name__ == "__main__":
    # Demo: Run 1 cycle with shortened durations for testing
    async def demo():
        scheduler = PulseScheduler(
            cycle_duration=60.0,  # 1 minute total
            harvest_duration=20.0,
            process_duration=15.0,
            archive_duration=10.0,
            hibernation_duration=15.0,
        )
        
        await scheduler.run_continuous(max_cycles=1)
        
        print("\n" + "="*60)
        print("DEMO COMPLETE - Final Metrics:")
        print("="*60)
        for key, value in scheduler.get_metrics().items():
            print(f"  {key}: {value}")
    
    asyncio.run(demo())
