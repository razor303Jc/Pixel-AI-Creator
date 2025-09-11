import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from services.web_analyzer import WebAnalyzer
from services.ai_generator import AIAssistantGenerator
from services.client_manager import ClientManager


class TestWebAnalyzer:
    """Test WebAnalyzer service"""

    @pytest.fixture
    def web_analyzer(self):
        return WebAnalyzer()

    @pytest.mark.asyncio
    async def test_scrape_website_basic(self, web_analyzer):
        """Test basic website scraping functionality"""
        with patch("services.web_analyzer.async_playwright") as mock_playwright:
            # Mock playwright components
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.content.return_value = "<html><head><title>Test</title></head><body><h1>Test Site</h1></body></html>"
            mock_page.title.return_value = "Test Site"
            mock_browser.new_page.return_value = mock_page

            mock_p = AsyncMock()
            mock_p.chromium.launch.return_value = mock_browser
            mock_playwright.return_value.__aenter__.return_value = mock_p

            # Test scraping
            result = await web_analyzer._scrape_website("https://test.com")

            assert result["url"] == "https://test.com"
            assert result["title"] == "Test Site"
            assert "headings" in result
            assert "text_content" in result

    @pytest.mark.asyncio
    async def test_ai_analyze_content(self, web_analyzer):
        """Test AI content analysis"""
        mock_content = {
            "title": "Pizza Palace",
            "text_content": "Best pizza in town. Open daily 11AM-10PM.",
            "headings": {"h1": ["Welcome to Pizza Palace"]},
        }

        with patch.object(web_analyzer, "openai_client") as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = (
                '{"business_insights": {"type": "restaurant"}, "personality_traits": {"tone": "friendly"}}'
            )
            mock_openai.chat.completions.create.return_value = mock_response

            result = await web_analyzer._ai_analyze_content(mock_content, "website")

            assert "business_insights" in result
            assert "personality_traits" in result

    @pytest.mark.asyncio
    async def test_extract_headings(self, web_analyzer):
        """Test heading extraction"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <h1>Main Title</h1>
                <h2>Subtitle 1</h2>
                <h2>Subtitle 2</h2>
                <h3>Sub-subtitle</h3>
            </body>
        </html>
        """

        soup = BeautifulSoup(html, "html.parser")
        headings = web_analyzer._extract_headings(soup)

        assert len(headings["h1"]) == 1
        assert len(headings["h2"]) == 2
        assert len(headings["h3"]) == 1
        assert "Main Title" in headings["h1"]


class TestAIAssistantGenerator:
    """Test AIAssistantGenerator service"""

    @pytest.fixture
    def ai_generator(self):
        return AIAssistantGenerator()

    @pytest.mark.asyncio
    async def test_generate_personality(self, ai_generator):
        """Test personality generation"""
        mock_client_data = {
            "client": {
                "name": "Test Client",
                "company": "Test Restaurant",
                "industry": "Food & Beverage",
            }
        }

        with patch.object(ai_generator, "openai_client") as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[
                0
            ].message.content = """
            {
                "communication_style": "friendly",
                "tone": "warm and welcoming",
                "traits": ["helpful", "knowledgeable"],
                "response_patterns": ["question answering"],
                "conversation_style": "casual but professional",
                "brand_alignment": "restaurant values",
                "guidelines": ["always be helpful"]
            }
            """
            mock_openai.chat.completions.create.return_value = mock_response

            result = await ai_generator._generate_personality(
                mock_client_data, "chatbot"
            )

            assert "communication_style" in result
            assert "tone" in result
            assert result["communication_style"] == "friendly"

    @pytest.mark.asyncio
    async def test_generate_chatbot_code(self, ai_generator):
        """Test chatbot code generation"""
        mock_client_data = {
            "client": {
                "company": "Test Restaurant",
                "industry": "Food & Beverage",
                "website": "https://test.com",
            }
        }

        mock_personality = {"communication_style": "friendly", "tone": "warm"}

        mock_flows = {"welcome_message": "Welcome to our restaurant!"}

        result = await ai_generator._generate_chatbot_code(
            mock_client_data, mock_personality, mock_flows, "basic"
        )

        assert "class TestRestaurantChatbot:" in result
        assert "def __init__" in result
        assert "async def respond" in result
        assert mock_client_data["client"]["company"] in result

    @pytest.mark.asyncio
    async def test_generate_deployment_config(self, ai_generator):
        """Test deployment configuration generation"""
        mock_client_data = {
            "client": {"company": "Test Restaurant", "website": "https://test.com"}
        }

        result = await ai_generator._generate_deployment_config(
            mock_client_data, "chatbot"
        )

        assert "container_name" in result
        assert "image_name" in result
        assert "environment_variables" in result
        assert "docker_compose" in result
        assert "testrestaurant" in result["container_name"]


class TestClientManager:
    """Test ClientManager service"""

    @pytest.fixture
    def client_manager(self):
        return ClientManager()

    @pytest.mark.asyncio
    async def test_generate_qa_insights(self, client_manager):
        """Test Q&A insights generation"""
        mock_qa_pairs = [
            {"question": "What are your hours?", "answer": "9AM-9PM daily"},
            {"question": "Do you take reservations?", "answer": "Yes, call us"},
            {"question": "What's your pricing?", "answer": "Varies by item"},
        ]

        insights = await client_manager._generate_qa_insights(mock_qa_pairs)

        assert insights["total_questions"] == 3
        assert "business_requirements" in insights
        assert "recommended_features" in insights
        assert "client_concerns" in insights

    @pytest.mark.asyncio
    async def test_empty_qa_insights(self, client_manager):
        """Test insights generation with no Q&A data"""
        insights = await client_manager._generate_qa_insights([])

        assert "No Q&A data" in insights["message"]


