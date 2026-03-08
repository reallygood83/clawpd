"""
Onboarding module for YouTube PD Agent
Handles initial channel analysis and source configuration
"""
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from youtube_api import YouTubeAPI
from keyword_suggest import YouTubeKeywordSuggest


class YouTubePDOnboarding:
    def __init__(self, data_dir: str = "data"):
        """Initialize onboarding process"""
        self.data_dir = data_dir
        self.ensure_data_directory()

        # File paths
        self.channel_profile_path = os.path.join(data_dir, "channel_profile.json")
        self.sources_path = os.path.join(data_dir, "sources.json")
        self.competitors_path = os.path.join(data_dir, "competitors.json")

        # Initialize API clients
        try:
            self.youtube_api = YouTubeAPI()
        except Exception as e:
            print(f"⚠️  YouTube API 초기화 실패: {e}")
            print("YOUTUBE_API_KEY 환경변수를 설정해주세요.")
            self.youtube_api = None

        self.keyword_suggest = YouTubeKeywordSuggest()

    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def start_onboarding(self) -> Dict[str, Any]:
        """Start the complete onboarding process"""
        print("🎬 YouTube PD Agent 온보딩을 시작합니다!")
        print("=" * 50)

        # Check if already onboarded
        if self.is_already_onboarded():
            print("✅ 이미 설정이 완료되었습니다.")
            choice = input("새로 설정하시겠습니까? (y/N): ").strip().lower()
            if choice != 'y':
                return self.load_existing_config()

        # Step 1: Channel Analysis
        print("\n📺 Step 1: 채널 분석")
        channel_profile = self.analyze_channel()

        if not channel_profile:
            print("❌ 채널 분석에 실패했습니다.")
            return {}

        # Step 2: Source Configuration
        print("\n📰 Step 2: 정보 소스 설정")
        sources_config = self.configure_sources(channel_profile.get('niche', 'general'))

        # Step 3: Competitor Configuration
        print("\n🏆 Step 3: 경쟁채널 설정")
        competitors_config = self.configure_competitors()

        # Step 4: Save Configuration
        self.save_configuration(channel_profile, sources_config, competitors_config)

        print("\n✅ 온보딩 완료!")
        print("이제 '/기획' 명령으로 기획안을 생성하거나 '/swot' 명령으로 경쟁분석을 할 수 있습니다.")

        return {
            'channel_profile': channel_profile,
            'sources': sources_config,
            'competitors': competitors_config
        }

    def analyze_channel(self) -> Dict[str, Any]:
        """Analyze user's YouTube channel"""
        while True:
            channel_url = input("\n채널 URL을 입력해주세요: ").strip()

            if not channel_url:
                continue

            if not self.youtube_api:
                print("❌ YouTube API가 설정되지 않았습니다.")
                return {}

            try:
                print("🔍 채널 분석 중...")

                # Extract channel ID
                channel_id = self.youtube_api.extract_channel_id(channel_url)

                # Get channel info
                channel_info = self.youtube_api.get_channel_info(channel_id)

                # Analyze performance
                performance = self.youtube_api.analyze_channel_performance(channel_id)

                # Detect niche and target
                niche_detection = self.detect_niche(channel_info, performance)

                # Present results
                print("\n📊 채널 분석 결과:")
                print(f"채널명: {channel_info['title']}")
                print(f"구독자: {channel_info['subscriber_count']:,}명")
                print(f"총 영상: {channel_info['video_count']:,}개")
                print(f"총 조회수: {channel_info['view_count']:,}")
                print(f"평균 조회수: {performance['avg_views_per_video']:,}")
                print(f"참여율: {performance['engagement_rate']}%")
                print(f"업로드 빈도: {performance['avg_upload_frequency_days']:.1f}일마다")

                print(f"\n🎯 감지된 니치: {niche_detection['niche']}")
                print(f"타겟 오디언스: {', '.join(niche_detection['target_audience'])}")
                print(f"주요 키워드: {', '.join(performance['top_keywords'][:5])}")

                # Confirm with user
                confirm = input("\n✅ 분석 결과가 정확한가요? (Y/n): ").strip().lower()

                if confirm in ['', 'y', 'yes']:
                    channel_profile = {
                        'channel_id': channel_id,
                        'channel_url': channel_url,
                        'basic_info': channel_info,
                        'performance_metrics': performance,
                        'niche': niche_detection['niche'],
                        'target_audience': niche_detection['target_audience'],
                        'tone_style': niche_detection['tone_style'],
                        'analyzed_at': datetime.now().isoformat()
                    }

                    return channel_profile

                # Allow manual correction
                print("\n수정할 부분이 있다면 입력해주세요:")
                niche = input(f"니치 ({niche_detection['niche']}): ").strip() or niche_detection['niche']
                target = input(f"타겟 ({', '.join(niche_detection['target_audience'])}): ").strip()

                if target:
                    target_list = [t.strip() for t in target.split(',')]
                else:
                    target_list = niche_detection['target_audience']

                channel_profile = {
                    'channel_id': channel_id,
                    'channel_url': channel_url,
                    'basic_info': channel_info,
                    'performance_metrics': performance,
                    'niche': niche,
                    'target_audience': target_list,
                    'tone_style': niche_detection['tone_style'],
                    'analyzed_at': datetime.now().isoformat()
                }

                return channel_profile

            except Exception as e:
                print(f"❌ 채널 분석 오류: {e}")
                retry = input("다시 시도하시겠습니까? (Y/n): ").strip().lower()
                if retry in ['n', 'no']:
                    return {}

    def detect_niche(self, channel_info: Dict, performance: Dict) -> Dict[str, Any]:
        """Detect channel niche and characteristics"""
        title = channel_info.get('title', '').lower()
        description = channel_info.get('description', '').lower()
        keywords = performance.get('top_keywords', [])

        all_text = f"{title} {description} {' '.join(keywords)}"

        # Niche detection patterns
        niche_patterns = {
            '부동산': ['부동산', '아파트', '재개발', '투자', '전세', '매매', '분양', 'real estate'],
            'AI/테크': ['ai', '인공지능', '테크', '개발', '프로그래밍', '자동화', 'chatgpt', 'claude'],
            '교육': ['교육', '학습', '강의', '공부', '스킬', '배움', '온라인', '튜토리얼'],
            '주식/재테크': ['주식', '투자', '재테크', '경제', '금융', '코인', '펀드', '자산'],
            '뷰티/패션': ['뷰티', '화장품', '패션', '스타일', '코디', '메이크업'],
            '요리/음식': ['요리', '음식', '레시피', '맛집', '쿠킹', '베이킹'],
            '여행/브이로그': ['여행', '브이로그', 'vlog', '일상', '라이프스타일'],
            '게임': ['게임', '스트리머', '플레이', '공략', 'gaming'],
            '운동/헬스': ['운동', '헬스', '피트니스', '다이어트', '요가', '홈트']
        }

        detected_niche = 'general'
        max_matches = 0

        for niche, patterns in niche_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in all_text)
            if matches > max_matches:
                max_matches = matches
                detected_niche = niche

        # Determine target audience based on niche
        target_audiences = {
            '부동산': ['투자자', '직장인', '30-40대', '예비 투자자'],
            'AI/테크': ['개발자', '직장인', '학생', '테크 얼리어답터'],
            '교육': ['학생', '직장인', '교사', '학부모'],
            '주식/재테크': ['투자자', '직장인', '20-40대', '경제 관심층'],
            'general': ['일반 시청자', '관심 분야 학습자']
        }

        # Determine tone/style
        tone_styles = {
            '부동산': '전문가 신뢰감 + 시의성 강조',
            'AI/테크': '친근한 교육자 + 실전 데모',
            '교육': '체계적 설명 + 친근한 선생님',
            '주식/재테크': '데이터 기반 + 실용적 조언',
            'general': '친근하고 정보 전달 중심'
        }

        return {
            'niche': detected_niche,
            'target_audience': target_audiences.get(detected_niche, target_audiences['general']),
            'tone_style': tone_styles.get(detected_niche, tone_styles['general'])
        }

    def configure_sources(self, niche: str = 'general') -> Dict[str, Any]:
        """Configure information sources"""
        print("\n📰 정보 소스를 설정합니다.")
        print("콘텐츠 소재를 주로 어디서 찾으시나요?")

        # Suggest default sources based on niche
        default_sources = self.get_default_sources(niche)

        print(f"\n💡 '{niche}' 니치 추천 소스:")
        for i, source in enumerate(default_sources, 1):
            print(f"{i}. {source['name']} - {source['description']}")

        sources = []

        # Ask if user wants to use default sources
        use_default = input("\n추천 소스를 사용하시겠습니까? (Y/n): ").strip().lower()

        if use_default in ['', 'y', 'yes']:
            sources.extend(default_sources)
            print("✅ 추천 소스가 추가되었습니다.")

        # Allow custom sources
        print("\n추가 소스를 등록하고 싶으면 URL을 입력하세요 (엔터로 종료):")

        while True:
            url = input("소스 URL: ").strip()
            if not url:
                break

            name = input("소스 이름: ").strip()
            description = input("설명 (선택): ").strip()

            source_type = self.detect_source_type(url)

            sources.append({
                'name': name or url,
                'url': url,
                'type': source_type,
                'description': description,
                'enabled': True,
                'added_at': datetime.now().isoformat()
            })

            print(f"✅ '{name or url}' 추가됨")

        return {
            'sources': sources,
            'niche': niche,
            'configured_at': datetime.now().isoformat()
        }

    def get_default_sources(self, niche: str) -> List[Dict[str, str]]:
        """Get default sources for a specific niche"""
        default_sources = {
            '부동산': [
                {
                    'name': '매일경제 부동산',
                    'url': 'https://www.mk.co.kr/news/realestate/',
                    'type': 'web',
                    'description': '부동산 뉴스 및 시장 분석',
                    'enabled': True
                },
                {
                    'name': '한경 부동산',
                    'url': 'https://www.hankyung.com/realestate',
                    'type': 'web',
                    'description': '부동산 시장 동향',
                    'enabled': True
                },
                {
                    'name': '네이버 부동산 뉴스',
                    'url': 'naver_search:부동산 투자',
                    'type': 'naver_news',
                    'description': '네이버 부동산 관련 뉴스',
                    'enabled': True
                }
            ],
            'AI/테크': [
                {
                    'name': 'AI 타임스',
                    'url': 'https://www.aitimes.com',
                    'type': 'web',
                    'description': 'AI 업계 뉴스',
                    'enabled': True
                },
                {
                    'name': '테크크런치',
                    'url': 'https://techcrunch.com/feed/',
                    'type': 'rss',
                    'description': '글로벌 테크 뉴스',
                    'enabled': True
                }
            ],
            '주식/재테크': [
                {
                    'name': '매일경제 증권',
                    'url': 'https://www.mk.co.kr/news/stock/',
                    'type': 'web',
                    'description': '주식 시장 뉴스',
                    'enabled': True
                },
                {
                    'name': '한국경제 증권',
                    'url': 'https://www.hankyung.com/finance/stock',
                    'type': 'web',
                    'description': '증권 시장 분석',
                    'enabled': True
                }
            ]
        }

        return default_sources.get(niche, [
            {
                'name': '네이버 뉴스',
                'url': f'naver_search:{niche}',
                'type': 'naver_news',
                'description': f'{niche} 관련 뉴스',
                'enabled': True
            }
        ])

    def detect_source_type(self, url: str) -> str:
        """Detect the type of source from URL"""
        if url.startswith('naver_search:'):
            return 'naver_search'
        elif '/rss' in url or '/feed' in url or url.endswith('.xml'):
            return 'rss'
        elif 'cafe.naver.com' in url:
            return 'naver_cafe'
        elif 'blog.naver.com' in url:
            return 'naver_blog'
        else:
            return 'web'

    def configure_competitors(self) -> Dict[str, Any]:
        """Configure competitor channels"""
        print("\n🏆 경쟁채널 설정 (선택사항)")
        print("참고하거나 경쟁하는 채널이 있다면 최대 5개까지 입력해주세요.")

        competitors = []
        competitor_count = 0

        while competitor_count < 5:
            url = input(f"\n경쟁채널 URL #{competitor_count + 1} (엔터로 종료): ").strip()

            if not url:
                break

            if not self.youtube_api:
                print("❌ YouTube API가 설정되지 않아 채널 분석을 할 수 없습니다.")
                competitors.append({
                    'url': url,
                    'analysis': {},
                    'added_at': datetime.now().isoformat()
                })
                competitor_count += 1
                continue

            try:
                print("🔍 경쟁채널 분석 중...")

                # Analyze competitor
                channel_id = self.youtube_api.extract_channel_id(url)
                channel_info = self.youtube_api.get_channel_info(channel_id)
                performance = self.youtube_api.analyze_channel_performance(channel_id)

                print(f"✅ {channel_info['title']} (구독자: {channel_info['subscriber_count']:,}명)")

                competitors.append({
                    'channel_id': channel_id,
                    'url': url,
                    'basic_info': channel_info,
                    'performance_metrics': performance,
                    'added_at': datetime.now().isoformat()
                })

                competitor_count += 1

            except Exception as e:
                print(f"❌ 채널 분석 오류: {e}")
                retry = input("다시 시도하시겠습니까? (y/N): ").strip().lower()
                if retry == 'y':
                    continue
                else:
                    break

        return {
            'competitors': competitors,
            'configured_at': datetime.now().isoformat()
        }

    def save_configuration(self, channel_profile: Dict, sources_config: Dict, competitors_config: Dict):
        """Save all configuration to JSON files"""
        try:
            # Save channel profile
            with open(self.channel_profile_path, 'w', encoding='utf-8') as f:
                json.dump(channel_profile, f, ensure_ascii=False, indent=2)

            # Save sources
            with open(self.sources_path, 'w', encoding='utf-8') as f:
                json.dump(sources_config, f, ensure_ascii=False, indent=2)

            # Save competitors
            with open(self.competitors_path, 'w', encoding='utf-8') as f:
                json.dump(competitors_config, f, ensure_ascii=False, indent=2)

            print("\n💾 설정이 저장되었습니다.")

        except Exception as e:
            print(f"❌ 설정 저장 오류: {e}")

    def is_already_onboarded(self) -> bool:
        """Check if onboarding is already completed"""
        return (os.path.exists(self.channel_profile_path) and
                os.path.exists(self.sources_path))

    def load_existing_config(self) -> Dict[str, Any]:
        """Load existing configuration"""
        config = {}

        try:
            if os.path.exists(self.channel_profile_path):
                with open(self.channel_profile_path, 'r', encoding='utf-8') as f:
                    config['channel_profile'] = json.load(f)

            if os.path.exists(self.sources_path):
                with open(self.sources_path, 'r', encoding='utf-8') as f:
                    config['sources'] = json.load(f)

            if os.path.exists(self.competitors_path):
                with open(self.competitors_path, 'r', encoding='utf-8') as f:
                    config['competitors'] = json.load(f)

        except Exception as e:
            print(f"❌ 설정 로드 오류: {e}")

        return config


def main():
    """Main function for running onboarding as standalone script"""
    print("🎬 YouTube PD Agent - 온보딩")

    onboarding = YouTubePDOnboarding()
    config = onboarding.start_onboarding()

    if config:
        print("\n🎉 온보딩 완료!")
        print("이제 다음 명령을 사용할 수 있습니다:")
        print("- python plan_generator.py : 기획안 생성")
        print("- python swot_analyzer.py : 경쟁분석")
    else:
        print("\n❌ 온보딩이 완료되지 않았습니다.")


if __name__ == "__main__":
    main()