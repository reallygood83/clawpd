"""
RSS/Atom feed fetcher for news and content sources
"""
import feedparser
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin
import re


class RSSFetcher:
    def __init__(self):
        """Initialize RSS fetcher"""
        self.user_agent = "YouTube-PD-Agent/1.0"

    def fetch_feed(self, url: str, max_entries: int = 20) -> Dict[str, Any]:
        """Fetch and parse RSS/Atom feed"""
        try:
            # Set user agent
            feedparser.USER_AGENT = self.user_agent

            feed = feedparser.parse(url)

            if feed.bozo and feed.bozo_exception:
                print(f"Warning: Feed parsing issue for {url}: {feed.bozo_exception}")

            entries = []
            for entry in feed.entries[:max_entries]:
                parsed_entry = self._parse_entry(entry)
                if parsed_entry:
                    entries.append(parsed_entry)

            return {
                'title': feed.feed.get('title', 'Unknown Feed'),
                'description': feed.feed.get('description', ''),
                'link': feed.feed.get('link', ''),
                'last_updated': feed.feed.get('updated', ''),
                'entries': entries,
                'status': feed.status if hasattr(feed, 'status') else 200,
                'url': url
            }

        except Exception as e:
            return {
                'error': str(e),
                'url': url,
                'entries': []
            }

    def _parse_entry(self, entry) -> Optional[Dict[str, Any]]:
        """Parse individual RSS entry"""
        try:
            # Get published date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6]).isoformat()

            # Clean content
            content = self._extract_content(entry)

            return {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': published,
                'summary': entry.get('summary', ''),
                'content': content,
                'author': entry.get('author', ''),
                'tags': [tag.term for tag in getattr(entry, 'tags', [])]
            }

        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None

    def _extract_content(self, entry) -> str:
        """Extract clean text content from entry"""
        content = ""

        # Try content first, then summary
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if isinstance(entry.content, list) else entry.content
        elif hasattr(entry, 'summary'):
            content = entry.summary

        # Clean HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        # Clean extra whitespace
        content = re.sub(r'\s+', ' ', content).strip()

        return content

    def fetch_multiple_feeds(self, feed_urls: List[str], max_entries_per_feed: int = 10) -> List[Dict]:
        """Fetch multiple RSS feeds"""
        all_entries = []

        for url in feed_urls:
            try:
                feed_data = self.fetch_feed(url, max_entries_per_feed)

                if 'error' not in feed_data:
                    # Add source info to each entry
                    for entry in feed_data['entries']:
                        entry['source_title'] = feed_data['title']
                        entry['source_url'] = url

                    all_entries.extend(feed_data['entries'])
                else:
                    print(f"Failed to fetch {url}: {feed_data['error']}")

            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue

        return all_entries

    def filter_recent_entries(self, entries: List[Dict], hours: int = 24) -> List[Dict]:
        """Filter entries from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_entries = []

        for entry in entries:
            if entry.get('published'):
                try:
                    published = datetime.fromisoformat(entry['published'].replace('Z', '+00:00').replace('+00:00', ''))
                    if published >= cutoff:
                        recent_entries.append(entry)
                except Exception:
                    continue

        return recent_entries

    def extract_trending_topics(self, entries: List[Dict], min_mentions: int = 2) -> List[Dict]:
        """Extract trending topics from RSS entries"""
        # Extract keywords from titles and content
        keyword_counts = {}

        for entry in entries:
            text = f"{entry.get('title', '')} {entry.get('summary', '')}"

            # Simple keyword extraction (Korean + English)
            words = re.findall(r'[\w가-힣]+', text.lower())

            # Filter meaningful words (length > 2)
            meaningful_words = [w for w in words if len(w) > 2]

            for word in meaningful_words:
                keyword_counts[word] = keyword_counts.get(word, 0) + 1

        # Filter and rank trends
        trending = []
        for keyword, count in keyword_counts.items():
            if count >= min_mentions:
                # Find sample entries for this keyword
                sample_entries = []
                for entry in entries:
                    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
                    if keyword in text:
                        sample_entries.append({
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'source': entry.get('source_title', '')
                        })

                    if len(sample_entries) >= 3:  # Max 3 samples
                        break

                trending.append({
                    'keyword': keyword,
                    'mention_count': count,
                    'sample_entries': sample_entries
                })

        # Sort by mention count
        trending.sort(key=lambda x: x['mention_count'], reverse=True)

        return trending[:20]  # Top 20 trends

    def get_korean_news_feeds(self) -> Dict[str, str]:
        """Get common Korean news RSS feeds"""
        return {
            'mk_economy': 'https://www.mk.co.kr/rss/30000001/',  # 매경 경제
            'mk_realestate': 'https://www.mk.co.kr/rss/30300002/',  # 매경 부동산
            'hankyung': 'https://www.hankyung.com/feed/economy',  # 한경 경제
            'yonhap_economy': 'https://www.yna.co.kr/rss/economy.xml',  # 연합뉴스 경제
            'chosun_economy': 'https://www.chosun.com/arc/outboundfeeds/rss/economy/',  # 조선일보 경제
            'joongang_economy': 'https://rss.joins.com/joins_economy.xml',  # 중앙일보 경제
        }

    def get_tech_feeds(self) -> Dict[str, str]:
        """Get tech/AI related RSS feeds"""
        return {
            'aitimes': 'https://www.aitimes.com/rss/allArticle.xml',
            'techcrunch': 'https://techcrunch.com/feed/',
            'hackernews': 'https://feeds.feedburner.com/ycombinator',
            'verge': 'https://www.theverge.com/rss/index.xml'
        }

    def analyze_news_sentiment(self, entries: List[Dict], keywords: List[str]) -> Dict:
        """Analyze sentiment around specific keywords in news"""
        keyword_analysis = {}

        for keyword in keywords:
            relevant_entries = []
            positive_indicators = ['상승', '증가', '호조', '성장', '개선', '좋은', '긍정']
            negative_indicators = ['하락', '감소', '악화', '위기', '부정', '나쁜', '우려']

            positive_count = 0
            negative_count = 0

            for entry in entries:
                text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()

                if keyword.lower() in text:
                    relevant_entries.append(entry)

                    # Simple sentiment scoring
                    for pos in positive_indicators:
                        if pos in text:
                            positive_count += 1

                    for neg in negative_indicators:
                        if neg in text:
                            negative_count += 1

            sentiment_score = positive_count - negative_count
            sentiment = 'positive' if sentiment_score > 0 else 'negative' if sentiment_score < 0 else 'neutral'

            keyword_analysis[keyword] = {
                'relevant_entries': len(relevant_entries),
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'sample_entries': relevant_entries[:3]
            }

        return keyword_analysis


def test_rss_fetcher():
    """Test RSS fetching functionality"""
    try:
        fetcher = RSSFetcher()

        print("=== 뉴스 피드 테스트 ===")
        korean_feeds = fetcher.get_korean_news_feeds()

        # Test one feed
        test_url = korean_feeds['mk_economy']
        feed_data = fetcher.fetch_feed(test_url, 5)

        print(f"Feed: {feed_data.get('title', 'Unknown')}")
        print(f"Entries: {len(feed_data.get('entries', []))}")

        for i, entry in enumerate(feed_data.get('entries', [])[:3], 1):
            print(f"{i}. {entry.get('title', '')[:50]}...")

        print("\n=== 트렌딩 토픽 분석 ===")
        entries = feed_data.get('entries', [])
        trending = fetcher.extract_trending_topics(entries)

        for trend in trending[:5]:
            print(f"키워드: {trend['keyword']} ({trend['mention_count']}회)")

    except Exception as e:
        print(f"테스트 오류: {e}")


if __name__ == "__main__":
    test_rss_fetcher()