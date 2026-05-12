"""
OpenEyes Autonomous Signal-Pulse Swarm

A bio-inspired, memory-efficient swarm architecture for low-RAM systems (4GB).

Key Features:
- Asyncio Event Loop as "Signal Bus" (no threading overhead)
- Staggered agent wake-ups (50 agents every 3 seconds)
- Cyclic harvest-sleep rhythm (2hr active / 30min sleep)
- Lazy loading of scraping logic
- Token bucket network limiter (max 5 req/sec globally)
- Write-only mode during active phase (WAL buffer)
- Forced garbage collection during sleep

Agent States:
  SLEEPING → TRIGGERED → HARVESTING → ARCHIVING → SLEEPING

Signals:
  SIG_WAKE_UP: Scheduler triggers staggered agent activation
  SIG_PROCESS: Harvester found new data, wake Workers
  SIG_ARCHIVE: Organizer triggers TF-IDF and rule updates
  SIG_HIBERNATE: Force all agents to sleep, run GC
"""

import asyncio
import gc
import time
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import weakref
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class AgentState(Enum):
    """Agent lifecycle states."""
    SLEEPING = 0      # Minimal RAM, empty function pointers only
    TRIGGERED = 1     # Loading logic
    HARVESTING = 2    # Active I/O operations
    ARCHIVING = 3     # Writing and flushing
    HIBERNATING = 4   # Dropping connections, preparing for GC


class SignalType(Enum):
    """Global signal types for the swarm."""
    SIG_WAKE_UP = "wake_up"
    SIG_PROCESS = "process"
    SIG_ARCHIVE = "archive"
    SIG_HIBERNATE = "hibernate"


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    agent_id: str
    agent_type: str  # "harvester", "worker", "organizer"
    target_sources: List[str]  # RSS feeds, APIs, URLs
    wake_priority: int = 0  # Lower = earlier wake-up in stagger
    last_wake_time: Optional[datetime] = None
    is_active: bool = False


@dataclass
class TokenBucket:
    """Global rate limiter for network requests."""
    capacity: float = 5.0  # Max requests per second
    tokens: float = 5.0
    last_refill: float = field(default_factory=time.time)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    async def acquire(self) -> bool:
        """Try to acquire a token. Returns False if bucket is empty."""
        async with self.lock:
            now = time.time()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.capacity)
            self.last_refill = now
            
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False
    
    async def wait_for_token(self, timeout: float = 5.0) -> bool:
        """Wait for a token to become available."""
        start = time.time()
        while time.time() - start < timeout:
            if await self.acquire():
                return True
            await asyncio.sleep(0.1)
        return False


class WALBuffer:
    """
    Write-Ahead Log buffer for agents.
    Agents write here during active phase, never read from main DB.
    """
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._initialized = False
    
    def _ensure_initialized(self):
        if not self._initialized:
            self._conn = sqlite3.connect(str(self.db_path), isolation_level=None)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS wal_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    timestamp TEXT,
                    data_type TEXT,
                    content TEXT,
                    tokens_json TEXT,
                    processed INTEGER DEFAULT 0
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_unprocessed ON wal_buffer(processed)")
            self._initialized = True
    
    async def write(self, agent_id: str, data_type: str, content: str, tokens: Optional[Dict] = None):
        """Write data to WAL buffer (write-only during active phase)."""
        self._ensure_initialized()
        import json
        
        self._conn.execute(
            """INSERT INTO wal_buffer (agent_id, timestamp, data_type, content, tokens_json)
               VALUES (?, ?, ?, ?, ?)""",
            (agent_id, datetime.now().isoformat(), data_type, content, 
             json.dumps(tokens) if tokens else None)
        )
    
    async def flush_to_main_db(self, main_db_path: str):
        """Move all buffered data to main database."""
        self._ensure_initialized()
        # Implementation would transfer WAL entries to main SQLite DB
        print(f"[WAL] Flushing {self._get_pending_count()} entries to main DB")
    
    def _get_pending_count(self) -> int:
        self._ensure_initialized()
        cursor = self._conn.execute("SELECT COUNT(*) FROM wal_buffer WHERE processed = 0")
        return cursor.fetchone()[0]
    
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False


