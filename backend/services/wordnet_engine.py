import nltk
from nltk.corpus import wordnet as wn
from typing import List, Set, Tuple
import logging

logger = logging.getLogger(__name__)

def ensure_wordnet():
    try:
        wn.synsets('test')
    except LookupError:
        logger.info("Downloading WordNet data")
        nltk.download('wordnet')
        nltk.download('omw-1.4')

def get_wordnet_family(word: str) -> List[Tuple[str, str, float]]:
    """
    Get word family from WordNet (synonyms, derivations, hypernyms, hyponyms)
    Returns list of tuples of (word, relation_type, score).
    """
    ensure_wordnet()
    
    results = []
    seen = set()
    
    synsets = wn.synsets(word)
    
    if not synsets:
        return results
    
    results.append((word, "root", 1.0))
    seen.add(word.lower())
    
    for synset in synsets[:3]:  # limit to top 3 synsets for speed
        for lemma in synset.lemmas():
            lemma_name = lemma.name().replace('_', ' ')
            if lemma_name.lower() not in seen:
                results.append((lemma_name, "synonym", 0.9))
                seen.add(lemma_name.lower())
        
        for lemma in synset.lemmas():
            for related in lemma.derivationally_related_forms():
                related_name = related.name().replace('_', ' ')
                if related_name.lower() not in seen:
                    results.append((related_name, "derivation", 0.85))
                    seen.add(related_name.lower())
        
        for hypernym in synset.hypernyms()[:2]:
            for lemma in hypernym.lemmas():
                lemma_name = lemma.name().replace('_', ' ')
                if lemma_name.lower() not in seen:
                    results.append((lemma_name, "hypernym", 0.7))
                    seen.add(lemma_name.lower())
        
        for hyponym in synset.hyponyms()[:2]:
            for lemma in hyponym.lemmas():
                lemma_name = lemma.name().replace('_', ' ')
                if lemma_name.lower() not in seen:
                    results.append((lemma_name, "hyponym", 0.7))
                    seen.add(lemma_name.lower())
    
    return results[:30] 
