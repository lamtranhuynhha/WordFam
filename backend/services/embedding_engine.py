from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import numpy as np
from scipy.spatial.distance import cosine
import logging

logger = logging.getLogger(__name__)

_model = None

def get_model():
    """lazy load the embedding model"""
    global _model
    if _model is None:
        logger.info("Loading SentenceTransformer model")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_embedding_neighbors(word: str, top_k: int = 15) -> List[Tuple[str, str, float]]:
    """
    Get semantically similar words using embeddings
    Returns list of tuples of (word, relation_type, score)
    """
    model = get_model()
    
    # For now: Common English words vocab (subset for speed)
    # Later dev: load a full vocab list, may be from db
    vocab = [
        word,  # original word
        # common related words will be added by morphological engine
    ]
    
    common_words = [
        "run", "running", "ran", "runner", "runs",
        "walk", "walking", "walked", "walker",
        "act", "action", "acting", "actor", "active",
        "create", "creation", "creative", "creator",
        "think", "thinking", "thought", "thinker",
        "write", "writing", "written", "writer",
        "read", "reading", "reader",
        "play", "playing", "player", "played",
        "work", "working", "worker", "worked",
        "build", "building", "builder", "built",
        "teach", "teaching", "teacher", "taught",
        "learn", "learning", "learner", "learned",
        "help", "helping", "helper", "helped",
        "move", "moving", "movement", "moved",
        "change", "changing", "changed",
        "grow", "growing", "growth", "grown",
    ]
    
    vocab = [w for w in common_words if w.lower() != word.lower()]
    
    if not vocab:
        return []
    
    try:
        word_embedding = model.encode([word])[0]
        vocab_embeddings = model.encode(vocab)
        
        # Cal cosine similarities
        similarities = []
        for i, v_word in enumerate(vocab):
            sim = 1 - cosine(word_embedding, vocab_embeddings[i])
            similarities.append((v_word, sim))
        
        # highest score first
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results as (word, type, score) tuples
        results = []
        for v_word, score in similarities[:top_k]:
            if score > 0.3:
                results.append((v_word, "embedding", float(score)))
        
        return results
    
    except Exception as e:
        logger.error(f"Error in embedding computation: {e}")
        return []