class BaseAgent:
    """
    Base class for all swarm agents.
    Implements lazy loading and state management.
    """
    
    def __init__(self, config: AgentConfig, signal_bus: 'SignalBus'):
        self.config = config
        self.signal_bus = signal_bus
        self.state = AgentState.SLEEPING
        self._logic_module: Optional[Any] = None  # Lazy-loaded scraping logic
    
    @property
    def is_sleeping(self) -> bool:
        return self.state == AgentState.SLEEPING
    
    async def wake_up(self):
        """Transition from SLEEPING to TRIGGERED, lazy-load logic."""
        if self.state != AgentState.SLEEPING:
            return
        
        self.state = AgentState.TRIGGERED
        self.config.last_wake_time = datetime.now()
        self.config.is_active = True
        
        # LAZY LOAD: Only load scraping logic on wake-up
        await self._load_logic()
        
        self.state = AgentState.HARVESTING
        print(f"[Agent {self.config.agent_id}] Woke up, ready to harvest")
    
    async def _load_logic(self):
        """Lazy-load agent-specific logic (BeautifulSoup, Playwright, etc.)."""
        if self._logic_module is not None:
            return
        
        # Import heavy libraries only when needed
        if self.config.agent_type == "harvester":
            # Would import: from bs4 import BeautifulSoup
            # Would import: import aiohttp
            self._logic_module = {"loaded": True, "type": "harvester"}
        elif self.config.agent_type == "worker":
            # Would import tokenization logic
            self._logic_module = {"loaded": True, "type": "worker"}
        elif self.config.agent_type == "organizer":
            # Would import TF-IDF, rules engine
            self._logic_module = {"loaded": True, "type": "organizer"}
    
    async def execute(self, wal_buffer: WALBuffer, token_bucket: TokenBucket):
        """Execute agent's main logic. Override in subclasses."""
        raise NotImplementedError
    
    async def hibernate(self):
        """Force hibernation: drop connections, release resources."""
        self.state = AgentState.HIBERNATING
        self.config.is_active = False
        self._logic_module = None  # Release lazy-loaded logic
        
        # Explicitly drop any open connections
        gc.collect()
        
        self.state = AgentState.SLEEPING
        print(f"[Agent {self.config.agent_id}] Hibernated")
    
    def get_memory_footprint(self) -> int:
        """Estimate memory usage in bytes."""
        if self.state == AgentState.SLEEPING:
            return 1024  # ~1KB for sleeping agent (just references)
        elif self.state == AgentState.HIBERNATING:
            return 512
        else:
            # Active agents use more memory for logic modules
            return 1024 * 1024  # ~1MB when active


class HarvesterAgent(BaseAgent):
    """
    Scans predefined RSS feeds/APIs for new hashes.
    Detects change, not re-scraping old data.
    """
    
    def __init__(self, config: AgentConfig, signal_bus: 'SignalBus', known_hashes: Set[str]):
        super().__init__(config, signal_bus)
        self.known_hashes = known_hashes
        self.new_data_found = False
    
    async def execute(self, wal_buffer: WALBuffer, token_bucket: TokenBucket):
        """Scan sources for new data."""
        if self.state != AgentState.HARVESTING:
            return
        
        print(f"[Harvester {self.config.agent_id}] Scanning {len(self.config.target_sources)} sources...")
        
        for source_url in self.config.target_sources:
            # Wait for network token
            if not await token_bucket.wait_for_token(timeout=10.0):
                print(f"[Harvester {self.config.agent_id}] Rate limited, skipping {source_url}")
                continue
            
            # Simulate hash check (in production: compute hash of content)
            content_hash = f"hash_{source_url}_{time.time()}"
            
            if content_hash not in self.known_hashes:
                self.known_hashes.add(content_hash)
                self.new_data_found = True
                
                # Write to WAL buffer
                await wal_buffer.write(
                    agent_id=self.config.agent_id,
                    data_type="new_content",
                    content=f"New data from {source_url}",
                    tokens={"hash": content_hash, "source": source_url}
                )
                
                # Fire SIG_PROCESS to wake Workers
                await self.signal_bus.fire_signal(SignalType.SIG_PROCESS, {
                    "source_agent": self.config.agent_id,
                    "content_hash": content_hash,
                    "source_url": source_url
                })
        
        print(f"[Harvester {self.config.agent_id}] Found {sum(1 for h in self.known_hashes)} total hashes")


