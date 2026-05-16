#!/usr/bin/env python3
"""
P1 Pre-Ingestion Validation Gate

This module provides validation for fragments BEFORE they are ingested into the system.
It ensures all required fields are present and valid, preventing bad data from entering.

Usage:
    from openeyes.ingestion.validation_gate import validate_fragment_before_ingest
    
    result = validate_fragment_before_ingest(fragment_data)
    if result.valid:
        # Proceed with ingestion
    else:
        # Reject and log errors
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of fragment validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    fixed_fields: Dict[str, Any]


class PreIngestionValidator:
    """
    Validates fragments before they enter the knowledge base.
    
    This is a P1-HIGH priority control that prevents:
    - Missing source_url
    - Future-dated content
    - Invalid domain/sector codes
    - Malformed metadata
    """
    
    # Valid domain codes
    VALID_DOMAINS = {'gov', 'eco', 'hc', 'eng', 'phi'}
    
    # Credible URL patterns
    CREDIBLE_PATTERNS = [
        r'\.gov/',
        r'\.edu/',
        r'\.org/',
        r'pubmed',
        r'arxiv',
        r'doi\.org',
        r'nature\.com',
        r'science\.org',
        r'who\.int',
        r'cdc\.gov',
        r'ecb\.europa',
        r'fed\.gov',
    ]
    
    # Suspicious URL patterns
    SUSPICIOUS_PATTERNS = [
        r'blogspot',
        r'wordpress\.com(?!/official)',
        r'reddit\.com',
        r'quora\.com',
        r'medium\.com(?!/official)',
        r'fake',
        r'pseudo',
    ]
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, reject fragments with any warnings
        """
        self.strict_mode = strict_mode
    
    def validate_fragment(self, data: Dict) -> ValidationResult:
        """
        Validate a fragment before ingestion.
        
        Args:
            data: Fragment data dictionary
            
        Returns:
            ValidationResult with validity status and any issues
        """
        errors = []
        warnings = []
        fixed_fields = {}
        
        # Check it's a dict
        if not isinstance(data, dict):
            return ValidationResult(
                valid=False,
                errors=["Fragment must be a dictionary"],
                warnings=[],
                fixed_fields={}
            )
        
        # 1. Validate source_url (P0 CRITICAL)
        source_url = data.get('source_url', '')
        if not source_url or not str(source_url).strip():
            # Try to extract from roles
            roles = data.get('roles', [])
            if roles and isinstance(roles, list):
                for role in roles:
                    if isinstance(role, dict) and role.get('url'):
                        source_url = role['url']
                        fixed_fields['source_url'] = source_url
                        break
            
            # Generate from source if still missing
            if not source_url:
                source = data.get('source', '')
                if source:
                    source_url = f"https://source/{source.lower().replace(' ', '_')}"
                    fixed_fields['source_url'] = source_url
                    warnings.append(f"Generated source_url from source field: {source_url}")
                else:
                    errors.append("Missing required field: source_url (and no source field to generate from)")
        
        # Validate URL format
        if source_url and source_url != fixed_fields.get('source_url'):
            if not self._is_valid_url(source_url):
                errors.append(f"Invalid URL format: {source_url}")
            
            # Check for suspicious patterns
            if self._is_suspicious_url(source_url):
                if not self._has_credible_markers(source_url):
                    warnings.append(f"Suspicious source URL detected: {source_url}")
        
        # 2. Validate year/date (no future dates)
        year = data.get('year')
        if year:
            try:
                year_int = int(year)
                current_year = datetime.now().year
                if year_int > current_year:
                    errors.append(f"Future year detected: {year_int} (current: {current_year})")
                    fixed_fields['year'] = current_year
                    warnings.append(f"Corrected year to current year: {current_year}")
            except (ValueError, TypeError):
                errors.append(f"Invalid year format: {year}")
        
        # 3. Validate domain/sector if present
        domain = data.get('domain', '').lower()
        if domain and domain not in self.VALID_DOMAINS:
            # Check if it's a full name vs code
            domain_map = {
                'government': 'gov',
                'economy': 'eco',
                'healthcare': 'hc',
                'engineering': 'eng',
                'philosophy': 'phi',
            }
            if domain in domain_map:
                fixed_fields['domain'] = domain_map[domain]
                warnings.append(f"Normalized domain '{domain}' to '{domain_map[domain]}'")
            else:
                errors.append(f"Unknown domain code: {domain}")
        
        # 4. Validate required content
        content = data.get('content', '') or data.get('claim', '')
        if not content or len(str(content).strip()) < 10:
            errors.append("Content/claim is too short or missing (min 10 chars)")
        
        # 5. Validate credibility_class if present
        cred_class = data.get('credibility_class', '')
        if cred_class:
            valid_classes = ['peer_reviewed_study', 'government_agency', 'textbook', 
                           'conference_paper', 'preprint_verified', 'A', 'B', 'C']
            if cred_class not in valid_classes:
                warnings.append(f"Unusual credibility class: {cred_class}")
        
        # Determine validity
        valid = len(errors) == 0
        if self.strict_mode and len(warnings) > 0:
            valid = False
        
        return ValidationResult(
            valid=valid,
            errors=errors,
            warnings=warnings,
            fixed_fields=fixed_fields
        )
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format."""
        if not url:
            return False
        # Basic URL pattern check
        pattern = r'^https?://[^\s]+$'
        return bool(re.match(pattern, url))
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL matches suspicious patterns."""
        url_lower = url.lower()
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        return False
    
    def _has_credible_markers(self, url: str) -> bool:
        """Check if URL has credible domain markers."""
        url_lower = url.lower()
        for pattern in self.CREDIBLE_PATTERNS:
            if re.search(pattern, url_lower):
                return True
        return False


