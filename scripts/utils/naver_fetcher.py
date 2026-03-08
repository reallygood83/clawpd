"""
Naver search and content fetcher
Handles Naver News, Cafe, and Blog searches
"""
import urllib.request
import urllib.parse
from urllib.error import HTTPError, URLError
import json
import re
import time
from typing import List, Dict, Optional, Any


class NaverFetcher:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, delay: float = 1.0):
        """Initialize Naver fetcher with optional API credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.delay = delay
        self.base_search_url = "https://search.naver.com/search.naver"

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
        }

        # If API credentials provided, use official API
        if self.client_id and self.client_secret:
            self.api_base_url = "https://openapi.naver.com/v1/search"
            self.headers.update({
                'X-Naver-Client-Id': self.client_id,
                'X-Naver-Client-Secret': self.client_secret
            })

    def search_news(self, query: str, max_results: int = 20, sort: str = 'sim') -> List[Dict]:
        """Search Naver News"""
        if self.client_id and self.client_secret:
            return self._api_search_news(query, max_results, sort)
        else:
            return self._web_search_news(query, max_results)

    def _api_search_news(self, query: str, max_results: int, sort: str) -> List[Dict]:
        """Search news using official Naver API"""
        try:
            params = {
                'query': query,
                'display': min(max_results, 100),  # Max 100 per request
                'sort': sort  # sim (similarity), date (recent)
            }

            url = f"{self.api_base_url}/news.json?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                news_items = []
                for item in data.get('items', []):
                    news_items.append({
                        'title': self._clean_html(item['title']),
                        'description': self._clean_html(item['description']),
                        'link': item['link'],
                        'pub_date': item['pubDate'],
                        'source': 'Naver News (API)',
                        'type': 'news'
                    })

                return news_items

        except Exception as e:
            print(f"Error using Naver News API: {e}")
            return self._web_search_news(query, max_results)

    def _web_search_news(self, query: str, max_results: int) -> List[Dict]:
        """Search news using web scraping (fallback)"""
        try:
            time.sleep(self.delay)

            params = {
                'where': 'news',
                'query': query,
                'sm': 'tab_jum'
            }

            url = f"{self.base_search_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')

            news_items = self._parse_news_results(html)
            return news_items[:max_results]

        except Exception as e:
            print(f"Error searching Naver news: {e}")
            return []

    def search_cafe(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search Naver Cafe posts"""
        if self.client_id and self.client_secret:
            return self._api_search_cafe(query, max_results)
        else:
            return self._web_search_cafe(query, max_results)

    def _api_search_cafe(self, query: str, max_results: int) -> List[Dict]:
        """Search cafe using official Naver API"""
        try:
            params = {
                'query': query,
                'display': min(max_results, 100),
                'sort': 'sim'
            }

            url = f"{self.api_base_url}/cafearticle.json?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                cafe_items = []
                for item in data.get('items', []):
                    cafe_items.append({
                        'title': self._clean_html(item['title']),
                        'description': self._clean_html(item['description']),
                        'link': item['link'],
                        'cafe_name': item.get('cafename', ''),
                        'cafe_url': item.get('cafeurl', ''),
                        'source': 'Naver Cafe (API)',
                        'type': 'cafe'
                    })

                return cafe_items

        except Exception as e:
            print(f"Error using Naver Cafe API: {e}")
            return self._web_search_cafe(query, max_results)

    def _web_search_cafe(self, query: str, max_results: int) -> List[Dict]:
        """Search cafe using web scraping"""
        try:
            time.sleep(self.delay)

            params = {
                'where': 'article',
                'query': query
            }

            url = f"{self.base_search_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')

            cafe_items = self._parse_cafe_results(html)
            return cafe_items[:max_results]

        except Exception as e:
            print(f"Error searching Naver cafe: {e}")
            return []

    def search_blog(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search Naver Blog posts"""
        if self.client_id and self.client_secret:
            return self._api_search_blog(query, max_results)
        else:
            return self._web_search_blog(query, max_results)

    def _api_search_blog(self, query: str, max_results: int) -> List[Dict]:
        """Search blog using official Naver API"""
        try:
            params = {
                'query': query,
                'display': min(max_results, 100),
                'sort': 'sim'
            }

            url = f"{self.api_base_url}/blog.json?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))

                blog_items = []
                for item in data.get('items', []):
                    blog_items.append({
                        'title': self._clean_html(item['title']),
                        'description': self._clean_html(item['description']),
                        'link': item['link'],
                        'blogger_name': item.get('bloggername', ''),
                        'blogger_link': item.get('bloggerlink', ''),
                        'post_date': item.get('postdate', ''),
                        'source': 'Naver Blog (API)',
                        'type': 'blog'
                    })

                return blog_items

        except Exception as e:
            print(f"Error using Naver Blog API: {e}")
            return self._web_search_blog(query, max_results)

    def _web_search_blog(self, query: str, max_results: int) -> List[Dict]:
        """Search blog using web scraping"""
        try:
            time.sleep(self.delay)

            params = {
                'where': 'post',
                'query': query
            }

            url = f"{self.base_search_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=self.headers)

            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')

            blog_items = self._parse_blog_results(html)
            return blog_items[:max_results]

        except Exception as e:
            print(f"Error searching Naver blog: {e}")
            return []

    def _parse_news_results(self, html: str) -> List[Dict]:
        """Parse news search results from HTML"""
        news_items = []

        # Pattern for news items (simplified - real implementation would be more robust)
        patterns = [
            r'<dt[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>.*?</dt>.*?<dd[^>]*>([^<]*)</dd>',
            r'<a[^>]*class="[^"]*news_tit[^"]*"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    link = match[0] if match[0].startswith('http') else f"https://news.naver.com{match[0]}"
                    title = self._clean_html(match[1])
                    description = self._clean_html(match[2]) if len(match) > 2 else ""

                    if title and len(title) > 5:
                        news_items.append({
                            'title': title,
                            'description': description,
                            'link': link,
                            'source': 'Naver News (Web)',
                            'type': 'news'
                        })

        return news_items

    def _parse_cafe_results(self, html: str) -> List[Dict]:
        """Parse cafe search results from HTML"""
        cafe_items = []

        # Simplified pattern for cafe results
        pattern = r'<a[^>]*href="([^"]*cafe[^"]*)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE)

        for match in matches:
            link, title = match
            title = self._clean_html(title)

            if title and len(title) > 5 and 'cafe.naver.com' in link:
                cafe_items.append({
                    'title': title,
                    'link': link,
                    'source': 'Naver Cafe (Web)',
                    'type': 'cafe'
                })

        return cafe_items

    def _parse_blog_results(self, html: str) -> List[Dict]:
        """Parse blog search results from HTML"""
        blog_items = []

        # Simplified pattern for blog results
        pattern = r'<a[^>]*href="([^"]*blog[^"]*)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE)

        for match in matches:
            link, title = match
            title = self._clean_html(title)

            if title and len(title) > 5 and 'blog.naver.com' in link:
                blog_items.append({
                    'title': title,
                    'link': link,
                    'source': 'Naver Blog (Web)',
                    'type': 'blog'
                })

        return blog_items

    def _clean_html(self, text: str) -> str:
        """Clean HTML tags and entities from text"""
        if not text:
            return ""

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Decode common HTML entities
        entities = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }

        for entity, char in entities.items():
            text = text.replace(entity, char)

        # Clean extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def search_comprehensive(self, query: str, include_types: List[str] = None) -> Dict[str, List[Dict]]:
        """Comprehensive search across multiple Naver services"""
        if include_types is None:
            include_types = ['news', 'cafe', 'blog']

        results = {}

        if 'news' in include_types:
            print(f"Searching news for: {query}")
            results['news'] = self.search_news(query, max_results=10)

        if 'cafe' in include_types:
            print(f"Searching cafe for: {query}")
            results['cafe'] = self.search_cafe(query, max_results=10)

        if 'blog' in include_types:
            print(f"Searching blog for: {query}")
            results['blog'] = self.search_blog(query, max_results=10)

        return results

    def get_trending_topics(self, niche: str) -> List[str]:
        """Get trending topics in a specific niche from Naver"""
        niche_queries = {
            'real_estate': ['부동산 투자', '아파트 시세', '재개발', '청약', '전세'],
            'finance': ['주식 투자', '코인', '재테크', '금리', '경제'],
            'tech': ['AI 기술', '스마트폰', '앱 개발', 'IT 트렌드'],
            'education': ['온라인 강의', '교육 프로그램', '자격증', '스킬업']
        }

        queries = niche_queries.get(niche, [niche])
        trending = []

        for query in queries:
            try:
                news_results = self.search_news(query, max_results=5)
                for item in news_results:
                    title = item['title']
                    # Extract keywords from title
                    keywords = re.findall(r'[\w가-힣]{2,}', title)
                    trending.extend(keywords)

            except Exception as e:
                print(f"Error getting trends for {query}: {e}")

        # Count frequency and return top keywords
        keyword_counts = {}
        for keyword in trending:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        # Sort and return top trending
        top_trending = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, count in top_trending[:20]]


def test_naver_fetcher():
    """Test Naver fetcher functionality"""
    try:
        # Test without API keys (web scraping mode)
        fetcher = NaverFetcher(delay=0.5)

        print("=== 네이버 뉴스 검색 테스트 ===")
        news_results = fetcher.search_news("부동산 투자", max_results=5)

        for i, item in enumerate(news_results, 1):
            print(f"{i}. {item['title'][:50]}...")
            print(f"   링크: {item['link']}")

        print("\n=== 네이버 카페 검색 테스트 ===")
        cafe_results = fetcher.search_cafe("부동산 정보", max_results=3)

        for i, item in enumerate(cafe_results, 1):
            print(f"{i}. {item['title'][:50]}...")

        print("\n=== 종합 검색 테스트 ===")
        comprehensive = fetcher.search_comprehensive("AI 투자")

        for search_type, items in comprehensive.items():
            print(f"{search_type}: {len(items)} results")

        print("\n=== 트렌딩 토픽 테스트 ===")
        trending = fetcher.get_trending_topics('real_estate')
        print(f"부동산 트렌딩 키워드: {trending[:10]}")

    except Exception as e:
        print(f"테스트 오류: {e}")


if __name__ == "__main__":
    test_naver_fetcher()