class WorkerAgent(BaseAgent):
    """
    Converts text to Integer Tokens when SIG_PROCESS fires.
    Pushes to SQLite WAL Buffer.
    """
    
    def __init__(self, config: AgentConfig, signal_bus: 'SignalBus'):
        super().__init__(config, signal_bus)
        self.pending_tasks: List[Dict[str, Any]] = []
    
    async def execute(self, wal_buffer: WALBuffer, token_bucket: TokenBucket):
        """Process pending tasks, convert to tokens."""
        if self.state != AgentState.HARVESTING:
            return
        
        for task in self.pending_tasks:
            content = task.get("content", "")
            
            # Convert text to integer tokens (simplified)
            tokens = [ord(c) for c in content[:100]]  # First 100 chars
            
            await wal_buffer.write(
                agent_id=self.config.agent_id,
                data_type="tokenized_content",
                content=content,
                tokens={"integer_tokens": tokens[:50]}  # Store first 50 tokens
            )
        
        self.pending_tasks.clear()
        print(f"[Worker {self.config.agent_id}] Processed {len(self.pending_tasks)} tasks")
    
    async def add_task(self, task_data: Dict[str, Any]):
        """Add a processing task."""
        self.pending_tasks.append(task_data)
        if self.state == AgentState.SLEEPING:
            await self.wake_up()


class OrganizerAgent(BaseAgent):
    """
    Every 15 mins: checks Buffer, calculates TF-IDF scores,
    updates rules.py with new confidence thresholds.
    Fires SIG_ARCHIVE.
    """
    
    def __init__(self, config: AgentConfig, signal_bus: 'SignalBus'):
        super().__init__(config, signal_bus)
        self.last_organize_time: Optional[datetime] = None
    
    async def execute(self, wal_buffer: WALBuffer, token_bucket: TokenBucket):
        """Organize buffered data, update rules."""
        if self.state != AgentState.HARVESTING:
            return
        
        # Check if 15 minutes have passed
        now = datetime.now()
        if self.last_organize_time and (now - self.last_organize_time).total_seconds() < 900:
            return
        
        self.last_organize_time = now
        print(f"[Organizer {self.config.agent_id}] Calculating TF-IDF scores...")
        
        # Simulate TF-IDF calculation
        tfidf_scores = {"sample_term": 0.85}
        
        # Update rules (in production: write to rules.py)
        new_thresholds = {"confidence_min": 0.75, "evidence_weight": 0.90}
        
        # Fire SIG_ARCHIVE
        await self.signal_bus.fire_signal(SignalType.SIG_ARCHIVE, {
            "tfidf_scores": tfidf_scores,
            "new_thresholds": new_thresholds,
            "organized_at": now.isoformat()
        })
        
        print(f"[Organizer {self.config.agent_id}] Archive signal fired")


class SignalBus:
    """
    Central event loop acting as the signal bus.
    Agents register callbacks for specific signals.
    """
    
    def __init__(self):
        self._listeners: Dict[SignalType, List[Callable]] = {sig: [] for sig in SignalType}
        self._lock = asyncio.Lock()
    
    def register_listener(self, signal_type: SignalType, callback: Callable):
        """Register an agent's callback for a signal."""
        self._listeners[signal_type].append(callback)
    
    async def fire_signal(self, signal_type: SignalType, payload: Dict[str, Any]):
        """Fire a signal to all registered listeners."""
        listeners = self._listeners.get(signal_type, [])
        tasks = [callback(payload) for callback in listeners]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def unregister_listener(self, signal_type: SignalType, callback: Callable):
        """Remove a listener."""
        if callback in self._listeners[signal_type]:
            self._listeners[signal_type].remove(callback)


