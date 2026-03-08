"""
Trend Matcher - Analyzes collected sources and matches trending topics with channel content
Cross-references news trends, YouTube search demand, and channel keywords
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
from math import log

# Import utility modules
from .utils.keyword_suggest import KeywordSuggester

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendMatcher:
    """Match trending topics with channel content strategy."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the trend matcher."""
        self.data_dir = data_dir
        self.keyword_suggester = KeywordSuggester()

        # Load channel profile and sources
        self.channel_profile = self._load_channel_profile()
        self.latest_collection = self._load_latest_collection()

        # TF-IDF related parameters
        self.stop_words = self._load_stop_words()

    def _load_channel_profile(self) -> Dict[str, Any]:
        """Load channel profile from file."""
        try:
            profile_file = os.path.join(self.data_dir, "channel_profile.json")
            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading channel profile: {e}")
            return {}

    def _load_latest_collection(self) -> Dict[str, Any]:
        """Load latest source collection results."""
        try:
            cache_file = os.path.join(self.data_dir, "latest_collection.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading latest collection: {e}")
            return {}

    def _load_stop_words(self) -> set:
        """Load Korean and English stop words."""
        # Common stop words for content analysis
        korean_stops = {
            '있다', '하다', '되다', '이다', '그리고', '또한', '하지만', '그러나', '따라서',
            '그래서', '이런', '저런', '이것', '그것', '여기', '거기', '때문에', '통해',
            '위해', '대해', '관해', '에서', '부터', '까지', '보다', '같은', '다른',
            '많은', '적은', '크다', '작다', '좋다', '나쁘다', '새로운', '오늘', '내일',
            '어제', '지금', '여전히', '아직', '이미', '벌써', '항상', '절대', '전혀'
        }

        english_stops = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his',
            'her', 'its', 'our', 'their', 'me', 'him', 'her', 'us', 'them'
        }

        return korean_stops.union(english_stops)

    def analyze_trending_topics(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Analyze and rank trending topics from collected sources."""
        try:
            if not self.latest_collection or not self.latest_collection.get("sources"):
                logger.warning("No collection data available")
                return []

            # Extract all content items
            all_items = []
            for source_name, source_data in self.latest_collection["sources"].items():
                if source_data.get("success", False):
                    items = source_data.get("items", [])
                    for item in items:
                        item["source_name"] = source_name
                        all_items.append(item)

            if not all_items:
                logger.warning("No items found in collection data")
                return []

            logger.info(f"Analyzing {len(all_items)} items from {len(self.latest_collection['sources'])} sources")

            # Extract keywords and topics using multiple methods
            trending_topics = self._extract_trending_topics(all_items)

            # Score topics based on multiple factors
            scored_topics = self._score_topics(trending_topics)

            # Filter and rank topics
            final_topics = self._filter_and_rank_topics(scored_topics)

            logger.info(f"Found {len(final_topics)} trending topics")
            return final_topics[:10]  # Return top 10

        except Exception as e:
            logger.error(f"Error analyzing trending topics: {e}")
            return []

    def _extract_trending_topics(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics from content items."""
        topics = []

        for item in items:
            try:
                # Extract from title
                title = item.get("title", "")
                if title:
                    title_keywords = self._extract_keywords_from_text(title)
                    for keyword in title_keywords:
                        topics.append({
                            "keyword": keyword,
                            "source": "title",
                            "source_name": item.get("source_name", ""),
                            "title": title,
                            "url": item.get("url", ""),
                            "published_at": item.get("published_at", ""),
                            "weight": 3.0  # Titles are more important
                        })

                # Extract from description/content
                description = item.get("description", "") or item.get("content", "")
                if description:
                    desc_keywords = self._extract_keywords_from_text(description, max_keywords=5)
                    for keyword in desc_keywords:
                        topics.append({
                            "keyword": keyword,
                            "source": "content",
                            "source_name": item.get("source_name", ""),
                            "title": title,
                            "url": item.get("url", ""),
                            "published_at": item.get("published_at", ""),
                            "weight": 1.0
                        })

                # Extract from tags if available
                tags = item.get("tags", [])
                for tag in tags[:5]:  # Limit tags
                    if len(tag.strip()) >= 2:
                        topics.append({
                            "keyword": tag.strip(),
                            "source": "tag",
                            "source_name": item.get("source_name", ""),
                            "title": title,
                            "url": item.get("url", ""),
                            "published_at": item.get("published_at", ""),
                            "weight": 2.0
                        })

            except Exception as e:
                logger.error(f"Error processing item: {e}")
                continue

        return topics

    def _extract_keywords_from_text(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using simple NLP techniques."""
        if not text:
            return []

        try:
            # Clean and normalize text
            text = re.sub(r'[^\w\s가-힣]', ' ', text.lower())
            words = text.split()

            # Filter stop words and short words
            filtered_words = [
                word for word in words
                if len(word) >= 2 and word not in self.stop_words
            ]

            # Count word frequencies
            word_counts = Counter(filtered_words)

            # Extract n-grams (2-3 word phrases)
            bigrams = []
            trigrams = []

            for i in range(len(filtered_words) - 1):
                bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
                bigrams.append(bigram)

            for i in range(len(filtered_words) - 2):
                trigram = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
                trigrams.append(trigram)

            bigram_counts = Counter(bigrams)
            trigram_counts = Counter(trigrams)

            # Combine and score keywords
            keywords = []

            # Single words (lower priority)
            for word, count in word_counts.most_common(max_keywords):
                if count >= 2 and len(word) >= 3:  # Minimum frequency and length
                    keywords.append(word)

            # Bigrams (higher priority)
            for bigram, count in bigram_counts.most_common(max_keywords // 2):
                if count >= 2:
                    keywords.append(bigram)

            # Trigrams (highest priority)
            for trigram, count in trigram_counts.most_common(max_keywords // 3):
                if count >= 2:
                    keywords.append(trigram)

            return keywords[:max_keywords]

        except Exception as e:
            logger.error(f"Error extracting keywords from text: {e}")
            return []

    def _score_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score topics based on multiple factors."""
        # Group topics by keyword
        keyword_groups = {}
        for topic in topics:
            keyword = topic["keyword"]
            if keyword not in keyword_groups:
                keyword_groups[keyword] = []
            keyword_groups[keyword].append(topic)

        scored_topics = []

        for keyword, topic_list in keyword_groups.items():
            try:
                # Calculate base score from frequency and weights
                frequency_score = len(topic_list)
                weight_score = sum(t["weight"] for t in topic_list) / len(topic_list)

                # Time decay (recent content is more important)
                recency_score = self._calculate_recency_score(topic_list)

                # Source diversity bonus
                unique_sources = len(set(t["source_name"] for t in topic_list))
                diversity_bonus = min(unique_sources * 0.5, 2.0)

                # Channel relevance score
                relevance_score = self._calculate_channel_relevance(keyword)

                # YouTube search demand score
                demand_score = self._calculate_search_demand(keyword)

                # Content quality indicators
                quality_score = self._calculate_content_quality(topic_list)

                # Calculate total score
                total_score = (
                    frequency_score * 1.0 +
                    weight_score * 1.5 +
                    recency_score * 2.0 +
                    diversity_bonus +
                    relevance_score * 3.0 +
                    demand_score * 2.5 +
                    quality_score * 1.0
                )

                scored_topics.append({
                    "keyword": keyword,
                    "total_score": round(total_score, 2),
                    "frequency": frequency_score,
                    "weight_score": round(weight_score, 2),
                    "recency_score": round(recency_score, 2),
                    "diversity_bonus": round(diversity_bonus, 2),
                    "relevance_score": round(relevance_score, 2),
                    "demand_score": round(demand_score, 2),
                    "quality_score": round(quality_score, 2),
                    "sources": list(set(t["source_name"] for t in topic_list)),
                    "sample_titles": [t["title"] for t in topic_list[:3] if t["title"]],
                    "sample_urls": [t["url"] for t in topic_list[:3] if t["url"]],
                    "latest_mention": max((t.get("published_at", "") for t in topic_list), default=""),
                    "mention_count": len(topic_list),
                })

            except Exception as e:
                logger.error(f"Error scoring topic {keyword}: {e}")
                continue

        return sorted(scored_topics, key=lambda x: x["total_score"], reverse=True)

    def _calculate_recency_score(self, topic_list: List[Dict[str, Any]]) -> float:
        """Calculate recency score based on publication dates."""
        try:
            now = datetime.now()
            total_score = 0
            valid_dates = 0

            for topic in topic_list:
                pub_date_str = topic.get("published_at", "")
                if pub_date_str:
                    try:
                        # Handle various date formats
                        if 'T' in pub_date_str:
                            pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        else:
                            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')

                        hours_ago = (now - pub_date).total_seconds() / 3600

                        # Exponential decay: more recent = higher score
                        if hours_ago <= 6:
                            score = 10.0
                        elif hours_ago <= 24:
                            score = 5.0
                        elif hours_ago <= 72:
                            score = 2.0
                        else:
                            score = 1.0

                        total_score += score
                        valid_dates += 1

                    except Exception:
                        # If date parsing fails, give neutral score
                        total_score += 1.0
                        valid_dates += 1

            return total_score / max(valid_dates, 1)

        except Exception as e:
            logger.error(f"Error calculating recency score: {e}")
            return 1.0

    def _calculate_channel_relevance(self, keyword: str) -> float:
        """Calculate how relevant a keyword is to the channel's niche."""
        try:
            if not self.channel_profile:
                return 1.0

            # Get channel keywords and niche
            channel_keywords = self.channel_profile.get("keywords_seed", [])
            niche = self.channel_profile.get("detected_niche", "").lower()

            # Check direct keyword match
            keyword_lower = keyword.lower()
            for channel_kw in channel_keywords:
                if channel_kw.lower() in keyword_lower or keyword_lower in channel_kw.lower():
                    return 5.0

            # Check niche relevance
            if niche and niche in keyword_lower:
                return 3.0

            # Check semantic similarity (simple word overlap)
            keyword_words = set(keyword_lower.split())
            channel_words = set()
            for kw in channel_keywords:
                channel_words.update(kw.lower().split())

            overlap_ratio = len(keyword_words.intersection(channel_words)) / max(len(keyword_words), 1)

            if overlap_ratio > 0.5:
                return 4.0
            elif overlap_ratio > 0.2:
                return 2.0
            else:
                return 1.0

        except Exception as e:
            logger.error(f"Error calculating channel relevance: {e}")
            return 1.0

    def _calculate_search_demand(self, keyword: str) -> float:
        """Calculate search demand score using YouTube suggestions."""
        try:
            # Get YouTube suggestions for the keyword
            suggestions = self.keyword_suggester.get_suggestions(keyword)

            if suggestions:
                # More suggestions indicate higher search demand
                suggestion_count = len(suggestions)

                # Check if our keyword appears in suggestions (auto-complete popularity)
                appears_in_suggestions = any(keyword.lower() in sugg.lower() for sugg in suggestions)

                demand_score = min(suggestion_count * 0.5, 5.0)  # Cap at 5.0

                if appears_in_suggestions:
                    demand_score += 2.0

                return demand_score

            return 1.0

        except Exception as e:
            logger.error(f"Error calculating search demand for {keyword}: {e}")
            return 1.0

    def _calculate_content_quality(self, topic_list: List[Dict[str, Any]]) -> float:
        """Calculate content quality indicators."""
        try:
            quality_factors = []

            # Title length diversity (good topics have varied coverage)
            title_lengths = [len(t.get("title", "")) for t in topic_list if t.get("title")]
            if title_lengths:
                length_variety = len(set(title_lengths[:5]))  # Check variety in top 5
                quality_factors.append(min(length_variety * 0.5, 2.0))

            # Source credibility (news sites vs blogs)
            credible_sources = 0
            for topic in topic_list:
                source_name = topic.get("source_name", "").lower()
                if any(indicator in source_name for indicator in ["news", "경제", "times", "official"]):
                    credible_sources += 1

            credibility_ratio = credible_sources / max(len(topic_list), 1)
            quality_factors.append(credibility_ratio * 3.0)

            # Keyword sophistication (longer keywords often indicate more specific topics)
            avg_keyword_length = len(topic_list[0]["keyword"].split()) if topic_list else 1
            sophistication_score = min(avg_keyword_length * 0.8, 2.0)
            quality_factors.append(sophistication_score)

            return sum(quality_factors) / max(len(quality_factors), 1)

        except Exception as e:
            logger.error(f"Error calculating content quality: {e}")
            return 1.0

    def _filter_and_rank_topics(self, scored_topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank topics for final recommendation."""
        try:
            filtered_topics = []

            for topic in scored_topics:
                keyword = topic["keyword"]

                # Filter criteria
                if len(keyword) < 2:  # Too short
                    continue

                if topic["total_score"] < 3.0:  # Score too low
                    continue

                if topic["mention_count"] < 2:  # Not mentioned enough
                    continue

                # Check for duplicate or very similar keywords
                is_duplicate = False
                for existing in filtered_topics:
                    existing_kw = existing["keyword"].lower()
                    current_kw = keyword.lower()

                    # Simple similarity check
                    if (current_kw in existing_kw or existing_kw in current_kw or
                        len(set(current_kw.split()).intersection(set(existing_kw.split()))) >= 2):
                        if existing["total_score"] >= topic["total_score"]:
                            is_duplicate = True
                            break

                if not is_duplicate:
                    filtered_topics.append(topic)

            # Final ranking with additional criteria
            for topic in filtered_topics:
                # Boost score for topics that appear across multiple sources
                if len(topic["sources"]) >= 3:
                    topic["total_score"] *= 1.2

                # Boost score for recent topics
                if topic.get("recency_score", 0) >= 5.0:
                    topic["total_score"] *= 1.1

            return sorted(filtered_topics, key=lambda x: x["total_score"], reverse=True)

        except Exception as e:
            logger.error(f"Error filtering and ranking topics: {e}")
            return scored_topics  # Return original if filtering fails

    def generate_content_recommendations(self, max_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Generate content recommendations based on trending topics."""
        try:
            # Get trending topics
            trending_topics = self.analyze_trending_topics()

            if not trending_topics:
                return []

            recommendations = []

            for i, topic in enumerate(trending_topics[:max_recommendations]):
                # Generate content angle based on channel profile
                content_angle = self._generate_content_angle(topic)

                # Estimate potential performance
                performance_estimate = self._estimate_performance(topic)

                recommendation = {
                    "rank": i + 1,
                    "topic": topic["keyword"],
                    "content_angle": content_angle,
                    "trend_score": topic["total_score"],
                    "search_demand": topic.get("demand_score", 0),
                    "channel_relevance": topic.get("relevance_score", 0),
                    "recency": topic.get("recency_score", 0),
                    "sources": topic["sources"],
                    "mention_count": topic["mention_count"],
                    "sample_titles": topic["sample_titles"],
                    "performance_estimate": performance_estimate,
                    "recommended_timeline": self._suggest_timeline(topic),
                    "content_format": self._suggest_format(topic),
                    "seo_keywords": self._generate_seo_keywords(topic),
                }

                recommendations.append(recommendation)

            logger.info(f"Generated {len(recommendations)} content recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Error generating content recommendations: {e}")
            return []

    def _generate_content_angle(self, topic: Dict[str, Any]) -> str:
        """Generate content angle based on topic and channel profile."""
        try:
            keyword = topic["keyword"]
            niche = self.channel_profile.get("detected_niche", "").lower()
            tone = self.channel_profile.get("detected_tone", "").lower()

            # Basic angle templates based on niche
            if "부동산" in niche or "real estate" in niche:
                return f"'{keyword}' 부동산 투자자가 꼭 알아야 할 핵심 포인트"
            elif "ai" in niche or "테크" in niche or "tech" in niche:
                return f"'{keyword}' AI/테크 트렌드 완벽 분석 및 활용법"
            elif "교육" in niche or "education" in niche:
                return f"'{keyword}' 실무에서 바로 써먹는 핵심 가이드"
            elif "주식" in niche or "재테크" in niche:
                return f"'{keyword}' 투자자 관점에서 본 기회와 위험"
            else:
                # Generic angle
                if "전문가" in tone or "expert" in tone:
                    return f"'{keyword}' 전문가가 알려주는 핵심 인사이트"
                elif "친근" in tone or "friendly" in tone:
                    return f"'{keyword}' 쉽게 이해하는 완벽 가이드"
                else:
                    return f"'{keyword}' 지금 주목해야 하는 이유"

        except Exception as e:
            logger.error(f"Error generating content angle: {e}")
            return f"'{topic['keyword']}' 완벽 분석"

    def _estimate_performance(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate potential performance of content based on topic."""
        try:
            channel_metrics = self.channel_profile.get("metrics", {})
            avg_views = channel_metrics.get("avg_views", 1000)

            # Performance multiplier based on topic scores
            trend_multiplier = min(topic["total_score"] / 10.0, 2.0)
            demand_multiplier = min(topic.get("demand_score", 1) / 5.0, 1.5)
            relevance_multiplier = min(topic.get("relevance_score", 1) / 5.0, 1.3)

            total_multiplier = trend_multiplier * demand_multiplier * relevance_multiplier

            estimated_views = int(avg_views * total_multiplier)
            estimated_engagement = estimated_views * 0.05  # Assume 5% engagement rate

            confidence = "높음" if total_multiplier > 1.5 else "보통" if total_multiplier > 1.0 else "낮음"

            return {
                "estimated_views": estimated_views,
                "estimated_engagement": int(estimated_engagement),
                "performance_multiplier": round(total_multiplier, 2),
                "confidence": confidence,
                "reasoning": f"트렌드 스코어 {topic['total_score']}, 검색수요 {topic.get('demand_score', 0)}, 채널 적합도 {topic.get('relevance_score', 0)}"
            }

        except Exception as e:
            logger.error(f"Error estimating performance: {e}")
            return {
                "estimated_views": 1000,
                "estimated_engagement": 50,
                "performance_multiplier": 1.0,
                "confidence": "보통",
                "reasoning": "분석 데이터 부족"
            }

    def _suggest_timeline(self, topic: Dict[str, Any]) -> str:
        """Suggest optimal publishing timeline."""
        recency_score = topic.get("recency_score", 1)

        if recency_score >= 8:
            return "즉시 제작 (24시간 내)"
        elif recency_score >= 5:
            return "빠른 제작 (3일 내)"
        elif recency_score >= 3:
            return "1주일 내 제작"
        else:
            return "2주 내 제작"

    def _suggest_format(self, topic: Dict[str, Any]) -> str:
        """Suggest content format based on topic characteristics."""
        keyword = topic["keyword"].lower()

        # Format suggestions based on keyword type
        if any(word in keyword for word in ["속보", "뉴스", "발표", "오늘"]):
            return "뉴스 분석형 (8-12분)"
        elif any(word in keyword for word in ["방법", "가이드", "튜토리얼", "how to"]):
            return "실습 가이드형 (15-25분)"
        elif any(word in keyword for word in ["분석", "전망", "예측"]):
            return "전문 분석형 (12-18분)"
        elif any(word in keyword for word in ["리뷰", "후기", "비교"]):
            return "리뷰/비교형 (10-15분)"
        else:
            return "종합 정보형 (10-15분)"

    def _generate_seo_keywords(self, topic: Dict[str, Any]) -> List[str]:
        """Generate SEO keywords based on topic."""
        try:
            base_keyword = topic["keyword"]
            seo_keywords = [base_keyword]

            # Add variations
            words = base_keyword.split()
            if len(words) > 1:
                # Add individual words
                seo_keywords.extend(words)

                # Add rearranged versions
                if len(words) == 2:
                    seo_keywords.append(f"{words[1]} {words[0]}")

            # Add common YouTube search patterns
            seo_keywords.extend([
                f"{base_keyword} 설명",
                f"{base_keyword} 분석",
                f"{base_keyword} 정리",
                f"{base_keyword} 가이드",
                f"{base_keyword} 뉴스",
                f"{base_keyword} 최신",
                f"{base_keyword} 2026"
            ])

            # Remove duplicates and return top 10
            unique_keywords = list(dict.fromkeys(seo_keywords))
            return unique_keywords[:10]

        except Exception as e:
            logger.error(f"Error generating SEO keywords: {e}")
            return [topic["keyword"]]


def test_trend_matcher():
    """Test function for TrendMatcher."""
    try:
        matcher = TrendMatcher()
        print("✅ TrendMatcher initialized")

        # Test topic analysis
        print("🔄 Analyzing trending topics...")
        topics = matcher.analyze_trending_topics()
        print(f"📊 Found {len(topics)} trending topics")

        if topics:
            print(f"Top topic: {topics[0]['keyword']} (score: {topics[0]['total_score']})")

        # Test content recommendations
        print("🎯 Generating content recommendations...")
        recommendations = matcher.generate_content_recommendations(max_recommendations=3)
        print(f"📝 Generated {len(recommendations)} recommendations")

        if recommendations:
            print(f"Top recommendation: {recommendations[0]['content_angle']}")

        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_trend_matcher()