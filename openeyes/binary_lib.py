"""
OpenEyes Binary Library Engine & Neuro-Sleep State Manager

This module implements:
1. Binary Serialization (.oelib): Compresses fragment library for instant loading (<10ms)
2. Neural Replay Buffer: Captures query paths during Wake Mode
3. Sleep Mode Consolidation: Prunes unused fragments, hardens patterns, integrates cross-domain links
4. Obsidian Vault Cleanup: Keeps only the latest run's audit trace
"""

import os
import json
import zlib
import struct
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configuration - Dynamic path resolution
import openeyes
_package_dir = Path(openeyes.__file__).parent
BINARY_LIB_PATH = _package_dir.parent / "knowledge.oelib"
REPLAY_BUFFER_PATH = _package_dir.parent / "logs" / "neural_replay_buffer.json"
OBSIDIAN_VAULT_PATH = _package_dir.parent / "obsidian_vault"
FRAGMENTS_DIR = _package_dir.parent / "fragment_library" / "fragments"

class BinaryLibraryEngine:
    """Handles binary serialization/deserialization of the fragment library."""
    
    MAGIC_HEADER = b'OELIB001'
    
    def __init__(self):
        self.fragments: Dict[str, Any] = {}
        self.tags_index: Dict[str, List[str]] = {}
        self.synapses: List[Dict] = []
        self.metadata: Dict[str, Any] = {}
        
    def load_from_fragment_files(self, fragments_dir: Path = FRAGMENTS_DIR):
        """Load fragments from individual JSON files in the fragments directory."""
        if not fragments_dir.exists():
            print(f"[BinaryLib] Warning: Fragments directory not found at {fragments_dir}")
            return False
            
        self.fragments = {}
        self.tags_index = {}
        
        for json_file in fragments_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    fragment = json.load(f)
                    frag_id = fragment.get('fragment_id', json_file.stem)
                    self.fragments[frag_id] = fragment
                    
                    # Build tags index
                    for tag in fragment.get('tags', []):
                        if tag not in self.tags_index:
                            self.tags_index[tag] = []
                        self.tags_index[tag].append(frag_id)
                        
            except Exception as e:
                print(f"[BinaryLib] Error loading {json_file}: {e}")
                
        self.metadata = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'fragment_count': len(self.fragments)
        }
        
        print(f"[BinaryLib] Loaded {len(self.fragments)} fragments from {fragments_dir}")
        return True
        
    def serialize_to_binary(self, output_path: Path = BINARY_LIB_PATH):
        """Compress and save library to binary format."""
        if not self.fragments:
            print("[BinaryLib] Error: No fragments to serialize")
            return False
            
        start_time = time.time()
        data_payload = {
            'fragments': self.fragments,
            'tags_index': self.tags_index,
            'synapses': self.synapses,
            'metadata': self.metadata
        }
        
        json_str = json.dumps(data_payload, separators=(',', ':')).encode('utf-8')
        compressed_data = zlib.compress(json_str, level=9)
        crc = zlib.crc32(compressed_data) & 0xffffffff
        
        with open(output_path, 'wb') as f:
            f.write(self.MAGIC_HEADER)
            f.write(struct.pack('<I', crc))
            f.write(struct.pack('<I', len(compressed_data)))
            f.write(compressed_data)
            
        elapsed = time.time() - start_time
        original_size = len(json_str)
        compressed_size = len(compressed_data)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        print(f"[BinaryLib] Serialized to {output_path}")
        print(f"  Original: {original_size:,} bytes")
        print(f"  Compressed: {compressed_size:,} bytes ({ratio:.1f}% reduction)")
        print(f"  Time: {elapsed*1000:.2f}ms")
        return True
        
    def load_from_binary(self, input_path: Path = BINARY_LIB_PATH) -> bool:
        """Load library from binary format (Fast Path)."""
        if not input_path.exists():
            print(f"[BinaryLib] Binary library not found, falling back to fragment files")
            return self.load_from_fragment_files()
            
        start_time = time.time()
        try:
            with open(input_path, 'rb') as f:
                header = f.read(8)
                if header != self.MAGIC_HEADER:
                    raise ValueError("Invalid magic header")
                
                stored_crc = struct.unpack('<I', f.read(4))[0]
                length = struct.unpack('<I', f.read(4))[0]
                compressed_data = f.read(length)
                
                calculated_crc = zlib.crc32(compressed_data) & 0xffffffff
                if calculated_crc != stored_crc:
                    raise ValueError("CRC mismatch: File corrupted")
                
                json_str = zlib.decompress(compressed_data).decode('utf-8')
                data = json.loads(json_str)
                
                self.fragments = data.get('fragments', {})
                self.tags_index = data.get('tags_index', {})
                self.synapses = data.get('synapses', [])
                self.metadata = data.get('metadata', {})
                
                elapsed = time.time() - start_time
                print(f"[BinaryLib] Loaded {len(self.fragments)} fragments from binary in {elapsed*1000:.2f}ms")
                return True
                
        except Exception as e:
            print(f"[BinaryLib] Error loading binary: {e}. Falling back to fragment files.")
            return self.load_from_fragment_files()

    def get_fragment(self, fragment_id: str) -> Optional[Dict]:
        """Extract specific fragment on demand."""
        return self.fragments.get(fragment_id)
    
    def get_fragments_by_tags(self, tags: List[str]) -> List[Dict]:
        """Extract fragments matching any of the given tags."""
        result = []
        seen_ids = set()
        for tag in tags:
            if tag in self.tags_index:
                for fid in self.tags_index[tag]:
                    if fid not in seen_ids and fid in self.fragments:
                        result.append(self.fragments[fid])
                        seen_ids.add(fid)
        return result

