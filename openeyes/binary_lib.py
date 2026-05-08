"""
OpenEyes Binary Library Engine (.oelib)
High-speed serialization and compression for fragment libraries.
Mimics biological memory consolidation into stable long-term storage.
"""

import struct
import zlib
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict

# Magic bytes for .oelib files
MAGIC_HEADER = b'OELIB001'
VERSION = 1

class BinaryLibError(Exception):
    """Exception raised for binary library operations."""
    pass

class BinaryLibrary:
    """
    Handles serialization/deserialization of FragmentLibrary to/from binary format.
    
    Binary Format Specification:
    - Header (16 bytes): Magic(8) + Version(4) + Checksum(4)
    - Metadata Block: JSON-encoded metadata (length-prefixed)
    - Fragment Count: 4-byte integer
    - Fragment Blocks: Variable length, compressed JSON blobs
    - Index Block: Fast lookup table for fragment IDs
    """
    
    def __init__(self):
        self.compression_level = 6  # Balance between speed and size
        
    def serialize(self, library_data: Dict[str, Any]) -> bytes:
        """
        Convert library dictionary to binary blob.
        
        Args:
            library_data: Dictionary containing fragments, index, and metadata
            
        Returns:
            Compressed binary bytes
        """
        try:
            # Serialize main data to JSON first
            json_data = json.dumps(library_data, separators=(',', ':')).encode('utf-8')
            
            # Compress
            compressed = zlib.compress(json_data, level=self.compression_level)
            
            # Calculate checksum
            checksum = zlib.crc32(compressed) & 0xffffffff
            
            # Build header: Magic(8) + Version(4) + Checksum(4) + Length(4)
            header = struct.pack('<8sIII', MAGIC_HEADER, VERSION, checksum, len(compressed))
            
            return header + compressed
            
        except Exception as e:
            raise BinaryLibError(f"Serialization failed: {str(e)}")
    
    def deserialize(self, binary_data: bytes) -> Dict[str, Any]:
        """
        Convert binary blob back to library dictionary.
        
        Args:
            binary_data: Binary bytes from .oelib file
            
        Returns:
            Dictionary with fragments, index, and metadata
        """
        try:
            if len(binary_data) < 20:
                raise BinaryLibError("Invalid binary data: too short")
            
            # Parse header
            magic, version, stored_checksum, compressed_len = struct.unpack('<8sIII', binary_data[:20])
            
            if magic != MAGIC_HEADER:
                raise BinaryLibError(f"Invalid magic header: {magic}")
            
            if version != VERSION:
                raise BinaryLibError(f"Unsupported version: {version}")
            
            # Extract compressed data
            compressed_data = binary_data[20:20+compressed_len]
            
            # Verify checksum
            actual_checksum = zlib.crc32(compressed_data) & 0xffffffff
            if actual_checksum != stored_checksum:
                raise BinaryLibError("Checksum mismatch: data corruption detected")
            
            # Decompress
            json_data = zlib.decompress(compressed_data)
            
            # Parse JSON
            library_data = json.loads(json_data.decode('utf-8'))
            
            return library_data
            
        except BinaryLibError:
            raise
        except Exception as e:
            raise BinaryLibError(f"Deserialization failed: {str(e)}")
    
    def save_to_file(self, library_data: Dict[str, Any], filepath: str) -> None:
        """Save library to .oelib file."""
        binary_data = self.serialize(library_data)
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(binary_data)
    
    def load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load library from .oelib file."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Binary library not found: {filepath}")
        binary_data = path.read_bytes()
        return self.deserialize(binary_data)
    
    def get_stats(self, binary_data: bytes) -> Dict[str, Any]:
        """Get compression statistics."""
        original_json_size = len(zlib.decompress(binary_data[20:]))
        compressed_size = len(binary_data)
        ratio = (1 - compressed_size / original_json_size) * 100
        
        return {
            "original_size": original_json_size,
            "compressed_size": compressed_size,
            "compression_ratio": f"{ratio:.1f}%",
            "space_saved": original_json_size - compressed_size
        }


def optimize_for_speed(library_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pre-process library data for faster access after deserialization.
    Converts lists to tuples, strings to interned versions where possible.
    """
    # Create optimized index
    if 'fragments' in library_data:
        # Pre-calculate fragment lookup
        library_data['_fast_lookup'] = {
            frag_id: idx 
            for idx, frag_id in enumerate(library_data['fragments'].keys())
        }
    
    return library_data
