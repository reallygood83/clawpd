"""
Web scraper utility for news and content sources
Uses requests + BeautifulSoup for robust HTML parsing
"""
import requests
import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import time
from datetime import datetime
import urllib.parse


class ArticleExtractor:
    """Enhanced article content extractor using BeautifulSoup"""

    def __init__(self):
        self.content_selectors = [
            'article', 'main', '.content', '.article', '.post',
            '.news-content', '.article-content', '.post-content',
            '.story-content', '.entry-content', '#content',
            '.article-body', '.news-body', '.post-body'
        ]

        self.title_selectors = [
            'h1', '.title', '.headline', '.article-title',
            '.post-title', '.news-title', 'title',
            '[property="og:title"]', '.entry-title'
        ]

    def extract(self, soup: BeautifulSoup, url: str = "") -> Dict[str, str]:
        """Extract title and content from BeautifulSoup object"""

        # Extract title
        title = self._extract_title(soup)

        # Extract main content
        content = self._extract_content(soup)

        # Extract additional metadata
        date = self._extract_date(soup)

        return {
            'title': title,
            'content': content,
            'date': date,
            'url': url
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""

        # Try various title selectors
        for selector in self.title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 5:
                    return title

        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        return "제목 없음"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""

        content_parts = []

        # Try content selectors in order of preference
        for selector in self.content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = self._clean_element_text(element)
                    if text and len(text) > 50:  # Minimum content length
                        content_parts.append(text)

                # If we found substantial content, use it
                if content_parts and sum(len(p) for p in content_parts) > 200:
                    break

        # If no content found with selectors, try paragraphs
        if not content_parts:
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = self._clean_element_text(p)
                if text and len(text) > 20:
                    content_parts.append(text)

        return ' '.join(content_parts) if content_parts else "내용을 추출할 수 없습니다"

    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication date"""

        date_selectors = [
            '[property="article:published_time"]',
            '.date', '.publish-date', '.article-date',
            'time', '.timestamp', '.created-date'
        ]

        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                # Try datetime attribute first
                date_text = element.get('datetime') or element.get('content') or element.get_text()
                if date_text:
                    return date_text.strip()

        return ""

    def _clean_element_text(self, element) -> str:
        """Clean text from HTML element"""
        if not element:
            return ""

        # Remove unwanted elements
        for unwanted in element.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'ad', 'advertisement']):
            unwanted.decompose()

        text = element.get_text(separator=' ')

        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove common noise patterns
        noise_patterns = [
            r'^\s*\[?\s*(광고|AD|Advertisement)\s*\]?\s*',
            r'^\s*\[?\s*(클릭|Click|More|더보기|Read More)\s*\]?\s*',
            r'^\s*\[?\s*(댓글|Comments?|Reply)\s*\]?\s*',
            r'^\s*\[?\s*(공유|Share|Like|좋아요)\s*\]?\s*'
        ]

        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text.strip()


class WebScraper:
    def __init__(self, delay: float = 1.0):
        """Initialize web scraper with request delay"""
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.article_extractor = ArticleExtractor()

    def fetch_url(self, url: str, timeout: int = 15) -> Dict[str, Any]:
        """Fetch and parse a web page using requests and BeautifulSoup"""
        try:
            # Add delay to be respectful
            time.sleep(self.delay)

            # Make request
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Handle encoding - requests usually handles this well
            if response.apparent_encoding and response.apparent_encoding != response.encoding:
                response.encoding = response.apparent_encoding

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract content using our enhanced extractor
            extracted_data = self.article_extractor.extract(soup, url)

            return {
                'url': url,
                'status_code': response.status_code,
                'title': extracted_data['title'],
                'content': extracted_data['content'],
                'date': extracted_data.get('date', ''),
                'success': True
            }

        except requests.exceptions.HTTPError as e:
            return {
                'url': url,
                'status_code': e.response.status_code if e.response else None,
                'error': f'HTTP Error: {e.response.status_code} - {e.response.reason}' if e.response else str(e),
                'success': False
            }
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'error': f'Request Error: {str(e)}',
                'success': False
            }
        except Exception as e:
            return {
                'url': url,
                'error': f'Unexpected error: {str(e)}',
                'success': False
            }

    def scrape_news_site(self, url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Scrape news articles from a website (method expected by source_collector)"""
        try:
            # First, get the main page
            main_result = self.fetch_url(url)
            if not main_result['success']:
                return []

            # Parse the main page to find article links
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'lxml')

            # Find article links
            article_links = self._extract_article_links_from_soup(soup, url)

            articles = []
            for link in article_links[:max_articles]:
                try:
                    article_result = self.fetch_url(link)
                    if article_result['success'] and len(article_result['content']) > 100:
                        articles.append({
                            'title': article_result['title'],
                            'content': article_result['content'][:500],  # First 500 chars for summary
                            'url': link,
                            'date': article_result.get('date', ''),
                            'source': self._get_domain_name(url)
                        })
                except Exception as e:
                    continue  # Skip failed articles

            return articles

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def _extract_article_links_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract article links from BeautifulSoup object"""
        links = []
        domain = self._get_domain_name(base_url)

        # Common article link selectors
        link_selectors = [
            'a[href*="/news/"]', 'a[href*="/article/"]', 'a[href*="/view/"]',
            'a[href*="/read/"]', 'a[href*="/story/"]', '.article-link a',
            '.news-link a', '.headline a', '.title a'
        ]

        for selector in link_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Convert to absolute URL
                    if href.startswith('/'):
                        full_url = f"https://{domain}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue

                    # Basic filtering
                    if self._is_article_url(full_url):
                        links.append(full_url)

        # Remove duplicates and limit
        return list(set(links))[:20]

    def _is_article_url(self, url: str) -> bool:
        """Check if URL looks like an article"""
        article_indicators = ['/news/', '/article/', '/view/', '/read/', '/story/']
        skip_indicators = ['javascript:', 'mailto:', '#', '.css', '.js', '.jpg', '.png', '.gif']

        return (any(indicator in url.lower() for indicator in article_indicators) and
                not any(skip in url.lower() for skip in skip_indicators))

    def fetch_news_headlines(self, base_urls: List[str]) -> List[Dict[str, str]]:
        """Fetch headlines from news websites"""
        headlines = []

        for base_url in base_urls:
            try:
                articles = self.scrape_news_site(base_url, max_articles=5)
                headlines.extend(articles)
            except Exception as e:
                print(f"Error fetching {base_url}: {e}")
                continue

        return headlines

    def _get_domain_name(self, url: str) -> str:
        """Extract domain name from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')

    def scrape_korean_news_sites(self) -> Dict[str, List[Dict]]:
        """Scrape common Korean news sites for content"""
        news_sites = {
            'mk': 'https://www.mk.co.kr/news/realestate/',  # 매경 부동산
            'hankyung': 'https://www.hankyung.com/realestate',  # 한경 부동산
            'chosun': 'https://www.chosun.com/economy/',  # 조선일보 경제
            'joongang': 'https://www.joongang.co.kr/economy/',  # 중앙일보 경제
        }

        all_news = {}

        for site_name, url in news_sites.items():
            try:
                print(f"Scraping {site_name}...")
                headlines = self.fetch_news_headlines([url])
                all_news[site_name] = headlines

                print(f"Found {len(headlines)} articles from {site_name}")

            except Exception as e:
                print(f"Error scraping {site_name}: {e}")
                all_news[site_name] = []

        return all_news

    def search_naver_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search Naver News using web scraping"""
        try:
            # Encode query for URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}"

            response = self.session.get(search_url, timeout=15)
            soup = BeautifulSoup(response.text, 'lxml')

            news_items = []

            # Find news articles in Naver search results
            news_links = soup.select('.news_tit')  # Naver news title selector

            for link_elem in news_links[:max_results]:
                try:
                    title = link_elem.get_text().strip()
                    href = link_elem.get('href')

                    if title and href and len(title) > 10:
                        news_items.append({
                            'title': title,
                            'url': href,
                            'source': 'Naver News'
                        })
                except Exception:
                    continue

            return news_items

        except Exception as e:
            print(f"Error searching Naver news for '{query}': {e}")
            return []

    def extract_trending_keywords(self, scraped_content: List[Dict]) -> List[Dict]:
        """Extract trending keywords from scraped content"""
        keyword_counts = {}

        for item in scraped_content:
            text = f"{item.get('title', '')} {item.get('content', '')}"

            # Extract Korean and English words
            words = re.findall(r'[\w가-힣]{2,}', text)

            for word in words:
                word_lower = word.lower()
                if len(word_lower) > 2:  # Filter short words
                    keyword_counts[word_lower] = keyword_counts.get(word_lower, 0) + 1

        # Convert to list and sort
        trending = []
        for keyword, count in keyword_counts.items():
            if count > 1:  # Appear in multiple articles
                trending.append({
                    'keyword': keyword,
                    'frequency': count,
                    'relevance_score': count * len(keyword)  # Simple relevance scoring
                })

        # Sort by relevance
        trending.sort(key=lambda x: x['relevance_score'], reverse=True)

        return trending[:20]  # Top 20

    def monitor_website_changes(self, url: str, check_interval: int = 3600) -> Dict:
        """Monitor a website for content changes"""
        # This would be implemented for continuous monitoring
        # For now, just return current content
        return self.fetch_url(url)

    def batch_scrape_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs efficiently"""
        results = []

        for url in urls:
            result = self.fetch_url(url)
            results.append(result)

            # Respectful delay between requests
            time.sleep(self.delay)

        return results