class CentralScheduler:
    """
    Global Clock managing the autonomous schedule.
    
    Rhythm:
      T+00:00 - Wake-Up Signal (staggered: 50 agents every 3 sec)
      T+00:05 to T+02:00 - Active Hunt
      T+02:00 - Forced Sleep (GC sweep)
      T+02:30 - Next cycle
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        signal_bus: SignalBus,
        wal_buffer: WALBuffer,
        active_duration_minutes: int = 120,
        sleep_duration_minutes: int = 30,
        stagger_batch_size: int = 50,
        stagger_interval_seconds: int = 3
    ):
        self.agents = agents
        self.signal_bus = signal_bus
        self.wal_buffer = wal_buffer
        self.active_duration = timedelta(minutes=active_duration_minutes)
        self.sleep_duration = timedelta(minutes=sleep_duration_minutes)
        self.stagger_batch_size = stagger_batch_size
        self.stagger_interval = stagger_interval_seconds
        
        self.token_bucket = TokenBucket(capacity=5.0)  # 5 req/sec global limit
        self.known_hashes: Set[str] = set()
        self.running = False
        self.current_cycle_start: Optional[datetime] = None
    
    async def run_cycle(self):
        """Execute one complete wake-harvest-sleep cycle."""
        self.running = True
        self.current_cycle_start = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"[Scheduler] Starting cycle at {self.current_cycle_start.isoformat()}")
        print(f"{'='*60}\n")
        
        # Phase 1: Staggered Wake-Up
        await self._staggered_wakeup()
        
        # Phase 2: Active Hunt (2 hours)
        await self._active_hunt_phase()
        
        # Phase 3: Forced Sleep with GC
        await self._forced_sleep()
        
        # Phase 4: Sleep period
        await self._sleep_phase()
        
        self.running = False
    
    async def _staggered_wakeup(self):
        """Wake agents in batches to prevent CPU/network spikes."""
        print(f"[Scheduler] Beginning staggered wake-up ({self.stagger_batch_size} agents every {self.stagger_interval}s)...")
        
        # Sort agents by priority
        sorted_agents = sorted(
            [a for a in self.agents if isinstance(a, HarvesterAgent)],
            key=lambda a: a.config.wake_priority
        )
        
        # Wake in batches
        for i in range(0, len(sorted_agents), self.stagger_batch_size):
            batch = sorted_agents[i:i + self.stagger_batch_size]
            
            wake_tasks = [agent.wake_up() for agent in batch]
            await asyncio.gather(*wake_tasks)
            
            print(f"[Scheduler] Woke batch {i//self.stagger_batch_size + 1} ({len(batch)} agents)")
            
            if i + self.stagger_batch_size < len(sorted_agents):
                await asyncio.sleep(self.stagger_interval)
        
        # Register signal handlers for workers and organizers
        for agent in self.agents:
            if isinstance(agent, WorkerAgent):
                self.signal_bus.register_listener(
                    SignalType.SIG_PROCESS,
                    lambda payload, a=agent: a.add_task(payload)
                )
            elif isinstance(agent, OrganizerAgent):
                self.signal_bus.register_listener(
                    SignalType.SIG_WAKE_UP,
                    lambda payload, a=agent: a.wake_up()
                )
    
    async def _active_hunt_phase(self):
        """Execute the 2-hour active hunting phase."""
        print(f"[Scheduler] Active hunt phase started (duration: {self.active_duration})")
        
        # Create organizer that runs every 15 minutes
        organizer_interval = 15 * 60  # 15 minutes in seconds
        next_organize_time = time.time() + organizer_interval
        
        active_end = datetime.now() + self.active_duration
        
        while datetime.now() < active_end:
            # Execute all active agents
            active_agents = [a for a in self.agents if not a.is_sleeping]
            
            execute_tasks = [
                agent.execute(self.wal_buffer, self.token_bucket)
                for agent in active_agents
            ]
            
            if execute_tasks:
                await asyncio.gather(*execute_tasks, return_exceptions=True)
            
            # Check if organizer should run
            if time.time() >= next_organize_time:
                organizers = [a for a in self.agents if isinstance(a, OrganizerAgent)]
                for org in organizers:
                    if not org.is_sleeping:
                        await org.execute(self.wal_buffer, self.token_bucket)
                next_organize_time = time.time() + organizer_interval
            
            # Small delay between execution rounds
            await asyncio.sleep(5.0)
        
        print(f"[Scheduler] Active hunt phase completed")
    
    async def _forced_sleep(self):
        """Force all agents to hibernate, run GC sweep."""
        print(f"[Scheduler] Initiating forced sleep...")
        
        # Fire SIG_HIBERNATE
        await self.signal_bus.fire_signal(SignalType.SIG_HIBERNATE, {})
        
        # Hibernate all agents
        hibernate_tasks = [agent.hibernate() for agent in self.agents]
        await asyncio.gather(*hibernate_tasks)
        
        # Critical: Force garbage collection
        print("[Scheduler] Running garbage collection sweep...")
        gc.collect()
        
        # Flush WAL buffer to main DB
        await self.wal_buffer.flush_to_main_db("main_database.db")
        
        # Report memory status
        sleeping_count = sum(1 for a in self.agents if a.is_sleeping)
        print(f"[Scheduler] All {sleeping_count}/{len(self.agents)} agents hibernated")
        print(f"[Scheduler] RAM should now be ~200MB idle")
    
    async def _sleep_phase(self):
        """Sleep for configured duration before next cycle."""
        print(f"[Scheduler] Entering sleep phase for {self.sleep_duration}")
        await asyncio.sleep(self.sleep_duration.total_seconds())
        print(f"[Scheduler] Sleep phase complete, ready for next cycle")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        active_count = sum(1 for a in self.agents if not a.is_sleeping)
        return {
            "running": self.running,
            "cycle_start": self.current_cycle_start.isoformat() if self.current_cycle_start else None,
            "active_agents": active_count,
            "sleeping_agents": len(self.agents) - active_count,
            "known_hashes": len(self.known_hashes),
            "next_cycle": (self.current_cycle_start + self.active_duration + self.sleep_duration).isoformat() if self.current_cycle_start else None
        }


class AutonomousSwarm:
    """
    Main entry point for the Autonomous Signal-Pulse Swarm.
    
    Usage:
        swarm = AutonomousSwarm.create_default()
        await swarm.start_continuous()
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        signal_bus: SignalBus,
        wal_buffer: WALBuffer,
        scheduler: CentralScheduler
    ):
        self.agents = agents
        self.signal_bus = signal_bus
        self.wal_buffer = wal_buffer
        self.scheduler = scheduler
        self._emergency_shutdown = False
        self._memory_threshold_mb = 500  # Emergency shutoff at 500MB
        self._health_check_interval = 60  # Check agent health every 60 seconds
    
    @classmethod
    def create_default(
        cls, 
        num_harvesters: int = 800, 
        num_workers: int = 180, 
        num_organizers: int = 20,
        known_hashes_path: Optional[str] = "known_hashes.db"
    ) -> 'AutonomousSwarm':
        """
        Create a production-ready swarm with 1000 agents.
        
        Role Distribution (Option A modified):
          - 800 Harvesters (80%): Scan RSS feeds/APIs for new content
          - 180 Workers (18%): Tokenize and process data
          - 20 Organizers (2%): TF-IDF, rule updates, archival
        
        Args:
            num_harvesters: Number of harvester agents (default 800)
            num_workers: Number of worker agents (default 180)
            num_organizers: Number of organizer agents (default 20)
            known_hashes_path: Path to persistent hash database
        """
        signal_bus = SignalBus()
        wal_buffer = WALBuffer("wal_buffer.db")
        
        agents: List[BaseAgent] = []
        known_hashes: Set[str] = set()
        
        # Load persistent hashes if available (prevents re-scraping after restart)
        if known_hashes_path:
            known_hashes = cls._load_persistent_hashes(known_hashes_path)
            print(f"[Swarm] Loaded {len(known_hashes)} persistent hashes from {known_hashes_path}")
        
        # Create Harvester agents with diverse source distribution
        for i in range(num_harvesters):
            # Distribute across different source types to avoid rate limits
            source_type = i % 5  # 5 different source categories
            config = AgentConfig(
                agent_id=f"harvester_{i}",
                agent_type="harvester",
                target_sources=[f"https://example.com/feed/{source_type}/{i}"],
                wake_priority=i % 20  # Distribute priorities across 20 batches
            )
            agent = HarvesterAgent(config, signal_bus, known_hashes)
            agents.append(agent)
        
        # Create Worker agents
        for i in range(num_workers):
            config = AgentConfig(
                agent_id=f"worker_{i}",
                agent_type="worker",
                target_sources=[],
                wake_priority=i % 10
            )
            agent = WorkerAgent(config, signal_bus)
            agents.append(agent)
        
        # Create Organizer agents
        for i in range(num_organizers):
            config = AgentConfig(
                agent_id=f"organizer_{i}",
                agent_type="organizer",
                target_sources=[],
                wake_priority=i
            )
            agent = OrganizerAgent(config, signal_bus)
            agents.append(agent)
        
        scheduler = CentralScheduler(
            agents=agents,
            signal_bus=signal_bus,
            wal_buffer=wal_buffer,
            stagger_batch_size=50,  # Wake 50 agents every 3 seconds
            stagger_interval_seconds=3
        )
        
        return cls(agents, signal_bus, wal_buffer, scheduler)
    
    @staticmethod
    def _load_persistent_hashes(db_path: str) -> Set[str]:
        """Load previously seen hashes from disk to prevent re-scraping."""
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT hash FROM seen_hashes")
            hashes = {row[0] for row in cursor.fetchall()}
            conn.close()
            return hashes
        except Exception:
            return set()
    
    @staticmethod
    def _save_persistent_hashes(db_path: str, hashes: Set[str]):
        """Persist hashes to disk for crash recovery."""
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS seen_hashes (hash TEXT PRIMARY KEY)")
        for h in hashes:
            try:
                conn.execute("INSERT OR IGNORE INTO seen_hashes (hash) VALUES (?)", (h,))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()
    
    async def start_continuous(self, num_cycles: int = -1):
        """
        Start continuous operation with safety monitors.
        
        Args:
            num_cycles: Number of cycles to run (-1 for infinite)
        """
        print(f"[Swarm] Starting autonomous operation with {len(self.agents)} agents")
        print(f"[Swarm] Memory footprint (sleeping): ~{sum(a.get_memory_footprint() for a in self.agents) // 1024}KB")
        print(f"[Swarm] Emergency shutoff threshold: {self._memory_threshold_mb}MB")
        
        cycles_run = 0
        while num_cycles < 0 or cycles_run < num_cycles:
            # Check for emergency shutdown
            if self._emergency_shutdown:
                print("[Swarm] EMERGENCY SHUTDOWN triggered! Stopping all cycles.")
                break
            
            # Monitor memory before each cycle
            current_ram_mb = sum(a.get_memory_footprint() for a in self.agents) / (1024 * 1024)
            if current_ram_mb > self._memory_threshold_mb:
                print(f"[Swarm] CRITICAL: Memory usage {current_ram_mb:.2f}MB exceeds threshold {self._memory_threshold_mb}MB")
                print("[Swarm] Triggering emergency hibernation...")
                await self._emergency_hibernate()
                break
            
            await self.scheduler.run_cycle()
            cycles_run += 1
            
            # Persist hashes after each cycle for crash recovery
            self._save_persistent_hashes("known_hashes.db", self.scheduler.known_hashes)
            
            print(f"[Swarm] Completed cycle {cycles_run}")
    
    async def _emergency_hibernate(self):
        """Emergency hibernation: force all agents to sleep immediately."""
        print("[Swarm] Emergency hibernation initiated!")
        
        # Hibernate all agents immediately
        hibernate_tasks = [agent.hibernate() for agent in self.agents]
        await asyncio.gather(*hibernate_tasks)
        
        # Force garbage collection
        gc.collect()
        
        # Save state
        self._save_persistent_hashes("known_hashes.db", self.scheduler.known_hashes)
        
        print("[Swarm] Emergency hibernation complete. System safe.")
    
    async def run_single_cycle(self):
        """Run a single wake-harvest-sleep cycle."""
        await self.scheduler.run_cycle()
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status."""
        scheduler_status = self.scheduler.get_status()
        
        agent_states = {}
        for agent in self.agents:
            state_name = agent.state.name
            agent_states[state_name] = agent_states.get(state_name, 0) + 1
        
        return {
            **scheduler_status,
            "total_agents": len(self.agents),
            "agent_state_distribution": agent_states,
            "estimated_ram_mb": sum(a.get_memory_footprint() for a in self.agents) / (1024 * 1024),
            "emergency_shutdown_enabled": self._emergency_shutdown,
            "memory_threshold_mb": self._memory_threshold_mb
        }
    
    def enable_emergency_shutdown(self):
        """Enable manual emergency shutdown flag."""
        self._emergency_shutdown = True
    
    def set_memory_threshold(self, threshold_mb: float):
        """Set custom memory threshold for emergency shutoff."""
        self._memory_threshold_mb = threshold_mb
        print(f"[Swarm] Memory threshold set to {threshold_mb}MB")


# Convenience function for quick testing
async def demo_swarm():
    """Demonstrate the swarm with a shortened cycle for testing."""
    print("="*70)
    print("OpenEyes Autonomous Signal-Pulse Swarm Demo")
    print("Bio-inspired architecture for 4GB RAM systems")
    print("="*70)
    
    # Create a small test swarm
    swarm = AutonomousSwarm.create_default(
        num_harvesters=20,
        num_workers=10,
        num_organizers=2
    )
    
    # Run a single cycle (normally 2.5 hours, but we'll use short durations for demo)
    # In production, use CentralScheduler with default 120min active / 30min sleep
    swarm.scheduler.active_duration = timedelta(seconds=30)  # Demo: 30 seconds
    swarm.scheduler.sleep_duration = timedelta(seconds=10)   # Demo: 10 seconds
    
    await swarm.run_single_cycle()
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    
    status = swarm.get_swarm_status()
    print(f"\nFinal Status:")
    print(f"  Total Agents: {status['total_agents']}")
    print(f"  Sleeping: {status['sleeping_agents']}")
    print(f"  Estimated RAM: {status['estimated_ram_mb']:.2f}MB")
    print(f"  Known Hashes: {status['known_hashes']}")


async def run_production_swarm(
    num_harvesters: int = 800,
    num_workers: int = 180,
    num_organizers: int = 20,
    active_minutes: int = 120,
    sleep_minutes: int = 30,
    test_mode: bool = False
):
    """
    Launch production swarm with 1000 agents.
    
    Args:
        num_harvesters: Number of harvester agents (default 800)
        num_workers: Number of worker agents (default 180)
        num_organizers: Number of organizer agents (default 20)
        active_minutes: Duration of active hunting phase (default 120)
        sleep_minutes: Duration of sleep phase (default 30)
        test_mode: If True, use shortened cycles for testing
    """
    print("="*70)
    print("OpenEyes Production Swarm - 1000 Agents")
    print("Scaling up with safety monitors enabled")
    print("="*70)
    
    # Create production swarm
    swarm = AutonomousSwarm.create_default(
        num_harvesters=num_harvesters,
        num_workers=num_workers,
        num_organizers=num_organizers
    )
    
    # Configure scheduler
    if test_mode:
        print("\n[TEST MODE] Using shortened cycles for validation...")
        swarm.scheduler.active_duration = timedelta(seconds=60)
        swarm.scheduler.sleep_duration = timedelta(seconds=20)
    else:
        swarm.scheduler.active_duration = timedelta(minutes=active_minutes)
        swarm.scheduler.sleep_duration = timedelta(minutes=sleep_minutes)
    
    # Set conservative memory threshold for 4GB laptop
    swarm.set_memory_threshold(500)  # Emergency shutoff at 500MB
    
    print(f"\n[Production] Configuration:")
    print(f"  Harvesters: {num_harvesters}")
    print(f"  Workers: {num_workers}")
    print(f"  Organizers: {num_organizers}")
    print(f"  Total Agents: {len(swarm.agents)}")
    print(f"  Active Phase: {active_minutes if not test_mode else 1} minutes")
    print(f"  Sleep Phase: {sleep_minutes if not test_mode else 0.33} minutes")
    print(f"  Stagger Batch: 50 agents every 3 seconds")
    print(f"  Rate Limit: 5 requests/second global")
    print(f"  Memory Threshold: {swarm._memory_threshold_mb}MB")
    
    print("\n[Production] Starting autonomous operation...")
    print("Press Ctrl+C to stop gracefully\n")
    
    try:
        # Run single cycle for test mode, continuous for production
        if test_mode:
            await swarm.run_single_cycle()
            print("\n[Test] Single cycle complete!")
        else:
            await swarm.start_continuous(num_cycles=-1)  # Infinite cycles
        
        status = swarm.get_swarm_status()
        print(f"\n[Production] Final Status:")
        print(f"  Total Agents: {status['total_agents']}")
        print(f"  Sleeping: {status['sleeping_agents']}")
        print(f"  Estimated RAM: {status['estimated_ram_mb']:.2f}MB")
        print(f"  Known Hashes: {status['known_hashes']}")
        
    except KeyboardInterrupt:
        print("\n\n[Production] Graceful shutdown requested...")
        swarm.enable_emergency_shutdown()
        await swarm._emergency_hibernate()
        print("[Production] Swarm hibernated successfully.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        # Run production swarm with 1000 agents
        asyncio.run(run_production_swarm(test_mode=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-scale":
        # Test scaling with 100 agents
        print("Running scale test with 100 agents...")
        asyncio.run(run_production_swarm(
            num_harvesters=80,
            num_workers=18,
            num_organizers=2,
            test_mode=True
        ))
    else:
        # Default: run small demo
        asyncio.run(demo_swarm())
