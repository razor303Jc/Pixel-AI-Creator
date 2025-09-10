import asyncio
import json
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx
from openai import AsyncOpenAI
from core.config import settings
from core.database import async_session, WebAnalysis, Client
from sqlalchemy import select, update
import structlog

logger = structlog.get_logger()

class WebAnalyzer:
    """Service for analyzing client websites and social media"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    async def analyze_website(self, url: str, client_id: int) -> Dict[str, Any]:
        """Analyze a client's website comprehensively"""
        logger.info("Starting website analysis", url=url, client_id=client_id)
        
        try:
            # Scrape website content
            content_data = await self._scrape_website(url)
            
            # Analyze with AI
            analysis_results = await self._ai_analyze_content(content_data, "website")
            
            # Store analysis in database
            await self._store_analysis(client_id, url, "website", analysis_results)
            
            # Update client record
            await self._update_client_analysis(client_id, "website_analysis", analysis_results)
            
            logger.info("Website analysis completed", url=url, client_id=client_id)
            return analysis_results
            
        except Exception as e:
            logger.error("Website analysis failed", url=url, error=str(e))
            raise
    
    async def analyze_social_media(self, platform: str, handle: str, client_id: int) -> Dict[str, Any]:
        """Analyze client's social media presence"""
        logger.info("Starting social media analysis", platform=platform, handle=handle, client_id=client_id)
        
        try:
            # Scrape social media content based on platform
            if platform.lower() == "twitter":
                content_data = await self._scrape_twitter(handle)
            elif platform.lower() == "instagram":
                content_data = await self._scrape_instagram(handle)
            elif platform.lower() == "linkedin":
                content_data = await self._scrape_linkedin(handle)
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Analyze with AI
            analysis_results = await self._ai_analyze_content(content_data, "social_media", platform)
            
            # Store analysis in database
            url = f"https://{platform}.com/{handle}"
            await self._store_analysis(client_id, url, "social_media", analysis_results, platform)
            
            # Update client record
            await self._update_client_analysis(client_id, "social_media_analysis", analysis_results)
            
            logger.info("Social media analysis completed", platform=platform, handle=handle, client_id=client_id)
            return analysis_results
            
        except Exception as e:
            logger.error("Social media analysis failed", platform=platform, handle=handle, error=str(e))
            raise
    
    async def _scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape website content using Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until="networkidle")
                
                # Get page content
                content = await page.content()
                title = await page.title()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract key information
                data = {
                    "url": url,
                    "title": title,
                    "meta_description": self._get_meta_description(soup),
                    "headings": self._extract_headings(soup),
                    "text_content": self._extract_text_content(soup),
                    "images": self._extract_images(soup),
                    "links": self._extract_links(soup),
                    "contact_info": self._extract_contact_info(soup),
                    "technologies": await self._detect_technologies(page),
                    "seo_data": self._analyze_seo(soup),
                    "page_structure": self._analyze_page_structure(soup)
                }
                
                return data
                
            finally:
                await browser.close()
    
    async def _scrape_twitter(self, handle: str) -> Dict[str, Any]:
        """Scrape Twitter profile (public content only)"""
        # Note: This is a simplified version. In production, use Twitter API
        url = f"https://twitter.com/{handle}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                return {
                    "platform": "twitter",
                    "handle": handle,
                    "profile_data": {
                        "bio": "Sample bio - would extract from API",
                        "follower_count": "Sample count",
                        "tweet_topics": ["business", "technology", "industry"],
                        "posting_frequency": "daily",
                        "engagement_style": "professional"
                    }
                }
            except Exception as e:
                logger.error("Twitter scraping failed", handle=handle, error=str(e))
                return {"platform": "twitter", "handle": handle, "error": str(e)}
    
    async def _scrape_instagram(self, handle: str) -> Dict[str, Any]:
        """Scrape Instagram profile (public content only)"""
        # Simplified version - would use Instagram API in production
        return {
            "platform": "instagram",
            "handle": handle,
            "profile_data": {
                "bio": "Sample Instagram bio",
                "post_types": ["photos", "stories", "reels"],
                "content_themes": ["business", "lifestyle", "products"],
                "posting_frequency": "3-4 times per week",
                "visual_style": "professional"
            }
        }
    
    async def _scrape_linkedin(self, handle: str) -> Dict[str, Any]:
        """Scrape LinkedIn profile (public content only)"""
        # Simplified version - would use LinkedIn API in production
        return {
            "platform": "linkedin",
            "handle": handle,
            "profile_data": {
                "headline": "Sample professional headline",
                "industry": "Sample industry",
                "company": "Sample company",
                "content_focus": ["industry insights", "thought leadership"],
                "network_size": "500+",
                "posting_style": "professional"
            }
        }
    
    async def _ai_analyze_content(self, content_data: Dict[str, Any], 
                                analysis_type: str, platform: str = None) -> Dict[str, Any]:
        """Use AI to analyze the scraped content"""
        
        prompt = f"""
        Analyze the following {analysis_type} content and provide insights for creating a custom AI assistant:

        Content Data: {json.dumps(content_data, indent=2)}

        Please provide a comprehensive analysis including:

        1. BUSINESS INSIGHTS:
           - What type of business this is
           - Target audience and customer segments
           - Key products/services offered
           - Unique value propositions
           - Business goals and objectives

        2. PERSONALITY TRAITS:
           - Communication style and tone
           - Brand personality characteristics
           - Professional vs casual approach
           - Key messaging themes

        3. TARGET AUDIENCE:
           - Demographics and psychographics
           - Customer pain points and needs
           - Preferred communication channels
           - Engagement preferences

        4. AI ASSISTANT RECOMMENDATIONS:
           - Recommended assistant type (chatbot, voice, automation)
           - Key features to implement
           - Conversation flows to prioritize
           - Integration opportunities

        5. CONTENT STRATEGY:
           - Topics the AI should be knowledgeable about
           - FAQ categories to cover
           - Business processes to automate
           - Customer journey touchpoints

        Provide the response as a JSON object with these categories.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert business analyst and AI consultant. Analyze the provided content and return insights as structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse AI response
            ai_analysis = json.loads(response.choices[0].message.content)
            
            return ai_analysis
            
        except Exception as e:
            logger.error("AI analysis failed", error=str(e))
            # Return fallback analysis
            return {
                "business_insights": {"error": "AI analysis failed", "fallback": True},
                "personality_traits": {"tone": "professional", "style": "helpful"},
                "target_audience": {"segment": "general business"},
                "ai_recommendations": {"type": "chatbot", "complexity": "basic"},
                "content_strategy": {"topics": ["general business inquiries"]}
            }
    
    # Helper methods for content extraction
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta.get('content', '') if meta else ''
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, list]:
        return {
            'h1': [h.get_text().strip() for h in soup.find_all('h1')],
            'h2': [h.get_text().strip() for h in soup.find_all('h2')],
            'h3': [h.get_text().strip() for h in soup.find_all('h3')]
        }
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text()[:5000]  # Limit content length
    
    def _extract_images(self, soup: BeautifulSoup) -> list:
        images = soup.find_all('img')
        return [img.get('src', '') for img in images[:10]]  # Limit to 10 images
    
    def _extract_links(self, soup: BeautifulSoup) -> list:
        links = soup.find_all('a', href=True)
        return [link['href'] for link in links[:20]]  # Limit to 20 links
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        text = soup.get_text()
        # Simple contact extraction (would be more sophisticated in production)
        return {
            "has_contact_form": bool(soup.find('form')),
            "has_phone": "phone" in text.lower() or "tel:" in text.lower(),
            "has_email": "@" in text,
            "has_address": any(word in text.lower() for word in ["address", "street", "city"])
        }
    
    async def _detect_technologies(self, page) -> list:
        """Detect technologies used on the website"""
        technologies = []
        
        # Check for common technologies
        try:
            # React
            if await page.evaluate("() => window.React !== undefined"):
                technologies.append("React")
            
            # WordPress
            if await page.evaluate("() => document.querySelector('meta[name=\"generator\"][content*=\"WordPress\"]') !== null"):
                technologies.append("WordPress")
            
            # Add more technology detection as needed
            
        except Exception:
            pass
        
        return technologies
    
    def _analyze_seo(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Basic SEO analysis"""
        return {
            "has_meta_description": bool(soup.find('meta', attrs={'name': 'description'})),
            "has_title": bool(soup.find('title')),
            "has_h1": bool(soup.find('h1')),
            "image_alt_texts": len([img for img in soup.find_all('img') if img.get('alt')])
        }
    
    def _analyze_page_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page structure"""
        return {
            "has_header": bool(soup.find('header')),
            "has_nav": bool(soup.find('nav')),
            "has_footer": bool(soup.find('footer')),
            "has_sidebar": bool(soup.find('aside')),
            "section_count": len(soup.find_all('section'))
        }
    
    async def _store_analysis(self, client_id: int, url: str, analysis_type: str, 
                            results: Dict[str, Any], platform: str = None):
        """Store analysis results in database"""
        async with async_session() as session:
            analysis = WebAnalysis(
                client_id=client_id,
                url=url,
                analysis_type=analysis_type,
                platform=platform,
                content_summary=json.dumps(results.get('content_summary', {})),
                key_features=results.get('key_features', {}),
                business_insights=results.get('business_insights', {}),
                personality_traits=results.get('personality_traits', {}),
                target_audience=results.get('target_audience', {}),
                page_structure=results.get('page_structure', {}),
                technologies_used=results.get('technologies', {}),
                seo_analysis=results.get('seo_data', {})
            )
            
            session.add(analysis)
            await session.commit()
    
    async def _update_client_analysis(self, client_id: int, field: str, data: Dict[str, Any]):
        """Update client record with analysis data"""
        async with async_session() as session:
            stmt = update(Client).where(Client.id == client_id).values(**{field: data})
            await session.execute(stmt)
            await session.commit()