class TestErrorHandling:
    """Test error handling across services"""

    @pytest.mark.asyncio
    async def test_web_analyzer_network_error(self):
        """Test web analyzer handles network errors gracefully"""
        web_analyzer = WebAnalyzer()

        with patch("services.web_analyzer.async_playwright") as mock_playwright:
            mock_playwright.side_effect = Exception("Network error")

            with pytest.raises(Exception) as exc_info:
                await web_analyzer._scrape_website("https://invalid-url.com")

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ai_generator_openai_error(self):
        """Test AI generator handles OpenAI API errors"""
        ai_generator = AIAssistantGenerator()

        with patch.object(ai_generator, "openai_client") as mock_openai:
            mock_openai.chat.completions.create.side_effect = Exception(
                "OpenAI API error"
            )

            with pytest.raises(Exception) as exc_info:
                await ai_generator._generate_personality({}, "chatbot")

            assert "OpenAI API error" in str(exc_info.value)


class TestDataValidation:
    """Test data validation and sanitization"""

    def test_extract_contact_info(self):
        """Test contact information extraction"""
        web_analyzer = WebAnalyzer()
        from bs4 import BeautifulSoup

        html_with_contact = """
        <html>
            <body>
                <p>Call us at phone: 555-1234</p>
                <p>Email: info@test.com</p>
                <form><input type="email"></form>
                <p>Address: 123 Main Street, City</p>
            </body>
        </html>
        """

        soup = BeautifulSoup(html_with_contact, "html.parser")
        contact_info = web_analyzer._extract_contact_info(soup)

        assert contact_info["has_phone"] is True
        assert contact_info["has_email"] is True
        assert contact_info["has_contact_form"] is True
        assert contact_info["has_address"] is True

    def test_seo_analysis(self):
        """Test SEO analysis functionality"""
        web_analyzer = WebAnalyzer()
        from bs4 import BeautifulSoup

        html_with_seo = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <h1>Main Heading</h1>
                <img src="test.jpg" alt="Test image">
                <img src="test2.jpg">
            </body>
        </html>
        """

        soup = BeautifulSoup(html_with_seo, "html.parser")
        seo_analysis = web_analyzer._analyze_seo(soup)

        assert seo_analysis["has_title"] is True
        assert seo_analysis["has_meta_description"] is True
        assert seo_analysis["has_h1"] is True
        assert seo_analysis["image_alt_texts"] == 1


class TestConcurrency:
    """Test concurrent operations in services"""

    @pytest.mark.asyncio
    async def test_concurrent_analysis_requests(self):
        """Test multiple analysis requests can run concurrently"""
        web_analyzer = WebAnalyzer()

        with patch.object(web_analyzer, "_scrape_website") as mock_scrape:
            mock_scrape.return_value = {"url": "test", "title": "test", "headings": {}}

            with patch.object(web_analyzer, "_ai_analyze_content") as mock_analyze:
                mock_analyze.return_value = {"business_insights": {}}

                with patch.object(web_analyzer, "_store_analysis") as mock_store:
                    with patch.object(
                        web_analyzer, "_update_client_analysis"
                    ) as mock_update:
                        # Run multiple analyses concurrently
                        tasks = [
                            web_analyzer.analyze_website("https://test1.com", 1),
                            web_analyzer.analyze_website("https://test2.com", 2),
                            web_analyzer.analyze_website("https://test3.com", 3),
                        ]

                        results = await asyncio.gather(*tasks, return_exceptions=True)

                        # All should complete without exceptions
                        for result in results:
                            assert not isinstance(result, Exception)


class TestIntegrationServices:
    """Test service integration scenarios"""

    @pytest.mark.asyncio
    async def test_client_to_ai_generation_flow(self):
        """Test complete flow from client creation to AI generation"""
        client_manager = ClientManager()
        ai_generator = AIAssistantGenerator()

        # Mock database operations
        with patch("services.client_manager.async_session"), patch(
            "services.ai_generator.async_session"
        ):

            # Mock AI generator methods
            with patch.object(
                ai_generator, "_create_project_record"
            ) as mock_create, patch.object(
                ai_generator, "_get_client_context"
            ) as mock_context, patch.object(
                ai_generator, "_generate_personality"
            ) as mock_personality, patch.object(
                ai_generator, "_generate_conversation_flows"
            ) as mock_flows, patch.object(
                ai_generator, "_generate_code"
            ) as mock_code, patch.object(
                ai_generator, "_generate_deployment_config"
            ) as mock_config, patch.object(
                ai_generator, "_generate_training_data"
            ) as mock_training, patch.object(
                ai_generator, "_save_generated_assistant"
            ) as mock_save, patch.object(
                ai_generator, "_update_project_status"
            ) as mock_status:

                # Setup mocks
                mock_project = Mock()
                mock_project.id = 1
                mock_create.return_value = mock_project

                mock_context.return_value = {"client": {"name": "Test"}}
                mock_personality.return_value = {"tone": "friendly"}
                mock_flows.return_value = {"welcome": "Hello"}
                mock_code.return_value = "# Generated code"
                mock_config.return_value = {"container": "test"}
                mock_training.return_value = {"data": "training"}

                # Test the flow
                result = await ai_generator.generate_assistant(1, "chatbot", "basic")

                assert result["status"] == "completed"
                assert mock_create.called
                assert mock_save.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
