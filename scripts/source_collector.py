"""
Source Collector - Gathers content from registered sources
Supports RSS feeds, web scraping, Naver cafe/blog, and YouTube trends
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import utility modules
from .utils.rss_fetcher import RSSFetcher
from .utils.web_scraper import WebScraper
from .utils.naver_fetcher import NaverFetcher
from .utils.keyword_suggest import KeywordSuggester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceCollector:
    """Collect content from various registered sources."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the source collector."""
        self.data_dir = data_dir
        self.sources_file = os.path.join(data_dir, "sources.json")

        # Initialize fetchers
        self.rss_fetcher = RSSFetcher()
        self.web_scraper = WebScraper()
        self.naver_fetcher = NaverFetcher()
        self.keyword_suggester = KeywordSuggester()

        # Load sources configuration
        self.sources = self._load_sources()

    def _load_sources(self) -> List[Dict[str, Any]]:
        """Load sources configuration from file."""
        try:
            if os.path.exists(self.sources_file):
                with open(self.sources_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading sources: {e}")
            return []

    def _save_sources(self):
        """Save sources configuration to file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.sources_file, 'w', encoding='utf-8') as f:
                json.dump(self.sources, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving sources: {e}")

    def add_source(self, name: str, url: str, source_type: str = "auto",
                   enabled: bool = True, keywords: List[str] = None) -> bool:
        """Add a new source."""
        try:
            # Auto-detect source type if not specified
            if source_type == "auto":
                source_type = self._detect_source_type(url)

            source = {
                "name": name,
                "url": url,
                "type": source_type,
                "enabled": enabled,
                "keywords": keywords or [],
                "added_at": datetime.now().isoformat(),
                "last_collected": None,
                "error_count": 0
            }

            # Check if source already exists
            for existing in self.sources:
                if existing["url"] == url:
                    logger.warning(f"Source {url} already exists")
                    return False

            self.sources.append(source)
            self._save_sources()
            logger.info(f"Added source: {name} ({source_type})")
            return True

        except Exception as e:
            logger.error(f"Error adding source {name}: {e}")
            return False

    def _detect_source_type(self, url: str) -> str:
        """Auto-detect source type from URL."""
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc

            # RSS/Atom feeds
            if url.endswith(('.rss', '.xml', '.atom')) or 'rss' in url or 'feed' in url:
                return "rss"

            # Naver sources
            elif 'naver.com' in domain:
                if 'cafe.naver.com' in domain:
                    return "naver_cafe"
                elif 'blog.naver.com' in domain:
                    return "naver_blog"
                else:
                    return "web"

            # News sites
            elif any(news_domain in domain for news_domain in [
                'mk.co.kr', 'hankyung.com', 'molit.go.kr', 'r114.com',
                'aitimes.com', 'techcrunch.com', 'news.ycombinator.com'
            ]):
                return "web"

            else:
                return "web"

        except Exception:
            return "web"

    def remove_source(self, name: str) -> bool:
        """Remove a source by name."""
        try:
            original_count = len(self.sources)
            self.sources = [s for s in self.sources if s["name"] != name]

            if len(self.sources) < original_count:
                self._save_sources()
                logger.info(f"Removed source: {name}")
                return True
            else:
                logger.warning(f"Source not found: {name}")
                return False

        except Exception as e:
            logger.error(f"Error removing source {name}: {e}")
            return False

    def enable_source(self, name: str, enabled: bool = True) -> bool:
        """Enable or disable a source."""
        try:
            for source in self.sources:
                if source["name"] == name:
                    source["enabled"] = enabled
                    self._save_sources()
                    logger.info(f"Source {name} {'enabled' if enabled else 'disabled'}")
                    return True

            logger.warning(f"Source not found: {name}")
            return False

        except Exception as e:
            logger.error(f"Error updating source {name}: {e}")
            return False

    def collect_all_sources(self, hours_back: int = 24) -> Dict[str, Any]:
        """Collect content from all enabled sources."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            results = {
                "collected_at": datetime.now().isoformat(),
                "hours_back": hours_back,
                "sources": {},
                "summary": {
                    "total_sources": 0,
                    "successful_sources": 0,
                    "total_items": 0,
                    "errors": []
                }
            }

            # Filter enabled sources
            enabled_sources = [s for s in self.sources if s.get("enabled", True)]
            results["summary"]["total_sources"] = len(enabled_sources)

            if not enabled_sources:
                logger.warning("No enabled sources found")
                return results

            # Collect from sources in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_source = {
                    executor.submit(self._collect_from_source, source, cutoff_time): source
                    for source in enabled_sources
                }

                for future in as_completed(future_to_source):
                    source = future_to_source[future]
                    try:
                        source_data = future.result(timeout=60)
                        results["sources"][source["name"]] = source_data

                        if source_data.get("success", False):
                            results["summary"]["successful_sources"] += 1
                            results["summary"]["total_items"] += len(source_data.get("items", []))
                        else:
                            error_msg = source_data.get("error", "Unknown error")
                            results["summary"]["errors"].append(f"{source['name']}: {error_msg}")

                    except Exception as e:
                        error_msg = f"Collection failed: {str(e)}"
                        results["sources"][source["name"]] = {
                            "success": False,
                            "error": error_msg,
                            "items": []
                        }
                        results["summary"]["errors"].append(f"{source['name']}: {error_msg}")

            # Update last collection times
            self._update_collection_times(results)

            # Save results to cache
            self._save_collection_results(results)

            logger.info(f"Collection completed: {results['summary']['successful_sources']}/{results['summary']['total_sources']} sources, {results['summary']['total_items']} items")

            return results

        except Exception as e:
            logger.error(f"Error in collect_all_sources: {e}")
            return {
                "collected_at": datetime.now().isoformat(),
                "error": str(e),
                "sources": {},
                "summary": {"total_sources": 0, "successful_sources": 0, "total_items": 0, "errors": [str(e)]}
            }

    def _collect_from_source(self, source: Dict[str, Any], cutoff_time: datetime) -> Dict[str, Any]:
        """Collect content from a single source."""
        try:
            source_type = source["type"]
            source_url = source["url"]

            logger.info(f"Collecting from {source['name']} ({source_type})")

            if source_type == "rss":
                items = self.rss_fetcher.fetch_feed(source_url, hours_back=24)

            elif source_type == "web":
                items = self.web_scraper.scrape_news_site(source_url, max_articles=10)

            elif source_type == "naver_cafe":
                items = self.naver_fetcher.search_cafe(source_url, keywords=source.get("keywords", []))

            elif source_type == "naver_blog":
                items = self.naver_fetcher.search_blogs(" ".join(source.get("keywords", [])))

            else:
                return {
                    "success": False,
                    "error": f"Unknown source type: {source_type}",
                    "items": []
                }

            # Filter by time if items have timestamps
            if items and cutoff_time:
                filtered_items = []
                for item in items:
                    try:
                        if 'published_at' in item:
                            pub_time = datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
                            if pub_time >= cutoff_time:
                                filtered_items.append(item)
                        else:
                            # Include items without timestamps
                            filtered_items.append(item)
                    except Exception:
                        # Include items with invalid timestamps
                        filtered_items.append(item)

                items = filtered_items

            return {
                "success": True,
                "source_type": source_type,
                "url": source_url,
                "items": items,
                "item_count": len(items),
                "collected_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source_type": source.get("type", "unknown"),
                "url": source.get("url", ""),
                "items": []
            }

    def _update_collection_times(self, results: Dict[str, Any]):
        """Update last collection times for sources."""
        try:
            collection_time = results["collected_at"]

            for source in self.sources:
                source_name = source["name"]
                if source_name in results["sources"]:
                    source_result = results["sources"][source_name]
                    if source_result.get("success", False):
                        source["last_collected"] = collection_time
                        source["error_count"] = 0
                    else:
                        source["error_count"] = source.get("error_count", 0) + 1

            self._save_sources()

        except Exception as e:
            logger.error(f"Error updating collection times: {e}")

    def _save_collection_results(self, results: Dict[str, Any]):
        """Save collection results to cache file."""
        try:
            cache_file = os.path.join(self.data_dir, "latest_collection.json")
            os.makedirs(self.data_dir, exist_ok=True)

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error saving collection results: {e}")

    def get_latest_collection(self) -> Optional[Dict[str, Any]]:
        """Get the latest collection results from cache."""
        try:
            cache_file = os.path.join(self.data_dir, "latest_collection.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None

        except Exception as e:
            logger.error(f"Error loading latest collection: {e}")
            return None

    def get_trending_keywords(self, niche_keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Get trending keywords from YouTube suggestions."""
        try:
            if not niche_keywords:
                # Get keywords from channel profile
                profile_file = os.path.join(self.data_dir, "channel_profile.json")
                if os.path.exists(profile_file):
                    with open(profile_file, 'r', encoding='utf-8') as f:
                        profile = json.load(f)
                        niche_keywords = profile.get("keywords_seed", [])

            if not niche_keywords:
                niche_keywords = ["trending", "viral", "popular"]

            trending_keywords = []

            for keyword in niche_keywords[:5]:  # Limit to avoid rate limits
                try:
                    suggestions = self.keyword_suggester.get_suggestions(keyword)
                    if suggestions:
                        trending_keywords.extend([
                            {
                                "keyword": sugg,
                                "seed": keyword,
                                "source": "youtube_suggest"
                            } for sugg in suggestions[:10]  # Top 10 per seed
                        ])
                except Exception as e:
                    logger.error(f"Error getting suggestions for {keyword}: {e}")
                    continue

            return trending_keywords[:50]  # Return top 50 overall

        except Exception as e:
            logger.error(f"Error getting trending keywords: {e}")
            return []

    def get_source_summary(self) -> Dict[str, Any]:
        """Get summary of all configured sources."""
        try:
            enabled_count = sum(1 for s in self.sources if s.get("enabled", True))

            summary = {
                "total_sources": len(self.sources),
                "enabled_sources": enabled_count,
                "disabled_sources": len(self.sources) - enabled_count,
                "sources_by_type": {},
                "recent_errors": [],
                "last_collection": None
            }

            # Group by type
            for source in self.sources:
                source_type = source["type"]
                if source_type not in summary["sources_by_type"]:
                    summary["sources_by_type"][source_type] = 0
                summary["sources_by_type"][source_type] += 1

            # Recent errors
            for source in self.sources:
                if source.get("error_count", 0) > 0:
                    summary["recent_errors"].append({
                        "name": source["name"],
                        "error_count": source["error_count"],
                        "last_collected": source.get("last_collected")
                    })

            # Last collection info
            latest = self.get_latest_collection()
            if latest:
                summary["last_collection"] = {
                    "collected_at": latest["collected_at"],
                    "total_items": latest["summary"]["total_items"],
                    "successful_sources": latest["summary"]["successful_sources"]
                }

            return summary

        except Exception as e:
            logger.error(f"Error getting source summary: {e}")
            return {}

    def list_sources(self) -> List[Dict[str, Any]]:
        """Get list of all sources with their status."""
        return [{
            "name": s["name"],
            "url": s["url"],
            "type": s["type"],
            "enabled": s.get("enabled", True),
            "last_collected": s.get("last_collected"),
            "error_count": s.get("error_count", 0),
            "keywords": s.get("keywords", [])
        } for s in self.sources]


def test_source_collector():
    """Test function for SourceCollector."""
    try:
        collector = SourceCollector()

        # Test adding sources
        collector.add_source(
            "Test RSS",
            "https://news.ycombinator.com/rss",
            "rss",
            keywords=["tech", "AI"]
        )

        collector.add_source(
            "Test News Site",
            "https://www.aitimes.com",
            "web",
            keywords=["AI", "automation"]
        )

        print("✅ Sources added successfully")

        # Test collection
        print("🔄 Testing collection...")
        results = collector.collect_all_sources(hours_back=24)

        print(f"📊 Collection Summary:")
        print(f"  - Sources: {results['summary']['successful_sources']}/{results['summary']['total_sources']}")
        print(f"  - Total items: {results['summary']['total_items']}")
        print(f"  - Errors: {len(results['summary']['errors'])}")

        # Test trending keywords
        print("🔥 Testing trending keywords...")
        keywords = collector.get_trending_keywords(["AI", "tech"])
        print(f"Found {len(keywords)} trending keywords")

        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_source_collector()