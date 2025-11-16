from typing import List, Dict, Tuple, Set
from models.response import GraphNode, GraphEdge, GraphMeta, GraphResponse
from services.wordnet_engine import get_wordnet_family
from services.embedding_engine import get_embedding_neighbors
from services.morph_engine import get_morphological_family
from services.wolfram_service import get_wolfram_info, get_wolfram_word_family
from utils.cache import cached
import logging

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
    Build a complete word family graph.
    Primary: Wolfram Cloud API (full graph computation)
    Fallback: Python engines (WordNet + Embeddings + Morphology)
    """
    logger.info(f"Building graph for word: {word}")
    
    wolfram_graph = await get_wolfram_word_family(word)
    
    if wolfram_graph and wolfram_graph.get('nodes'):
        logger.info(f"✓ Using Wolfram Cloud (PRIMARY SOURCE)")
        return build_from_wolfram(word, wolfram_graph)
    
    # Fallback: Python engines
    logger.info(f"⚠ Wolfram unavailable, using Python engines (fallback)")
    
    wordnet_results = get_wordnet_family(word)
    logger.info(f"WordNet found {len(wordnet_results)} results")
    
    embedding_results = get_embedding_neighbors(word)
    logger.info(f"Embeddings found {len(embedding_results)} results")
    
    morph_results = get_morphological_family(word)
    logger.info(f"Morphology found {len(morph_results)} results")
    
    wolfram_meta = await get_wolfram_info(word)
    
    word_data = merge_word_sources(wordnet_results, embedding_results, morph_results)

    nodes = []
    
    nodes.append(GraphNode(
        id=word,
        label=word,
        score=1.0
    ))
    
    for w, (score, relation_types) in sorted(word_data.items(), key=lambda x: x[1][0], reverse=True):
        if w != word:
            nodes.append(GraphNode(
                id=w,
                label=w,
                score=round(score, 3)
            ))
    
    nodes = nodes[:50]
    
    node_ids = {node.id for node in nodes}
    edges = []
    
    for word_id, (score, relation_types) in word_data.items():
        if word_id != word and word_id in node_ids:
            edge_type = relation_types[0] if relation_types else "related"
            edges.append(GraphEdge(
                source=word,
                target=word_id,
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
        meta=meta
    )
    
    logger.info(f"Graph built: {len(nodes)} nodes, {len(edges)} edges")
    
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