# Singleton instance
_validator = PreIngestionValidator()


def validate_fragment_before_ingest(data: Dict, strict: bool = False) -> ValidationResult:
    """
    Validate a fragment before ingesting it into the knowledge base.
    
    This is the main entry point for pre-ingestion validation.
    
    Args:
        data: Fragment data dictionary
        strict: If True, use strict mode (reject on warnings)
    
    Returns:
        ValidationResult with validity status
    
    Example:
        >>> result = validate_fragment_before_ingest(fragment_data)
        >>> if result.valid:
        ...     ingest_fragment(fragment_data)
        ... else:
        ...     print(f"Validation failed: {result.errors}")
    """
    validator = PreIngestionValidator(strict_mode=strict)
    return validator.validate_fragment(data)


def apply_fixes(data: Dict, validation_result: ValidationResult) -> Dict:
    """
    Apply automatic fixes from validation result to fragment data.
    
    Args:
        data: Original fragment data
        validation_result: Result from validate_fragment_before_ingest
    
    Returns:
        Fixed fragment data
    """
    if not validation_result.fixed_fields:
        return data
    
    # Create a copy to avoid modifying original
    fixed_data = data.copy()
    
    # Apply each fix
    for field, value in validation_result.fixed_fields.items():
        fixed_data[field] = value
    
    # Add validation metadata
    if 'metadata' not in fixed_data:
        fixed_data['metadata'] = {}
    fixed_data['metadata']['validated_at'] = datetime.now().isoformat()
    fixed_data['metadata']['validation_fixes_applied'] = list(validation_result.fixed_fields.keys())
    
    return fixed_data


if __name__ == '__main__':
    # Test the validator
    test_fragments = [
        # Valid fragment
        {
            'domain': 'hc',
            'sector': 'med',
            'content': 'Test medical content',
            'source_url': 'https://pubmed.gov/test',
            'year': 2024,
        },
        # Missing source_url (should be fixed)
        {
            'domain': 'eco',
            'sector': 'fin',
            'content': 'Test economy content',
            'source': 'Federal Reserve',
            'year': 2024,
        },
        # Future date (should error)
        {
            'domain': 'gov',
            'sector': 'leg',
            'content': 'Test government content',
            'source_url': 'https://congress.gov/test',
            'year': 2030,
        },
        # Invalid domain
        {
            'domain': 'invalid',
            'content': 'Test content',
            'source_url': 'https://example.com',
        },
    ]
    
    print("Pre-Ingestion Validation Gate Tests")
    print("=" * 60)
    
    for i, frag in enumerate(test_fragments, 1):
        print(f"\nTest {i}: {frag.get('content', '')[:40]}...")
        result = validate_fragment_before_ingest(frag)
        print(f"  Valid: {result.valid}")
        if result.errors:
            print(f"  Errors: {result.errors}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        if result.fixed_fields:
            print(f"  Fixed: {result.fixed_fields}")
