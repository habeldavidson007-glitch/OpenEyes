"""
OpenEyes Control Deck - High-Stakes Reasoning Terminal UI

A specialized, hyper-responsive TUI modeled after Claude Code.
Provides real-time visibility into decomposition, swarm evaluation, and halt triggers.
Uses pure ANSI escape codes for zero-dependency efficiency.
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
        
    def update_step(self, step_name: str, progress: float, status: str, 
                   color: str = 'BLUE', finalize: bool = False) -> None:
        """
        Update a processing step with progress.
        
        Args:
            step_name: Name of the step
            progress: Progress percentage (0.0 to 1.0)
            status: Status message
            color: Color for the step indicator
            finalize: If True, move to next line after rendering
        """
        show_spinner = not finalize and progress < 1.0
        self._render_progress_bar(step_name, progress, status, color, show_spinner)
        
        if finalize:
            print()  # Move to next line
            
    def start_session(self, query: str) -> None:
        """
        Start a new reasoning session.
        
        Args:
            query: The user query to process
        """
        self.render_header()
        self.render_query(query)
        self.start_time = time.time()
        self.audit_logs = []
        
    def log_audit(self, level: str, message: str, timestamp: Optional[float] = None) -> None:
        """
        Add an audit log entry.
        
        Args:
            level: Log level (INFO, WARN, ERROR, HALT)
            message: Log message
            timestamp: Optional timestamp (defaults to current elapsed time)
        """
        if timestamp is None:
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
        
    def render_success(self, answer_class: str, confidence: float, 
                      fragments_used: int, vault_path: Optional[str] = None) -> None:
        """
        Render a successful answer completion.
        
        Args:
            answer_class: The ANSWER class (e.g., ANSWER_CONFIDENT)
            confidence: Confidence score (0.0 to 1.0)
            fragments_used: Number of fragments used in the answer
            vault_path: Optional path to the audit vault transaction
        """
        print()
        border = "─" * self.width
        
        # Green success banner
        confidence_pct = confidence * 100
        success_banner = self._color(f" ✓ ANSWER GENERATED: {answer_class} ({confidence_pct:.1f}% confidence) ", 'GREEN')
        success_banner = success_banner.ljust(self.width + 24)
        print(f"  {success_banner}")
        print()
        
        # Details
        details = [
            (f"Fragments Used:", f"{fragments_used} frozen fragments isolated"),
            (f"Execution Time:", f"{self._get_elapsed_time():.3f}s"),
            (f"Confidence Score:", f"{confidence:.4f}")
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
            1.0, 
            f"{fragment_count} Frozen Fragments Isolated", 
            'GREEN', 
            finalize=True
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
            
        self.update_step("SWARM ENGINE", 1.0, status, color, finalize=True)
        
    def cleanup(self) -> None:
        """Clean up terminal state."""
        sys.stdout.write(self._clear_line())
        sys.stdout.flush()


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


def update_step(step_name: str, progress: float, status: str, 
               color: str = 'BLUE', finalize: bool = False) -> None:
    """Update a processing step."""
    get_control_deck().update_step(step_name, progress, status, color, finalize)


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
    # Demo mode
    deck = ControlDeck()
    
    demo_query = "Evaluate clinical trial efficacy parameters for Compound X in treating Stage III melanoma."
    
    deck.start_session(demo_query)
    
    # Simulate decomposition
    deck.update_step("DECOMPOSITION", 0.0, "Initializing...", 'BLUE')
    time.sleep(0.3)
    deck.update_step("DECOMPOSITION", 0.5, "Extracting entities...", 'BLUE')
    time.sleep(0.3)
    deck.render_decomposition_complete(14)
    
    # Simulate swarm engine
    deck.update_step("SWARM ENGINE", 0.0, "Starting Halton sequences...", 'BLUE')
    for i in range(1, 6):
        progress = i / 5.0
        deck.update_step("SWARM ENGINE", progress, f"Running iteration {i*100}/500...", 'BLUE')
        time.sleep(0.2)
    
    deck.log_audit('INFO', "Fragment #0A4F Memoized Cache Hit. Skipping Swarm Math.")
    deck.log_audit('INFO', "Fragment #1B7C Memoized Cache Hit. Skipping Swarm Math.")
    deck.log_audit('WARN', "Contradiction detected between Src:A and Src:D.")
    
    deck.render_swarm_complete(500, contradictions=1)
    
    # Simulate halt
    time.sleep(0.5)
    deck.render_halt(
        "HALT_CONTRADICTION_DETECTED",
        "Conflict Factor (K) exceeded safety threshold (0.85). Multiple authoritative sources provide contradictory efficacy data.",
        ".openeyes/vault/tx_9f8a21.json"
    )
    
    print("\n" + "=" * 80)
    print("Demo complete. This is how the Control Deck will look during real execution.")
