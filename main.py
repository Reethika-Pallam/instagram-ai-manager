#!/usr/bin/env python3
"""Main entry point for Instagram AI Manager application."""

import logging
import sys
from typing import Optional

from utils.logger import setup_logger
from config.settings import (
    ENABLE_ANALYTICS,
    ENABLE_PREDICTIONS,
    ENABLE_RECOMMENDATIONS,
    ENABLE_CAPTION_GENERATION,
)
from api.instagram_client import InstagramClient
from analytics.data_analyzer import DataAnalyzer
from analytics.predictions import ViewPredictionModel
from content.caption_generator import CaptionGenerator
from content.recommendations import ContentRecommender

# Setup logger
logger = setup_logger(__name__)


class InstagramAIManager:
    """Main application class for Instagram AI Management."""
    
    def __init__(self):
        """
        Initialize the Instagram AI Manager.
        
        Sets up all required components for Instagram management,
        analytics, predictions, and content recommendations.
        """
        logger.info('Initializing Instagram AI Manager')
        
        try:
            # Initialize API client
            self.instagram_client = InstagramClient()
            logger.info('Instagram API client initialized')
            
            # Initialize analytics components
            self.data_analyzer = DataAnalyzer()
            logger.info('Data analyzer initialized')
            
            # Initialize ML models
            if ENABLE_PREDICTIONS:
                self.prediction_model = ViewPredictionModel()
                logger.info('Prediction model initialized')
            else:
                self.prediction_model = None
            
            # Initialize content generators
            if ENABLE_CAPTION_GENERATION:
                self.caption_generator = CaptionGenerator()
                logger.info('Caption generator initialized')
            else:
                self.caption_generator = None
            
            if ENABLE_RECOMMENDATIONS:
                self.content_recommender = ContentRecommender()
                logger.info('Content recommender initialized')
            else:
                self.content_recommender = None
            
            logger.info('Instagram AI Manager initialized successfully')
            
        except Exception as e:
            logger.error(f'Failed to initialize Instagram AI Manager: {str(e)}')
            raise
    
    def fetch_analytics(self) -> Optional[dict]:
        """
        Fetch and analyze Instagram account analytics.
        
        Returns:
            Dictionary containing analytics data
        """
        if not ENABLE_ANALYTICS:
            logger.warning('Analytics disabled')
            return None
        
        logger.info('Fetching analytics...')
        
        try:
            # Fetch recent posts
            posts = self.instagram_client.get_recent_posts(limit=20)
            logger.info(f'Fetched {len(posts)} recent posts')
            
            # Fetch account info
            account_info = self.instagram_client.get_account_info()
            logger.info('Fetched account information')
            
            # Fetch audience demographics
            demographics = self.instagram_client.get_audience_demographics()
            logger.info('Fetched audience demographics')
            
            # Calculate average metrics
            avg_metrics = self.data_analyzer.calculate_average_metrics(posts)
            
            analytics_data = {
                'posts': posts,
                'account_info': account_info,
                'demographics': demographics,
                'average_metrics': avg_metrics,
            }
            
            logger.info('Analytics fetch completed')
            return analytics_data
            
        except Exception as e:
            logger.error(f'Failed to fetch analytics: {str(e)}')
            return None
    
    def generate_predictions(self, posts: list) -> Optional[dict]:
        """
        Generate view predictions for posts.
        
        Args:
            posts: List of posts to generate predictions for
            
        Returns:
            Dictionary containing predictions
        """
        if not ENABLE_PREDICTIONS or not self.prediction_model:
            logger.warning('Predictions disabled')
            return None
        
        logger.info('Generating predictions...')
        
        try:
            # Train model if needed
            if not self.prediction_model.is_trained:
                self.prediction_model.train(posts)
            
            # Generate predictions
            predictions = self.prediction_model.predict_batch(posts)
            
            logger.info(f'Generated predictions for {len(predictions)} posts')
            return {'predictions': predictions}
            
        except Exception as e:
            logger.error(f'Failed to generate predictions: {str(e)}')
            return None
    
    def get_recommendations(self, analytics_data: dict) -> Optional[dict]:
        """
        Get content recommendations based on analytics.
        
        Args:
            analytics_data: Analytics data from fetch_analytics()
            
        Returns:
            Dictionary containing recommendations
        """
        if not ENABLE_RECOMMENDATIONS or not self.content_recommender:
            logger.warning('Recommendations disabled')
            return None
        
        logger.info('Generating recommendations...')
        
        try:
            # Get posting time recommendations
            posting_times = self.content_recommender.suggest_posting_times(
                analytics_data.get('posts', []),
            )
            
            # Get content type recommendations
            content_types = self.content_recommender.recommend_content_types(
                account_niche='General',
                audience_data=analytics_data.get('demographics', {}),
            )
            
            # Get growth recommendations
            growth_tips = self.content_recommender.get_growth_recommendations(
                account_stats=analytics_data.get('account_info', {}),
                performance_trends={},
            )
            
            recommendations = {
                'posting_times': posting_times,
                'content_types': content_types,
                'growth_tips': growth_tips,
            }
            
            logger.info('Recommendations generated')
            return recommendations
            
        except Exception as e:
            logger.error(f'Failed to generate recommendations: {str(e)}')
            return None
    
    def generate_captions(
        self,
        topic: str,
        post_type: str = 'photo',
        count: int = 3,
    ) -> Optional[list]:
        """
        Generate captions for a post.
        
        Args:
            topic: Topic for the caption
            post_type: Type of post (photo, reel, carousel)
            count: Number of caption options to generate
            
        Returns:
            List of generated captions
        """
        if not ENABLE_CAPTION_GENERATION or not self.caption_generator:
            logger.warning('Caption generation disabled')
            return None
        
        logger.info(f'Generating {count} captions for {topic}')
        
        try:
            captions = self.caption_generator.generate_multiple_captions(
                post_type=post_type,
                topic=topic,
                count=count,
            )
            logger.info(f'Generated {len(captions)} captions')
            return captions
            
        except Exception as e:
            logger.error(f'Failed to generate captions: {str(e)}')
            return None
    
    def run(self):
        """
        Run the main application workflow.
        
        Executes the complete Instagram AI management pipeline:
        1. Fetch analytics
        2. Generate predictions
        3. Get recommendations
        4. Generate sample captions
        """
        logger.info('Starting Instagram AI Manager workflow')
        
        try:
            # Step 1: Fetch analytics
            analytics_data = self.fetch_analytics()
            if not analytics_data:
                logger.warning('No analytics data available')
                return
            
            # Step 2: Generate predictions
            if ENABLE_PREDICTIONS:
                predictions = self.generate_predictions(
                    analytics_data.get('posts', [])
                )
                logger.info(f'Predictions: {predictions}')
            
            # Step 3: Get recommendations
            if ENABLE_RECOMMENDATIONS:
                recommendations = self.get_recommendations(analytics_data)
                logger.info(f'Recommendations: {recommendations}')
            
            # Step 4: Generate sample captions
            if ENABLE_CAPTION_GENERATION:
                captions = self.generate_captions(
                    topic='AI and Machine Learning',
                    post_type='photo',
                    count=3,
                )
                logger.info(f'Generated captions: {captions}')
            
            logger.info('Instagram AI Manager workflow completed successfully')
            
        except Exception as e:
            logger.error(f'Workflow execution failed: {str(e)}')
            sys.exit(1)


def main():
    """
    Main function - entry point for the application.
    """
    try:
        manager = InstagramAIManager()
        manager.run()
    except KeyboardInterrupt:
        logger.info('Application interrupted by user')
        sys.exit(0)
    except Exception as e:
        logger.error(f'Fatal error: {str(e)}')
        sys.exit(1)


if __name__ == '__main__':
    main()
