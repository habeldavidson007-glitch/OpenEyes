"""
OpenEyes Control Deck - High-Stakes Reasoning Terminal UI

A specialized, hyper-responsive TUI modeled after Claude Code.
Provides real-time visibility into decomposition, swarm evaluation, and halt triggers.
Uses pure ANSI escape codes for zero-dependency efficiency.

UPDATED: Integrated with Unified Orchestrator for cascading retrieval visualization,
source credibility indicators, adaptive confidence meters, and cross-domain fusion status.
"""

import sys
import time
from typing import Optional, List, Dict, Any
from datetime import datetime


class ControlDeck:
    """
    The OpenEyes "Control Deck" Terminal UI.
    
    Features:
    - Inline live progress spinners with in-place line overwriting
    - Color-coded status thresholds (Green/Yellow/Red)
    - Collapsible interactive audit streams
    - Real-time fragment isolation and swarm iteration visualization
    - Prominent HALT alarms with precise trace logs
    - NEW: Unified Orchestrator cascade visualization (Cache → DB → API → Fallback)
    - NEW: Source credibility indicators (HIGH/MEDIUM/LOW/UNVERIFIED)
    - NEW: Adaptive confidence meter with base vs adjusted scores
    - NEW: Cross-domain fusion status indicator
    - NEW: Live metrics side panel (latency, cache hits, fragment counts)
    - NEW: Interactive feedback loop (thumbs up/down)
    """
    
    # ANSI Color Codes
    COLORS = {
        'RESET': '\033[0m',
        'BOLD': '\033[1m',
        'DIM': '\033[2m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
        'BG_RED': '\033[41m',
        'BG_YELLOW': '\033[43m',
        'BG_BLUE': '\033[44m',
        'BG_GREEN': '\033[42m',
    }
    
    # Credibility Level Colors
    CREDIBILITY_COLORS = {
        'HIGH': 'GREEN',
        'MEDIUM': 'BLUE',
        'LOW': 'YELLOW',
        'UNVERIFIED': 'RED'
    }
    
    # Progress Bar Characters
    BAR_FULL = '█'
    BAR_EMPTY = '░'
    SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, width: int = 80):
        """
        Initialize the Control Deck.
        
        Args:
            width: Terminal width for progress bars (default: 80)
        """
        self.width = width
        self.audit_logs: List[Dict[str, Any]] = []
        self.current_step: Optional[str] = None
        self.start_time: Optional[float] = None
        self._spinner_index = 0
        self._last_render_time = 0
        
        # New unified system state
        self.cascade_stage: str = "IDLE"
        self.credibility_sources: List[Dict[str, Any]] = []
        self.base_confidence: float = 0.0
        self.adjusted_confidence: float = 0.0
        self.cross_domain_active: bool = False
        self.domains_involved: List[str] = []
        self.metrics: Dict[str, Any] = {}
        
    def _color(self, text: str, color: str) -> str:
        """Apply ANSI color to text."""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['RESET']}"
    
    def _clear_line(self) -> str:
        """Return ANSI code to clear current line."""
        return '\033[K'
    
    def _move_cursor_up(self, lines: int = 1) -> str:
        """Return ANSI code to move cursor up."""
        return f'\033[{lines}A'
    
    def _get_elapsed_time(self) -> float:
        """Get elapsed time since start."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def render_header(self) -> None:
        """Render the OpenEyes Control Deck header."""
        header = self._color("👁️  OPENEYES :: HIGH-STAKES REASONING ENGINE", 'BOLD')
        border = "─" * self.width
        
        print(f"\n┌{border}┐")
        print(f"│ {header:<{self.width-2}} │")
        print(f"└{border}┘")
        print()
        
    def render_query(self, query: str) -> None:
        """Render the user query."""
        query_label = self._color("> Query:", 'CYAN')
        print(f"  {query_label} \"{query[:100]}{'...' if len(query) > 100 else ''}\"")
        print()
        
    def _render_progress_bar(self, step_name: str, progress: float, status: str, 
                            color: str = 'BLUE', show_spinner: bool = False) -> None:
        """
        Render a single progress line with bar and status.
        
        Args:
            step_name: Name of the current step
            progress: Progress percentage (0.0 to 1.0)
            status: Current status text
            color: Color code for the step indicator
            show_spinner: Whether to show animated spinner
        """
        # Calculate bar dimensions
        bar_width = 20
        filled = int(bar_width * progress)
        empty = bar_width - filled
        
        # Build progress bar
        bar = self.BAR_FULL * filled + self.BAR_EMPTY * empty
        
        # Get spinner frame if needed
        spinner = ""
        if show_spinner and progress < 1.0:
            spinner = f"{self.SPINNER_FRAMES[self._spinner_index % len(self.SPINNER_FRAMES)]} "
            self._spinner_index += 1
            
        # Format status with color
        status_colored = self._color(status, color)
        
        # Build the line
        line = f"  {spinner}{self._color('●', color)} {step_name:<20} [{bar}] {progress*100:5.1f}% ──► {status_colored}"
        
        # Clear line and print
        sys.stdout.write(f"\r{self._clear_line()}{line}")
        sys.stdout.flush()
        self._last_render_time = time.time()
        
    def update_step(self, step_name: str, status: str, color: str = 'BLUE', progress: Optional[float] = None) -> None:
        """
        Update a processing step with status.
        
        Args:
            step_name: Name of the step
            status: Status message (e.g., "PROCESSING...", "14 FRAGMENTS ✓")
            color: Color for the step indicator
            progress: Optional progress (0.0-1.0). Auto-calculated if status contains percentage
        """
        # Auto-detect progress from status or use provided value
        if progress is None:
            if "✓" in status or "100%" in status:
                progress = 1.0
            elif "PROCESSING" in status.upper() or "SEARCHING" in status.upper() or "RUNNING" in status.upper():
                progress = 0.5
            else:
                progress = 0.0
        
        show_spinner = progress < 1.0
        self._render_progress_bar(step_name, progress, status, color, show_spinner)
        
        if progress >= 1.0:
            print()  # Move to next line when complete
            
    def start_session(self, query: str, domain: str = "auto") -> None:
        """
        Start a new reasoning session.
        
        Args:
            query: The user query to process
            domain: The domain context (default: "auto")
        """
        self.render_header()
        self.render_query(query)
        self.start_time = time.time()
        self.audit_logs = []
        
    def log_audit(self, message: str, level: str = "INFO") -> None:
        """
        Add an audit log entry.
        
        Args:
            message: Log message
            level: Log level (INFO, WARN, ERROR, HALT) - defaults to INFO
        """
        timestamp = self._get_elapsed_time()
            
        self.audit_logs.append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })
        
    def render_audit_log(self, expanded: bool = True) -> None:
        """
        Render the audit log stream.
        
        Args:
            expanded: If True, show all logs; if False, show only critical
        """
        if not self.audit_logs:
            return
            
        print()
        audit_header = self._color("[LIVE AUDIT LOG]", 'DIM')
        print(f"  {audit_header}")
        
        for log in self.audit_logs:
            # Skip non-critical if not expanded
            if not expanded and log['level'] not in ['WARN', 'ERROR', 'HALT']:
                continue
                
            # Color code by level
            level_colors = {
                'INFO': 'DIM',
                'WARN': 'YELLOW',
                'ERROR': 'RED',
                'HALT': 'BG_RED'
            }
            
            level_str = f"[{log['level']}]"
            level_colored = self._color(level_str, level_colors.get(log['level'], 'DIM'))
            time_str = f"[{log['timestamp']:.2f}s]"
            
            print(f"    ├── {time_str} {level_colored} {log['message']}")
            
    def render_halt(self, halt_code: str, reason: str, vault_path: Optional[str] = None) -> None:
        """
        Render a prominent HALT alarm.
        
        Args:
            halt_code: The HALT code (e.g., HALT_CONTRADICTION_DETECTED)
            reason: Human-readable reason for the halt
            vault_path: Optional path to the audit vault transaction
        """
        print()
        border = "─" * self.width
        
        # Red background halt banner
        halt_banner = self._color(f" 🛑 ENGINE EXECUTION HALTED: {halt_code} ", 'BG_RED')
        halt_banner = halt_banner.ljust(self.width + 24)  # Account for ANSI codes
        print(f"  {halt_banner}")
        print()
        
        # Reason
        reason_label = self._color("Reason:", 'RED')
        print(f"  {reason_label} {reason}")
        print()
        
        # Vault reference
        if vault_path:
            vault_label = self._color("🔒 Transaction locked in Audit Vault:", 'DIM')
            print(f"  {vault_label} {vault_path}")
            print()
            
        # Show audit logs expanded on halt
        self.render_audit_log(expanded=True)
        print(f"\n  └{border}┘")
        
    def render_success(self, answer_class: str, answer: str, confidence, 
                      data_recency: int = 0, vault_path: Optional[str] = None) -> None:
        """
        Render a successful answer completion.
        
        Args:
            answer_class: The ANSWER class (e.g., ANSWER_CONFIDENT)
            answer: The generated answer text
            confidence: Confidence score (float or string representation)
            data_recency: Data recency in years
            vault_path: Optional path to the audit vault transaction
        """
        print()
        border = "─" * self.width
        
        # Ensure confidence is a float
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except ValueError:
                confidence = 0.0
        
        # Green success banner
        confidence_pct = float(confidence)
        success_banner = self._color(f" ✓ ANSWER GENERATED: {answer_class} ({confidence_pct:.1f}% confidence) ", 'GREEN')
        success_banner = success_banner.ljust(self.width + 24)
        print(f"  {success_banner}")
        print()
        
        # Details
        details = [
            (f"Answer Length:", f"{len(answer)} characters"),
            (f"Execution Time:", f"{self._get_elapsed_time():.3f}s"),
            (f"Confidence Score:", f"{confidence_pct:.1f}%"),
            (f"Data Recency:", f"{data_recency} years")
        ]
        
        for label, value in details:
            label_colored = self._color(f"{label}", 'DIM')
            print(f"  {label_colored} {value}")
            
        print()
        
        # Vault reference
        if vault_path:
            vault_label = self._color("🔒 Transaction locked in Audit Vault:", 'DIM')
            print(f"  {vault_label} {vault_path}")
            print()
            
        # Show minimal audit logs on success
        self.render_audit_log(expanded=False)
        print(f"\n  └{border}┘")
        
    def render_decomposition_complete(self, fragment_count: int) -> None:
        """Render completion of query decomposition."""
        self.update_step(
            "DECOMPOSITION", 
            f"{fragment_count} Frozen Fragments Isolated", 
            'GREEN',
            progress=1.0
        )
        self.log_audit('INFO', f"Fragment #{hex(hash(fragment_count))[-4:].upper()} Memoized Cache Hit. Skipping Swarm Math.")
        
    def render_swarm_complete(self, iterations: int, contradictions: int = 0) -> None:
        """Render completion of Monte Carlo swarm evaluation."""
        if contradictions > 0:
            status = f"{iterations} Halton Iterations Run, {contradictions} Contradictions Detected"
            color = 'YELLOW'
            self.log_audit('WARN', f"Contradiction detected between sources. Conflict factor elevated.")
        else:
            status = f"{iterations} Halton Iterations Run"
            color = 'GREEN'
            
        self.update_step("SWARM_ENGINE", status, color, progress=1.0)
        
    def cleanup(self) -> None:
        """Clean up terminal state."""
        sys.stdout.write(self._clear_line())
        sys.stdout.flush()

    # ========== NEW UNIFIED SYSTEM VISUALIZATION METHODS ==========

    def render_cascade_stage(self, stage: str, progress: float = 0.0) -> None:
        """
        Render the cascading retrieval stage (Cache → DB → API → Fallback).
        
        Args:
            stage: Current stage (CACHE, LOCAL_DB, LIVE_API, FALLBACK)
            progress: Progress within this stage (0.0-1.0)
        """
        self.cascade_stage = stage
        
        stages = [
            ("CACHE", "Checking local cache..."),
            ("LOCAL_DB", "Querying local database..."),
            ("LIVE_API", "Fetching from live APIs..."),
            ("FALLBACK", "Using fallback estimation...")
        ]
        
        print()
        cascade_header = self._color("⟳ RETRIEVAL CASCADE:", 'CYAN')
        print(f"  {cascade_header}")
        
        current_index = -1
        for i, (stage_name, description) in enumerate(stages):
            if stage_name == stage:
                current_index = i
                # Current stage - show spinner and progress
                spinner = self.SPINNER_FRAMES[self._spinner_index % len(self.SPINNER_FRAMES)]
                self._spinner_index += 1
                bar_width = 15
                filled = int(bar_width * progress)
                bar = self.BAR_FULL * filled + self.BAR_EMPTY * (bar_width - filled)
                line = f"    {spinner} [{stage_name:>8}] [{bar}] {progress*100:5.1f}% ──► {description}"
                print(self._color(line, 'YELLOW'))
            elif i < current_index:
                # Completed stage
                print(f"    {self._color('✓', 'GREEN')} [{stage_name:>8}] ──► Complete")
            else:
                # Pending stage
                print(f"    {self._color('○', 'DIM')} [{stage_name:>8}] ──► Pending")
        
        sys.stdout.flush()

    def render_credibility_sources(self, sources: List[Dict[str, Any]]) -> None:
        """
        Render source credibility indicators.
        
        Args:
            sources: List of dicts with 'url', 'credibility' keys
        """
        self.credibility_sources = sources
        
        if not sources:
            return
            
        print()
        cred_header = self._color("📊 SOURCE CREDIBILITY:", 'MAGENTA')
        print(f"  {cred_header}")
        
        for source in sources[:5]:  # Show top 5 sources
            url = source.get('url', 'Unknown')[:50]
            credibility = source.get('credibility', 'UNVERIFIED')
            color = self.CREDIBILITY_COLORS.get(credibility, 'DIM')
            
            # Truncate URL if too long
            if len(url) > 50:
                url = url[:47] + "..."
            
            badge = self._color(f"[{credibility:>10}]", color)
            print(f"    ├── {badge} {url}")
        
        if len(sources) > 5:
            print(f"    └── {self._color(f'+ {len(sources)-5} more sources', 'DIM')}")

    def render_confidence_meter(self, base_conf: float, adjusted_conf: float, 
                                domain: str, domain_accuracy: float = 0.0) -> None:
        """
        Render adaptive confidence meter showing base vs adjusted scores.
        
        Args:
            base_conf: Base confidence score (0.0-1.0)
            adjusted_conf: Adjusted confidence after calibration (0.0-1.0)
            domain: Domain name
            domain_accuracy: Historical domain accuracy
        """
        self.base_confidence = base_conf
        self.adjusted_confidence = adjusted_conf
        
        print()
        conf_header = self._color("🎯 ADAPTIVE CONFIDENCE:", 'BLUE')
        print(f"  {conf_header}")
        
        # Create meter visualization
        meter_width = 30
        base_filled = int(meter_width * base_conf)
        adj_filled = int(meter_width * adjusted_conf)
        
        base_bar = '█' * base_filled + '░' * (meter_width - base_filled)
        adj_bar = '█' * adj_filled + '░' * (meter_width - adj_filled)
        
        # Determine color based on adjusted confidence
        if adjusted_conf >= 0.8:
            color = 'GREEN'
        elif adjusted_conf >= 0.6:
            color = 'YELLOW'
        else:
            color = 'RED'
        
        print(f"    Base Confidence:     [{self._color(base_bar, 'DIM')}] {base_conf*100:5.1f}%")
        print(f"    Adjusted Confidence: [{self._color(adj_bar, color)}] {adjusted_conf*100:5.1f}%")
        print(f"    Domain: {domain} (Historical Accuracy: {domain_accuracy*100:.1f}%)")
        
        if adjusted_conf < base_conf:
            adjustment = self._color(f"↓ {(base_conf - adjusted_conf)*100:.1f}% penalty", 'RED')
        elif adjusted_conf > base_conf:
            adjustment = self._color(f"↑ {(adjusted_conf - base_conf)*100:.1f}% bonus", 'GREEN')
        else:
            adjustment = self._color("No adjustment", 'DIM')
        
        print(f"    Adjustment: {adjustment}")

    def render_cross_domain_status(self, domains: List[str], fusion_active: bool) -> None:
        """
        Render cross-domain fusion status.
        
        Args:
            domains: List of domains involved
            fusion_active: Whether fusion engine is active
        """
        self.cross_domain_active = fusion_active
        self.domains_involved = domains
        
        if not fusion_active or len(domains) <= 1:
            return
            
        print()
        fusion_header = self._color("🔗 CROSS-DOMAIN FUSION ACTIVE", 'MAGENTA')
        print(f"  {fusion_header}")
        
        domain_bubbles = []
        for domain in domains:
            bubble = self._color(f"⬡ {domain}", 'CYAN')
            domain_bubbles.append(bubble)
        
        print(f"    Synthesizing: {' + '.join(domain_bubbles)}")
        print(f"    {self._color('Multi-domain reasoning enabled', 'GREEN')}")

    def render_live_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Render live metrics side panel.
        
        Args:
            metrics: Dict with latency_ms, cache_hit_rate, fragment_count, etc.
        """
        self.metrics = metrics
        
        print()
        metrics_header = self._color("📈 LIVE METRICS:", 'GREEN')
        print(f"  {metrics_header}")
        
        metric_items = [
            ("Latency", f"{metrics.get('latency_ms', 0):.1f}ms", 'CYAN'),
            ("Cache Hit Rate", f"{metrics.get('cache_hit_rate', 0)*100:.1f}%", 'BLUE'),
            ("Fragments Used", str(metrics.get('fragment_count', 0)), 'WHITE'),
            ("API Calls", str(metrics.get('api_calls', 0)), 'YELLOW'),
            ("Execution Time", f"{metrics.get('execution_time_s', 0):.3f}s", 'GREEN')
        ]
        
        for label, value, color in metric_items:
            label_colored = self._color(f"{label:<18}", 'DIM')
            print(f"    {label_colored} {value}")

    def render_feedback_prompt(self) -> Optional[bool]:
        """
        Render interactive feedback prompt (thumbs up/down).
        
        Returns:
            True if positive feedback, False if negative, None if skipped
        """
        print()
        prompt = self._color("💬 Was this answer helpful?", 'CYAN')
        options = self._color("[y/n]", 'DIM')
        
        try:
            response = input(f"  {prompt} {options}: ").strip().lower()
            if response in ['y', 'yes', '✓']:
                print(f"  {self._color('✓ Thank you! Feedback recorded.', 'GREEN')}")
                return True
            elif response in ['n', 'no', '✗']:
                print(f"  {self._color('✗ Feedback recorded. We will improve.', 'YELLOW')}")
                return False
            else:
                print(f"  {self._color('○ Skipped.', 'DIM')}")
                return None
        except (EOFError, KeyboardInterrupt):
            print(f"  {self._color('○ Skipped.', 'DIM')}")
            return None

    def render_enhanced_success(self, answer_class: str, answer: str, 
                                confidence: float, sources: List[Dict[str, Any]],
                                domain: str, base_confidence: float,
                                adjusted_confidence: float, domain_accuracy: float,
                                domains_involved: List[str], cross_domain_active: bool,
                                metrics: Dict[str, Any],
                                vault_path: Optional[str] = None) -> None:
        """
        Render enhanced success output with all unified system features.
        
        Args:
            answer_class: Answer classification
            answer: The generated answer
            confidence: Final confidence score
            sources: List of source dictionaries
            domain: Primary domain
            base_confidence: Base confidence before adjustment
            adjusted_confidence: Confidence after adaptive calibration
            domain_accuracy: Historical domain accuracy
            domains_involved: List of domains (for cross-domain)
            cross_domain_active: Whether cross-domain fusion was used
            metrics: Live metrics dictionary
            vault_path: Optional audit vault path
        """
        print()
        border = "─" * self.width
        
        # Success banner with final confidence
        confidence_pct = confidence * 100
        success_banner = self._color(f" ✓ ANSWER GENERATED: {answer_class} ({confidence_pct:.1f}% confidence) ", 'BG_GREEN')
        success_banner = success_banner.ljust(self.width + 24)
        print(f"  {success_banner}")
        print()
        
        # Render all new visualizations
        self.render_credibility_sources(sources)
        self.render_confidence_meter(base_confidence, adjusted_confidence, domain, domain_accuracy)
        
        if cross_domain_active:
            self.render_cross_domain_status(domains_involved, True)
        
        self.render_live_metrics(metrics)
        
        # Answer preview (first 500 chars)
        print()
        answer_header = self._color("📝 ANSWER:", 'BOLD')
        print(f"  {answer_header}")
        answer_preview = answer[:500]
        if len(answer) > 500:
            answer_preview += f"\n  {self._color('... (truncated)', 'DIM')}"
        print(f"  {answer_preview}")
        
        print()
        
        # Vault reference
        if vault_path:
            vault_label = self._color("🔒 Transaction locked in Audit Vault:", 'DIM')
            print(f"  {vault_label} {vault_path}")
            print()
        
        # Show minimal audit logs
        self.render_audit_log(expanded=False)
        
        # Feedback prompt
        feedback = self.render_feedback_prompt()
        if feedback is not None:
            self.log_audit('INFO', f"User feedback: {'POSITIVE' if feedback else 'NEGATIVE'}")
        
        print(f"\n  └{border}┘")


