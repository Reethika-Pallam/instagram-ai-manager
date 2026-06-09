"""Claude AI-powered caption generation using Anthropic API."""

import logging
from typing import List, Dict, Any, Literal
import json

from anthropic import Anthropic

from config.settings import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CAPTION_OPTIONS_COUNT,
    DEFAULT_CAPTION_TONE,
)

logger = logging.getLogger(__name__)


class ClaudeCaption:
    """Generate Instagram captions using Anthropic Claude API."""
    
    # Valid caption tones
    VALID_TONES = {'casual', 'professional', 'funny'}
    
    # Emoji styles for different tones
    EMOJI_STYLES = {
        'casual': ['🎉', '😎', '✨', '🔥', '💯', '🎯', '👀', '💫'],
        'professional': ['📈', '💼', '🎯', '📊', '✅', '🚀', '⭐', '📱'],
        'funny': ['😂', '🤣', '😜', '🎪', '🎭', '🤪', '😆', '🎉'],
    }
    
    def __init__(self):
        """Initialize Claude caption generator."""
        logger.info('Initializing Claude Caption Generator')
        self.client = Anthropic()
        self.api_key = ANTHROPIC_API_KEY
        self.model = CLAUDE_MODEL
    
    def generate_caption(
        self,
        input_text: str,
        tone: str = DEFAULT_CAPTION_TONE,
        include_hashtags: bool = True,
        hashtag_count: int = 10,
    ) -> str:
        """
        Generate a single Instagram caption using Claude.
        
        Args:
            input_text: Image description or reel description
            tone: Caption tone (casual, professional, funny)
            include_hashtags: Whether to include hashtags
            hashtag_count: Number of hashtags to include
            
        Returns:
            Generated caption string
        """
        if tone not in self.VALID_TONES:
            logger.warning(f'Invalid tone: {tone}. Using default: {DEFAULT_CAPTION_TONE}')
            tone = DEFAULT_CAPTION_TONE
        
        logger.info(f'Generating {tone} caption for: {input_text[:50]}...')
        
        try:
            prompt = self._build_prompt(
                input_text,
                tone,
                include_hashtags,
                hashtag_count,
            )
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            caption = message.content[0].text.strip()
            logger.info('Caption generated successfully')
            return caption
            
        except Exception as e:
            logger.error(f'Failed to generate caption: {str(e)}')
            raise
    
    def generate_multiple_captions(
        self,
        input_text: str,
        tone: str = DEFAULT_CAPTION_TONE,
        count: int = None,
        include_hashtags: bool = True,
        hashtag_count: int = 10,
    ) -> List[str]:
        """
        Generate multiple caption options using Claude.
        
        Args:
            input_text: Image or reel description
            tone: Caption tone (casual, professional, funny)
            count: Number of captions to generate (default: CAPTION_OPTIONS_COUNT)
            include_hashtags: Whether to include hashtags
            hashtag_count: Number of hashtags per caption
            
        Returns:
            List of generated captions
        """
        if count is None:
            count = CAPTION_OPTIONS_COUNT
        
        if tone not in self.VALID_TONES:
            logger.warning(f'Invalid tone: {tone}. Using default: {DEFAULT_CAPTION_TONE}')
            tone = DEFAULT_CAPTION_TONE
        
        logger.info(f'Generating {count} {tone} captions')
        
        try:
            prompt = self._build_multiple_prompt(
                input_text,
                tone,
                count,
                include_hashtags,
                hashtag_count,
            )
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            captions = self._parse_multiple_captions(response_text, count)
            
            logger.info(f'Generated {len(captions)} captions')
            return captions
            
        except Exception as e:
            logger.error(f'Failed to generate multiple captions: {str(e)}')
            raise
    
    def _build_prompt(
        self,
        input_text: str,
        tone: str,
        include_hashtags: bool,
        hashtag_count: int,
    ) -> str:
        """
        Build the prompt for single caption generation.
        
        Args:
            input_text: Description of the content
            tone: Desired tone
            include_hashtags: Whether to include hashtags
            hashtag_count: Number of hashtags
            
        Returns:
            Formatted prompt string
        """
        emoji_examples = ', '.join(self.EMOJI_STYLES[tone][:3])
        
        hashtag_instruction = (
            f"Include {hashtag_count} relevant hashtags at the end. "
            if include_hashtags
            else "Do not include hashtags. "
        )
        
        prompt = f"""Generate an Instagram caption with a {tone} tone for the following content:

Content: {input_text}

Requirements:
- Keep it engaging and authentic
- {hashtag_instruction}
- Use emojis that match this tone: {emoji_examples}
- Make it suitable for Instagram
- Keep it under 150 words
- Use line breaks for readability

Generate only the caption, nothing else."""
        
        return prompt
    
    def _build_multiple_prompt(
        self,
        input_text: str,
        tone: str,
        count: int,
        include_hashtags: bool,
        hashtag_count: int,
    ) -> str:
        """
        Build the prompt for multiple caption generation.
        
        Args:
            input_text: Description of the content
            tone: Desired tone
            count: Number of captions to generate
            include_hashtags: Whether to include hashtags
            hashtag_count: Number of hashtags
            
        Returns:
            Formatted prompt string
        """
        emoji_examples = ', '.join(self.EMOJI_STYLES[tone][:3])
        
        hashtag_instruction = (
            f"Include {hashtag_count} relevant hashtags at the end of each caption. "
            if include_hashtags
            else "Do not include hashtags. "
        )
        
        prompt = f"""Generate {count} different Instagram captions with a {tone} tone for the following content:

Content: {input_text}

Requirements for each caption:
- Keep each one engaging and unique from the others
- {hashtag_instruction}
- Use emojis that match this tone: {emoji_examples}
- Make them suitable for Instagram
- Keep each under 150 words
- Use line breaks for readability

Format your response as a numbered list (1., 2., etc.) with each caption separated by a blank line.
Generate only the captions, nothing else."""
        
        return prompt
    
    def _parse_multiple_captions(self, response_text: str, expected_count: int) -> List[str]:
        """
        Parse multiple captions from the API response.
        
        Args:
            response_text: Raw response from Claude
            expected_count: Expected number of captions
            
        Returns:
            List of parsed captions
        """
        captions = []
        
        # Split by numbered format (1., 2., 3., etc.)
        lines = response_text.strip().split('\n\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('Note'):
                # Remove numbering if present
                if line[0].isdigit() and '.' in line[:3]:
                    line = line.split('.', 1)[1].strip()
                
                if line:
                    captions.append(line)
        
        # Return first expected_count captions
        return captions[:expected_count]
    
    def generate_caption_variants(
        self,
        input_text: str,
        base_caption: str,
    ) -> Dict[str, List[str]]:
        """
        Generate caption variants in different tones for the same content.
        
        Args:
            input_text: Description of the content
            base_caption: Original caption to use as reference
            
        Returns:
            Dictionary with tones as keys and caption lists as values
        """
        logger.info('Generating caption variants in different tones')
        
        variants = {}
        for tone in self.VALID_TONES:
            try:
                captions = self.generate_multiple_captions(
                    input_text,
                    tone=tone,
                    count=2,
                )
                variants[tone] = captions
            except Exception as e:
                logger.error(f'Failed to generate {tone} variants: {str(e)}')
                variants[tone] = []
        
        return variants
    
    def optimize_caption(
        self,
        caption: str,
        target_tone: str = None,
    ) -> str:
        """
        Optimize an existing caption for better engagement.
        
        Args:
            caption: Original caption to optimize
            target_tone: Tone to optimize for (optional)
            
        Returns:
            Optimized caption
        """
        if target_tone and target_tone not in self.VALID_TONES:
            logger.warning(f'Invalid tone: {target_tone}')
            target_tone = None
        
        logger.info('Optimizing caption for engagement')
        
        try:
            tone_instruction = f"in a {target_tone} tone" if target_tone else ""
            
            prompt = f"""Optimize the following Instagram caption for better engagement {tone_instruction}:

Original caption: {caption}

Improvements to make:
- Enhance readability with better line breaks
- Add more compelling emojis if missing
- Improve call-to-action
- Ensure hashtags are relevant and trending
- Keep the core message intact

Return only the optimized caption."""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            optimized = message.content[0].text.strip()
            logger.info('Caption optimized successfully')
            return optimized
            
        except Exception as e:
            logger.error(f'Failed to optimize caption: {str(e)}')
            raise
