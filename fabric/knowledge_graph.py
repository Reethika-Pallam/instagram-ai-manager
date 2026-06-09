"""Knowledge graph for Instagram content relationships and recommendations."""

import logging
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
import networkx as nx
from datetime import datetime

logger = logging.getLogger(__name__)


class InstagramKnowledgeGraph:
    """
    Build and query a knowledge graph linking:
    - Content types
    - Posting times
    - Hashtags
    - Engagement metrics
    
    A knowledge graph is a network of interconnected nodes and edges
    that represent relationships between entities. This allows us to
    identify patterns and make recommendations based on correlations.
    """
    
    def __init__(self):
        """
        Initialize knowledge graph.
        
        Creates a directed graph where:
        - Nodes represent entities (content type, time, hashtag, metric)
        - Edges represent relationships (co-occurrence, causation)
        - Edge weights represent strength of relationship
        """
        logger.info('Initializing Instagram Knowledge Graph')
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.node_metadata = {}  # Store additional info about nodes
        self.edge_weights = defaultdict(float)  # Track relationship strengths
    
    def build_graph_from_posts(
        self,
        posts: List[Dict[str, Any]],
    ) -> None:
        """
        Build knowledge graph from Instagram post data.
        
        Logic:
        1. Extract entities from each post (content type, time, hashtags, metrics)
        2. Create nodes for each unique entity
        3. Create edges connecting related entities
        4. Weight edges based on engagement metrics
        5. Build relationship patterns
        
        Args:
            posts: List of Instagram posts with metadata and metrics
        """
        logger.info(f'Building knowledge graph from {len(posts)} posts')
        
        try:
            # Clear existing graph
            self.graph.clear()
            self.node_metadata.clear()
            
            # Process each post
            for post in posts:
                self._add_post_to_graph(post)
            
            logger.info(f'Knowledge graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges')
            
        except Exception as e:
            logger.error(f'Failed to build knowledge graph: {str(e)}')
            raise
    
    def _add_post_to_graph(self, post: Dict[str, Any]) -> None:
        """
        Add a single post and its relationships to the graph.
        
        Logic:
        1. Extract all entities (content type, posting time, hashtags, engagement)
        2. Create node for each entity
        3. Connect related entities with weighted edges
        4. Update edge weights based on engagement performance
        
        Args:
            post: Single Instagram post
        """
        # Extract entities
        content_type = post.get('media_type', 'unknown')
        timestamp = post.get('timestamp', '')
        caption = post.get('caption', '')
        
        # Extract posting hour and day
        posting_hour = self._extract_hour(timestamp)
        posting_day = self._extract_day(timestamp)
        
        # Extract hashtags
        hashtags = self._extract_hashtags(caption)
        
        # Extract engagement metrics
        engagement_score = self._calculate_engagement_score(post)
        
        # Add nodes
        self._add_node(f'type:{content_type}', 'content_type', {'name': content_type})
        self._add_node(f'hour:{posting_hour}', 'posting_time', {'hour': posting_hour})
        self._add_node(f'day:{posting_day}', 'posting_day', {'day': posting_day})
        self._add_node(f'engagement:high' if engagement_score > 0.5 else 'engagement:low', 'engagement_level', {})
        
        # Add hashtag nodes
        for hashtag in hashtags:
            self._add_node(f'hashtag:{hashtag}', 'hashtag', {'name': hashtag})
        
        # Add edges with weights
        # Content type -> Posting time relationship
        self._add_weighted_edge(
            f'type:{content_type}',
            f'hour:{posting_hour}',
            engagement_score,
            'posted_at'
        )
        
        # Content type -> Posting day relationship
        self._add_weighted_edge(
            f'type:{content_type}',
            f'day:{posting_day}',
            engagement_score,
            'posted_on'
        )
        
        # Content type -> Engagement relationship
        self._add_weighted_edge(
            f'type:{content_type}',
            f'engagement:high' if engagement_score > 0.5 else 'engagement:low',
            engagement_score,
            'generates'
        )
        
        # Hashtag -> Engagement relationships
        for hashtag in hashtags:
            self._add_weighted_edge(
                f'hashtag:{hashtag}',
                f'engagement:high' if engagement_score > 0.5 else 'engagement:low',
                engagement_score,
                'promotes'
            )
            
            # Content type -> Hashtag relationship
            self._add_weighted_edge(
                f'type:{content_type}',
                f'hashtag:{hashtag}',
                engagement_score,
                'uses'
            )
        
        # Time-based relationships
        self._add_weighted_edge(
            f'hour:{posting_hour}',
            f'day:{posting_day}',
            engagement_score,
            'occurs_on'
        )
    
    def query_recommendations(
        self,
        target_node: str,
        depth: int = 2,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Query knowledge graph to generate recommendations.
        
        Logic:
        1. Start from target node (e.g., current content type)
        2. Traverse graph up to specified depth
        3. Find paths leading to high engagement
        4. Score recommendation paths by weight
        5. Return top-k recommendations
        
        Args:
            target_node: Starting node (e.g., 'type:reel')
            depth: How many hops to explore
            top_k: Number of recommendations to return
            
        Returns:
            List of recommendations with reasoning
        """
        logger.info(f'Querying recommendations from node: {target_node}')
        
        if target_node not in self.graph:
            logger.warning(f'Node {target_node} not found in graph')
            return []
        
        recommendations = []
        
        try:
            # Find all paths leading to high engagement
            high_engagement_paths = self._find_high_engagement_paths(
                target_node,
                depth
            )
            
            # Score and rank paths
            scored_paths = [
                {
                    'path': path,
                    'score': score,
                    'recommendations': self._path_to_recommendations(path),
                }
                for path, score in high_engagement_paths
            ]
            
            # Sort by score and return top-k
            scored_paths.sort(key=lambda x: x['score'], reverse=True)
            recommendations = scored_paths[:top_k]
            
            logger.info(f'Generated {len(recommendations)} recommendations')
            return recommendations
            
        except Exception as e:
            logger.error(f'Failed to query recommendations: {str(e)}')
            return []
    
    def _find_high_engagement_paths(
        self,
        start_node: str,
        max_depth: int,
    ) -> List[Tuple[List[str], float]]:
        """
        Find all paths from start node to high engagement nodes.
        
        Logic:
        1. Use breadth-first search to explore all paths
        2. Track path weights and depths
        3. Only explore paths with sufficient edge weights
        4. Filter for high engagement endpoints
        
        Args:
            start_node: Starting node
            max_depth: Maximum path length
            
        Returns:
            List of (path, total_weight) tuples
        """
        paths = []
        
        # BFS to find paths
        queue = [(start_node, [start_node], 0, 0)]  # (node, path, depth, weight)
        
        while queue:
            current, path, depth, weight = queue.pop(0)
            
            # Stop if max depth reached
            if depth >= max_depth:
                # Check if end node is high engagement
                if 'engagement:high' in current:
                    paths.append((path, weight / max(1, len(path))))
                continue
            
            # Explore neighbors
            for neighbor in self.graph.successors(current):
                if neighbor not in path:  # Avoid cycles
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    edge_weight = edge_data.get('weight', 0.5) if edge_data else 0.5
                    
                    new_weight = weight + edge_weight
                    queue.append((neighbor, path + [neighbor], depth + 1, new_weight))
        
        return paths
    
    def _path_to_recommendations(self, path: List[str]) -> List[str]:
        """
        Convert a graph path to human-readable recommendations.
        
        Args:
            path: List of nodes in the path
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        for node in path:
            if node.startswith('type:'):
                content_type = node.split(':')[1]
                recommendations.append(f'Use {content_type} content')
            elif node.startswith('hour:'):
                hour = node.split(':')[1]
                recommendations.append(f'Post at {hour}:00')
            elif node.startswith('day:'):
                day = node.split(':')[1]
                recommendations.append(f'Post on {day}')
            elif node.startswith('hashtag:'):
                hashtag = node.split(':')[1]
                recommendations.append(f'Include #{hashtag}')
            elif node.startswith('engagement:'):
                level = node.split(':')[1]
                recommendations.append(f'This leads to {level} engagement')
        
        return recommendations
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dictionary with graph metrics
        """
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': self._get_node_types(),
            'graph_density': nx.density(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / max(1, self.graph.number_of_nodes()),
        }
    
    def _get_node_types(self) -> Dict[str, int]:
        """
        Count nodes by type.
        
        Returns:
            Dictionary with node type counts
        """
        type_counts = defaultdict(int)
        for node_id, metadata in self.node_metadata.items():
            node_type = metadata.get('type', 'unknown')
            type_counts[node_type] += 1
        return dict(type_counts)
    
    # ===== Helper Methods =====
    
    def _add_node(
        self,
        node_id: str,
        node_type: str,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Add a node to the graph."""
        if node_id not in self.graph:
            self.graph.add_node(node_id)
            self.node_metadata[node_id] = {
                'type': node_type,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat(),
            }
    
    def _add_weighted_edge(
        self,
        source: str,
        target: str,
        weight: float,
        relationship: str,
    ) -> None:
        """Add weighted edge to graph."""
        if source in self.graph and target in self.graph:
            self.graph.add_edge(
                source,
                target,
                weight=weight,
                relationship=relationship,
            )
    
    def _extract_hashtags(self, caption: str) -> Set[str]:
        """Extract hashtags from caption."""
        return set(tag.strip('#') for tag in caption.split() if tag.startswith('#'))
    
    def _extract_hour(self, timestamp: str) -> int:
        """Extract hour from ISO timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.hour
        except:
            return 0
    
    def _extract_day(self, timestamp: str) -> str:
        """Extract day name from ISO timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return days[dt.weekday()]
        except:
            return 'Unknown'
    
    def _calculate_engagement_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate engagement score (0-1) for a post.
        
        Logic:
        - Normalize engagement metrics
        - Weight by platform norms
        - Return score indicating performance level
        
        Args:
            post: Instagram post
            
        Returns:
            Engagement score between 0 and 1
        """
        likes = min(post.get('likes', 0) / 1000, 1)
        comments = min(post.get('comments', 0) / 100, 1)
        saves = min(post.get('saves', 0) / 200, 1)
        
        # Weighted average
        score = (likes * 0.4 + comments * 0.4 + saves * 0.2)
        return min(score, 1.0)
