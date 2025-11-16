from typing import List, Dict, Tuple, Set
from models.response import GraphNode, GraphEdge, GraphMeta, GraphResponse
from .wordnet_engine import get_wordnet_family
from .embedding_engine import get_embedding_neighbors
from .morph_engine import get_morphological_family
from .wolfram_service import get_wolfram_word_family, get_wolfram_info
from .datamuse_engine import get_datamuse_related, get_word_forms, check_etymology, validate_word
from .dictionary_service import get_word_definition
from utils.cache import cached
import logging
import asyncio

logger = logging.getLogger(__name__)

def merge_word_sources(
    wordnet_results: List[Tuple[str, str, float]],
    embedding_results: List[Tuple[str, str, float]],
    morph_results: List[Tuple[str, str, float]]
) -> Dict[str, Tuple[float, List[str]]]:
    """
    Merge results from different sources.
    Returns dict: word -> (max_score, [relation_types])
    """
    word_data = {}
    
    all_results = wordnet_results + embedding_results + morph_results
    
    for word, relation_type, score in all_results:
        if word not in word_data:
            word_data[word] = (score, [relation_type])
        else:
            current_score, types = word_data[word]
            new_score = max(current_score, score)

            if relation_type not in types:
                types.append(relation_type)
            word_data[word] = (new_score, types)
    
    return word_data

def build_edges(root_word: str, word_data: Dict[str, Tuple[float, List[str]]]) -> List[GraphEdge]:
    """
    Build edges connecting the root word to related words.
    """
    edges = []
    
    for word, (score, relation_types) in word_data.items():
        if word != root_word:
            edge_type = relation_types[0] if relation_types else "related"
            
            edges.append(GraphEdge(
                source=root_word,
                target=word,
                type=edge_type
            ))
    
    return edges

