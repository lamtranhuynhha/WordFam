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
    Get word family from WordNet with deeper relationships.
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
    
    # Process synsets with priority to most common senses
    for synset in synsets[:5]:  # Increased to 5 for better coverage
        # Direct synonyms (highest score)
        for lemma in synset.lemmas():
            lemma_name = lemma.name().replace('_', ' ')
            if lemma_name.lower() not in seen:
                results.append((lemma_name, "synonym", 0.95))
                seen.add(lemma_name.lower())
        
        # Derivationally related forms (e.g., act -> action, actor)
        for lemma in synset.lemmas():
            for related in lemma.derivationally_related_forms():
                related_name = related.name().replace('_', ' ')
                if related_name.lower() not in seen:
                    results.append((related_name, "derivation", 0.90))
                    seen.add(related_name.lower())
                    
                    # Get derivations of derivations (e.g., act -> action -> transaction)
                    for second_level in related.derivationally_related_forms():
                        second_name = second_level.name().replace('_', ' ')
                        if second_name.lower() not in seen and second_name.lower() != word.lower():
                            results.append((second_name, "derivation", 0.85))
                            seen.add(second_name.lower())
        
        # Hypernyms (more general terms)
        for hypernym in synset.hypernyms()[:3]:
            for lemma in hypernym.lemmas():
                lemma_name = lemma.name().replace('_', ' ')
                if lemma_name.lower() not in seen:
                    results.append((lemma_name, "hypernym", 0.75))
                    seen.add(lemma_name.lower())
        
        # Hyponyms (more specific terms)
        for hyponym in synset.hyponyms()[:3]:
            for lemma in hyponym.lemmas():
                lemma_name = lemma.name().replace('_', ' ')
                if lemma_name.lower() not in seen:
                    results.append((lemma_name, "hyponym", 0.75))
                    seen.add(lemma_name.lower())
        
        # Also-see relations (related concepts)
        for also_see in synset.also_sees()[:2]:
            for lemma in also_see.lemmas():
                lemma_name = lemma.name().replace('_', ' ')
                if lemma_name.lower() not in seen:
                    results.append((lemma_name, "related", 0.70))
                    seen.add(lemma_name.lower())
    
    return results[:40] 
