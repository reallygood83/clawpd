# YouTube PD Agent v1.1

AI 기반 유튜브 콘텐츠 기획 전문 에이전트. 실시간 트렌드 분석, PD급 기획안 생성, 경쟁사 SWOT 분석을 수행합니다.

## 명령어

### `/기획` - PD급 콘텐츠 기획안 생성

최신 트렌드를 분석하여 전문 PD 수준의 유튜브 콘텐츠 기획안을 생성합니다.

사용법:
- `/기획` - 이번 주 추천 주제로 기획안 생성
- `/기획 [특정 주제]` - 지정한 주제로 기획안 생성

이 명령어를 실행하면 다음과 같은 작업을 수행합니다:

1. **소스 수집**: 등록된 RSS 피드, 뉴스 사이트, 네이버 카페에서 최신 콘텐츠 수집
2. **트렌드 매칭**: 수집된 정보와 YouTube 키워드 트렌드 교차 분석
3. **LLM 프롬프트 생성**: OpenClaw LLM이 처리할 상세한 프롬프트 생성
4. **PD급 기획안 출력**: 초 단위 큐시트, 완전한 대본, 썸네일 디자인, SEO 패키지 포함

```python
import sys
sys.path.append("scripts")
sys.path.append("scripts/utils")

from source_collector import SourceCollector
from trend_matcher import TrendMatcher
from plan_generator import PlanGenerator
import json

def execute_planning(topic=None):
    try:
        print("🚀 YouTube PD Agent v1.1 실행 중...")

        # 1. 소스 수집
        print("📡 최신 트렌드 수집 중...")
        collector = SourceCollector()
        collection_results = collector.collect_all_sources(hours_back=24)

        if collection_results['summary']['total_items'] == 0:
            print("⚠️ 소스에서 새로운 컨텐츠를 찾지 못했습니다. 기본 키워드로 진행합니다.")

        # 2. 트렌드 매칭
        print("🎯 트렌드 분석 중...")
        trend_matcher = TrendMatcher()

        if topic:
            # 특정 주제 지정
            recommendations = trend_matcher.analyze_topic_trend(topic)
        else:
            # 자동 추천
            recommendations = trend_matcher.match_sources_to_trends(collection_results)

        if not recommendations or len(recommendations) == 0:
            print("❌ 추천할 만한 트렌드를 찾지 못했습니다.")
            return

        best_recommendation = recommendations[0]
        print(f"✅ 최적 주제 선정: {best_recommendation.get('topic', 'Unknown')}")

        # 3. LLM 프롬프트 생성
        print("🤖 OpenClaw LLM용 프롬프트 생성 중...")
        plan_generator = PlanGenerator()
        llm_prompt = plan_generator.generate_llm_prompt(best_recommendation)

        print("\n" + "="*80)
        print("📋 OpenClaw LLM 프롬프트")
        print("="*80)
        print(llm_prompt)
        print("="*80)

        # 4. 백업: 기본 기획안도 생성
        print("\n📄 기본 기획안 생성 중...")
        plan_content = plan_generator.generate_comprehensive_plan(best_recommendation)

        print(f"\n✅ 완료! PD급 기획안이 생성되었습니다.")
        print(f"📁 파일 경로: data/plan_history/")

        # 5. 요약 출력
        print(f"\n📊 기획안 요약:")
        print(f"  • 주제: {best_recommendation.get('topic', 'N/A')}")
        print(f"  • 예상 조회수: {best_recommendation.get('target_views', 'N/A'):,}회" if best_recommendation.get('target_views') else "  • 예상 조회수: 분석 중")
        print(f"  • 트렌드 스코어: {best_recommendation.get('demand_score', 0):.1f}/5.0")
        print(f"  • 소스: {', '.join(best_recommendation.get('sources', [])[:3])}")

        return {
            "success": True,
            "topic": best_recommendation.get('topic'),
            "llm_prompt": llm_prompt,
            "plan_content": plan_content,
            "recommendation": best_recommendation
        }

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return {"success": False, "error": str(e)}

# 실행
if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    result = execute_planning(topic)
```

