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

def is_valid_word(word: str) -> bool:
    """Check if a word exists in WordNet (basic validation)"""
    try:
        from nltk.corpus import wordnet as wn
        return len(wn.synsets(word)) > 0
    except:
        # Fallback: basic heuristics
        return len(word) >= 3 and word.isalpha()

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
    
    # Generate prefix variants (for words like re-act, trans-act)
    common_prefixes = ['re', 'un', 'trans', 'inter', 'pre', 'post', 'over', 
                       'under', 'counter', 'de', 'dis', 'mis', 'sub', 'super',
                       'co', 'pro', 'con', 'ex', 'en']
    
    for prefix in common_prefixes:
        prefix_variant = prefix + working_base
        if len(prefix_variant) > 4:  # Avoid very short words
            variants.add(prefix_variant)
    
    needs_doubling = should_double_consonant(working_base)
    
    # Add -ing form
    if not working_base.endswith('ing'):
        if needs_doubling:
            variants.add(working_base + working_base[-1] + 'ing')  # run → running
        elif working_base.endswith('e'):
            variants.add(working_base[:-1] + 'ing')  # make → making
        else:
            variants.add(working_base + 'ing')
    
    # Add -ed form
    if not working_base.endswith('ed'):
        if needs_doubling:
            variants.add(working_base + working_base[-1] + 'ed')  # stop → stopped
        elif working_base.endswith('e'):
            variants.add(working_base + 'd')  # make → made
        else:
            variants.add(working_base + 'ed')
    
    # Add -er form
    if not working_base.endswith('er'):
        if needs_doubling:
            variants.add(working_base + working_base[-1] + 'er')  # run → runner
        elif working_base.endswith('e'):
            variants.add(working_base + 'r')  # large → larger
        else:
            variants.add(working_base + 'er')
    
    # Add -s form
    if not working_base.endswith('s'):
        if working_base.endswith(('s', 'x', 'z', 'ch', 'sh')):
            variants.add(working_base + 'es')
        elif working_base.endswith('y') and len(working_base) > 1 and working_base[-2] not in 'aeiou':
            variants.add(working_base[:-1] + 'ies')  # happy → happies
        else:
            variants.add(working_base + 's')
    
    # Add -tion/-sion/-ation forms
    if len(working_base) > 2:
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'ion')  # create → creation
            variants.add(working_base[:-1] + 'ation')  # create → creation
        elif working_base.endswith('t'):
            variants.add(working_base + 'ion')  # act → action
            variants.add(working_base + 'ation')  # act → actation (rare but possible)
        elif working_base.endswith('d'):
            variants.add(working_base[:-1] + 'sion')  # decide → decision
        else:
            variants.add(working_base + 'tion')  # act → action
            variants.add(working_base + 'ation')  # act → actation
    
    # Add complex derivations with prefix + suffix (like trans-act-ion)
    if len(working_base) > 2:
        important_prefixes = ['re', 'trans', 'inter', 'counter', 'over', 'under', 'pre', 'post', 'de', 'pro', 'con', 'ex']
        important_suffixes = ['ion', 'tion', 'ation', 'ive', 'or', 'er', 'al', 'ual', 'ing', 'ed']
        
        for prefix in important_prefixes:
            for suffix in important_suffixes:
                # Create complex words like trans-act-ion
                if working_base.endswith('e') and suffix.startswith(('i', 'a')):
                    complex_word = prefix + working_base[:-1] + suffix
                elif working_base.endswith('t') and suffix in ['ion', 'tion', 'ation']:
                    complex_word = prefix + working_base + suffix
                else:
                    complex_word = prefix + working_base + suffix
                
                # Only add if reasonable length (avoid too long words)
                if 6 <= len(complex_word) <= 15:
                    variants.add(complex_word)
    
    # Add -or/-er agent forms
    if len(working_base) > 2:
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'or')  # create → creator
        else:
            variants.add(working_base + 'or')  # act → actor
    
    # Add -ive adjective forms
    if len(working_base) > 2:
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'ive')  # create → creative
        elif working_base.endswith('t'):
            variants.add(working_base + 'ive')  # act → active
        else:
            variants.add(working_base + 'ive')
    
    # Add -ity/-ty noun forms
    if len(working_base) > 3:
        if working_base.endswith('e'):
            variants.add(working_base[:-1] + 'ity')  # active → activity
        else:
            variants.add(working_base + 'ity')  # active → activity
    
    # Add -ly form (for adjectives)
    if len(working_base) > 3:
        if working_base.endswith('y'):
            variants.add(working_base[:-1] + 'ily')  # happy → happily
        elif working_base.endswith('le'):
            variants.add(working_base[:-2] + 'ly')  # simple → simply
        else:
            variants.add(working_base + 'ly')
    
    # Add -ness form (for adjectives)
    if len(working_base) > 3:
        if working_base.endswith('y'):
            variants.add(working_base[:-1] + 'iness')  # happy → happiness
        else:
            variants.add(working_base + 'ness')
    
    # Filter out invalid words
    valid_variants = [v for v in variants if is_valid_word(v)]
    
    # Return valid variants, or if none found, return top variants by length preference
    if valid_variants:
        return valid_variants
    else:
        # Prefer variants that are reasonable length (not too short, not too long)
        sorted_variants = sorted(variants, key=lambda x: abs(len(x) - 8))
        return sorted_variants[:15]

