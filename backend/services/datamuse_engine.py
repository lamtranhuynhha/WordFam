import httpx
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

DATAMUSE_API = "https://api.datamuse.com/words"

async def get_datamuse_related(word: str) -> List[Tuple[str, str, float]]:
    """
    Get related words from Datamuse API.
    Uses multiple relationship queries to find derivations.
    """
    results = []
    seen = set()
    
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            queries = [
                # Means like (synonyms and related concepts)
                {"ml": word, "max": 30},
                
                # Related words (broader semantic field)
                {"rel_trg": word, "max": 25},  # Triggered by word
                
                # Words with similar spelling - multiple patterns
                {"sp": f"{word}*", "max": 30},  # Starts with word (act -> action, actor)
                {"sp": f"*{word}", "max": 25},  # Ends with word (react -> act)
                {"sp": f"*{word}*", "max": 40},  # Contains word (transaction -> act)
                
                # Additional prefix patterns for common derivations
                {"sp": f"re{word}*", "max": 10},  # react, reaction
                {"sp": f"*{word}ion", "max": 15},  # action, transaction
                {"sp": f"*{word}ive", "max": 15},  # active, reactive
                {"sp": f"*{word}or", "max": 10},  # actor, reactor
                {"sp": f"*{word}ual", "max": 10},  # actual, factual
                
                # Left/Right context
                {"lc": word, "max": 15},
                {"rc": word, "max": 15},
            ]
            
            for params in queries:
                try:
                    response = await client.get(DATAMUSE_API, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data:
                            w = item.get('word', '').lower()
                            score = item.get('score', 0)
                            
                            if w and w != word.lower() and w not in seen:
                                # Normalize score to 0-1 range
                                normalized_score = min(score / 100000, 1.0)
                                
                                # Determine relationship type with better detection
                                word_lower = word.lower()
                                if word_lower in w:
                                    # Check if it's a morphological relationship
                                    # (contains the root word as a meaningful part)
                                    rel_type = "morphological"
                                    # Higher score if word is at boundary (start/end)
                                    if w.startswith(word_lower) or w.endswith(word_lower):
                                        normalized_score = max(normalized_score, 0.90)
                                    else:
                                        # Word in middle (e.g., transaction contains act)
                                        normalized_score = max(normalized_score, 0.85)
                                elif w.startswith(word_lower[:3]) and len(word_lower) >= 3:
                                    # Similar start (might be related)
                                    rel_type = "morphological"
                                    normalized_score = max(normalized_score, 0.75)
                                else:
                                    rel_type = "semantic"
                                    normalized_score = max(normalized_score, 0.70)
                                
                                results.append((w, rel_type, normalized_score))
                                seen.add(w)
                                
                except Exception as e:
                    logger.debug(f"Datamuse query failed: {e}")
                    continue
        
        # Sort by score
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:50]  # Increased limit for more diversity
        
    except Exception as e:
        logger.error(f"Datamuse API error: {e}")
        return []