### `/swot [채널URL]` - 경쟁 채널 SWOT 분석

경쟁 채널들을 분석하여 상세한 SWOT 분석 리포트를 생성합니다.

사용법:
- `/swot https://youtube.com/@경쟁채널` - 특정 채널 분석
- `/swot https://youtube.com/@채널1 https://youtube.com/@채널2` - 여러 채널 비교 분석

```python
import sys
sys.path.append("scripts")
sys.path.append("scripts/utils")

from swot_analyzer import SWOTAnalyzer

def execute_swot_analysis(competitor_urls):
    try:
        print("📊 SWOT 분석 시작...")

        if isinstance(competitor_urls, str):
            competitor_urls = [competitor_urls]

        analyzer = SWOTAnalyzer()
        result = analyzer.analyze_competitors(competitor_urls)

        if result["success"]:
            print("✅ SWOT 분석 완료!")
            print(f"📁 리포트 저장: {result['file_path']}")
            print(f"📈 분석된 채널 수: {result['competitor_count']}")

            print("\n" + "="*80)
            print("📋 SWOT 분석 리포트")
            print("="*80)
            print(result["report_content"])
            print("="*80)

            return result
        else:
            print(f"❌ SWOT 분석 실패: {result['error']}")
            return result

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return {"success": False, "error": str(e)}

# 실행
if __name__ == "__main__":
    urls = sys.argv[1:] if len(sys.argv) > 1 else []
    if not urls:
        print("❌ 채널 URL을 지정해주세요")
        print("예: /swot https://youtube.com/@경쟁채널")
    else:
        result = execute_swot_analysis(urls)
```

### `/온보딩` - 채널 초기 설정

새로운 채널의 니치, 톤앤매너, 타겟 오디언스를 분석하고 정보 소스를 등록합니다.

```python
import sys
sys.path.append("scripts")

from onboard import OnboardingAgent

def execute_onboarding():
    try:
        print("🎬 YouTube PD Agent 온보딩 시작...")

        agent = OnboardingAgent()
        result = agent.run_onboarding()

        if result["success"]:
            print("✅ 온보딩 완료!")
            print(f"📁 설정 저장: data/channel_profile.json")

            profile = result["profile"]
            print(f"\n📊 채널 프로필:")
            print(f"  • 니치: {profile.get('detected_niche', 'N/A')}")
            print(f"  • 톤앤매너: {profile.get('detected_tone', 'N/A')}")
            print(f"  • 등록된 소스 수: {len(profile.get('sources', []))}")

            return result
        else:
            print(f"❌ 온보딩 실패: {result['error']}")
            return result

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return {"success": False, "error": str(e)}

# 실행
if __name__ == "__main__":
    result = execute_onboarding()
```

### `/소스관리` - 정보 소스 관리

RSS 피드, 뉴스 사이트, 네이버 카페 등 정보 수집 소스를 관리합니다.

사용법:
- `/소스관리` - 현재 등록된 소스 목록 조회
- `/소스관리 추가 "소스명" "URL"` - 새 소스 추가
- `/소스관리 삭제 "소스명"` - 소스 삭제
- `/소스관리 테스트` - 모든 소스 수집 테스트

