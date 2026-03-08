"""
Web scraper utility for news and content sources
Uses urllib for HTTP requests and basic HTML parsing
"""
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
import json
import re
from html.parser import HTMLParser
from typing import List, Dict, Optional, Any
import time


class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract text content"""

    def __init__(self):
        super().__init__()
        self.content = []
        self.title = ""
        self.in_title = False
        self.in_content = False
        self.skip_tags = {'script', 'style', 'nav', 'footer', 'header', 'aside'}
        self.current_tag = ""

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()

        if tag.lower() == 'title':
            self.in_title = True
        elif tag.lower() in {'p', 'div', 'article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'main', 'content'}:
            # Check for content-related attributes
            attrs_dict = dict(attrs) if attrs else {}
            class_name = attrs_dict.get('class', '').lower()
            id_name = attrs_dict.get('id', '').lower()

            # Look for content-related classes and IDs
            content_indicators = ['content', 'article', 'post', 'story', 'news', 'text', 'body', 'main']
            if any(indicator in class_name or indicator in id_name for indicator in content_indicators):
                self.in_content = True
            elif tag.lower() in {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                self.in_content = True
            elif tag.lower() in {'div', 'article', 'section', 'main'}:
                self.in_content = True
        elif tag.lower() in self.skip_tags:
            self.in_content = False

    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False
        elif tag.lower() in {'p', 'div', 'article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'main', 'content'}:
            self.in_content = False

        self.current_tag = ""

    def handle_data(self, data):
        data = data.strip()
        if data:
            if self.in_title:
                if not self.title:  # Only take first title found
                    self.title = data
            elif self.in_content and self.current_tag not in self.skip_tags:
                # Filter out very short content and navigation-like text
                if len(data) >= 10 and not any(skip_word in data.lower() for skip_word in ['클릭', 'more', 'read more', '더보기', '광고', 'ad', 'advertisement']):
                    self.content.append(data)

    def get_content(self) -> Dict[str, str]:
        """Get extracted content"""
        content_text = ' '.join(self.content)
        # Clean extra whitespace
        content_text = re.sub(r'\s+', ' ', content_text).strip()

        return {
            'title': self.title.strip(),
            'content': content_text
        }


class WebScraper:
    def __init__(self, delay: float = 1.0):
        """Initialize web scraper with request delay"""
        self.delay = delay
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def fetch_url(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Fetch and parse a web page"""
        try:
            # Add delay to be respectful
            time.sleep(self.delay)

            req = urllib.request.Request(url, headers=self.session_headers)

            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Get content type and encoding
                content_type = response.getheader('Content-Type', '')
                encoding = 'utf-8'  # Default encoding

                if 'charset=' in content_type:
                    encoding = content_type.split('charset=')[1].split(';')[0]

                html_content = response.read()

                # Decode with proper encoding
                try:
                    html_content = html_content.decode(encoding)
                except UnicodeDecodeError:
                    # Fallback to common encodings
                    for enc in ['utf-8', 'euc-kr', 'cp949']:
                        try:
                            html_content = html_content.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        html_content = html_content.decode('utf-8', errors='ignore')

                # Parse content
                parsed_content = self._parse_html(html_content)

                return {
                    'url': url,
                    'status_code': response.getcode(),
                    'title': parsed_content['title'],
                    'content': parsed_content['content'],
                    'success': True
                }

        except HTTPError as e:
            return {
                'url': url,
                'status_code': e.code,
                'error': f'HTTP Error: {e.code} - {e.reason}',
                'success': False
            }
        except URLError as e:
            return {
                'url': url,
                'error': f'URL Error: {str(e)}',
                'success': False
            }
        except Exception as e:
            return {
                'url': url,
                'error': f'Unexpected error: {str(e)}',
                'success': False
            }

    def _parse_html(self, html: str) -> Dict[str, str]:
        """Parse HTML content to extract title and text"""
        parser = SimpleHTMLParser()
        parser.feed(html)
        result = parser.get_content()

        # If no title found, try meta tags
        if not result['title']:
            meta_title_pattern = r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']'
            meta_match = re.search(meta_title_pattern, html, re.IGNORECASE)
            if meta_match:
                result['title'] = meta_match.group(1)

        # If still no content, try to extract from common patterns
        if not result['content'] or len(result['content']) < 100:
            # Try to find main content areas
            content_patterns = [
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                r'<article[^>]*>(.*?)</article>',
                r'<main[^>]*>(.*?)</main>',
                r'<div[^>]*class="[^"]*article[^"]*"[^>]*>(.*?)</div>'
            ]

            for pattern in content_patterns:
                matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
                if matches:
                    # Strip HTML tags and clean up
                    content_text = re.sub(r'<[^>]+>', ' ', ' '.join(matches))
                    content_text = re.sub(r'\s+', ' ', content_text).strip()
                    if len(content_text) > len(result['content']):
                        result['content'] = content_text
                    break

        return result

    def fetch_news_headlines(self, base_urls: List[str]) -> List[Dict[str, str]]:
        """Fetch headlines from news websites"""
        headlines = []

        for base_url in base_urls:
            try:
                result = self.fetch_url(base_url)

                if result['success']:
                    # Extract links that look like article URLs
                    article_links = self._extract_article_links(result['content'], base_url)

                    for link in article_links[:5]:  # Limit to 5 articles per site
                        article_result = self.fetch_url(link)

                        if article_result['success']:
                            headlines.append({
                                'title': article_result['title'],
                                'content': article_result['content'][:500],  # First 500 chars
                                'url': link,
                                'source': self._get_domain_name(base_url)
                            })

            except Exception as e:
                print(f"Error fetching {base_url}: {e}")
                continue

        return headlines

    def _extract_article_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract article links from HTML content"""
        links = []
        domain = self._get_domain_name(base_url)

        # Simple regex to find href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(href_pattern, html_content)

        for match in matches:
            # Skip non-article URLs
            if any(skip in match.lower() for skip in ['javascript:', 'mailto:', '#', 'css', 'js', 'img']):
                continue

            # Convert relative URLs to absolute
            if match.startswith('/'):
                link = f"https://{domain}{match}"
            elif match.startswith('http'):
                link = match
            else:
                continue

            # Filter for article-like URLs
            if any(indicator in match.lower() for indicator in ['article', 'news', 'story', '/view/', '/read/']):
                links.append(link)

        return list(set(links))  # Remove duplicates

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
        """Search Naver News (simple approach without API)"""
        try:
            # Encode query for URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}"

            result = self.fetch_url(search_url)

            if result['success']:
                # Parse search results (simplified)
                news_items = self._parse_naver_search_results(result['content'])
                return news_items[:max_results]

        except Exception as e:
            print(f"Error searching Naver news for '{query}': {e}")

        return []

    def _parse_naver_search_results(self, html_content: str) -> List[Dict]:
        """Parse Naver search results (simplified)"""
        news_items = []

        # Simple pattern to find news titles and links
        # This is a basic implementation - real scraping would be more sophisticated
        pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html_content)

        for link, title in matches:
            if 'news.naver.com' in link and len(title.strip()) > 10:
                news_items.append({
                    'title': title.strip(),
                    'link': link,
                    'source': 'Naver News'
                })

        return news_items

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

        # Test single URL
        test_url = "https://www.mk.co.kr/news/realestate/"
        result = scraper.fetch_url(test_url)

        if result['success']:
            print(f"Title: {result['title'][:50]}...")
            print(f"Content length: {len(result['content'])} characters")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

        print("\n=== 뉴스 사이트 스크래핑 테스트 ===")
        news_data = scraper.scrape_korean_news_sites()

        for site, articles in news_data.items():
            print(f"{site}: {len(articles)} articles")
            if articles:
                print(f"  Sample: {articles[0]['title'][:50]}...")

    except Exception as e:
        print(f"테스트 오류: {e}")


if __name__ == "__main__":
    test_web_scraper()