async def get_word_forms(word: str) -> List[Tuple[str, str, float]]:
    """
    Get specific word forms (inflections and derivations) from Datamuse.
    """
    results = []
    seen = set()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Multiple queries to find all forms
            queries = [
                {"rel_jjb": word, "max": 20},  # Popular adjectives
                {"rel_jja": word, "max": 20},  # Adjectives describing
                {"rel_gen": word, "max": 15},  # More general
                {"rel_com": word, "max": 15},  # Comprises/made of
                {"rel_bga": word, "max": 15},  # Frequent followers
                {"rel_bgb": word, "max": 15},  # Frequent predecessors
            ]
            
            for params in queries:
                try:
                    response = await client.get(DATAMUSE_API, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for item in data:
                            w = item.get('word', '').lower()
                            score = item.get('score', 0)
                            
                            if w and w != word.lower() and w not in seen:
                                normalized_score = min(score / 100000, 1.0)
                                results.append((w, "derivation", max(normalized_score, 0.80)))
                                seen.add(w)
                except Exception as e:
                    logger.debug(f"Word forms query failed: {e}")
                    continue
        
        return results[:25]
        
    except Exception as e:
        logger.error(f"Datamuse word forms error: {e}")
        return []


async def validate_word(word: str) -> bool:
    """
    Check if a word exists using Datamuse API.
    """
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            params = {"sp": word, "max": 1}
            response = await client.get(DATAMUSE_API, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return len(data) > 0 and data[0].get('word', '').lower() == word.lower()
        
        return False
        
    except Exception as e:
        logger.debug(f"Word validation error: {e}")
        return False


async def check_etymology_etymonline(word: str) -> str:
    """
    Scrape etymology from etymonline.com directly.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            url = f"https://www.etymonline.com/word/{word}"
            response = await client.get(url)
            
            if response.status_code == 200:
                text = response.text.lower()
                return text
        return ""
    except Exception as e:
        logger.debug(f"Etymonline scraping error: {e}")
        return ""


async def check_etymology(word: str, root_word: str) -> bool:
    """
    Check if a word is etymologically derived from root_word.
    Enhanced to handle complex derivations like transaction (trans-act-ion) from act.
    """
    word_lower = word.lower()
    root_lower = root_word.lower()
    
    # Reject identical words
    if word_lower == root_lower:
        logger.debug(f"Etymology: {word} == {root_word} → Reject (identical)")
        return False
    
    # Allow words longer than root (potential derivations)
    # Removed the strict length check to allow complex derivations
    
    # Hard reject list (known false positives)
    false_positives = {
        'run': ['runt', 'runty', 'runes', 'rune'],
        'act': ['acta', 'acute', 'acts'],  # 'acts' is just plural, not derivation
        'happy': ['hap'],
    }
    if word_lower in false_positives.get(root_lower, []):
        logger.debug(f"Etymology: {word} in false_positive list → Reject")
        return False
    
    # Strategy 1: Direct morphological patterns (HIGH CONFIDENCE)
    if word_lower.startswith(root_lower):
        suffix = word_lower[len(root_lower):]
        valid_suffixes = ['ion', 'ions', 'or', 'ors', 'er', 'ers', 'ing', 'ed', 's', 'es',
                          'ive', 'ives', 'ity', 'ities', 'al', 'ual', 'ation', 'ations',
                          'tion', 'tions', 'ness', 'ly', 'ment', 'ments', 'ance', 'ence',
                          'able', 'ible', 'ant', 'ent', 'ency', 'ancy', 'ual', 'ually']
        if any(suffix == suf or suffix.startswith(suf) for suf in valid_suffixes):
            logger.debug(f"Etymology: {word} = {root_word} + '{suffix}' → Accept (direct suffix)")
            return True
    
    # Strategy 2: Ends with root + valid prefix (HIGH CONFIDENCE)
    if word_lower.endswith(root_lower):
        prefix = word_lower[:word_lower.rindex(root_lower)]
        valid_prefixes = ['re', 'un', 'dis', 'trans', 'inter', 'over', 'under',
                         'pre', 'post', 'anti', 'de', 'mis', 'non', 'sub', 'super',
                         'counter', 'ex', 'in', 'co', 'en', 'pro', 'fore', 'out']
        if prefix in valid_prefixes:
            logger.debug(f"Etymology: {word} = '{prefix}' + {root_word} → Accept (prefix)")
            return True
    
    # Strategy 3: Root in middle with valid affixes (HIGH CONFIDENCE for strong patterns)
    if root_lower in word_lower and len(root_lower) >= 3:
        pos = word_lower.find(root_lower)
        
        if pos > 0:
            prefix = word_lower[:pos]
            suffix = word_lower[pos + len(root_lower):]
            
            # Expanded prefix list for middle patterns
            valid_prefixes = ['trans', 'inter', 're', 'counter', 'over', 'under',
                            'sub', 'super', 'circum', 'extra', 'intra', 'retro',
                            'contra', 'co', 'multi', 'semi', 'bi', 'tri', 'uni',
                            'pre', 'post', 'anti', 'de', 'mis', 'non', 'pro', 'con',
                            'ex', 'auto', 'hyper', 'hypo', 'macro', 'micro', 'neo',
                            'para', 'pseudo', 'quasi', 'ultra', 'meta']
            
            # Expanded suffix list
            valid_suffixes = ['ion', 'ions', 'tion', 'tions', 'ation', 'ations',
                            'ing', 'ed', 'or', 'ors', 'er', 'ers', 'ive', 'ives',
                            'ual', 'ually', 's', 'es', 'al', 'ally', 'ment', 'ments',
                            'ness', 'less', 'ful', 'able', 'ible', 'ant', 'ent',
                            'ence', 'ance', 'ency', 'ancy', 'ity', 'ities', 'ly',
                            'ize', 'ise', 'ate', 'ous', 'eous', 'ious']
            
            # Check if prefix is valid
            if prefix in valid_prefixes:
                # Check if suffix is valid (exact match or starts with valid suffix)
                if any(suffix == suf or suffix.startswith(suf) for suf in valid_suffixes):
                    logger.debug(f"Etymology: {word} = '{prefix}'-{root_word}-'{suffix}' → Accept (middle with affixes)")
                    return True
                # Also accept if just prefix, no suffix (e.g., react from act)
                elif not suffix or len(suffix) <= 1:
                    logger.debug(f"Etymology: {word} = '{prefix}'-{root_word} → Accept (prefix only)")
                    return True
            
            # Even without valid prefix, if there's a strong suffix pattern, consider it
            # (e.g., for cases where prefix might be part of compound)
            if any(suffix == suf for suf in ['ion', 'tion', 'ation', 'ive', 'or', 'er']):
                # Check if prefix could be a valid word part (at least 2 chars)
                if len(prefix) >= 2:
                    logger.debug(f"Etymology: {word} = '{prefix}'-{root_word}-'{suffix}' → Accept (strong suffix)")
                    return True
    
    # Strategy 4: For longer words with root in meaningful position
    if len(word_lower) >= 7 and root_lower in word_lower:
        # Check if root appears in a meaningful position
        pos = word_lower.find(root_lower)
        
        # Check what's before and after the root
        before = word_lower[:pos] if pos > 0 else ''
        after = word_lower[pos + len(root_lower):]
        
        # If before/after looks like morphological components (2+ chars)
        # and not just random letters, likely a valid derivation
        if (len(before) >= 2 or len(after) >= 2):
            # Check if this isn't just a random substring match
            # by ensuring the surrounding parts are reasonable length
            if len(before) <= 6 and len(after) <= 6:
                logger.debug(f"Etymology: {word} = '{before}'-{root_word}-'{after}' → Accept (reasonable composition)")
                return True
    
    # Strategy 5: Relaxed check for words that clearly contain the root
    # as a meaningful component (not just random substring)
    if root_lower in word_lower and len(word_lower) >= len(root_lower) + 2:
        pos = word_lower.find(root_lower)
        
        # If root is at start or end with reasonable suffix/prefix
        if pos == 0 and len(word_lower) - len(root_lower) >= 2:
            logger.debug(f"Etymology: {word} starts with {root_word} + suffix → Accept")
            return True
        elif word_lower.endswith(root_lower) and pos >= 2:
            logger.debug(f"Etymology: {word} = prefix + {root_word} → Accept")
            return True
    
    logger.debug(f"Etymology: {word} from {root_word} → Reject (no match)")
    return False