@cached
async def build_word_family_graph(word: str) -> GraphResponse:
    """
    Build a word formation tree (derivations only).
    Synonyms are returned as separate lists, not in the graph.
    """
    logger.info(f"Building word formation tree for: {word}")
    
    wordnet_results = get_wordnet_family(word)
    logger.info(f"WordNet found {len(wordnet_results)} results")
    
    try:
        datamuse_results = await get_datamuse_related(word)
        logger.info(f"Datamuse found {len(datamuse_results)} results")
    except Exception as e:
        logger.warning(f"Datamuse API failed: {e}")
        datamuse_results = []
    
    try:
        datamuse_forms = await get_word_forms(word)
        logger.info(f"Datamuse forms found {len(datamuse_forms)} results")
    except Exception as e:
        logger.warning(f"Datamuse forms failed: {e}")
        datamuse_forms = []
    
    try:
        embedding_results = get_embedding_neighbors(word)
        logger.info(f"Embeddings found {len(embedding_results)} results")
    except Exception as e:
        logger.warning(f"Embeddings failed: {e}")
        embedding_results = []
    
    morph_results = get_morphological_family(word)
    logger.info(f"Morphology found {len(morph_results)} results")
    
    # Free Dictionary API
    try:
        wolfram_meta = await get_wolfram_info(word)
    except:
        wolfram_meta = {"definition": None, "etymology": None, "usage": None}
    
    derivations = {}
    synonyms = []
    semantic_neighbors = []
    
    logger.info(f"Generating automatic morphological variants for: {word}")
    auto_variants = []
    
    if len(word) >= 4:
        # For adjectives (happy -> happiness, happily)
        variants_to_try = [
            f"{word}ness",      # happiness
            f"{word}ly",        # happily
            f"{word}er",        # happier
            f"{word}est",       # happiest
            f"un{word}",        # unhappy
        ]
        
        # Handle -y ending (happy -> happiness, happily)
        if word.endswith('y') and len(word) >= 4:
            stem = word[:-1]
            variants_to_try.extend([
                f"{stem}iness",   # happiness
                f"{stem}ily",     # happily
                f"{stem}ier",     # happier
                f"{stem}iest",    # happiest
            ])
        
        # Handle -e ending (create -> creation, creator)
        if word.endswith('e') and len(word) >= 4:
            stem = word[:-1]
            variants_to_try.extend([
                f"{stem}ion",     # creation
                f"{stem}or",      # creator
                f"{stem}ing",     # creating
            ])
        
        # Validate each variant
        for variant in variants_to_try:
            if variant != word:
                word_exists = await validate_word(variant)
                if word_exists:
                    auto_variants.append((variant, 'morphological', 0.92))
                    logger.info(f"✓ Auto-generated: {variant}")
    
    logger.info(f"Generated {len(auto_variants)} automatic variants")
    
    # Add auto-generated variants to derivations
    for w, rel_type, score in auto_variants:
        if w not in derivations:
            derivations[w] = (score, [rel_type])
    
    # Priority 1: WordNet derivations (validated with etymology)
    logger.info(f"Processing {len(wordnet_results)} WordNet results")
    wordnet_added = 0
    wordnet_rejected = 0
    
    for w, rel_type, score in wordnet_results:
        if rel_type in ['derivation', 'root']:
            if w == word:  # Root word always accepted
                derivations[w] = (score, [rel_type])
                wordnet_added += 1
            elif w not in derivations:
                word_lower = w.lower()
                root_lower = word.lower()
                
                if (word_lower.startswith(root_lower) or 
                    word_lower.endswith(root_lower) or 
                    root_lower in word_lower):

                    derivations[w] = (score, [rel_type])
                    wordnet_added += 1
                    logger.info(f"✓ WordNet derivation: {w}")
                else:
                    
                    is_derived = await check_etymology(w, word)
                    if is_derived:
                        derivations[w] = (score, [rel_type])
                        wordnet_added += 1
                        logger.info(f"✓ WordNet derivation: {w}")
                    else:
                        
                        wordnet_rejected += 1
                        logger.debug(f"✗ WordNet: {w} rejected as derivation (treating as synonym)")
                        if w not in synonyms:
                            synonyms.append(w)
        
        elif rel_type == 'synonym':
            if w not in synonyms:
                synonyms.append(w)
        elif rel_type in ['hypernym', 'hyponym', 'related']:
            
            if w not in semantic_neighbors:
                semantic_neighbors.append(w)
    
    logger.info(f"WordNet added {wordnet_added} derivations (rejected {wordnet_rejected} false derivations)")
    
    # Priority 2: Datamuse API (real words, validated with etymology AND existence)
    logger.info(f"Processing {len(datamuse_results)} Datamuse results")
    datamuse_added = 0
    max_to_check = 30  # Limit to avoid timeout
    for w, rel_type, score in datamuse_results[:max_to_check]:
        if rel_type == 'morphological':
   
            word_exists = await validate_word(w)
            if not word_exists:
                logger.debug(f"✗ Datamuse: {w} rejected (not a real word)")
                continue
            
            is_derived = await check_etymology(w, word)
            if is_derived and w not in derivations:
                derivations[w] = (score, [rel_type])
                datamuse_added += 1
                logger.info(f"✓ Datamuse: {w} (score: {score:.2f})")
        elif rel_type == 'semantic':
            
            word_exists = await validate_word(w)
            if word_exists and w not in synonyms:
                semantic_neighbors.append(w)
    
    logger.info(f"Datamuse added {datamuse_added} morphological derivations")
    
    logger.info(f"Processing {len(datamuse_forms)} Datamuse forms")
    forms_added = 0
    max_forms = 20  
    for w, rel_type, score in datamuse_forms[:max_forms]:
        
        word_exists = await validate_word(w)
        if not word_exists:
            logger.debug(f"✗ Form: {w} rejected (not a real word)")
            continue
            
        is_derived = await check_etymology(w, word)
        if is_derived and w not in derivations:
            derivations[w] = (score, [rel_type])
            forms_added += 1
            logger.info(f"✓ Form: {w} (score: {score:.2f})")
    
    logger.info(f"Datamuse forms added {forms_added} derivations")
    
    # Priority 3: Morphology (only if validated with etymology AND existence)
    logger.info(f"Processing {len(morph_results)} morphology results")
    morph_added = 0
    morph_rejected = 0
    max_morph = 25  
    for w, rel_type, score in morph_results[:max_morph]:
        if w not in derivations and len(w) > 3:
            
            word_exists = await validate_word(w)
            if not word_exists:
                morph_rejected += 1
                logger.debug(f"✗ Morph: {w} rejected (not a real word)")
                continue
            
            is_derived = await check_etymology(w, word)
            if is_derived:
                derivations[w] = (score, [rel_type])
                morph_added += 1
                logger.info(f"✓ Morph: {w} (score: {score:.2f})")
    
    logger.info(f"Morphology added {morph_added} derivations (rejected {morph_rejected} fake words)")
    
    # Priority 4: Embeddings (semantic only, also validate)
    for w, rel_type, score in embedding_results:
        if score > 0.5 and w not in semantic_neighbors:  # High threshold
            
            word_exists = await validate_word(w)
            if word_exists:
                semantic_neighbors.append(w)

    # Build nodes from derivations only (word formation tree)
    sorted_derivations = sorted(derivations.items(), key=lambda x: x[1][0], reverse=True)
    
    # Take top derivations
    max_nodes = 50 
    words_to_define = [word] + [w for w, _ in sorted_derivations[:max_nodes] if w != word]
    
    logger.info(f"Fetching definitions for {len(words_to_define)} words...")
    definition_tasks = [get_word_definition(w) for w in words_to_define]
    definitions = await asyncio.gather(*definition_tasks)
    
    word_definitions = {w: d for w, d in zip(words_to_define, definitions)}
    
    nodes = [GraphNode(
        id=word, 
        label=word, 
        score=1.0,
        definition=word_definitions.get(word)
    )]
    
    for w, (score, relation_types) in sorted_derivations[:max_nodes]:
        if w != word:
            nodes.append(GraphNode(
                id=w, 
                label=w, 
                score=score,
                definition=word_definitions.get(w)
            ))
    
    edges = []
    for w, (score, relation_types) in derivations.items():
        if w != word:
            edge_type = relation_types[0] if relation_types else "derivation"
            edges.append(GraphEdge(
                source=word,
                target=w,
                type=edge_type
            ))
    
    meta = GraphMeta(
        definition=wolfram_meta.get("definition"),
        etymology=wolfram_meta.get("etymology"),
        usage=wolfram_meta.get("usage")
    )
    
    response = GraphResponse(
        nodes=nodes,
        edges=edges,
        meta=meta,
        synonyms=synonyms[:20],  # Increased for more diversity
        semantic=semantic_neighbors[:15],  # Increased
        morphological=[w for w, (s, t) in derivations.items() if 'morphological' in t or 'base_form' in t][:15]  # Increased
    )
    
    logger.info(f"✅ Word family tree completed: {len(nodes)} nodes, {len(edges)} edges")
    logger.info(f"   📚 Synonyms: {len(response.synonyms)} | Semantic: {len(response.semantic)} | Morphological: {len(response.morphological)}")
    
    # Log top derivations for debugging
    if nodes:
        top_5 = [n.label for n in nodes[1:6]]  # Skip root word
        logger.info(f"   🎯 Top derivations: {', '.join(top_5) if top_5 else 'none'}")
    
    return response