class NeuralReplayBuffer:
    """Captures query paths during Wake Mode for later consolidation."""
    
    def __init__(self, buffer_path: Path = REPLAY_BUFFER_PATH):
        self.buffer_path = buffer_path
        self.replays: List[Dict] = []
        self._load_buffer()
        
    def _load_buffer(self):
        if self.buffer_path.exists():
            try:
                with open(self.buffer_path, 'r') as f:
                    self.replays = json.load(f)
            except:
                self.replays = []
    
    def _save_buffer(self):
        self.buffer_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.buffer_path, 'w') as f:
            json.dump(self.replays, f, indent=2)
            
    def record_query(self, query: str, domain: str, used_fragments: List[str], 
                     success: bool, confidence: float, synapse_hit: bool = False):
        """Record a query execution path."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'domain': domain,
            'used_fragments': used_fragments,
            'success': success,
            'confidence': confidence,
            'synapse_hit': synapse_hit
        }
        self.replays.append(entry)
        self._save_buffer()
        print(f"[NeuralReplay] Recorded: '{query[:40]}...' Success={success}")
        
    def get_usage_stats(self) -> Dict[str, int]:
        """Count how many times each fragment was used."""
        stats = {}
        for replay in self.replays:
            if replay['success']:
                for fid in replay['used_fragments']:
                    stats[fid] = stats.get(fid, 0) + 1
        return stats
        
    def clear(self):
        """Clear buffer after consolidation."""
        self.replays = []
        self._save_buffer()
        print("[NeuralReplay] Buffer cleared")

class SleepModeConsolidator:
    """Executes Sleep Mode: Pruning, Hardening, and Integration."""
    
    def __init__(self, binary_engine: BinaryLibraryEngine, replay_buffer: NeuralReplayBuffer):
        self.engine = binary_engine
        self.buffer = replay_buffer
        
    def run_consolidation(self):
        """Execute full sleep cycle."""
        print("\n" + "="*60)
        print("ENTERING SLEEP MODE: Consolidation Started")
        print("="*60)
        
        usage_stats = self.buffer.get_usage_stats()
        total_fragments = len(self.engine.fragments)
        used_count = len(usage_stats)
        unused_count = total_fragments - used_count
        
        print(f"\nAnalysis:")
        print(f"  Total Fragments: {total_fragments}")
        print(f"  Used in Session: {used_count}")
        print(f"  Unused (Candidates for Pruning): {unused_count}")
        
        pruned_ids = []
        for fid in self.engine.fragments:
            if fid not in usage_stats:
                self.engine.fragments[fid]['_prune_candidate'] = True
                pruned_ids.append(fid)
                
        if pruned_ids:
            print(f"\nSynaptic Pruning: Marked {len(pruned_ids)} unused fragments")
        else:
            print("\nNo fragments to prune")
            
        new_synapses = self._harden_patterns(usage_stats)
        print(f"\nPattern Hardening: Created {len(new_synapses)} new synapses")
        
        self.engine.metadata['last_sleep'] = datetime.now().isoformat()
        self.engine.metadata['total_queries_processed'] = len(self.buffer.replays)
        self.engine.serialize_to_binary()
        
        self.buffer.clear()
        self._cleanup_obsidian_vault()
        
        print("\nSLEEP MODE COMPLETE: Library Optimized")
        print("="*60 + "\n")
        
    def _harden_patterns(self, usage_stats: Dict[str, int]) -> List[Dict]:
        """Convert high-frequency fragment combinations into synapses."""
        new_synapses = []
        domain_sets = {}
        for replay in self.buffer.replays:
            if replay['success'] and not replay['synapse_hit']:
                domain = replay['domain']
                frags = tuple(sorted(replay['used_fragments']))
                if domain not in domain_sets:
                    domain_sets[domain] = {}
                domain_sets[domain][frags] = domain_sets[domain].get(frags, 0) + 1
                
        for domain, patterns in domain_sets.items():
            for pattern, count in patterns.items():
                if count >= 2:
                    synapse = {
                        'id': f"syn_{hashlib.md5(str(pattern).encode()).hexdigest()[:8]}",
                        'domain': domain,
                        'fragment_ids': list(pattern),
                        'trigger_count': count,
                        'created': datetime.now().isoformat()
                    }
                    new_synapses.append(synapse)
                    self.engine.synapses.append(synapse)
        return new_synapses
        
    def _cleanup_obsidian_vault(self):
        """Delete all but the latest audit log in Obsidian vault (recursive)."""
        if not OBSIDIAN_VAULT_PATH.exists():
            return
            
        # Recursively find all .md files in vault
        md_files = []
        for root, dirs, files in os.walk(OBSIDIAN_VAULT_PATH):
            for f in files:
                if f.endswith('.md'):
                    md_files.append(Path(root) / f)
                    
        if len(md_files) <= 1:
            return
            
        md_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        deleted_count = 0
        for old_file in md_files[1:]:
            try:
                old_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {old_file}: {e}")
                
        if deleted_count > 0:
            print(f"Obsidian Cleanup: Removed {deleted_count} old audit logs")

# Global Instances
binary_engine = BinaryLibraryEngine()
replay_buffer = NeuralReplayBuffer()
consolidator = SleepModeConsolidator(binary_engine, replay_buffer)

def initialize_wake_mode():
    """Start Wake Mode: Load binary library instantly."""
    print("\nWAKE MODE: Initializing OpenEyes...")
    success = binary_engine.load_from_binary()
    if success:
        print("System Ready: Binary Library Loaded")
    else:
        print("System Ready: Fallback to fragment files")
    return success

def record_query_execution(query: str, domain: str, used_fragments: List[str], 
                           success: bool, confidence: float, synapse_hit: bool = False):
    """Wrapper to record query during Wake Mode."""
    replay_buffer.record_query(query, domain, used_fragments, success, confidence, synapse_hit)

def trigger_sleep_mode():
    """Manually trigger Sleep Mode consolidation."""
    consolidator.run_consolidation()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--sleep":
        initialize_wake_mode()
        trigger_sleep_mode()
    else:
        print("Testing Binary Library Engine...")
        engine = BinaryLibraryEngine()
        if engine.load_from_fragment_files():
            engine.serialize_to_binary()
            engine.load_from_binary()
            print("\nTest successful! Binary library created and loaded.")
        else:
            print("Test failed!")
