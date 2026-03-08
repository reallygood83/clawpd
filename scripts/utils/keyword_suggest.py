"""
YouTube keyword suggestions and trend analysis
Uses YouTube's suggest API and search trends
"""
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional
import re


class YouTubeKeywordSuggest:
    def __init__(self):
        """Initialize YouTube keyword suggestion tool"""
        self.suggest_url = "http://suggestqueries.google.com/complete/search"

    def get_suggestions(self, query: str, language: str = "ko") -> List[str]:
        """Get YouTube keyword suggestions for a query"""
        try:
            params = {
                'client': 'youtube',
                'ds': 'yt',
                'q': query,
                'hl': language
            }

            url = f"{self.suggest_url}?{urllib.parse.urlencode(params)}"

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            with urllib.request.urlopen(req) as response:
                data = response.read().decode('utf-8')

            # Parse JSONP response
            # Response format: window.google.ac.h(["query",[["suggestion1"],["suggestion2"],...]])
            json_start = data.find('[')
            json_end = data.rfind(']') + 1
            json_data = json.loads(data[json_start:json_end])

            if len(json_data) >= 2 and json_data[1]:
                suggestions = [item[0] for item in json_data[1] if isinstance(item, list) and item]
                return suggestions

            return []

        except Exception as e:
            print(f"Error getting suggestions for '{query}': {e}")
            return []

    def expand_keyword_tree(self, base_keyword: str, max_depth: int = 2) -> Dict[str, List[str]]:
        """Expand keyword suggestions to build a keyword tree"""
        keyword_tree = {}

        # Get suggestions for base keyword
        suggestions = self.get_suggestions(base_keyword)
        keyword_tree[base_keyword] = suggestions

        if max_depth > 1:
            # Expand top suggestions
            for suggestion in suggestions[:5]:  # Limit to top 5 to avoid API abuse
                try:
                    sub_suggestions = self.get_suggestions(suggestion)
                    keyword_tree[suggestion] = sub_suggestions
                except Exception as e:
                    print(f"Error expanding '{suggestion}': {e}")
                    continue

        return keyword_tree

    def get_trending_keywords(self, seed_keywords: List[str]) -> List[Dict[str, any]]:
        """Get trending keywords based on seed keywords"""
        trending = []

        for seed in seed_keywords:
            suggestions = self.get_suggestions(seed)

            for suggestion in suggestions:
                # Simple trending score based on suggestion order and completeness
                score = self._calculate_trend_score(suggestion, seed)

                trending.append({
                    'keyword': suggestion,
                    'seed': seed,
                    'trend_score': score,
                    'search_volume_indicator': self._estimate_search_volume(suggestion)
                })

        # Sort by trend score
        trending.sort(key=lambda x: x['trend_score'], reverse=True)

        # Remove duplicates
        seen = set()
        unique_trending = []
        for item in trending:
            if item['keyword'] not in seen:
                seen.add(item['keyword'])
                unique_trending.append(item)

        return unique_trending[:20]  # Top 20

    def _calculate_trend_score(self, suggestion: str, seed: str) -> float:
        """Calculate trending score for a keyword suggestion"""
        score = 100.0  # Base score

        # Boost for completeness (longer phrases often indicate specific trends)
        words = len(suggestion.split())
        score += words * 10

        # Boost for numbers (often indicates recent events, years, etc.)
        if re.search(r'\d{4}', suggestion):  # Year
            score += 30
        elif re.search(r'\d+', suggestion):  # Any number
            score += 15

        # Boost for time indicators
        time_keywords = ['2024', '2025', '2026', '최근', '오늘', '신규', '새로운', '최신']
        for keyword in time_keywords:
            if keyword in suggestion:
                score += 25
                break

        # Boost for action words
        action_keywords = ['방법', '하는법', '만들기', '분석', '리뷰', '전망', '예측', '투자']
        for keyword in action_keywords:
            if keyword in suggestion:
                score += 20
                break

        return score

    def _estimate_search_volume(self, keyword: str) -> str:
        """Estimate search volume based on keyword characteristics"""
        # Simple heuristic based on keyword length and type
        if len(keyword.split()) <= 2:
            return "high"
        elif len(keyword.split()) <= 4:
            return "medium"
        else:
            return "low"

    def analyze_keyword_gaps(self, my_keywords: List[str], competitor_keywords: List[str]) -> Dict:
        """Find keyword gaps and opportunities"""
        my_set = set(kw.lower() for kw in my_keywords)
        competitor_set = set(kw.lower() for kw in competitor_keywords)

        gaps = competitor_set - my_set  # Keywords competitors use but I don't
        unique = my_set - competitor_set  # Keywords only I use

        opportunities = []
        for gap in gaps:
            suggestions = self.get_suggestions(gap)
            opportunities.extend(suggestions)

        return {
            'keyword_gaps': list(gaps)[:10],
            'unique_keywords': list(unique)[:10],
            'gap_opportunities': opportunities[:15],
            'gap_count': len(gaps),
            'unique_count': len(unique)
        }

    def generate_content_ideas(self, niche_keywords: List[str], trend_keywords: List[str]) -> List[Dict]:
        """Generate content ideas by combining niche and trend keywords"""
        content_ideas = []

        for niche in niche_keywords[:5]:  # Top 5 niche keywords
            for trend in trend_keywords[:5]:  # Top 5 trending
                # Try different combination patterns
                combinations = [
                    f"{niche} {trend}",
                    f"{trend} {niche}",
                    f"{niche}로 {trend}하기",
                    f"{trend} {niche} 분석",
                    f"{niche} {trend} 전망"
                ]

                for combo in combinations:
                    suggestions = self.get_suggestions(combo)
                    if suggestions:
                        content_ideas.append({
                            'base_idea': combo,
                            'suggestions': suggestions[:3],
                            'niche_relevance': niche,
                            'trend_relevance': trend
                        })

        return content_ideas[:10]  # Top 10 ideas

    def get_niche_trending(self, niche: str) -> Dict:
        """Get trending keywords for a specific niche"""
        niche_seeds = {
            'real_estate': ['부동산', '아파트', '투자', '매매', '전세', '재개발'],
            'tech_ai': ['AI', '인공지능', 'ChatGPT', '자동화', '테크', '개발'],
            'education': ['교육', '학습', '공부', '온라인', '강의', '스킬'],
            'finance': ['주식', '투자', '재테크', '경제', '금융', '코인']
        }

        seeds = niche_seeds.get(niche, [niche])
        trending = self.get_trending_keywords(seeds)

        return {
            'niche': niche,
            'trending_keywords': trending,
            'content_opportunities': self.generate_content_ideas(seeds, [t['keyword'] for t in trending[:5]])
        }


def test_keyword_suggest():
    """Test keyword suggestion functionality"""
    try:
        ks = YouTubeKeywordSuggest()

        # Test basic suggestions
        print("=== 부동산 키워드 제안 ===")
        suggestions = ks.get_suggestions("부동산")
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"{i}. {suggestion}")

        print("\n=== 트렌딩 키워드 분석 ===")
        trending = ks.get_trending_keywords(["부동산", "AI", "투자"])
        for item in trending[:5]:
            print(f"키워드: {item['keyword']} (점수: {item['trend_score']:.1f})")

        print("\n=== 부동산 니치 트렌드 ===")
        niche_trend = ks.get_niche_trending('real_estate')
        for trend in niche_trend['trending_keywords'][:5]:
            print(f"- {trend['keyword']} (시드: {trend['seed']})")

    except Exception as e:
        print(f"테스트 오류: {e}")


if __name__ == "__main__":
    test_keyword_suggest()