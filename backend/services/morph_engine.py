from typing import List, Tuple
import re

#manually listed for now
SUFFIXES = [
    'ing', 'ed', 'er', 'est', 's', 'es',
    'tion', 'sion', 'ment', 'ness', 'ity', 'ty',
    'ly', 'al', 'ous', 'ive', 'ful', 'less',
    'able', 'ible', 'ant', 'ent', 'ence', 'ance',
    'y', 'en', 'ize', 'ise', 'ate'
]

PREFIXES = [
    'un', 're', 'in', 'im', 'il', 'ir', 'dis',
    'en', 'em', 'non', 'over', 'mis', 'sub',
    'pre', 'inter', 'fore', 'de', 'trans', 'super',
    'semi', 'anti', 'mid', 'under', 'pseudo'
]

def strip_suffix(word: str) -> str:
    """strip common suffixes to find the base form"""
    word_lower = word.lower()
    
    for suffix in sorted(SUFFIXES, key=len, reverse=True):
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
            base = word_lower[:-len(suffix)]
            # Handle doubling (running -> run)
            if len(base) >= 2 and base[-1] == base[-2]:
                return base[:-1]
            # Handle e-dropping (making -> make)
            if suffix in ['ing', 'ed', 'er'] and len(base) >= 2:
                return base + 'e'
            return base
    
    return word_lower

def strip_suffix_recursive(word: str, max_depth: int = 3) -> List[str]:
    """recursively strip suffixes to handle multi-layered words
    like additionally -> addition -> add
    """
    results = [word]
    current = word
    
    for _ in range(max_depth):
        stripped = strip_suffix(current)
        if stripped == current or len(stripped) < 3:
            break
        results.append(stripped)
        current = stripped
    
    return results

def strip_prefix(word: str) -> str:
    """strip common prefixes to find the base form."""
    word_lower = word.lower()
    
    for prefix in sorted(PREFIXES, key=len, reverse=True):
        if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
            return word_lower[len(prefix):]
    
    return word_lower

def strip_prefix_recursive(word: str, max_depth: int = 2) -> List[str]:
    """recursively strip prefixes to handle multi-layered prefixes
    like unrewritable -> rewritable -> writable
    """
    results = [word]
    current = word
    
    for _ in range(max_depth):
        stripped = strip_prefix(current)
        if stripped == current or len(stripped) < 3:
            break
        results.append(stripped)
        current = stripped
    
    return results

def should_double_consonant(word: str) -> bool:
    """Check if word should double final consonant before suffix"""
    if len(word) < 3:
        return False
    
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    
    # Check CVC pattern (consonant-vowel-consonant)
    if (word[-1] in consonants and 
        word[-2] in vowels and 
        word[-3] in consonants and
        word[-1] not in 'wxy'):  # Don't double w, x, y
        return True
    return False

def generate_variants(word: str) -> List[str]:
    variants = set()
    base = word.lower()
    
    variants.add(base)
    
    # Try stripping suffix to get base
    base_from_suffix = strip_suffix(base)
    if base_from_suffix != base:
        variants.add(base_from_suffix)
    
    # Try stripping prefix
    base_from_prefix = strip_prefix(base)
    if base_from_prefix != base:
        variants.add(base_from_prefix)
    
    # Gen common variants from the base
    working_base = base_from_suffix if base_from_suffix != base else base
    
    needs_doubling = should_double_consonant(working_base)
    
    # Add -ing form
    if not working_base.endswith('ing'):
        if needs_doubling:
            variants.add(working_base + working_base[-1] + 'ing')  # run → running
        variants.add(working_base + 'ing')
        # Handle e-dropping
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'ing')
    
    # Add -ed form
    if not working_base.endswith('ed'):
        if needs_doubling:
            variants.add(working_base + working_base[-1] + 'ed')  # stop → stopped
        variants.add(working_base + 'ed')
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'ed')
    
    # Add -er form
    if not working_base.endswith('er'):
        if needs_doubling:
            variants.add(working_base + working_base[-1] + 'er')  # strip → stripper
        variants.add(working_base + 'er')
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'er')
    
    # Add -s form
    if not working_base.endswith('s'):
        if working_base.endswith(('s', 'x', 'z', 'ch', 'sh')):
            variants.add(working_base + 'es')
        else:
            variants.add(working_base + 's')
    
    # Add -tion form
    if len(working_base) > 3:
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'tion')
        else:
            variants.add(working_base + 'tion')
            variants.add(working_base + 'ation')
    
    # Add -ly form
    variants.add(working_base + 'ly')
    
    # Add -ness form
    variants.add(working_base + 'ness')
    
    return list(variants)

def get_morphological_family(word: str) -> List[Tuple[str, str, float]]:
    """
    Get morphological word family.
    Returns list of (word, relation_type, score) tuples.
    """
    results = []
    seen = set()
    
    # Get base forms using recursive stripping
    suffix_bases = strip_suffix_recursive(word)
    prefix_bases = strip_prefix_recursive(word)
    
    # Add all intermediate base forms
    for i, base in enumerate(suffix_bases[1:], 1):  # Skip first (original word)
        if base not in seen and len(base) > 2:
            # Score decreases with depth: 0.95, 0.90, 0.85...
            score = 0.95 - (i - 1) * 0.05
            results.append((base, "base_form", max(score, 0.80)))
            seen.add(base)
    
    for i, base in enumerate(prefix_bases[1:], 1):
        if base not in seen and len(base) > 2:
            score = 0.95 - (i - 1) * 0.05
            results.append((base, "base_form", max(score, 0.80)))
            seen.add(base)
    
    variants = generate_variants(word)
    
    for variant in variants:
        if variant != word.lower() and variant not in seen and len(variant) > 2:
            results.append((variant, "morphological", 0.80))
            seen.add(variant)
    
    return results[:20] 