def build_from_wolfram(word: str, wolfram_data: Dict) -> GraphResponse:
    """
    Convert Wolfram Cloud response to GraphResponse format.
    Wolfram provides: nodes, edges, metadata from WordData + FeatureExtraction.
    """
    nodes = []
    edges = []
    
    for node_data in wolfram_data.get('nodes', []):
        nodes.append(GraphNode(
            id=node_data['id'],
            label=node_data['label'],
            score=node_data.get('score', 0.8)
        ))
    
    for edge_data in wolfram_data.get('edges', []):
        edges.append(GraphEdge(
            source=edge_data['source'],
            target=edge_data['target'],
            type=edge_data.get('type', 'related')
        ))
    
    definitions = wolfram_data.get('definitions', [])
    meta = GraphMeta(
        definition=definitions[0] if definitions else None,
        etymology=None,
        usage=None
    )
    
    response = GraphResponse(
        nodes=nodes,
        edges=edges,
        meta=meta
    )
    
    metadata = wolfram_data.get('metadata', {})
    logger.info(f"✓ Wolfram graph: {len(nodes)} nodes, {len(edges)} edges | Source: {metadata.get('source')}")
    logger.info(f"✓ Wolfram capabilities: {', '.join(metadata.get('capabilities', []))}")
    
    return response

def build_word_family_graph_sync(word: str) -> GraphResponse:
    """
    Synchronous version of build_word_family_graph.
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(build_word_family_graph(word))