# Convenience functions for direct integration
_control_deck: Optional[ControlDeck] = None


def get_control_deck() -> ControlDeck:
    """Get or create the global ControlDeck instance."""
    global _control_deck
    if _control_deck is None:
        _control_deck = ControlDeck()
    return _control_deck


def start_session(query: str) -> None:
    """Start a new reasoning session."""
    get_control_deck().start_session(query)


def update_step(step_name: str, status: str, 
               color: str = 'BLUE', finalize: bool = False) -> None:
    """Update a processing step."""
    get_control_deck().update_step(step_name, status, color, finalize)


def log_audit(level: str, message: str) -> None:
    """Add an audit log entry."""
    get_control_deck().log_audit(level, message)


def render_halt(halt_code: str, reason: str, vault_path: Optional[str] = None) -> None:
    """Render a HALT alarm."""
    get_control_deck().render_halt(halt_code, reason, vault_path)


def render_success(answer_class: str, confidence: float, 
                  fragments_used: int, vault_path: Optional[str] = None) -> None:
    """Render a successful answer."""
    get_control_deck().render_success(answer_class, confidence, fragments_used, vault_path)


if __name__ == "__main__":
    # Enhanced Demo mode showcasing all new unified system features
    deck = ControlDeck()
    
    demo_query = "What is the economic impact of diabetes treatment costs on healthcare systems?"
    
    deck.start_session(demo_query)
    
    # Simulate cascading retrieval
    time.sleep(0.3)
    deck.render_cascade_stage("CACHE", 0.8)
    time.sleep(0.2)
    deck.render_cascade_stage("LOCAL_DB", 1.0)
    time.sleep(0.2)
    deck.render_cascade_stage("LIVE_API", 0.6)
    time.sleep(0.3)
    deck.render_cascade_stage("LIVE_API", 1.0)
    
    # Simulate decomposition
    print()
    deck.update_step("DECOMPOSITION", "Initializing...", 'BLUE')
    time.sleep(0.3)
    deck.update_step("DECOMPOSITION", "Extracting entities...", 'BLUE')
    time.sleep(0.3)
    deck.render_decomposition_complete(14)
    
    # Simulate swarm engine
    deck.update_step("SWARM_ENGINE", "Starting Halton sequences...", 'BLUE')
    for i in range(1, 6):
        progress = i / 5.0
        deck.update_step("SWARM_ENGINE", f"Running iteration {i*100}/500...", 'BLUE', progress=progress)
        time.sleep(0.2)
    
    deck.log_audit('INFO', "Fragment #0A4F Memoized Cache Hit. Skipping Swarm Math.")
    deck.log_audit('INFO', "Fragment #1B7C Memoized Cache Hit. Skipping Swarm Math.")
    
    deck.render_swarm_complete(500, contradictions=0)
    
    # Simulate cross-domain detection
    domains_involved = ["Healthcare", "Economy"]
    deck.render_cross_domain_status(domains_involved, True)
    
    # Simulate source credibility display
    sample_sources = [
        {"url": "https://www.cdc.gov/diabetes/data-statistics.html", "credibility": "HIGH"},
        {"url": "https://www.who.int/health-topics/diabetes", "credibility": "HIGH"},
        {"url": "https://www.reuters.com/healthcare/diabetes-costs-2024", "credibility": "MEDIUM"},
        {"url": "https://www.bloomberg.com/news/healthcare-economics", "credibility": "MEDIUM"},
        {"url": "https://diabetesblog.example.com/cost-analysis", "credibility": "LOW"},
        {"url": "https://unverified-source.net/claims", "credibility": "UNVERIFIED"}
    ]
    deck.render_credibility_sources(sample_sources)
    
    # Simulate adaptive confidence meter
    deck.render_confidence_meter(
        base_conf=0.92,
        adjusted_conf=0.87,
        domain="Healthcare",
        domain_accuracy=0.98
    )
    
    # Simulate live metrics
    sample_metrics = {
        "latency_ms": 245.3,
        "cache_hit_rate": 0.65,
        "fragment_count": 14,
        "api_calls": 2,
        "execution_time_s": 1.234
    }
    deck.render_live_metrics(sample_metrics)
    
    # Show enhanced success output
    demo_answer = """
Diabetes treatment imposes significant economic burdens on healthcare systems globally. 
According to CDC data, total diagnosed diabetes costs in the US reached $413 billion in 2022, 
with $306 billion in direct medical expenses and $107 billion in reduced productivity.

Key findings:
- Hospital inpatient care accounts for 30% of direct costs
- Prescription medications represent 24% of expenditures  
- Physician visits comprise 13% of total costs
- Indirect costs include absenteeism, presenteeism, and premature mortality

The economic impact extends beyond direct healthcare spending to include substantial 
productivity losses affecting national GDP. Cross-domain analysis reveals strong 
correlations between diabetes prevalence rates and regional economic performance.
"""
    
    deck.render_enhanced_success(
        answer_class="ANSWER_CONFIDENT",
        answer=demo_answer.strip(),
        confidence=0.87,
        sources=sample_sources,
        domain="Healthcare",
        base_confidence=0.92,
        adjusted_confidence=0.87,
        domain_accuracy=0.98,
        domains_involved=domains_involved,
        cross_domain_active=True,
        metrics=sample_metrics,
        vault_path=".openeyes/vault/tx_demo_123.json"
    )
    
    print("\n" + "=" * 80)
    print("Demo complete. This showcases the enhanced Control Deck with unified system features.")
    print("=" * 80)
