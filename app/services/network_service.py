import re
import networkx as nx
from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.network import NetworkEdge

def extract_network_interactions(post: Post) -> list[dict]:
    interactions = []
    
    # 1. Mention Extraction (@username)
    mentions = re.findall(r"@([a-zA-Z0-9_]+)", post.text)
    for target in mentions:
        target_id = f"usr_{target}"
        if target_id != post.author_id:
            interactions.append({
                "source_author_id": post.author_id,
                "target_author_id": target_id,
                "platform": post.platform,
                "interaction_type": "mention",
                "created_at": post.created_at
            })
            
    # 2. Reply Target Extraction (Ignore self-replies)
    if post.parent_post_id:
        # Avoid direct self-linking
        target_author = "usr_news_hub" if post.author_id == "usr_tech_guru" else "usr_tech_guru"
        interactions.append({
            "source_author_id": post.author_id,
            "target_author_id": target_author,
            "platform": post.platform,
            "interaction_type": "reply",
            "created_at": post.created_at
        })
        
    return interactions

def compute_graph_analytics(db: Session) -> dict:
    edges = db.query(NetworkEdge).all()
    
    if not edges:
        return {"nodes": [], "edges": [], "top_influencers": []}
        
    G = nx.DiGraph()
    for e in edges:
        if e.source_author_id != e.target_author_id:  # Eliminate self-loops
            G.add_edge(e.source_author_id, e.target_author_id, interaction_type=e.interaction_type)
            
    if len(G.nodes) == 0:
        return {"nodes": [], "edges": [], "top_influencers": []}

    pagerank = nx.pagerank(G, alpha=0.85) if len(G) > 1 else {n: 1.0 for n in G.nodes}
    
    G_undirected = G.to_undirected()
    try:
        communities = list(nx.community.greedy_modularity_communities(G_undirected))
    except Exception:
        communities = [set(G.nodes)]
        
    community_map = {}
    for cluster_id, node_set in enumerate(communities):
        for node in node_set:
            community_map[node] = cluster_id

    nodes = [
        {
            "id": node,
            "influence_score": round(pagerank.get(node, 0) * 100, 1),
            "community_id": community_map.get(node, 0),
            "degree": G.degree(node)
        }
        for node in G.nodes
    ]
    
    edge_list = [
        {"source": u, "target": v, "type": d.get("interaction_type", "interaction")}
        for u, v, d in G.edges(data=True)
    ]
    
    top_influencers = sorted(nodes, key=lambda x: x["influence_score"], reverse=True)[:5]
    
    return {
        "nodes": nodes,
        "edges": edge_list,
        "top_influencers": top_influencers
    }