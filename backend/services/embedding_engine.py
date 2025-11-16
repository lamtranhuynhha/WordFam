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

def get_embedding_neighbors(word: str, top_k: int = 20) -> List[Tuple[str, str, float]]:
    """
    Get semantically similar words using embeddings with expanded vocabulary.
    Returns list of tuples of (word, relation_type, score)
    """
    model = get_model()
    
    # Expanded vocabulary for better coverage
    common_words = [
        # Movement/Action
        "run", "running", "ran", "runner", "runs", "jog", "sprint", "dash", "race",
        "walk", "walking", "walked", "walker", "stroll", "march", "stride",
        "move", "moving", "movement", "moved", "motion", "shift",
        
        # Action/Activity
        "act", "action", "acting", "actor", "active", "activity", "activate",
        "react", "reaction", "reactive", "interact", "interaction", "transaction",
        "do", "doing", "done", "deed",
        "perform", "performance", "performer",
        
        # Creation
        "create", "creation", "creative", "creator", "creativity",
        "make", "making", "maker", "made",
        "build", "building", "builder", "built",
        "form", "forming", "formation", "formed",
        "construct", "construction", "constructive",
        
        # Cognition
        "think", "thinking", "thought", "thinker", "thoughtful",
        "consider", "consideration", "considerate",
        "reflect", "reflection", "reflective",
        "understand", "understanding",
        "know", "knowing", "knowledge", "known",
        
        # Communication
        "write", "writing", "written", "writer",
        "read", "reading", "reader",
        "speak", "speaking", "speaker", "speech",
        "talk", "talking", "talked",
        "say", "saying", "said",
        
        # Work/Effort
        "work", "working", "worker", "worked",
        "labor", "laborer",
        "effort", "endeavor",
        "try", "trying", "tried",
        
        # Learning/Teaching
        "teach", "teaching", "teacher", "taught",
        "learn", "learning", "learner", "learned",
        "study", "studying", "student", "studied",
        "educate", "education", "educational",
        
        # Support
        "help", "helping", "helper", "helped", "helpful",
        "assist", "assistance", "assistant",
        "support", "supporting", "supporter", "supported",
        
        # Change/Growth
        "change", "changing", "changed",
        "grow", "growing", "growth", "grown",
        "develop", "development", "developer", "developed",
        "evolve", "evolution", "evolutionary",
        "transform", "transformation",
        
        # Entertainment
        "play", "playing", "player", "played",
        "game", "gaming", "gamer",
        "enjoy", "enjoying", "enjoyment", "enjoyed",
        
        # Emotion
        "happy", "happiness", "happily",
        "sad", "sadness", "sadly",
        "joy", "joyful", "joyfully",
        "love", "loving", "loved", "lovely",
        "feel", "feeling", "felt",
    ]
    
    vocab = [w for w in common_words if w.lower() != word.lower()]
    
    if not vocab:
        return []
    
    try:
        word_embedding = model.encode([word])[0]
        vocab_embeddings = model.encode(vocab)
        
        # Calculate cosine similarities
        similarities = []
        for i, v_word in enumerate(vocab):
            sim = 1 - cosine(word_embedding, vocab_embeddings[i])
            similarities.append((v_word, sim))
        
        # Sort by highest score first
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results with higher threshold
        results = []
        for v_word, score in similarities[:top_k]:
            if score > 0.4:  # Increased threshold for better quality
                results.append((v_word, "semantic", float(score * 0.85)))  # Scale down slightly
        
        return results
    
    except Exception as e:
        logger.error(f"Error in embedding computation: {e}")
        return []