def test_web_scraper():
    """Test web scraper functionality"""
    try:
        scraper = WebScraper(delay=0.5)  # 0.5 second delay

        print("=== 웹 스크래퍼 테스트 ===")

        # Test single URL (the one mentioned in the critical issue)
        test_url = "https://www.mk.co.kr/news/realestate/"
        result = scraper.fetch_url(test_url)

        if result['success']:
            print(f"✅ SUCCESS - Title: {result['title'][:50]}...")
            print(f"✅ Content length: {len(result['content'])} characters")
            if len(result['content']) > 100:
                print("✅ Content extraction working properly")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

        print("\n=== 뉴스 사이트 스크래핑 테스트 ===")
        news_data = scraper.scrape_korean_news_sites()

        for site, articles in news_data.items():
            print(f"{site}: {len(articles)} articles")
            if articles:
                print(f"  Sample: {articles[0]['title'][:50]}...")

        print("\n=== 개별 기사 스크래핑 테스트 ===")
        articles = scraper.scrape_news_site("https://www.mk.co.kr/news/realestate/", max_articles=3)
        print(f"Found {len(articles)} articles from mk.co.kr")
        for i, article in enumerate(articles[:2]):
            print(f"  {i+1}. {article['title'][:50]}... ({len(article['content'])} chars)")

    except Exception as e:
        print(f"❌ 테스트 오류: {e}")


if __name__ == "__main__":
    test_web_scraper()