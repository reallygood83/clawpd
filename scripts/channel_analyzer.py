"""
YouTube channel analyzer - Deep analysis of channel performance and characteristics
"""
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import Counter
import re

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from youtube_api import YouTubeAPI
from keyword_suggest import YouTubeKeywordSuggest


class ChannelAnalyzer:
    def __init__(self, data_dir: str = "data"):
        """Initialize channel analyzer"""
        self.data_dir = data_dir

        try:
            self.youtube_api = YouTubeAPI()
        except Exception as e:
            print(f"⚠️  YouTube API 초기화 실패: {e}")
            self.youtube_api = None

        self.keyword_suggest = YouTubeKeywordSuggest()

    def analyze_channel_dna(self, channel_id: str) -> Dict[str, Any]:
        """Comprehensive channel DNA analysis"""
        if not self.youtube_api:
            return {'error': 'YouTube API not available'}

        try:
            # Get channel info and recent videos
            channel_info = self.youtube_api.get_channel_info(channel_id)
            recent_videos = self.youtube_api.get_recent_videos(channel_id, 50)  # More videos for better analysis

            if not recent_videos:
                return {'error': 'No videos found for analysis'}

            # Perform various analyses
            analysis = {
                'basic_metrics': self._analyze_basic_metrics(channel_info, recent_videos),
                'content_patterns': self._analyze_content_patterns(recent_videos),
                'performance_analysis': self._analyze_performance(recent_videos),
                'keyword_strategy': self._analyze_keyword_strategy(recent_videos),
                'upload_strategy': self._analyze_upload_strategy(recent_videos),
                'engagement_analysis': self._analyze_engagement(recent_videos),
                'content_categories': self._categorize_content(recent_videos),
                'growth_metrics': self._analyze_growth_trajectory(recent_videos),
                'optimization_score': self._calculate_optimization_score(recent_videos),
                'recommendations': self._generate_recommendations(recent_videos),
                'analyzed_at': datetime.now().isoformat()
            }

            return analysis

        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}

    def _analyze_basic_metrics(self, channel_info: Dict, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze basic channel metrics"""
        total_views = sum(v['view_count'] for v in videos)
        total_likes = sum(v['like_count'] for v in videos)
        total_comments = sum(v['comment_count'] for v in videos)

        avg_views = total_views / len(videos) if videos else 0
        avg_likes = total_likes / len(videos) if videos else 0
        avg_comments = total_comments / len(videos) if videos else 0

        # Calculate engagement rate
        engagement_rate = (total_likes + total_comments) / total_views * 100 if total_views > 0 else 0

        # Find best and worst performing videos
        best_video = max(videos, key=lambda x: x['view_count']) if videos else {}
        worst_video = min(videos, key=lambda x: x['view_count']) if videos else {}

        return {
            'subscriber_count': channel_info['subscriber_count'],
            'total_video_count': channel_info['video_count'],
            'analyzed_video_count': len(videos),
            'avg_views_per_video': round(avg_views),
            'avg_likes_per_video': round(avg_likes),
            'avg_comments_per_video': round(avg_comments),
            'overall_engagement_rate': round(engagement_rate, 2),
            'best_performing_video': {
                'title': best_video.get('title', ''),
                'views': best_video.get('view_count', 0),
                'engagement_rate': self._calculate_video_engagement(best_video) if best_video else 0
            },
            'worst_performing_video': {
                'title': worst_video.get('title', ''),
                'views': worst_video.get('view_count', 0),
                'engagement_rate': self._calculate_video_engagement(worst_video) if worst_video else 0
            }
        }

    def _analyze_content_patterns(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze content patterns and themes"""
        titles = [video['title'] for video in videos]

        # Analyze title patterns
        title_lengths = [len(title) for title in titles]
        avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0

        # Extract common words/phrases
        all_words = []
        for title in titles:
            # Extract Korean and English words
            words = re.findall(r'[\w가-힣]+', title.lower())
            all_words.extend([w for w in words if len(w) > 2])

        word_freq = Counter(all_words)
        common_words = word_freq.most_common(20)

        # Analyze punctuation patterns
        punctuation_patterns = {
            '물음표': sum(title.count('?') for title in titles),
            '느낌표': sum(title.count('!') for title in titles),
            '괄호': sum(title.count('(') + title.count('[') for title in titles),
            '숫자': sum(bool(re.search(r'\d', title)) for title in titles),
        }

        # Video duration analysis
        durations = []
        for video in videos:
            duration_str = video.get('duration', '')
            if duration_str:
                duration_seconds = self._parse_duration(duration_str)
                if duration_seconds:
                    durations.append(duration_seconds)

        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            'avg_title_length': round(avg_title_length, 1),
            'common_words': common_words[:10],
            'title_patterns': punctuation_patterns,
            'avg_duration_seconds': round(avg_duration),
            'avg_duration_formatted': self._format_duration(avg_duration),
            'duration_range': {
                'shortest': min(durations) if durations else 0,
                'longest': max(durations) if durations else 0
            },
            'shorts_count': len([d for d in durations if d <= 60]),  # Videos under 60 seconds
            'long_form_count': len([d for d in durations if d > 600])  # Videos over 10 minutes
        }

    def _analyze_performance(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze performance metrics and trends"""
        # Sort videos by publication date
        videos_sorted = sorted(videos, key=lambda x: x['published_at'])

        # Calculate view velocity (views per day since publication)
        view_velocities = []
        for video in videos_sorted:
            try:
                pub_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                days_since_pub = (datetime.now(pub_date.tzinfo) - pub_date).days
                if days_since_pub > 0:
                    velocity = video['view_count'] / days_since_pub
                    view_velocities.append(velocity)
            except:
                continue

        avg_view_velocity = sum(view_velocities) / len(view_velocities) if view_velocities else 0

        # Performance consistency
        view_counts = [v['view_count'] for v in videos]
        if view_counts:
            view_variance = sum((x - sum(view_counts)/len(view_counts))**2 for x in view_counts) / len(view_counts)
            consistency_score = 100 / (1 + view_variance / (sum(view_counts)/len(view_counts))**2)
        else:
            consistency_score = 0

        # Find performance patterns
        top_10_percent = int(len(videos) * 0.1) or 1
        top_performers = sorted(videos, key=lambda x: x['view_count'], reverse=True)[:top_10_percent]

        top_performer_patterns = self._analyze_top_performer_patterns(top_performers)

        return {
            'avg_view_velocity_per_day': round(avg_view_velocity),
            'performance_consistency_score': round(consistency_score, 1),
            'top_performer_count': len(top_performers),
            'top_performer_patterns': top_performer_patterns,
            'performance_quartiles': self._calculate_performance_quartiles(view_counts)
        }

    def _analyze_keyword_strategy(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze keyword usage and SEO strategy"""
        all_tags = []
        all_titles = []
        all_descriptions = []

        for video in videos:
            all_tags.extend(video.get('tags', []))
            all_titles.append(video['title'])
            all_descriptions.append(video.get('description', ''))

        # Tag analysis
        tag_freq = Counter([tag.lower() for tag in all_tags])
        top_tags = tag_freq.most_common(15)

        # Title keyword analysis
        title_words = []
        for title in all_titles:
            words = re.findall(r'[\w가-힣]+', title.lower())
            title_words.extend([w for w in words if len(w) > 2])

        title_keyword_freq = Counter(title_words)
        top_title_keywords = title_keyword_freq.most_common(15)

        # SEO optimization score
        seo_scores = []
        for video in videos:
            score = self._calculate_video_seo_score(video)
            seo_scores.append(score)

        avg_seo_score = sum(seo_scores) / len(seo_scores) if seo_scores else 0

        return {
            'most_used_tags': top_tags,
            'most_used_title_keywords': top_title_keywords,
            'avg_tags_per_video': round(len(all_tags) / len(videos), 1) if videos else 0,
            'avg_seo_optimization_score': round(avg_seo_score, 1),
            'keyword_diversity_score': len(set(all_tags)) / len(all_tags) if all_tags else 0
        }

    def _analyze_upload_strategy(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze upload timing and frequency patterns"""
        upload_times = []
        upload_days = []

        for video in videos:
            try:
                pub_date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                upload_times.append(pub_date.hour)
                upload_days.append(pub_date.weekday())  # 0=Monday, 6=Sunday
            except:
                continue

        # Most common upload times
        time_freq = Counter(upload_times)
        most_common_hours = time_freq.most_common(3)

        # Most common upload days
        day_freq = Counter(upload_days)
        day_names = ['월', '화', '수', '목', '금', '토', '일']
        most_common_days = [(day_names[day], count) for day, count in day_freq.most_common(3)]

        # Upload frequency
        if len(videos) >= 2:
            date_diffs = []
            sorted_videos = sorted(videos, key=lambda x: x['published_at'])
            for i in range(1, len(sorted_videos)):
                try:
                    date1 = datetime.fromisoformat(sorted_videos[i-1]['published_at'].replace('Z', '+00:00'))
                    date2 = datetime.fromisoformat(sorted_videos[i]['published_at'].replace('Z', '+00:00'))
                    diff_days = (date2 - date1).days
                    if diff_days > 0:
                        date_diffs.append(diff_days)
                except:
                    continue

            avg_upload_interval = sum(date_diffs) / len(date_diffs) if date_diffs else 0
            upload_consistency = 100 - (sum(abs(d - avg_upload_interval) for d in date_diffs) / len(date_diffs) / avg_upload_interval * 100 if avg_upload_interval > 0 else 100)
        else:
            avg_upload_interval = 0
            upload_consistency = 0

        return {
            'most_common_upload_hours': most_common_hours,
            'most_common_upload_days': most_common_days,
            'avg_upload_interval_days': round(avg_upload_interval, 1),
            'upload_consistency_score': max(0, round(upload_consistency, 1))
        }

    def _analyze_engagement(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        engagement_rates = []
        like_ratios = []
        comment_ratios = []

        for video in videos:
            engagement_rate = self._calculate_video_engagement(video)
            engagement_rates.append(engagement_rate)

            if video['view_count'] > 0:
                like_ratio = video['like_count'] / video['view_count'] * 100
                comment_ratio = video['comment_count'] / video['view_count'] * 100
                like_ratios.append(like_ratio)
                comment_ratios.append(comment_ratio)

        return {
            'avg_engagement_rate': round(sum(engagement_rates) / len(engagement_rates), 2) if engagement_rates else 0,
            'avg_like_ratio': round(sum(like_ratios) / len(like_ratios), 3) if like_ratios else 0,
            'avg_comment_ratio': round(sum(comment_ratios) / len(comment_ratios), 3) if comment_ratios else 0,
            'engagement_consistency': self._calculate_engagement_consistency(engagement_rates)
        }

    def _categorize_content(self, videos: List[Dict]) -> Dict[str, Any]:
        """Categorize content types"""
        categories = {
            '튜토리얼/교육': 0,
            '리뷰/분석': 0,
            '뉴스/시사': 0,
            '개인생각/오피니언': 0,
            '엔터테인먼트': 0,
            'Q&A/FAQ': 0,
            '라이브/실시간': 0,
            '기타': 0
        }

        category_keywords = {
            '튜토리얼/교육': ['방법', '하는법', '튜토리얼', '강의', '배우기', '설명', '가이드'],
            '리뷰/분석': ['리뷰', '분석', '평가', '비교', '후기', '장단점'],
            '뉴스/시사': ['뉴스', '속보', '발표', '정책', '변화', '업데이트'],
            '개인생각/오피니언': ['생각', '의견', '개인적', '솔직', '진솔'],
            '엔터테인먼트': ['재밌는', '웃긴', '놀라운', '신기한', '흥미'],
            'Q&A/FAQ': ['질문', '답변', 'Q&A', 'FAQ', '궁금한'],
            '라이브/실시간': ['라이브', '실시간', 'LIVE', '생방송']
        }

        for video in videos:
            title = video['title'].lower()
            description = video.get('description', '').lower()
            text = f"{title} {description}"

            categorized = False
            for category, keywords in category_keywords.items():
                if any(keyword in text for keyword in keywords):
                    categories[category] += 1
                    categorized = True
                    break

            if not categorized:
                categories['기타'] += 1

        # Convert to percentages
        total = len(videos)
        category_percentages = {cat: round(count/total*100, 1) for cat, count in categories.items()}

        return category_percentages

    def _analyze_growth_trajectory(self, videos: List[Dict]) -> Dict[str, Any]:
        """Analyze channel growth trajectory"""
        # Sort videos chronologically
        sorted_videos = sorted(videos, key=lambda x: x['published_at'])

        if len(sorted_videos) < 5:
            return {'error': 'Not enough videos for growth analysis'}

        # Split into periods (first half vs second half)
        mid_point = len(sorted_videos) // 2
        early_videos = sorted_videos[:mid_point]
        recent_videos = sorted_videos[mid_point:]

        early_avg_views = sum(v['view_count'] for v in early_videos) / len(early_videos)
        recent_avg_views = sum(v['view_count'] for v in recent_videos) / len(recent_videos)

        growth_rate = (recent_avg_views - early_avg_views) / early_avg_views * 100 if early_avg_views > 0 else 0

        # Engagement growth
        early_engagement = sum(self._calculate_video_engagement(v) for v in early_videos) / len(early_videos)
        recent_engagement = sum(self._calculate_video_engagement(v) for v in recent_videos) / len(recent_videos)

        engagement_growth = recent_engagement - early_engagement

        return {
            'view_growth_rate': round(growth_rate, 1),
            'early_period_avg_views': round(early_avg_views),
            'recent_period_avg_views': round(recent_avg_views),
            'engagement_trend': round(engagement_growth, 2),
            'growth_status': 'growing' if growth_rate > 10 else 'stable' if growth_rate > -10 else 'declining'
        }

    def _calculate_optimization_score(self, videos: List[Dict]) -> Dict[str, Any]:
        """Calculate overall channel optimization score"""
        scores = {
            'seo_score': 0,
            'consistency_score': 0,
            'engagement_score': 0,
            'content_strategy_score': 0
        }

        if not videos:
            return {'overall_score': 0, 'breakdown': scores}

        # SEO Score
        seo_scores = [self._calculate_video_seo_score(video) for video in videos]
        scores['seo_score'] = sum(seo_scores) / len(seo_scores)

        # Consistency Score (upload frequency and timing)
        upload_analysis = self._analyze_upload_strategy(videos)
        scores['consistency_score'] = upload_analysis.get('upload_consistency_score', 0)

        # Engagement Score
        engagement_rates = [self._calculate_video_engagement(video) for video in videos]
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        scores['engagement_score'] = min(avg_engagement * 20, 100)  # Scale to 100

        # Content Strategy Score (diversity and targeting)
        content_categories = self._categorize_content(videos)
        category_distribution = list(content_categories.values())
        diversity_score = 100 - max(category_distribution)  # Lower concentration = higher diversity
        scores['content_strategy_score'] = diversity_score

        overall_score = sum(scores.values()) / len(scores)

        return {
            'overall_score': round(overall_score, 1),
            'breakdown': {k: round(v, 1) for k, v in scores.items()},
            'grade': self._get_score_grade(overall_score)
        }

    def _generate_recommendations(self, videos: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Analyze current state
        performance_analysis = self._analyze_performance(videos)
        keyword_analysis = self._analyze_keyword_strategy(videos)
        upload_analysis = self._analyze_upload_strategy(videos)
        engagement_analysis = self._analyze_engagement(videos)

        # Performance recommendations
        if performance_analysis['performance_consistency_score'] < 50:
            recommendations.append("콘텐츠 성과의 일관성을 높이기 위해 성공한 영상의 패턴을 분석하고 적용하세요.")

        # SEO recommendations
        if keyword_analysis['avg_seo_optimization_score'] < 70:
            recommendations.append("SEO 최적화를 위해 제목에 검색 키워드를 더 효과적으로 포함시키고, 태그를 다양화하세요.")

        # Upload recommendations
        if upload_analysis['upload_consistency_score'] < 70:
            recommendations.append("업로드 일정을 일정하게 유지하여 구독자들의 기대를 관리하세요.")

        # Engagement recommendations
        if engagement_analysis['avg_engagement_rate'] < 3:
            recommendations.append("참여도 향상을 위해 영상에 질문을 포함하고, 댓글 참여를 유도하는 CTA를 추가하세요.")

        # Content recommendations
        content_patterns = self._analyze_content_patterns(videos)
        if content_patterns['shorts_count'] == 0:
            recommendations.append("YouTube Shorts 형태의 짧은 콘텐츠도 제작하여 새로운 시청자층에게 노출되세요.")

        if not recommendations:
            recommendations.append("전반적으로 잘 최적화된 채널입니다. 현재 전략을 유지하면서 새로운 콘텐츠 형식을 실험해보세요.")

        return recommendations[:5]  # Top 5 recommendations

    # Helper methods
    def _calculate_video_engagement(self, video: Dict) -> float:
        """Calculate engagement rate for a single video"""
        if video['view_count'] == 0:
            return 0.0
        return (video['like_count'] + video['comment_count']) / video['view_count'] * 100

    def _calculate_video_seo_score(self, video: Dict) -> float:
        """Calculate SEO optimization score for a video"""
        score = 0

        # Title optimization (30 points)
        title = video['title']
        if len(title) >= 30:  # Good length
            score += 10
        if any(char in title for char in ['?', '!', '|', '-']):  # Engaging punctuation
            score += 10
        if re.search(r'\d', title):  # Numbers in title
            score += 10

        # Description optimization (30 points)
        description = video.get('description', '')
        if len(description) > 100:
            score += 15
        if len(description) > 500:
            score += 15

        # Tags optimization (40 points)
        tags = video.get('tags', [])
        if len(tags) >= 5:
            score += 20
        if len(tags) >= 10:
            score += 20

        return score

    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse YouTube duration format (PT1H2M3S) to seconds"""
        try:
            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = int(match.group(3) or 0)
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return None

    def _format_duration(self, seconds: float) -> str:
        """Format seconds to readable duration"""
        if seconds < 60:
            return f"{int(seconds)}초"
        elif seconds < 3600:
            return f"{int(seconds//60)}분 {int(seconds%60)}초"
        else:
            return f"{int(seconds//3600)}시간 {int((seconds%3600)//60)}분"

    def _calculate_performance_quartiles(self, view_counts: List[int]) -> Dict[str, int]:
        """Calculate performance quartiles"""
        if not view_counts:
            return {'q1': 0, 'median': 0, 'q3': 0}

        sorted_views = sorted(view_counts)
        n = len(sorted_views)

        return {
            'q1': sorted_views[n//4],
            'median': sorted_views[n//2],
            'q3': sorted_views[3*n//4]
        }

    def _analyze_top_performer_patterns(self, top_videos: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in top performing videos"""
        if not top_videos:
            return {}

        # Common words in top performer titles
        top_titles = [video['title'] for video in top_videos]
        all_words = []
        for title in top_titles:
            words = re.findall(r'[\w가-힣]+', title.lower())
            all_words.extend([w for w in words if len(w) > 2])

        common_words = Counter(all_words).most_common(5)

        # Average metrics
        avg_duration = sum(self._parse_duration(v.get('duration', '')) or 0 for v in top_videos) / len(top_videos)
        avg_engagement = sum(self._calculate_video_engagement(v) for v in top_videos) / len(top_videos)

        return {
            'common_title_words': common_words,
            'avg_duration_seconds': round(avg_duration),
            'avg_engagement_rate': round(avg_engagement, 2),
            'sample_titles': [v['title'][:50] + '...' for v in top_videos[:3]]
        }

    def _calculate_engagement_consistency(self, engagement_rates: List[float]) -> float:
        """Calculate how consistent engagement rates are"""
        if len(engagement_rates) < 2:
            return 0.0

        mean_engagement = sum(engagement_rates) / len(engagement_rates)
        variance = sum((rate - mean_engagement) ** 2 for rate in engagement_rates) / len(engagement_rates)
        cv = (variance ** 0.5) / mean_engagement if mean_engagement > 0 else 0

        # Convert coefficient of variation to consistency score (0-100)
        consistency_score = max(0, 100 - cv * 100)
        return round(consistency_score, 1)

    def _get_score_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        else:
            return 'D'


def test_channel_analyzer():
    """Test channel analyzer"""
    analyzer = ChannelAnalyzer()

    # Test with a sample channel
    test_channel_id = input("분석할 채널 ID 입력: ").strip()
    if not test_channel_id:
        print("채널 ID가 제공되지 않았습니다.")
        return

    print("채널 분석 중...")
    analysis = analyzer.analyze_channel_dna(test_channel_id)

    if 'error' in analysis:
        print(f"오류: {analysis['error']}")
        return

    print("\n=== 채널 DNA 분석 결과 ===")
    print(f"전체 최적화 점수: {analysis['optimization_score']['overall_score']}/100 ({analysis['optimization_score']['grade']})")
    print(f"평균 조회수: {analysis['basic_metrics']['avg_views_per_video']:,}")
    print(f"참여율: {analysis['basic_metrics']['overall_engagement_rate']}%")
    print(f"업로드 일관성: {analysis['upload_strategy']['upload_consistency_score']}/100")

    print(f"\n주요 추천사항:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"{i}. {rec}")


if __name__ == "__main__":
    test_channel_analyzer()