def get_morphological_family(word: str) -> List[Tuple[str, str, float]]:
    """
    Get morphological word family with validation and recursive generation.
    Returns list of (word, relation_type, score) tuples.
    """
    results = []
    seen = set([word.lower()])
    
    # Get base forms using recursive stripping
    suffix_bases = strip_suffix_recursive(word)
    prefix_bases = strip_prefix_recursive(word)
    
    # Add all intermediate base forms (validated)
    for i, base in enumerate(suffix_bases[1:], 1):  # Skip first (original word)
        if base not in seen and len(base) > 2 and is_valid_word(base):
            score = 0.95 - (i - 1) * 0.05
            results.append((base, "base_form", max(score, 0.80)))
            seen.add(base)
    
    for i, base in enumerate(prefix_bases[1:], 1):
        if base not in seen and len(base) > 2 and is_valid_word(base):
            score = 0.95 - (i - 1) * 0.05
            results.append((base, "base_form", max(score, 0.80)))
            seen.add(base)
    
    # Generate variants from the original word
    variants = generate_variants(word)
    
    for variant in variants:
        if variant not in seen and len(variant) > 2:
            results.append((variant, "morphological", 0.85))
            seen.add(variant)
    
    # Generate variants from base forms (2nd level derivations)
    # Example: act -> action -> transaction
    for base in suffix_bases[1:2]:  # Only first base to avoid explosion
        if len(base) > 2:
            base_variants = generate_variants(base)
            for variant in base_variants:
                if variant not in seen and len(variant) > 2:
                    results.append((variant, "morphological", 0.80))
                    seen.add(variant)
    
    # Generate explicit complex derivations (prefix + root + suffix)
    # This ensures we capture words like "transaction" from "act"
    working_base = word.lower()
    complex_prefixes = ['trans', 're', 'inter', 'counter', 'ex', 'pro', 'con']
    complex_suffixes = ['ion', 'tion', 'ation', 'ive', 'or', 'er', 'al']
    
    for prefix in complex_prefixes:
        for suffix in complex_suffixes:
            # Generate prefix + base + suffix
            if working_base.endswith('t') and suffix in ['ion', 'tion', 'ation']:
                complex_word = prefix + working_base + suffix
            elif working_base.endswith('e') and suffix.startswith(('i', 'a')):
                complex_word = prefix + working_base[:-1] + suffix
            else:
                complex_word = prefix + working_base + suffix
            
            if complex_word not in seen and 6 <= len(complex_word) <= 15:
                results.append((complex_word, "morphological", 0.82))
                seen.add(complex_word)
    
    return results[:40]  # Increased limit for more diversity 
