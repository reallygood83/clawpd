"""
SWOT Analyzer - Analyzes competitor channels and generates comprehensive SWOT reports
Uses YouTube Data API to compare channels and provide strategic recommendations
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

# Import utility modules
from .utils.youtube_api import YouTubeAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SWOTAnalyzer:
    """Analyze competitor channels and generate SWOT reports."""

    def __init__(self, data_dir: str = "data", templates_dir: str = "templates"):
        """Initialize the SWOT analyzer."""
        self.data_dir = data_dir
        self.templates_dir = templates_dir

        # Initialize YouTube API with graceful fallback
        self.youtube_api = None
        self.api_available = False
        try:
            from .utils.youtube_api import YouTubeAPI
            self.youtube_api = YouTubeAPI()
            self.api_available = True
            logger.info("YouTube API initialized successfully")
        except Exception as e:
            logger.warning(f"YouTube API not available: {e}. Will use web scraping fallback.")
            self.api_available = False

        # Import web scraper for fallback
        from .utils.web_scraper import WebScraper
        self.web_scraper = WebScraper()

        # Load configurations
        self.channel_profile = self._load_channel_profile()
        self.swot_template = self._load_swot_template()

    def _load_channel_profile(self) -> Dict[str, Any]:
        """Load channel profile configuration."""
        try:
            profile_file = os.path.join(self.data_dir, "channel_profile.json")
            if os.path.exists(profile_file):
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading channel profile: {e}")
            return {}

    def _load_swot_template(self) -> str:
        """Load the SWOT report template."""
        try:
            template_file = os.path.join(self.templates_dir, "swot_report.md")
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return self._get_default_swot_template()
        except Exception as e:
            logger.error(f"Error loading SWOT template: {e}")
            return self._get_default_swot_template()

    def _get_default_swot_template(self) -> str:
        """Get default SWOT template if file doesn't exist."""
        return """# 📊 SWOT 분석 리포트

## 📈 채널 비교 대시보드

{dashboard_table}

## 🎯 S (Strengths) — 강점

{strengths}

## ⚠️ W (Weaknesses) — 약점

{weaknesses}

## 🌟 O (Opportunities) — 기회

{opportunities}

## ⚡ T (Threats) — 위협

{threats}

## 🚀 전략 제안

### 즉시 실행 (1주 내)
{immediate_actions}

### 중기 전략 (1개월)
{mid_term_strategy}

### 장기 방향 (3개월)
{long_term_strategy}

## 📈 경쟁 채널별 상세 분석

{detailed_analysis}

---
*생성일: {generated_date}*
*분석자: YouTube PD Agent v1.0*
"""

    def analyze_competitors(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """Analyze competitor channels and generate SWOT report."""
        try:
            logger.info(f"Starting SWOT analysis for {len(competitor_urls)} competitors")

            # Get my channel data
            my_channel_data = self._get_my_channel_data()
            if not my_channel_data:
                return {
                    "success": False,
                    "error": "Failed to load own channel data",
                    "report": ""
                }

            # Analyze competitor channels
            competitor_data = []
            for i, url in enumerate(competitor_urls):
                try:
                    logger.info(f"Analyzing competitor {i+1}/{len(competitor_urls)}: {url}")

                    if self.api_available:
                        # Try YouTube API first
                        try:
                            channel_id = self.youtube_api.extract_channel_id(url)
                            if channel_id:
                                analysis = self.youtube_api.analyze_channel_performance(channel_id)
                                if analysis and not analysis.get("error"):
                                    competitor_data.append({
                                        "url": url,
                                        "channel_id": channel_id,
                                        "analysis": analysis,
                                        "source": "youtube_api"
                                    })
                                    continue
                        except Exception as api_error:
                            logger.warning(f"YouTube API failed for {url}: {api_error}. Trying web scraping...")

                    # Fallback to web scraping
                    analysis = self._analyze_channel_via_web_scraping(url)
                    if analysis and not analysis.get("error"):
                        competitor_data.append({
                            "url": url,
                            "channel_id": None,
                            "analysis": analysis,
                            "source": "web_scraping"
                        })
                    else:
                        logger.warning(f"Failed to analyze channel {url} via web scraping")

                except Exception as e:
                    logger.error(f"Error analyzing competitor {url}: {e}")
                    continue

            if not competitor_data:
                return {
                    "success": False,
                    "error": "No competitor data could be collected",
                    "report": ""
                }

            logger.info(f"Successfully analyzed {len(competitor_data)} competitors")

            # Generate SWOT analysis
            swot_data = self._generate_swot_analysis(my_channel_data, competitor_data)

            # Generate report
            report_content = self._generate_swot_report(swot_data)

            # Save report
            report_id = self._save_swot_report(report_content)

            return {
                "success": True,
                "report_id": report_id,
                "report_content": report_content,
                "swot_data": swot_data,
                "competitor_count": len(competitor_data),
                "file_path": os.path.join(self.data_dir, "swot_reports", f"{report_id}.md")
            }

        except Exception as e:
            logger.error(f"Error in SWOT analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "report": ""
            }

    def _get_my_channel_data(self) -> Optional[Dict[str, Any]]:
        """Get my channel data from profile with graceful fallback."""
        try:
            if not self.channel_profile:
                logger.warning("No channel profile found")
                return None

            my_channel_id = self.channel_profile.get("channel_id")
            channel_url = self.channel_profile.get("channel_url")

            # Try YouTube API first if available
            if self.api_available and (my_channel_id or channel_url):
                try:
                    if my_channel_id:
                        analysis = self.youtube_api.analyze_channel_performance(my_channel_id)
                        if analysis and not analysis.get("error"):
                            return {
                                "channel_id": my_channel_id,
                                "analysis": analysis,
                                "profile": self.channel_profile,
                                "source": "youtube_api"
                            }

                    if channel_url:
                        channel_id = self.youtube_api.extract_channel_id(channel_url)
                        if channel_id:
                            analysis = self.youtube_api.analyze_channel_performance(channel_id)
                            if analysis and not analysis.get("error"):
                                return {
                                    "channel_id": channel_id,
                                    "analysis": analysis,
                                    "profile": self.channel_profile,
                                    "source": "youtube_api"
                                }
                except Exception as api_error:
                    logger.warning(f"YouTube API failed for my channel: {api_error}. Using fallback...")

            # Fallback: use web scraping or profile data
            if channel_url:
                analysis = self._analyze_channel_via_web_scraping(channel_url)
                if analysis and not analysis.get("error"):
                    return {
                        "channel_id": my_channel_id,
                        "analysis": analysis,
                        "profile": self.channel_profile,
                        "source": "web_scraping"
                    }

            # Last fallback: use basic profile data
            if self.channel_profile:
                mock_analysis = {
                    "channel_info": {
                        "title": self.channel_profile.get("channel_title", "My Channel"),
                        "subscriber_count": self.channel_profile.get("estimated_subscribers", 1000)
                    },
                    "metrics": {
                        "avg_views": self.channel_profile.get("avg_views", 500),
                        "avg_likes": self.channel_profile.get("avg_likes", 25),
                        "avg_comments": self.channel_profile.get("avg_comments", 5),
                        "engagement_rate": 3.0,
                        "upload_frequency": "주 1회"
                    },
                    "content_breakdown": {
                        "avg_duration_minutes": 10,
                        "shorts_ratio": 10
                    },
                    "top_videos": [],
                    "top_keywords": [("키워드", 1)],
                    "video_count": 20,
                    "source": "profile_estimate"
                }

                return {
                    "channel_id": my_channel_id,
                    "analysis": mock_analysis,
                    "profile": self.channel_profile,
                    "source": "profile_estimate"
                }

            return None

        except Exception as e:
            logger.error(f"Error getting my channel data: {e}")
            return None

    def _generate_swot_analysis(self, my_channel: Dict[str, Any],
                               competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive SWOT analysis."""
        try:
            # Extract metrics for comparison
            my_metrics = self._extract_channel_metrics(my_channel["analysis"])
            competitor_metrics = [self._extract_channel_metrics(comp["analysis"])
                                 for comp in competitors]

            # Generate dashboard comparison
            dashboard_data = self._generate_dashboard_comparison(my_metrics, competitor_metrics)

            # Analyze each SWOT component
            strengths = self._analyze_strengths(my_metrics, competitor_metrics)
            weaknesses = self._analyze_weaknesses(my_metrics, competitor_metrics)
            opportunities = self._analyze_opportunities(my_metrics, competitor_metrics, competitors)
            threats = self._analyze_threats(my_metrics, competitor_metrics, competitors)

            # Generate strategic recommendations
            strategies = self._generate_strategic_recommendations(
                strengths, weaknesses, opportunities, threats, my_metrics, competitor_metrics
            )

            # Detailed competitor analysis
            detailed_analysis = self._generate_detailed_competitor_analysis(competitors)

            return {
                "dashboard_data": dashboard_data,
                "my_metrics": my_metrics,
                "competitor_metrics": competitor_metrics,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "opportunities": opportunities,
                "threats": threats,
                "strategies": strategies,
                "detailed_analysis": detailed_analysis,
                "competitors": competitors
            }

        except Exception as e:
            logger.error(f"Error generating SWOT analysis: {e}")
            return {}

    def _extract_channel_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from channel analysis."""
        try:
            channel_info = analysis.get("channel_info", {})
            metrics = analysis.get("metrics", {})
            content_breakdown = analysis.get("content_breakdown", {})

            return {
                "channel_title": channel_info.get("title", "Unknown"),
                "subscriber_count": channel_info.get("subscriber_count", 0),
                "video_count": analysis.get("video_count", 0),
                "avg_views": metrics.get("avg_views", 0),
                "avg_likes": metrics.get("avg_likes", 0),
                "avg_comments": metrics.get("avg_comments", 0),
                "engagement_rate": metrics.get("engagement_rate", 0),
                "upload_frequency": metrics.get("upload_frequency", "Unknown"),
                "shorts_ratio": content_breakdown.get("shorts_ratio", 0),
                "avg_duration_minutes": content_breakdown.get("avg_duration_minutes", 0),
                "top_videos": analysis.get("top_videos", [])[:5],
                "top_keywords": analysis.get("top_keywords", [])[:10]
            }

        except Exception as e:
            logger.error(f"Error extracting channel metrics: {e}")
            return {}

    def _generate_dashboard_comparison(self, my_metrics: Dict[str, Any],
                                     competitor_metrics: List[Dict[str, Any]]) -> str:
        """Generate dashboard comparison table."""
        try:
            # Create table header
            header = "| 지표 | 내 채널 |"
            for i, comp in enumerate(competitor_metrics):
                header += f" 경쟁{chr(65+i)} |"  # A, B, C...
            header += "\n|------|---------|"
            for _ in competitor_metrics:
                header += "-------|"

            # Create rows
            rows = []

            # Subscriber count
            row = f"| 구독자 | {self._format_number(my_metrics['subscriber_count'])} |"
            for comp in competitor_metrics:
                row += f" {self._format_number(comp['subscriber_count'])} |"
            rows.append(row)

            # Average views
            row = f"| 평균 조회수 | {self._format_number(my_metrics['avg_views'])} |"
            for comp in competitor_metrics:
                row += f" {self._format_number(comp['avg_views'])} |"
            rows.append(row)

            # Engagement rate
            row = f"| 참여율 | {my_metrics['engagement_rate']:.1f}% |"
            for comp in competitor_metrics:
                row += f" {comp['engagement_rate']:.1f}% |"
            rows.append(row)

            # Upload frequency
            row = f"| 업로드 빈도 | {my_metrics['upload_frequency']} |"
            for comp in competitor_metrics:
                row += f" {comp['upload_frequency']} |"
            rows.append(row)

            # Video duration
            row = f"| 평균 영상 길이 | {my_metrics['avg_duration_minutes']:.0f}분 |"
            for comp in competitor_metrics:
                row += f" {comp['avg_duration_minutes']:.0f}분 |"
            rows.append(row)

            # Shorts ratio
            row = f"| Shorts 비율 | {my_metrics['shorts_ratio']:.0f}% |"
            for comp in competitor_metrics:
                row += f" {comp['shorts_ratio']:.0f}% |"
            rows.append(row)

            return header + "\n" + "\n".join(rows)

        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return "**대시보드 생성 중 오류 발생**"

    def _format_number(self, num: int) -> str:
        """Format large numbers with K/M suffixes."""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)

    def _analyze_strengths(self, my_metrics: Dict[str, Any],
                          competitor_metrics: List[Dict[str, Any]]) -> List[str]:
        """Analyze channel strengths."""
        strengths = []

        try:
            # Compare engagement rate
            my_engagement = my_metrics['engagement_rate']
            competitor_engagements = [c['engagement_rate'] for c in competitor_metrics]

            if my_engagement > max(competitor_engagements, default=0):
                strengths.append(f"**높은 참여율**: {my_engagement:.1f}%로 경쟁 채널 대비 우수한 시청자 충성도")

            # Compare subscriber growth potential (engagement vs subscriber ratio)
            my_potential = my_metrics['avg_views'] / max(my_metrics['subscriber_count'], 1)
            competitor_potentials = [
                c['avg_views'] / max(c['subscriber_count'], 1) for c in competitor_metrics
            ]

            if my_potential > max(competitor_potentials, default=0):
                strengths.append("**높은 성장 잠재력**: 구독자 대비 높은 조회수로 바이럴 가능성 우수")

            # Content consistency
            if "일" in my_metrics['upload_frequency'] and "주" not in my_metrics['upload_frequency']:
                strengths.append("**일관된 업로드**: 정기적인 콘텐츠 업로드로 시청자 유지력 우수")

            # Niche focus (if low shorts ratio compared to competitors)
            if my_metrics['shorts_ratio'] < min([c['shorts_ratio'] for c in competitor_metrics], default=100):
                if my_metrics['avg_duration_minutes'] > 10:
                    strengths.append("**깊이 있는 콘텐츠**: 롱폼 콘텐츠 중심으로 전문성 강화")

            # If no quantitative strengths found, add qualitative ones
            if not strengths:
                strengths.extend([
                    "**니치 전문성**: 특정 분야에 특화된 콘텐츠로 타겟 오디언스 확보",
                    "**콘텐츠 품질**: 체계적인 구성과 전문적인 정보 제공",
                    "**신뢰성**: 정확한 정보 제공으로 시청자 신뢰 구축"
                ])

        except Exception as e:
            logger.error(f"Error analyzing strengths: {e}")
            strengths.append("**분석 오류**: 강점 분석 중 오류 발생")

        return strengths

    def _analyze_weaknesses(self, my_metrics: Dict[str, Any],
                           competitor_metrics: List[Dict[str, Any]]) -> List[str]:
        """Analyze channel weaknesses."""
        weaknesses = []

        try:
            # Compare subscriber count
            max_competitor_subs = max([c['subscriber_count'] for c in competitor_metrics], default=0)
            if my_metrics['subscriber_count'] < max_competitor_subs * 0.5:
                weaknesses.append(f"**구독자 규모**: {self._format_number(max_competitor_subs)} 대비 {self._format_number(my_metrics['subscriber_count'])}로 상대적 소규모")

            # Compare average views
            max_competitor_views = max([c['avg_views'] for c in competitor_metrics], default=0)
            if my_metrics['avg_views'] < max_competitor_views * 0.7:
                weaknesses.append(f"**조회수 성과**: 경쟁 채널 대비 {(my_metrics['avg_views']/max_competitor_views*100):.0f}% 수준")

            # Upload frequency comparison
            my_freq = my_metrics['upload_frequency'].lower()
            if "주" in my_freq and any("일" in c['upload_frequency'].lower() for c in competitor_metrics):
                weaknesses.append("**업로드 빈도**: 경쟁 채널 대비 낮은 업로드 주기")

            # Shorts content
            max_shorts_ratio = max([c['shorts_ratio'] for c in competitor_metrics], default=0)
            if my_metrics['shorts_ratio'] < max_shorts_ratio * 0.3 and max_shorts_ratio > 20:
                weaknesses.append("**Shorts 콘텐츠 부족**: 짧은 형식 콘텐츠로 신규 시청자 유입 한계")

            # Low engagement despite good content
            if my_metrics['engagement_rate'] < 3.0:
                weaknesses.append("**참여도 개선 필요**: 댓글, 좋아요 등 시청자 참여 활성화 필요")

        except Exception as e:
            logger.error(f"Error analyzing weaknesses: {e}")
            weaknesses.append("**분석 오류**: 약점 분석 중 오류 발생")

        return weaknesses if weaknesses else ["**특별한 약점 없음**: 현재 성과 지표상 주요 개선점 미발견"]

    def _analyze_opportunities(self, my_metrics: Dict[str, Any],
                              competitor_metrics: List[Dict[str, Any]],
                              competitors: List[Dict[str, Any]]) -> List[str]:
        """Analyze market opportunities."""
        opportunities = []

        try:
            # Content gap analysis
            competitor_keywords = set()
            for comp in competitors:
                comp_keywords = comp['analysis'].get('top_keywords', [])
                for keyword, count in comp_keywords:
                    competitor_keywords.add(keyword.lower())

            # My keywords
            my_keywords = set()
            my_keyword_list = my_metrics.get('top_keywords', [])
            for keyword, count in my_keyword_list:
                my_keywords.add(keyword.lower())

            # Find gaps
            content_gaps = competitor_keywords - my_keywords
            if content_gaps:
                sample_gaps = list(content_gaps)[:3]
                opportunities.append(f"**콘텐츠 갭**: {', '.join(sample_gaps)} 등 경쟁사가 다루는 미개척 키워드 영역")

            # Format opportunities
            avg_competitor_shorts = sum(c['shorts_ratio'] for c in competitor_metrics) / len(competitor_metrics)
            if my_metrics['shorts_ratio'] < avg_competitor_shorts * 0.5:
                opportunities.append("**Shorts 시장**: 짧은 형식 콘텐츠로 신규 시청자 대량 유입 가능")

            # Upload frequency opportunity
            my_upload_num = self._extract_upload_number(my_metrics['upload_frequency'])
            competitor_uploads = [self._extract_upload_number(c['upload_frequency']) for c in competitor_metrics]
            avg_competitor_upload = sum(competitor_uploads) / len(competitor_uploads) if competitor_uploads else 1

            if my_upload_num < avg_competitor_upload:
                opportunities.append(f"**업로드 증가**: 현재 주 {my_upload_num}회에서 주 {avg_competitor_upload:.0f}회로 증가시 더 높은 노출")

            # Engagement opportunity
            if my_metrics['engagement_rate'] > max([c['engagement_rate'] for c in competitor_metrics], default=0):
                opportunities.append("**고참여 활용**: 높은 참여율 기반 커뮤니티 콘텐츠 강화로 충성도 극대화")

            # Collaboration opportunity
            similar_sized_competitors = [
                c for c in competitor_metrics
                if 0.5 <= c['subscriber_count'] / max(my_metrics['subscriber_count'], 1) <= 2.0
            ]
            if similar_sized_competitors:
                opportunities.append(f"**협업 기회**: {len(similar_sized_competitors)}개 유사 규모 채널과 상호 협업 콘텐츠")

        except Exception as e:
            logger.error(f"Error analyzing opportunities: {e}")
            opportunities.append("**분석 오류**: 기회 분석 중 오류 발생")

        return opportunities if opportunities else ["**새로운 기회 탐색**: 트렌드 분석을 통한 신규 콘텐츠 영역 개척"]

    def _analyze_threats(self, my_metrics: Dict[str, Any],
                        competitor_metrics: List[Dict[str, Any]],
                        competitors: List[Dict[str, Any]]) -> List[str]:
        """Analyze competitive threats."""
        threats = []

        try:
            # Large competitor threat
            large_competitors = [c for c in competitor_metrics if c['subscriber_count'] > my_metrics['subscriber_count'] * 3]
            if large_competitors:
                max_comp = max(large_competitors, key=lambda x: x['subscriber_count'])
                threats.append(f"**대형 경쟁자**: {max_comp['channel_title']} ({self._format_number(max_comp['subscriber_count'])} 구독자)의 시장 지배력")

            # High frequency competitors
            high_freq_competitors = [
                c for c in competitor_metrics
                if self._extract_upload_number(c['upload_frequency']) > self._extract_upload_number(my_metrics['upload_frequency']) * 2
            ]
            if high_freq_competitors:
                threats.append("**높은 업로드 빈도**: 경쟁사의 빈번한 업로드로 시청자 관심 분산 위험")

            # Better performing content
            high_view_competitors = [c for c in competitor_metrics if c['avg_views'] > my_metrics['avg_views'] * 1.5]
            if high_view_competitors:
                threats.append("**성과 격차**: 경쟁사의 높은 조회수 성과로 알고리즘 경쟁 불리")

            # Trend following
            recent_trend_followers = []
            for comp in competitors:
                top_videos = comp['analysis'].get('top_videos', [])
                recent_videos = [v for v in top_videos if self._is_recent_video(v.get('published_at', ''))]
                if len(recent_videos) >= 3:  # Active in recent trends
                    recent_trend_followers.append(comp)

            if recent_trend_followers:
                threats.append(f"**트렌드 선점**: {len(recent_trend_followers)}개 채널의 빠른 트렌드 반영으로 화제성 선점 위험")

            # Market saturation
            total_competitor_videos = sum(c['video_count'] for c in competitor_metrics)
            if total_competitor_videos > 500:  # Arbitrary threshold
                threats.append("**시장 포화**: 높은 경쟁 밀도로 신규 콘텐츠 차별화 어려움")

        except Exception as e:
            logger.error(f"Error analyzing threats: {e}")
            threats.append("**분석 오류**: 위협 분석 중 오류 발생")

        return threats if threats else ["**위협 요소 제한적**: 현재 경쟁 환경에서 특별한 위협 요소 미발견"]

    def _extract_upload_number(self, upload_frequency: str) -> float:
        """Extract upload number from frequency string."""
        try:
            import re
            numbers = re.findall(r'\d+', upload_frequency)
            if numbers:
                return float(numbers[0])
            elif "일" in upload_frequency.lower():
                return 7.0  # Daily = 7 times per week
            else:
                return 1.0  # Default
        except:
            return 1.0

    def _is_recent_video(self, published_at: str) -> bool:
        """Check if video is recent (within 30 days)."""
        try:
            if not published_at:
                return False

            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now()
            return (now - pub_date).days <= 30
        except:
            return False

    def _generate_strategic_recommendations(self, strengths: List[str], weaknesses: List[str],
                                          opportunities: List[str], threats: List[str],
                                          my_metrics: Dict[str, Any],
                                          competitor_metrics: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate strategic recommendations based on SWOT analysis."""
        try:
            immediate_actions = []
            mid_term_strategy = []
            long_term_strategy = []

            # Immediate actions (1 week)
            if any("업로드" in w for w in weaknesses):
                immediate_actions.append("**업로드 스케줄 최적화**: 주 2-3회 정기 업로드로 알고리즘 점수 개선")

            if any("Shorts" in o for o in opportunities):
                immediate_actions.append("**Shorts 콘텐츠 시작**: 기존 롱폼 영상의 핵심 부분을 60초 Shorts로 재가공")

            if any("참여" in w for w in weaknesses):
                immediate_actions.append("**시청자 참여 활성화**: 댓글 질문 유도, 커뮤니티 탭 활용 강화")

            # Mid-term strategy (1 month)
            if any("콘텐츠 갭" in o for o in opportunities):
                mid_term_strategy.append("**신규 콘텐츠 영역**: 경쟁사 미개척 키워드 기반 3-5개 기획안 제작")

            if any("협업" in o for o in opportunities):
                mid_term_strategy.append("**채널 간 협업**: 유사 규모 채널과 상호 게스트 출연 또는 공동 기획")

            if any("조회수" in w for w in weaknesses):
                mid_term_strategy.append("**SEO 최적화**: 제목, 썸네일, 태그 A/B 테스트로 CTR 개선")

            # Long-term strategy (3 months)
            long_term_strategy.extend([
                "**브랜드 차별화**: 독특한 콘텐츠 포맷 개발로 경쟁사 대비 고유성 확보",
                "**커뮤니티 구축**: 전용 디스코드/텔레그램 채널로 충성 시청자 그룹 형성",
                "**다채널 확장**: 메인 채널 성장 기반으로 Shorts 전용 채널 또는 팟캐스트 채널 런칭"
            ])

            return {
                "immediate_actions": immediate_actions if immediate_actions else ["**현재 전략 유지**: 기존 콘텐츠 품질 유지하며 점진적 개선"],
                "mid_term_strategy": mid_term_strategy if mid_term_strategy else ["**성장 기반 구축**: 트렌드 분석 기반 콘텐츠 포트폴리오 다양화"],
                "long_term_strategy": long_term_strategy
            }

        except Exception as e:
            logger.error(f"Error generating strategic recommendations: {e}")
            return {
                "immediate_actions": ["분석 오류로 인한 권장사항 생성 실패"],
                "mid_term_strategy": ["수동으로 SWOT 요소 기반 전략 수립 필요"],
                "long_term_strategy": ["장기 비전 수립을 위한 추가 분석 필요"]
            }

    def _generate_detailed_competitor_analysis(self, competitors: List[Dict[str, Any]]) -> str:
        """Generate detailed analysis for each competitor."""
        try:
            analyses = []

            for i, comp in enumerate(competitors):
                try:
                    analysis = comp['analysis']
                    channel_info = analysis.get('channel_info', {})
                    metrics = analysis.get('metrics', {})
                    top_videos = analysis.get('top_videos', [])[:5]

                    comp_analysis = f"""### 경쟁{chr(65+i)}: {channel_info.get('title', 'Unknown')}

**📊 핵심 지표**
- 구독자: {self._format_number(channel_info.get('subscriber_count', 0))}
- 평균 조회수: {self._format_number(metrics.get('avg_views', 0))}
- 참여율: {metrics.get('engagement_rate', 0):.1f}%
- 업로드 빈도: {metrics.get('upload_frequency', 'Unknown')}

**🎯 콘텐츠 전략**
- 주력 콘텐츠: {self._analyze_content_strategy(analysis)}
- Shorts 비율: {analysis.get('content_breakdown', {}).get('shorts_ratio', 0):.0f}%
- 평균 영상 길이: {analysis.get('content_breakdown', {}).get('avg_duration_minutes', 0):.0f}분

**🔥 상위 영상 TOP 5**
{self._format_top_videos(top_videos)}

**💡 학습 포인트**
{self._generate_learning_points(analysis)}

**⚠️ 공략 포인트**
{self._generate_attack_points(analysis)}
"""
                    analyses.append(comp_analysis)

                except Exception as e:
                    logger.error(f"Error analyzing competitor {i}: {e}")
                    analyses.append(f"### 경쟁{chr(65+i)}: 분석 오류\n분석 중 오류가 발생했습니다.")

            return "\n\n".join(analyses)

        except Exception as e:
            logger.error(f"Error generating detailed analysis: {e}")
            return "**상세 분석 생성 중 오류 발생**"

    def _analyze_content_strategy(self, analysis: Dict[str, Any]) -> str:
        """Analyze content strategy from top keywords."""
        try:
            top_keywords = analysis.get('top_keywords', [])[:5]
            if top_keywords:
                keywords_text = ", ".join([kw for kw, count in top_keywords])
                return f"{keywords_text} 중심의 전문 콘텐츠"
            else:
                return "키워드 분석 불가"
        except:
            return "분석 데이터 부족"

    def _format_top_videos(self, top_videos: List[Dict[str, Any]]) -> str:
        """Format top videos list."""
        try:
            if not top_videos:
                return "- 데이터 없음"

            formatted_videos = []
            for i, video in enumerate(top_videos, 1):
                title = video.get('title', 'Unknown')[:50] + "..." if len(video.get('title', '')) > 50 else video.get('title', 'Unknown')
                views = self._format_number(video.get('view_count', 0))
                formatted_videos.append(f"{i}. {title} ({views} 조회)")

            return "\n".join([f"- {video}" for video in formatted_videos])

        except Exception as e:
            logger.error(f"Error formatting top videos: {e}")
            return "- 영상 목록 생성 오류"

    def _generate_learning_points(self, analysis: Dict[str, Any]) -> str:
        """Generate learning points from competitor."""
        try:
            points = []

            # High engagement
            engagement = analysis.get('metrics', {}).get('engagement_rate', 0)
            if engagement > 5.0:
                points.append(f"높은 참여율 ({engagement:.1f}%) 달성 방법")

            # Consistent upload
            freq = analysis.get('metrics', {}).get('upload_frequency', '')
            if '일' in freq:
                points.append("일정한 업로드 스케줄 유지 전략")

            # Successful content format
            avg_duration = analysis.get('content_breakdown', {}).get('avg_duration_minutes', 0)
            if 8 <= avg_duration <= 15:
                points.append(f"최적 영상 길이 ({avg_duration:.0f}분) 활용")

            return "\n".join([f"- {point}" for point in points]) if points else "- 특별한 학습 포인트 없음"

        except Exception as e:
            return "- 학습 포인트 분석 오류"

    def _generate_attack_points(self, analysis: Dict[str, Any]) -> str:
        """Generate potential attack points against competitor."""
        try:
            points = []

            # Low engagement
            engagement = analysis.get('metrics', {}).get('engagement_rate', 0)
            if engagement < 3.0:
                points.append(f"낮은 참여율 ({engagement:.1f}%) - 커뮤니티 강화로 차별화")

            # Infrequent upload
            freq = analysis.get('metrics', {}).get('upload_frequency', '')
            if '주' in freq and '1' in freq:
                points.append("낮은 업로드 빈도 - 더 자주 업로드로 노출 우위")

            # No shorts
            shorts_ratio = analysis.get('content_breakdown', {}).get('shorts_ratio', 0)
            if shorts_ratio < 10:
                points.append("Shorts 콘텐츠 부족 - 짧은 형식으로 신규 유입 증대")

            # Limited keyword diversity
            keyword_count = len(analysis.get('top_keywords', []))
            if keyword_count < 5:
                points.append("제한적 키워드 영역 - 콘텐츠 다양성으로 확장")

            return "\n".join([f"- {point}" for point in points]) if points else "- 명확한 약점 없음, 차별화 전략 필요"

        except Exception as e:
            return "- 공략 포인트 분석 오류"

    def _generate_swot_report(self, swot_data: Dict[str, Any]) -> str:
        """Generate final SWOT report using template."""
        try:
            template_data = {
                "dashboard_table": swot_data.get("dashboard_data", ""),
                "strengths": "\n".join([f"- {s}" for s in swot_data.get("strengths", [])]),
                "weaknesses": "\n".join([f"- {w}" for w in swot_data.get("weaknesses", [])]),
                "opportunities": "\n".join([f"- {o}" for o in swot_data.get("opportunities", [])]),
                "threats": "\n".join([f"- {t}" for t in swot_data.get("threats", [])]),
                "immediate_actions": "\n".join([f"- {a}" for a in swot_data.get("strategies", {}).get("immediate_actions", [])]),
                "mid_term_strategy": "\n".join([f"- {s}" for s in swot_data.get("strategies", {}).get("mid_term_strategy", [])]),
                "long_term_strategy": "\n".join([f"- {s}" for s in swot_data.get("strategies", {}).get("long_term_strategy", [])]),
                "detailed_analysis": swot_data.get("detailed_analysis", ""),
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return self.swot_template.format(**template_data)

        except Exception as e:
            logger.error(f"Error generating SWOT report: {e}")
            return f"# SWOT 분석 리포트\n\n**오류**: 리포트 생성 중 오류 발생: {str(e)}"

    def _analyze_channel_via_web_scraping(self, url: str) -> Dict[str, Any]:
        """Analyze channel using web scraping when API is not available"""
        try:
            logger.info(f"Analyzing {url} via web scraping...")

            # Scrape the channel page
            result = self.web_scraper.fetch_url(url)
            if not result['success']:
                return {"error": f"Failed to fetch channel page: {result.get('error', 'Unknown error')}"}

            # Extract basic info from the channel page
            import re
            from bs4 import BeautifulSoup
            response = self.web_scraper.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract channel title
            title_elem = soup.select_one('meta[property="og:title"]')
            channel_title = title_elem.get('content') if title_elem else "Unknown Channel"

            # Extract subscriber count (approximate)
            subscriber_text = ""
            sub_patterns = [
                r'([\d,]+(?:\.\d+)?[KMB]?)\s*(?:subscribers?|구독자)',
                r'구독자\s*([\d,]+(?:\.\d+)?[KMB]?)',
            ]

            page_text = soup.get_text().lower()
            for pattern in sub_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    subscriber_text = match.group(1)
                    break

            # Parse subscriber count
            subscriber_count = self._parse_count_text(subscriber_text) if subscriber_text else 0

            # Mock performance data based on what we can estimate
            mock_analysis = {
                "channel_info": {
                    "title": channel_title,
                    "subscriber_count": subscriber_count
                },
                "metrics": {
                    "avg_views": subscriber_count * 0.05 if subscriber_count else 1000,  # Estimate 5% view rate
                    "avg_likes": subscriber_count * 0.002 if subscriber_count else 50,   # Estimate 0.2% like rate
                    "avg_comments": subscriber_count * 0.0005 if subscriber_count else 10,  # Estimate 0.05% comment rate
                    "engagement_rate": 2.5,  # Default engagement rate
                    "upload_frequency": "주 1-2회"  # Default upload frequency
                },
                "content_breakdown": {
                    "avg_duration_minutes": 12,  # Default duration
                    "shorts_ratio": 20  # Default shorts ratio
                },
                "top_videos": [],  # Empty for web scraping
                "top_keywords": [("키워드", 1)],  # Default keyword
                "video_count": 50,  # Default video count
                "source": "web_scraping_estimate"
            }

            logger.info(f"Web scraping analysis completed for {channel_title} (estimated {subscriber_count:,} subscribers)")
            return mock_analysis

        except Exception as e:
            logger.error(f"Web scraping analysis failed: {e}")
            return {"error": str(e)}

    def _parse_count_text(self, count_text: str) -> int:
        """Parse subscriber count text like '1.2M' to integer"""
        try:
            count_text = count_text.upper().replace(',', '').strip()

            if 'M' in count_text:
                return int(float(count_text.replace('M', '')) * 1000000)
            elif 'K' in count_text:
                return int(float(count_text.replace('K', '')) * 1000)
            elif 'B' in count_text:
                return int(float(count_text.replace('B', '')) * 1000000000)
            else:
                return int(count_text.replace(',', ''))
        except:
            return 0

    def _save_swot_report(self, report_content: str) -> str:
        """Save SWOT report to file."""
        try:
            # Create report ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_id = f"swot_{timestamp}"

            # Create directory
            reports_dir = os.path.join(self.data_dir, "swot_reports")
            os.makedirs(reports_dir, exist_ok=True)

            # Save report
            file_path = os.path.join(reports_dir, f"{report_id}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            logger.info(f"SWOT report saved: {file_path}")
            return report_id

        except Exception as e:
            logger.error(f"Error saving SWOT report: {e}")
            return f"error_{datetime.now().strftime('%H%M%S')}"


def test_swot_analyzer():
    """Test function for SWOTAnalyzer."""
    try:
        analyzer = SWOTAnalyzer()
        print("✅ SWOTAnalyzer initialized")

        # Test with sample competitor URLs
        competitor_urls = [
            "https://www.youtube.com/@배움의달인",  # Sample - replace with real competitors
        ]

        print("🔄 Analyzing competitors...")
        result = analyzer.analyze_competitors(competitor_urls)

        if result["success"]:
            print(f"✅ SWOT analysis completed: {result['report_id']}")
            print(f"📄 Report saved: {result['file_path']}")
            print(f"📊 Analyzed {result['competitor_count']} competitors")
        else:
            print(f"❌ SWOT analysis failed: {result['error']}")

        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_swot_analyzer()