```python
import sys
sys.path.append("scripts")
sys.path.append("scripts/utils")

from source_collector import SourceCollector

def execute_source_management(action=None, *args):
    try:
        collector = SourceCollector()

        if action == "추가" and len(args) >= 2:
            name, url = args[0], args[1]
            keywords = list(args[2:]) if len(args) > 2 else []

            success = collector.add_source(name, url, keywords=keywords)
            if success:
                print(f"✅ 소스 추가됨: {name} ({url})")
            else:
                print(f"❌ 소스 추가 실패: {name}")

        elif action == "삭제" and len(args) >= 1:
            name = args[0]
            success = collector.remove_source(name)
            if success:
                print(f"✅ 소스 삭제됨: {name}")
            else:
                print(f"❌ 소스 삭제 실패: {name}")

        elif action == "테스트":
            print("🧪 소스 수집 테스트 중...")
            results = collector.collect_all_sources(hours_back=6)

            print(f"📊 수집 결과:")
            print(f"  • 성공한 소스: {results['summary']['successful_sources']}/{results['summary']['total_sources']}")
            print(f"  • 총 수집 아이템: {results['summary']['total_items']}")
            if results['summary']['errors']:
                print(f"  • 오류: {len(results['summary']['errors'])}개")
                for error in results['summary']['errors'][:3]:
                    print(f"    - {error}")

        else:
            # 소스 목록 조회 (기본 동작)
            sources = collector.list_sources()
            summary = collector.get_source_summary()

            print(f"📋 등록된 정보 소스: {summary['total_sources']}개")
            print(f"  • 활성화: {summary['enabled_sources']}개")
            print(f"  • 비활성화: {summary['disabled_sources']}개")

            if summary.get('last_collection'):
                last = summary['last_collection']
                print(f"  • 마지막 수집: {last['collected_at']}")
                print(f"  • 수집된 아이템: {last['total_items']}개")

            print(f"\n📄 소스 목록:")
            for source in sources:
                status = "🟢" if source['enabled'] else "🔴"
                print(f"  {status} {source['name']} ({source['type']}) - {source['url']}")

        return {"success": True}

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return {"success": False, "error": str(e)}

# 실행
if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    result = execute_source_management(*args)
```

## OpenClaw 통합

이 스킬은 OpenClaw의 LLM과 완전 통합되어 작동합니다:

1. **명령어 실행** → 데이터 수집 및 분석
2. **LLM 프롬프트 생성** → 주제별 맞춤 프롬프트 생성
3. **OpenClaw LLM 처리** → 구체적이고 실용적인 콘텐츠 생성
4. **최종 결과** → 바로 사용 가능한 PD급 기획안

### LLM 프롬프트 템플릿

각 명령어는 OpenClaw LLM이 처리할 수 있는 상세한 프롬프트를 생성합니다:

- **주제 특화**: 실제 주제에 맞는 구체적 내용 생성 지시
- **플레이스홀더 금지**: `[핵심 내용 1]` 등 일반적 표현 사용 금지
- **채널 맞춤**: 니치, 톤앤매너, 타겟 반영
- **데이터 기반**: 수집된 실제 소스와 트렌드 반영
- **구조화된 출력**: 마크다운 형식의 완성된 기획안

## 설치 및 설정

### 1. 환경 설정
```bash
# 필수 패키지 설치
pip install -r requirements.txt

# 환경변수 설정 (.env 파일 생성)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 2. 데이터 디렉터리 생성
```bash
mkdir -p data/plan_history
mkdir -p data/swot_reports
mkdir -p templates
```

### 3. 초기 온보딩 실행
```bash
python -c "
import sys; sys.path.append('scripts')
from onboard import OnboardingAgent
agent = OnboardingAgent()
result = agent.run_onboarding()
print('온보딩 완료:', result['success'])
"
```

## 결과물 예시

### PD급 기획안 구성
- 📊 기획 의도 + 데이터 근거
- 🎯 초 단위 큐시트 (12분)
- 📝 전체 대본 초안 (2000자+)
- 🎨 썸네일 시안 3종
- 🔍 SEO 패키지 (제목/설명/태그)
- 📈 예상 성과 지표

### SWOT 분석 리포트 구성
- 📈 채널 비교 대시보드
- 🎯 강점 (Strengths)
- ⚠️ 약점 (Weaknesses)
- 🌟 기회 (Opportunities)
- ⚡ 위협 (Threats)
- 🚀 3단계 전략 제안

모든 결과물은 `data/` 디렉터리에 마크다운 파일로 저장되며, 바로 사용 가능한 실무적 내용으로 구성됩니다.