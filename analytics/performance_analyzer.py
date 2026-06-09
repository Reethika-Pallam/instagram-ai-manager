"""Instagram performance analytics and insights generation."""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import statistics

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze Instagram post performance and generate actionable insights."""
    
    # Performance metric weights for scoring
    METRIC_WEIGHTS = {
        'views': 0.25,
        'likes': 0.25,
        'comments': 0.30,
        'saves': 0.10,
        'reach': 0.10,
    }
    
    # Content types for classification
    CONTENT_TYPES = {
        'photo',
        'carousel',
        'reel',
        'story',
        'video',
    }
    
    def __init__(self):
        """Initialize performance analyzer."""
        logger.info('Initializing PerformanceAnalyzer')
    
    def analyze_performance(
        self,
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of Instagram post performance.
        
        Args:
            posts: List of posts with performance metrics and metadata
            
        Returns:
            Dictionary containing:
            - best_performing_content_type: Most successful content type
            - best_posting_times: Recommended posting times
            - best_posting_days: Recommended posting days
            - engagement_insights: Engagement metrics and trends
            - recommendations: Actionable recommendations
            - performance_summary: Overall performance summary
        """
        logger.info(f'Analyzing performance for {len(posts)} posts')
        
        if not posts:
            logger.warning('No posts provided for analysis')
            return self._empty_analysis()
        
        try:
            # Analyze content type performance
            content_analysis = self._analyze_content_types(posts)
            
            # Analyze posting times and days
            time_analysis = self._analyze_posting_times(posts)
            
            # Calculate engagement metrics
            engagement_metrics = self._calculate_engagement_metrics(posts)
            
            # Generate insights and recommendations
            insights = self._generate_insights(
                content_analysis,
                time_analysis,
                engagement_metrics,
                posts,
            )
            
            # Compile comprehensive results
            results = {
                'analysis_date': datetime.now().isoformat(),
                'posts_analyzed': len(posts),
                'best_performing_content_type': content_analysis['best_type'],
                'content_type_performance': content_analysis['type_metrics'],
                'best_posting_times': time_analysis['best_times'],
                'best_posting_days': time_analysis['best_days'],
                'posting_frequency_analysis': time_analysis['frequency_analysis'],
                'engagement_insights': engagement_metrics,
                'performance_trends': self._analyze_trends(posts),
                'recommendations': insights['recommendations'],
                'summary': insights['summary'],
            }
            
            logger.info('Performance analysis completed successfully')
            return results
            
        except Exception as e:
            logger.error(f'Performance analysis failed: {str(e)}')
            raise
    
    def _analyze_content_types(
        self,
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Identify which content type performs best.
        
        Logic:
        1. Group posts by content type
        2. Calculate average performance metrics for each type
        3. Score each type using weighted metrics
        4. Rank types by performance score
        
        Args:
            posts: List of posts with content type and metrics
            
        Returns:
            Dictionary with best performing content type and detailed metrics
        """
        logger.info('Analyzing content type performance')
        
        # Group posts by content type
        content_groups = defaultdict(list)
        for post in posts:
            content_type = post.get('media_type', 'unknown').lower()
            content_groups[content_type].append(post)
        
        # Calculate metrics for each content type
        type_metrics = {}
        for content_type, type_posts in content_groups.items():
            metrics = self._calculate_average_metrics(type_posts)
            
            # Calculate weighted engagement score (0-100)
            # Higher score = better performing content
            engagement_score = (
                (metrics['avg_likes'] / max(1, metrics['avg_reach'])) * 40 +
                (metrics['avg_comments'] / max(1, metrics['avg_likes'])) * 30 +
                (metrics['avg_saves'] / max(1, metrics['avg_reach'])) * 20 +
                (metrics['avg_views'] / max(1, metrics['avg_reach'])) * 10
            ) * 100
            
            type_metrics[content_type] = {
                'post_count': len(type_posts),
                'average_views': round(metrics['avg_views'], 2),
                'average_likes': round(metrics['avg_likes'], 2),
                'average_comments': round(metrics['avg_comments'], 2),
                'average_saves': round(metrics['avg_saves'], 2),
                'average_reach': round(metrics['avg_reach'], 2),
                'engagement_rate': round(metrics['engagement_rate'], 2),
                'performance_score': round(engagement_score, 2),
            }
        
        # Find best performing content type
        best_type = max(
            type_metrics.items(),
            key=lambda x: x[1]['performance_score'],
        )[0]
        
        logger.info(f'Best performing content type: {best_type}')
        
        return {
            'best_type': best_type,
            'type_metrics': type_metrics,
        }
    
    def _analyze_posting_times(
        self,
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Find the best days and times to post.
        
        Logic:
        1. Extract posting timestamps from posts
        2. Group performance by day of week and hour
        3. Calculate average engagement for each time slot
        4. Identify peak engagement hours and days
        
        Args:
            posts: List of posts with timestamp and metrics
            
        Returns:
            Dictionary with best posting times and days
        """
        logger.info('Analyzing posting times and days')
        
        # Group engagement by day of week and hour
        day_performance = defaultdict(lambda: {'total_engagement': 0, 'count': 0})
        hour_performance = defaultdict(lambda: {'total_engagement': 0, 'count': 0})
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for post in posts:
            # Extract timestamp
            timestamp_str = post.get('timestamp')
            if not timestamp_str:
                continue
            
            try:
                # Parse ISO 8601 timestamp
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                logger.warning(f'Could not parse timestamp: {timestamp_str}')
                continue
            
            # Calculate engagement score for this post
            engagement_score = self._calculate_engagement_score(post)
            
            # Group by day of week
            day_of_week = day_names[timestamp.weekday()]
            day_performance[day_of_week]['total_engagement'] += engagement_score
            day_performance[day_of_week]['count'] += 1
            
            # Group by hour of day
            hour = timestamp.hour
            hour_performance[hour]['total_engagement'] += engagement_score
            hour_performance[hour]['count'] += 1
        
        # Calculate average engagement for each time slot
        day_averages = {
            day: perf['total_engagement'] / perf['count']
            for day, perf in day_performance.items()
            if perf['count'] > 0
        }
        
        hour_averages = {
            hour: perf['total_engagement'] / perf['count']
            for hour, perf in hour_performance.items()
            if perf['count'] > 0
        }
        
        # Find top 3 best days
        best_days = sorted(
            day_averages.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        
        # Find top 3 best hours
        best_hours = sorted(
            hour_averages.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        
        # Convert hours to readable format
        best_times = [
            {
                'hour': hour,
                'time': f'{hour:02d}:00 - {hour + 1:02d}:00',
                'performance_score': round(score, 2),
            }
            for hour, score in best_hours
        ]
        
        logger.info(f'Best posting times identified: {best_times}')
        
        return {
            'best_days': [{'day': day, 'performance_score': round(score, 2)} for day, score in best_days],
            'best_times': best_times,
            'frequency_analysis': {
                'posts_per_day': len(posts) / 30 if posts else 0,  # Assuming 30-day period
                'days_with_posts': len(day_performance),
                'peak_posting_hour': max(hour_averages.items(), key=lambda x: x[1])[0] if hour_averages else 0,
            },
        }
    
    def _calculate_engagement_metrics(
        self,
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive engagement metrics.
        
        Logic:
        1. Extract key metrics from all posts
        2. Calculate average, median, min, max for each metric
        3. Calculate engagement rate (interactions/reach)
        4. Identify outliers and trends
        
        Args:
            posts: List of posts with metrics
            
        Returns:
            Dictionary with engagement statistics
        """
        logger.info('Calculating engagement metrics')
        
        # Extract metric lists
        views = [p.get('views', 0) for p in posts]
        likes = [p.get('likes', 0) for p in posts]
        comments = [p.get('comments', 0) for p in posts]
        saves = [p.get('saves', 0) for p in posts]
        reach = [p.get('reach', 0) for p in posts]
        
        # Calculate statistics for each metric
        metrics = {
            'views': self._calculate_stats(views),
            'likes': self._calculate_stats(likes),
            'comments': self._calculate_stats(comments),
            'saves': self._calculate_stats(saves),
            'reach': self._calculate_stats(reach),
        }
        
        # Calculate engagement rate
        engagement_rates = [
            (likes[i] + comments[i] + saves[i]) / max(1, reach[i])
            for i in range(len(posts))
        ]
        
        avg_engagement_rate = statistics.mean(engagement_rates) if engagement_rates else 0
        
        return {
            'total_posts': len(posts),
            'views': metrics['views'],
            'likes': metrics['likes'],
            'comments': metrics['comments'],
            'saves': metrics['saves'],
            'reach': metrics['reach'],
            'average_engagement_rate': round(avg_engagement_rate * 100, 2),
            'total_interactions': sum(likes) + sum(comments) + sum(saves),
        }
    
    def _analyze_trends(
        self,
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time.
        
        Logic:
        1. Divide posts into early and recent periods
        2. Compare metrics between periods
        3. Calculate trend direction (improving, declining, stable)
        4. Identify growth rate
        
        Args:
            posts: Chronologically ordered list of posts
            
        Returns:
            Dictionary with trend analysis
        """
        logger.info('Analyzing performance trends')
        
        if len(posts) < 2:
            return {'trend': 'insufficient_data', 'analysis': 'Need at least 2 posts for trend analysis'}
        
        # Split posts into early and recent (roughly 50/50)
        midpoint = len(posts) // 2
        early_posts = posts[:midpoint]
        recent_posts = posts[midpoint:]
        
        # Calculate average metrics for each period
        early_metrics = self._calculate_average_metrics(early_posts)
        recent_metrics = self._calculate_average_metrics(recent_posts)
        
        # Calculate growth rates (percentage change)
        growth_rates = {
            'views_growth': self._calculate_growth_rate(
                early_metrics['avg_views'],
                recent_metrics['avg_views'],
            ),
            'likes_growth': self._calculate_growth_rate(
                early_metrics['avg_likes'],
                recent_metrics['avg_likes'],
            ),
            'comments_growth': self._calculate_growth_rate(
                early_metrics['avg_comments'],
                recent_metrics['avg_comments'],
            ),
            'engagement_growth': self._calculate_growth_rate(
                early_metrics['engagement_rate'],
                recent_metrics['engagement_rate'],
            ),
        }
        
        # Determine overall trend
        avg_growth = statistics.mean(growth_rates.values())
        if avg_growth > 5:
            trend = 'improving'
        elif avg_growth < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'growth_rates': {k: round(v, 2) for k, v in growth_rates.items()},
            'average_growth': round(avg_growth, 2),
        }
    
    def _generate_insights(
        self,
        content_analysis: Dict[str, Any],
        time_analysis: Dict[str, Any],
        engagement_metrics: Dict[str, Any],
        posts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate actionable insights and recommendations.
        
        Args:
            content_analysis: Content type analysis results
            time_analysis: Posting time analysis results
            engagement_metrics: Engagement metrics
            posts: Original posts data
            
        Returns:
            Dictionary with insights and recommendations
        """
        logger.info('Generating insights and recommendations')
        
        recommendations = []
        
        # Content type recommendations
        best_type = content_analysis['best_type'].title()
        recommendations.append(
            f'Focus on {best_type} content - it has the highest engagement score'
        )
        
        # Posting time recommendations
        if time_analysis['best_times']:
            best_time = time_analysis['best_times'][0]['time']
            recommendations.append(
                f'Post during {best_time} for maximum engagement'
            )
        
        if time_analysis['best_days']:
            best_day = time_analysis['best_days'][0]['day']
            recommendations.append(
                f'{best_day} is your best performing day - increase posting frequency'
            )
        
        # Engagement recommendations
        avg_comments = engagement_metrics['comments']['average']
        if avg_comments < 5:
            recommendations.append(
                'Increase engagement with questions in captions or CTAs to boost comments'
            )
        
        # Reach recommendations
        avg_reach = engagement_metrics['reach']['average']
        avg_views = engagement_metrics['views']['average']
        if avg_views > 0 and avg_reach / avg_views < 0.5:
            recommendations.append(
                'Your reach is lower than views - use more relevant hashtags and location tags'
            )
        
        # Saves recommendations
        avg_saves = engagement_metrics['saves']['average']
        if avg_saves < avg_comments * 0.5:
            recommendations.append(
                'Increase saves by creating educational or inspirational content'
            )
        
        # Generate summary
        summary = {
            'total_posts_analyzed': len(posts),
            'average_engagement_rate': engagement_metrics['average_engagement_rate'],
            'total_interactions': engagement_metrics['total_interactions'],
            'most_effective_content': best_type,
            'peak_day': time_analysis['best_days'][0]['day'] if time_analysis['best_days'] else 'N/A',
            'peak_hour': time_analysis['best_times'][0]['time'] if time_analysis['best_times'] else 'N/A',
        }
        
        return {
            'recommendations': recommendations,
            'summary': summary,
        }
    
    # ===== Helper Methods =====
    
    def _calculate_average_metrics(self, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average metrics for a list of posts.
        
        Args:
            posts: List of posts with metrics
            
        Returns:
            Dictionary with average values
        """
        if not posts:
            return {
                'avg_views': 0,
                'avg_likes': 0,
                'avg_comments': 0,
                'avg_saves': 0,
                'avg_reach': 0,
                'engagement_rate': 0,
            }
        
        views = [p.get('views', 0) for p in posts]
        likes = [p.get('likes', 0) for p in posts]
        comments = [p.get('comments', 0) for p in posts]
        saves = [p.get('saves', 0) for p in posts]
        reach = [p.get('reach', 0) for p in posts]
        
        avg_reach = statistics.mean(reach) if reach else 0
        
        engagement_rate = (
            statistics.mean(likes) + 
            statistics.mean(comments) + 
            statistics.mean(saves)
        ) / max(1, avg_reach)
        
        return {
            'avg_views': statistics.mean(views) if views else 0,
            'avg_likes': statistics.mean(likes) if likes else 0,
            'avg_comments': statistics.mean(comments) if comments else 0,
            'avg_saves': statistics.mean(saves) if saves else 0,
            'avg_reach': avg_reach,
            'engagement_rate': engagement_rate,
        }
    
    def _calculate_engagement_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate weighted engagement score for a single post.
        
        Args:
            post: Post with metrics
            
        Returns:
            Engagement score (0-1)
        """
        # Normalize metrics to 0-1 range (using reasonable Instagram metrics)
        views = min(post.get('views', 0) / 100000, 1)
        likes = min(post.get('likes', 0) / 5000, 1)
        comments = min(post.get('comments', 0) / 500, 1)
        saves = min(post.get('saves', 0) / 1000, 1)
        reach = min(post.get('reach', 0) / 100000, 1)
        
        # Apply weights
        score = (
            views * self.METRIC_WEIGHTS['views'] +
            likes * self.METRIC_WEIGHTS['likes'] +
            comments * self.METRIC_WEIGHTS['comments'] +
            saves * self.METRIC_WEIGHTS['saves'] +
            reach * self.METRIC_WEIGHTS['reach']
        )
        
        return score
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate statistical measures for a list of values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Dictionary with average, median, min, max
        """
        if not values:
            return {'average': 0, 'median': 0, 'min': 0, 'max': 0}
        
        return {
            'average': round(statistics.mean(values), 2),
            'median': round(statistics.median(values), 2),
            'min': round(min(values), 2),
            'max': round(max(values), 2),
        }
    
    def _calculate_growth_rate(self, old_value: float, new_value: float) -> float:
        """
        Calculate percentage growth rate between two values.
        
        Args:
            old_value: Previous value
            new_value: Current value
            
        Returns:
            Percentage growth rate
        """
        if old_value == 0:
            return 0 if new_value == 0 else 100
        
        return ((new_value - old_value) / old_value) * 100
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """
        Return empty analysis structure.
        
        Returns:
            Empty analysis dictionary
        """
        return {
            'analysis_date': datetime.now().isoformat(),
            'posts_analyzed': 0,
            'best_performing_content_type': 'N/A',
            'content_type_performance': {},
            'best_posting_times': [],
            'best_posting_days': [],
            'engagement_insights': {},
            'performance_trends': {},
            'recommendations': ['Insufficient data for analysis'],
            'summary': {},
        }


# Convenience function for direct usage
def analyze_instagram_performance(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to analyze Instagram performance.
    
    Args:
        posts: List of Instagram posts with performance metrics
        
    Returns:
        Dictionary with comprehensive performance analysis
    """
    analyzer = PerformanceAnalyzer()
    return analyzer.analyze_performance(posts)
