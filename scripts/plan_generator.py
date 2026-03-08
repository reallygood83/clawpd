"""
Plan Generator - Creates comprehensive PD-level YouTube content plans
Generates cue sheets, full scripts, thumbnails, SEO packages, and shooting guides
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlanGenerator:
    """Generate comprehensive YouTube content plans at PD level."""

    def __init__(self, data_dir: str = "data", templates_dir: str = "templates"):
        """Initialize the plan generator."""
        self.data_dir = data_dir
        self.templates_dir = templates_dir

        # Load configurations
        self.channel_profile = self._load_channel_profile()
        self.plan_template = self._load_plan_template()

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

    def _load_plan_template(self) -> str:
        """Load the PD plan template."""
        try:
            template_file = os.path.join(self.templates_dir, "pd_plan.md")
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return self._get_default_template()
        except Exception as e:
            logger.error(f"Error loading plan template: {e}")
            return self._get_default_template()

    def _get_default_template(self) -> str:
        """Get default plan template if file doesn't exist."""
        return """# 🎬 [PD급 기획안] {title}

## 📊 1. 기획 의도 + 데이터 근거

### 트렌드 분석
- **주제**: {topic}
- **트렌드 스코어**: {trend_score}/10
- **검색 수요**: {search_demand}
- **시의성**: {timeliness}
- **소스 근거**: {sources}

### 채널 적합도
- **니치 매칭**: {niche_match}
- **타겟 관심도**: {target_interest}
- **예상 성과**: {performance_estimate}

### 경쟁 분석
- **동일 주제 영상 수**: {competitor_count}
- **상위 영상 평균 조회수**: {avg_competitor_views}
- **차별화 포인트**: {differentiation}

---

## 🎯 2. 초 단위 큐시트 ({duration}분)

{cue_sheet}

---

## 📝 3. 전체 대본 초안

{full_script}

---

## 🎨 4. 썸네일 시안 3종

{thumbnail_designs}

---

## 🎬 5. 촬영 가이드

{shooting_guide}

---

## 🔍 6. SEO 패키지

{seo_package}

---

## 📈 7. 예상 성과

{performance_metrics}

---

## 🚀 8. 경쟁 차별화 전략

{competitive_strategy}

---

*생성일: {generated_date}*
*기획자: YouTube PD Agent v1.0*
"""

    def generate_llm_prompt(self, recommendation: Dict[str, Any],
                           additional_context: Dict[str, Any] = None) -> str:
        """Generate a detailed LLM prompt for OpenClaw to create SPECIFIC content"""
        try:
            logger.info(f"Generating LLM prompt for: {recommendation.get('topic', 'Unknown')}")

            topic = recommendation.get("topic", "")
            content_angle = recommendation.get("content_angle", "")
            sources = recommendation.get("sources", [])
            tags = recommendation.get("tags", [])

            # Extract channel info
            channel_niche = self.channel_profile.get("detected_niche", "")
            channel_tone = self.channel_profile.get("detected_tone", "친근한")

            prompt = f"""# YouTube PD Agent v1.1 - SPECIFIC Content Creation Prompt

## 📋 PROJECT BRIEF
- **주제**: {topic}
- **콘텐츠 각도**: {content_angle}
- **채널 니치**: {channel_niche}
- **톤앤매너**: {channel_tone}
- **소스 근거**: {', '.join(sources[:5])}
- **타겟 키워드**: {', '.join(tags[:10])}

## 🎯 CREATION REQUIREMENTS

### CRITICAL: NO PLACEHOLDERS ALLOWED
- 절대로 [핵심 내용 1], [구체적 설명] 등 플레이스홀더 사용 금지
- 모든 내용은 주제에 SPECIFIC하게 작성
- 실제 사용 가능한 콘텐츠만 생성

### 1. 초 단위 큐시트 (12분 영상 기준)
다음 구조로 SPECIFIC한 멘트와 B-roll 지시사항 작성:

```
0:00-0:15 훅
- 실제 멘트: "{topic}에 대한 충격적인 사실을 발견했는데..."
- B-roll: {topic} 관련 뉴스 헤드라인
- 그래픽: "놓치면 후회" 텍스트 오버레이

0:15-0:45 문제 제기
- 실제 멘트: 구체적인 현황과 문제점 설명
- B-roll: 관련 데이터, 차트
- 그래픽: 핵심 수치 강조

[계속해서 12분까지 구체적 구성]
```

### 2. 완전한 대본 (2000자 이상)
- 인트로: 구체적인 인사말과 오늘 주제 소개
- 본론: 5개 핵심 포인트를 실제 정보로 작성
- 마무리: 구체적인 결론과 액션 아이템

### 3. 썸네일 디자인 3종
각 디자인마다:
- 정확한 텍스트 (예: "{topic} 완전 분석" 대신 실제 제목)
- 구체적 컬러 코드
- 정확한 레이아웃 지시사항

### 4. SEO 패키지
- 제목 3안: CTR 8% 이상 목표로 실제 제목
- 설명란: 실제 타임스탬프와 구체적 내용 요약
- 태그 30개: 실제 검색 가능한 한국어/영어 태그

### 5. 성과 예측
- 구체적 조회수 예측 (근거와 함께)
- 참여율 예상 (채널 히스토리 기반)
- 신뢰도 및 근거

## 📊 DATA TO USE
"""

            # Add specific data if available
            if recommendation.get("demand_score"):
                prompt += f"\n- 검색 수요 스코어: {recommendation['demand_score']}"
            if recommendation.get("competition_score"):
                prompt += f"\n- 경쟁 강도: {recommendation['competition_score']}"
            if recommendation.get("target_views"):
                prompt += f"\n- 목표 조회수: {recommendation['target_views']:,}회"

            prompt += f"""

## 🎬 OUTPUT FORMAT
마크다운 형식으로 다음 구조 준수:

# 🎬 [PD급 기획안] {{실제_제목}}

## 📊 1. 기획 의도 + 데이터 근거
[구체적 트렌드 분석 및 기획 근거]

## 🎯 2. 초 단위 큐시트 (12분)
[실제 멘트와 구체적 B-roll 지시사항]

## 📝 3. 전체 대본 초안
[2000자 이상의 실제 사용 가능한 대본]

## 🎨 4. 썸네일 시안 3종
[구체적 디자인 지시사항]

## 🔍 5. SEO 패키지
[실제 제목, 설명, 태그]

## 📈 6. 예상 성과
[구체적 수치와 근거]

---

**REMEMBER**: 이 프롬프트는 OpenClaw LLM이 처리하여 완전한 PD급 기획안을 생성합니다. 모든 내용은 {topic}에 SPECIFIC해야 하며, 플레이스홀더나 일반적인 내용은 절대 불허합니다.
"""

            return prompt

        except Exception as e:
            logger.error(f"Error generating LLM prompt: {e}")
            return f"# LLM 프롬프트 생성 오류\n\n오류: {str(e)}"

    def generate_comprehensive_plan(self, recommendation: Dict[str, Any],
                                   additional_context: Dict[str, Any] = None) -> str:
        """Generate a comprehensive PD-level content plan."""
        try:
            logger.info(f"Generating comprehensive plan for: {recommendation.get('topic', 'Unknown')}")

            # Extract basic information
            topic = recommendation.get("topic", "")
            content_angle = recommendation.get("content_angle", "")

            # Generate all plan components
            plan_data = {
                "title": self._generate_title_options(topic, content_angle),
                "topic": topic,
                "content_angle": content_angle,
                "trend_score": recommendation.get("trend_score", 0),
                "search_demand": self._format_search_demand(recommendation.get("search_demand", 0)),
                "timeliness": self._assess_timeliness(recommendation),
                "sources": self._format_sources(recommendation.get("sources", [])),
                "niche_match": self._assess_niche_match(recommendation),
                "target_interest": self._assess_target_interest(recommendation),
                "performance_estimate": self._format_performance_estimate(recommendation.get("performance_estimate", {})),
                "competitor_count": self._estimate_competitor_count(topic),
                "avg_competitor_views": self._estimate_competitor_views(topic),
                "differentiation": self._generate_differentiation_points(topic, content_angle),
                "duration": self._suggest_video_duration(recommendation),
                "cue_sheet": self._generate_cue_sheet(topic, content_angle, recommendation),
                "full_script": self._generate_full_script(topic, content_angle, recommendation),
                "thumbnail_designs": self._generate_thumbnail_designs(topic, content_angle),
                "shooting_guide": self._generate_shooting_guide(recommendation),
                "seo_package": self._generate_seo_package(topic, content_angle, recommendation),
                "performance_metrics": self._generate_performance_metrics(recommendation),
                "competitive_strategy": self._generate_competitive_strategy(topic, recommendation),
                "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Fill template
            plan_content = self.plan_template.format(**plan_data)

            # Save plan
            plan_id = self._save_plan(plan_content, topic)

            logger.info(f"Plan generated successfully: {plan_id}")
            return plan_content

        except Exception as e:
            logger.error(f"Error generating comprehensive plan: {e}")
            return f"# 오류 발생\n\n기획안 생성 중 오류가 발생했습니다: {str(e)}"

    def _generate_title_options(self, topic: str, content_angle: str) -> List[Dict[str, str]]:
        """Generate multiple title options with SEO strategies."""
        try:
            channel_niche = self.channel_profile.get("detected_niche", "").lower()

            titles = []

            # Title option 1: Direct and urgent
            title1 = f"🔥 {topic} 지금 주목해야 하는 이유 (놓치면 후회)"
            titles.append({
                "title": title1,
                "strategy": "긴급성 + 감정적 호소",
                "target_ctr": "8-12%"
            })

            # Title option 2: Expert authority
            if "부동산" in channel_niche:
                title2 = f"부동산 전문가가 알려주는 {topic} 핵심 포인트 BEST 5"
            elif "ai" in channel_niche or "테크" in channel_niche:
                title2 = f"AI 전문가가 분석한 {topic} 완벽 가이드"
            else:
                title2 = f"전문가가 직접 분석한 {topic} 핵심 정리"

            titles.append({
                "title": title2,
                "strategy": "권위성 + 구조화된 정보",
                "target_ctr": "6-9%"
            })

            # Title option 3: Trend and timing
            current_year = datetime.now().year
            title3 = f"{current_year} {topic} 트렌드 총정리 | 지금 알아야 할 모든 것"
            titles.append({
                "title": title3,
                "strategy": "최신성 + 포괄성",
                "target_ctr": "5-8%"
            })

            return titles

        except Exception as e:
            logger.error(f"Error generating title options: {e}")
            return [{"title": f"{topic} 완벽 분석", "strategy": "기본형", "target_ctr": "4-6%"}]

    def _format_search_demand(self, demand_score: float) -> str:
        """Format search demand score into readable text."""
        if demand_score >= 4.0:
            return f"높음 (스코어: {demand_score:.1f}) - YouTube 자동완성 상위 등장"
        elif demand_score >= 2.5:
            return f"보통 (스코어: {demand_score:.1f}) - 검색 수요 확인"
        else:
            return f"낮음 (스코어: {demand_score:.1f}) - 니치 키워드"

    def _assess_timeliness(self, recommendation: Dict[str, Any]) -> str:
        """Assess the timeliness of the topic."""
        recency = recommendation.get("recency", 0)

        if recency >= 8:
            return "매우 높음 - 24시간 내 핫이슈"
        elif recency >= 5:
            return "높음 - 최근 3일 내 화제"
        elif recency >= 3:
            return "보통 - 1주일 내 관심 증가"
        else:
            return "낮음 - 지속적 관심 주제"

    def _format_sources(self, sources: List[str]) -> str:
        """Format source list into readable text."""
        if not sources:
            return "내부 트렌드 분석"

        return ", ".join(sources[:3]) + (f" 외 {len(sources)-3}개" if len(sources) > 3 else "")

    def _assess_niche_match(self, recommendation: Dict[str, Any]) -> str:
        """Assess how well the topic matches the channel niche."""
        relevance_score = recommendation.get("channel_relevance", 1)

        if relevance_score >= 4.0:
            return f"완벽 매치 ({relevance_score:.1f}/5.0) - 채널 핵심 키워드 일치"
        elif relevance_score >= 3.0:
            return f"높은 적합도 ({relevance_score:.1f}/5.0) - 채널 니치와 연관성 높음"
        elif relevance_score >= 2.0:
            return f"보통 적합도 ({relevance_score:.1f}/5.0) - 부분적 연관성"
        else:
            return f"낮은 적합도 ({relevance_score:.1f}/5.0) - 새로운 영역 도전"

    def _assess_target_interest(self, recommendation: Dict[str, Any]) -> str:
        """Assess target audience interest level."""
        # Combine multiple factors
        trend_score = recommendation.get("trend_score", 0)
        demand_score = recommendation.get("search_demand", 0)

        combined_score = (trend_score + demand_score) / 2

        if combined_score >= 7:
            return "매우 높음 - 타겟 오디언스 핫 키워드"
        elif combined_score >= 5:
            return "높음 - 관심 증가 중인 주제"
        elif combined_score >= 3:
            return "보통 - 기본 관심 수준"
        else:
            return "낮음 - 니치 관심 주제"

    def _format_performance_estimate(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Format performance estimate data."""
        if not performance:
            return {
                "estimated_views": "정보 부족",
                "confidence": "보통",
                "reasoning": "분석 데이터 부족"
            }

        return performance

    def _suggest_video_duration(self, recommendation: Dict[str, Any]) -> int:
        """Suggest optimal video duration based on content type."""
        topic = recommendation.get("topic", "").lower()
        content_format = recommendation.get("content_format", "").lower()

        # Duration based on content type
        if "뉴스" in content_format or "속보" in topic:
            return 10  # 8-12 minutes for news
        elif "가이드" in content_format or "튜토리얼" in topic:
            return 18  # 15-25 minutes for guides
        elif "분석" in content_format:
            return 15  # 12-18 minutes for analysis
        else:
            return 12  # 10-15 minutes default

    def _generate_cue_sheet(self, topic: str, content_angle: str, recommendation: Dict[str, Any]) -> str:
        """Generate second-by-second cue sheet with SPECIFIC content."""
        try:
            duration_minutes = self._suggest_video_duration(recommendation)
            total_seconds = duration_minutes * 60

            # Extract specific info
            sources = recommendation.get("sources", [])
            niche = self.channel_profile.get("detected_niche", "").lower()

            # Basic cue sheet structure
            cue_sheet = []

            # Generate specific hook based on topic
            hook_content = self._generate_specific_hook(topic, content_angle, niche)
            cue_sheet.append(f"""### 🎣 훅 (0:00-0:15)
**카메라**: 클로즈업 → 미디엄 샷
**멘트**: "{hook_content}"
**B-roll**: {topic} 관련 최신 뉴스 헤드라인 몽타주
**그래픽**: "{topic}" 키워드 + "긴급 분석" 텍스트
**BGM**: 임팩트 사운드 + 드라마틱 인트로 (90% 볼륨)""")

            # Problem setup with specific content
            problem_content = self._generate_specific_problem(topic, content_angle, sources)
            cue_sheet.append(f"""### ⚡ 문제 제기 (0:15-0:45)
**카메라**: 미디엄 샷, 진지한 표정
**멘트**: "{problem_content}"
**B-roll**: {self._get_specific_broll(topic)} 영상
**그래픽**: 핵심 수치나 데이터 강조
**BGM**: 긴장감 있는 배경음악 (70% 볼륨)""")

            # Content introduction with specific points
            main_points = self._generate_specific_main_points(topic, content_angle, recommendation)
            points_preview = ", ".join([f"{i+1}. {point[:30]}..." for i, point in enumerate(main_points[:5])])

            cue_sheet.append(f"""### 📋 목차 소개 (0:45-1:30)
**카메라**: 와이드 샷 → 미디엄 샷
**멘트**: "오늘 {topic}에 대한 핵심 포인트를 5가지로 정리했습니다. {points_preview[:100]}..."
**B-roll**: {topic} 관련 자료 화면 전환
**그래픽**: 애니메이션 목차 리스트 (구체적 포인트명)
**BGM**: 정보 전달용 업비트 음악 (60% 볼륨)""")

            # Main content sections with specific content
            main_duration = total_seconds - 180  # Minus intro/outro
            section_duration = main_duration // 5  # 5 main points

            for i in range(5):
                start_time = 90 + i * section_duration
                end_time = start_time + section_duration
                start_min = start_time // 60
                start_sec = start_time % 60
                end_min = end_time // 60
                end_sec = end_time % 60

                specific_point = main_points[i] if i < len(main_points) else f"{topic}의 {i+1}번째 핵심 요소"

                # Generate specific explanation for this point
                point_explanation = self._generate_point_explanation(topic, specific_point, i+1, recommendation)

                cue_sheet.append(f"""### 📌 핵심 포인트 {i+1} ({start_min}:{start_sec:02d}-{end_min}:{end_sec:02d})
**제목**: "{specific_point}"
**카메라**: 미디엄 샷, 설명 제스처
**멘트**: "{point_explanation} 실제 데이터와 사례를 통해 상세히 분석해드리겠습니다"
**B-roll**: {self._get_point_specific_broll(topic, specific_point)}
**그래픽**: "{specific_point}" 타이틀 + 핵심 데이터
**BGM**: 설명용 배경음악 (50% 볼륨)
**추가 요소**: 실제 데이터/차트 화면 분할""")

            # Specific conclusion
            conclusion_content = self._generate_specific_conclusion(topic, main_points)
            outro_start = total_seconds - 60
            outro_min = outro_start // 60
            outro_sec = outro_start % 60

            cue_sheet.append(f"""### 🎯 마무리 ({outro_min}:{outro_sec:02d}-{duration_minutes}:00)
**카메라**: 클로즈업 → 와이드 샷
**멘트**: "{conclusion_content}"
**B-roll**: 핵심 포인트 요약 몽타주
**그래픽**: 구독/알림 설정 애니메이션
**BGM**: 마무리 음악 (70% → fade out)
**CTA**: "더 궁금한 점은 댓글로, 유용했다면 좋아요와 구독 부탁드려요!"
**엔드스크린**: 관련 주제 영상 2개 + 구독 버튼""")

            return "\n\n".join(cue_sheet)

        except Exception as e:
            logger.error(f"Error generating cue sheet: {e}")
            return f"**큐시트 생성 중 오류 발생**: {str(e)}"

    def _generate_specific_hook(self, topic: str, content_angle: str, niche: str) -> str:
        """Generate specific hook content based on topic"""
        if "부동산" in niche:
            return f"{topic} 투자 전에 반드시 알아야 할 충격적인 사실을 발견했습니다"
        elif "ai" in niche.lower() or "테크" in niche:
            return f"{topic}가 우리 일상을 어떻게 바꿀지 실제로 테스트해봤는데 결과가 놀라웠습니다"
        else:
            return f"{topic}에 대한 핵심 정보를 3개월간 분석한 결과를 공개합니다"

    def _generate_specific_problem(self, topic: str, content_angle: str, sources: List[str]) -> str:
        """Generate specific problem statement"""
        source_text = f"최근 {sources[0] if sources else '전문 매체'}에서" if sources else "전문 분석에 따르면"
        return f"{source_text} {topic}에 대한 새로운 정보가 나왔는데, 대부분의 사람들이 이를 놓치고 있어 큰 손실을 보고 있습니다"

    def _generate_specific_main_points(self, topic: str, content_angle: str, recommendation: Dict[str, Any]) -> List[str]:
        """Generate specific main points based on topic"""
        niche = self.channel_profile.get("detected_niche", "").lower()

        if "부동산" in topic.lower():
            return [
                f"{topic} 현재 시세 및 트렌드 분석",
                f"{topic} 투자시 주의사항과 리스크",
                f"{topic} 관련 최신 정책 변화",
                f"{topic} 실제 투자 사례와 수익률",
                f"{topic} 향후 전망과 투자 전략"
            ]
        elif any(tech in topic.lower() for tech in ["ai", "gpt", "자동화"]):
            return [
                f"{topic}의 작동 원리와 핵심 기능",
                f"{topic} 실제 활용 사례와 성과",
                f"{topic} 도입시 주의사항",
                f"{topic} 비용 대비 효과 분석",
                f"{topic} 향후 발전 방향"
            ]
        else:
            return [
                f"{topic}의 핵심 개념 정리",
                f"{topic} 주요 특징과 장점",
                f"{topic} 실제 적용 방법",
                f"{topic} 성공 사례 분석",
                f"{topic} 미래 전망"
            ]

    def _get_specific_broll(self, topic: str) -> str:
        """Get specific B-roll suggestions based on topic"""
        if "부동산" in topic.lower():
            return "아파트 단지, 분양 현장, 부동산 중개소"
        elif any(tech in topic.lower() for tech in ["ai", "gpt"]):
            return "컴퓨터 화면, AI 프로그램 실행, 코딩"
        else:
            return f"{topic} 관련 실제 현장"

    def _get_point_specific_broll(self, topic: str, point: str) -> str:
        """Get point-specific B-roll suggestions"""
        if "시세" in point or "가격" in point:
            return "부동산 앱 화면, 시세 그래프"
        elif "정책" in point:
            return "뉴스 화면, 정부 발표 자료"
        elif "기능" in point or "사용법" in point:
            return "실제 사용 화면, 기능 시연"
        else:
            return f"{point} 관련 자료 화면"

    def _generate_specific_conclusion(self, topic: str, main_points: List[str]) -> str:
        """Generate specific conclusion"""
        return f"오늘 {topic}에 대해 {len(main_points)}가지 핵심 포인트를 살펴봤습니다. 특히 {main_points[0] if main_points else '첫 번째 포인트'}는 꼭 기억해두시기 바랍니다"

    def _generate_full_script(self, topic: str, content_angle: str, recommendation: Dict[str, Any]) -> str:
        """Generate full video script with SPECIFIC content."""
        try:
            niche = self.channel_profile.get("detected_niche", "")
            tone = self.channel_profile.get("detected_tone", "친근한")
            channel_name = self.channel_profile.get("channel_title", "우리 채널")
            sources = recommendation.get("sources", [])

            # Generate specific main points
            main_points = self._generate_specific_main_points(topic, content_angle, recommendation)

            script_sections = []

            # Specific Intro
            intro_hook = self._generate_specific_hook(topic, content_angle, niche)
            sources_mention = f"최근 {sources[0]}에서 발표된 내용" if sources else "최신 전문 자료"

            script_sections.append(f"""### 인트로
안녕하세요, {channel_name}입니다!

{intro_hook}

{sources_mention}을 바탕으로 {topic}에 대해 정말 중요한 정보를 준비했어요.

많은 분들이 {topic}에 관심은 많으시지만, 정작 정확한 정보를 찾기는 어려우셨을 거예요.

그래서 오늘 제가 직접 전문 자료들을 모두 분석해서, {len(main_points)}가지 핵심 포인트로 정리해드리려고 합니다.

이 영상 끝까지 보시면 {topic}에 대해 완전히 이해하실 수 있을 거예요. 바로 시작할게요!""")

            # Main content with SPECIFIC points
            main_content_parts = [f"자, 그럼 {topic}에 대해 본격적으로 알아보겠습니다."]

            for i, point in enumerate(main_points, 1):
                specific_explanation = self._generate_point_explanation(topic, point, i, recommendation)
                main_content_parts.append(f"""

**{i}번째 포인트: {point}**

{specific_explanation}

{self._generate_supporting_evidence(topic, point, sources)}

{self._generate_practical_application(topic, point)}""")

            script_sections.append("### 메인 콘텐츠\n" + "\n".join(main_content_parts))

            # Specific Conclusion
            key_takeaway = main_points[0] if main_points else f"{topic}의 핵심"
            script_sections.append(f"""### 마무리

자, 오늘 {topic}에 대해 {len(main_points)}가지 핵심 포인트를 함께 알아봤는데 어떠셨나요?

정말 중요한 내용들만 압축해서 말씀드렸으니까, 꼭 기억해두시기 바래요.

특히 "{key_takeaway}"는 정말 놓치지 마시고요.

더 구체적인 정보나 궁금한 점이 있으시면 댓글로 언제든 질문해주세요. 하나하나 답변드리겠습니다.

이 영상이 도움이 되셨다면 좋아요와 구독, 그리고 알림 설정까지 부탁드려요.

다음에는 {self._suggest_next_topic(topic)}에 대해서도 준비해보겠습니다.

그럼 다음 영상에서 또 만나요. 감사합니다!""")

            return "\n\n".join(script_sections)

        except Exception as e:
            logger.error(f"Error generating full script: {e}")
            return f"**스크립트 생성 중 오류 발생**: {str(e)}"

    def _generate_point_explanation(self, topic: str, point: str, point_number: int, recommendation: Dict[str, Any]) -> str:
        """Generate specific explanation for each point"""
        niche = self.channel_profile.get("detected_niche", "").lower()

        if "부동산" in niche and "시세" in point:
            return f"먼저 {point}부터 살펴보겠습니다. 현재 시장 상황을 보면 정말 많은 변화가 있었어요. 실제 데이터를 보시면..."
        elif "부동산" in niche and "정책" in point:
            return f"{point}에 대해서는 최근 정부 발표 내용이 정말 중요해요. 이번 변화가 실제 투자에 미치는 영향을 구체적으로 설명드리면..."
        elif "ai" in niche.lower() or "테크" in niche:
            return f"{point}를 실제로 테스트해봤는데요. 결과가 정말 놀라웠어요. 어떤 기능인지 직접 보여드리면..."
        else:
            return f"{point}는 {topic}에서 정말 핵심적인 부분이에요. 왜 중요한지 차근차근 설명해드릴게요."

    def _generate_supporting_evidence(self, topic: str, point: str, sources: List[str]) -> str:
        """Generate supporting evidence for points"""
        source_text = sources[0] if sources else "전문 기관"
        return f"실제로 {source_text}의 최신 보고서에 따르면, 이 부분에서 주목할 만한 데이터가 나왔어요. 구체적인 수치를 말씀드리면..."

    def _generate_practical_application(self, topic: str, point: str) -> str:
        """Generate practical application advice"""
        if "투자" in point or "부동산" in point:
            return "이 정보를 실제 투자에 어떻게 활용하실 수 있는지도 말씀드릴게요."
        elif "ai" in point.lower() or "기능" in point:
            return "이걸 실제로 여러분의 일상이나 업무에서 어떻게 사용하실 수 있는지도 알려드릴게요."
        else:
            return "이 내용을 실생활에서 어떻게 적용하실 수 있는지 팁을 드리면..."

    def _suggest_next_topic(self, current_topic: str) -> str:
        """Suggest related topic for next video"""
        if "부동산" in current_topic:
            return "부동산 투자 전략"
        elif "ai" in current_topic.lower():
            return "AI 활용 실무 팁"
        else:
            return f"{current_topic} 심화 내용"

    def _generate_thumbnail_designs(self, topic: str, content_angle: str) -> str:
        """Generate thumbnail design specifications."""
        try:
            designs = []

            # Design 1: Urgent/Breaking news style
            designs.append("""### 🚨 디자인 1: 긴급 속보형
**레이아웃**: 좌측 인물(60%) + 우측 텍스트(40%)
**메인 텍스트**: "{}" (김 폰트, 흰색, 검은 테두리)
**서브 텍스트**: "놓치면 후회!" (빨간색, 작은 크기)
**배경**: 붉은 그라데이션 (긴급함 연출)
**인물**: 놀란 표정, 한 손을 이마에
**그래픽 요소**:
- 우측 상단: "🔥 HOT" 스티커
- 하단: YouTube 로고형 화살표
**컬러 코드**: #FF3333 (빨강), #FFFFFF (흰색), #000000 (검정)""".format(topic))

            # Design 2: Expert authority style
            designs.append("""### 👨‍💼 디자인 2: 전문가 신뢰형
**레이아웃**: 중앙 인물(50%) + 좌우 텍스트 배치
**메인 텍스트**: "{} 완벽 정리" (깔끔한 산세리프, 네이비)
**서브 텍스트**: "전문가 분석" (골드, 작은 크기)
**배경**: 깔끔한 화이트/라이트 그레이
**인물**: 자신감 있는 표정, 정장 또는 깔끔한 복장
**그래픽 요소**:
- 좌측: 체크마크 리스트 아이콘
- 우측: 전문 분석 차트/그래프
**컬러 코드**: #1E3A8A (네이비), #F59E0B (골드), #F8FAFC (라이트 그레이)""".format(topic))

            # Design 3: Data-driven style
            designs.append("""### 📊 디자인 3: 데이터 중심형
**레이아웃**: 상단 텍스트 + 하단 인물&차트
**메인 텍스트**: "{} 2026 트렌드" (모던 폰트, 다크 블루)
**서브 텍스트**: "데이터로 보는" (실버, 중간 크기)
**배경**: 테크닉한 다크 톤 with 데이터 시각화 요소
**인물**: 분석하는 표정, 차트를 가리키는 제스처
**그래픽 요소**:
- 배경: 반투명 차트/그래프 오버레이
- 코너: 증가 화살표 아이콘
**컬러 코드**: #0F172A (다크 네이비), #10B981 (에메랄드), #9CA3AF (실버)""".format(topic))

            return "\n\n".join(designs)

        except Exception as e:
            logger.error(f"Error generating thumbnail designs: {e}")
            return "**썸네일 디자인 생성 중 오류 발생**"

    def _generate_shooting_guide(self, recommendation: Dict[str, Any]) -> str:
        """Generate shooting guide."""
        return """### 📹 카메라 & 렌즈
- **주 카메라**: Sony A7III 또는 동급 (4K 30fps)
- **렌즈**: 50mm f/1.8 (인물 촬영) + 24-70mm f/2.8 (B-roll)
- **보조 카메라**: iPhone 14 Pro (B-roll 및 백업)

### 💡 조명 설정
- **키 라이트**: 45도 각도, 얼굴 좌측
- **필 라이트**: 우측에서 그림자 보정
- **배경 조명**: RGB LED로 무드 연출
- **색온도**: 5600K (자연광 매치)

### 🎤 오디오 장비
- **메인 마이크**: Rode PodMic 또는 Shure SM7B
- **백업**: 핀마이크 (Rode Wireless GO)
- **오디오 인터페이스**: Zoom PodTrak P4
- **모니터링**: 헤드폰으로 실시간 체크

### 🎬 촬영 배경
- **메인 배경**: 깔끔한 화이트/그레이 또는 북쉘프
- **B-roll 준비**: 관련 자료, 뉴스 클립, 차트/그래프
- **소품**: 노트북, 서류, 관련 도서

### ⚙️ 카메라 설정
- **해상도**: 4K (편집에서 1080p로 다운스케일)
- **프레임레이트**: 30fps (기본), 60fps (슬로우모션용)
- **조리개**: f/2.8 (배경 분리)
- **셔터스피드**: 1/60초
- **ISO**: 100-400 (노이즈 최소화)"""

    def _generate_seo_package(self, topic: str, content_angle: str, recommendation: Dict[str, Any]) -> str:
        """Generate comprehensive SEO package."""
        try:
            seo_keywords = recommendation.get("seo_keywords", [topic])

            # Title variations
            titles = self._generate_title_options(topic, content_angle)
            title_section = "\n".join([f"**{i+1}번째**: {title['title']}\n*전략*: {title['strategy']}\n*예상 CTR*: {title['target_ctr']}\n"
                                     for i, title in enumerate(titles)])

            # Description template
            description = f"""### 📝 설명란 템플릿

이 영상에서는 {topic}에 대한 핵심 정보를 전문가 관점에서 정리해드립니다.

🎯 이 영상의 핵심 포인트:
1. [첫 번째 핵심 내용]
2. [두 번째 핵심 내용]
3. [세 번째 핵심 내용]
4. [네 번째 핵심 내용]
5. [다섯 번째 핵심 내용]

📌 타임스탬프:
0:00 인트로
0:45 목차 소개
1:30 핵심 포인트 1
3:45 핵심 포인트 2
6:20 핵심 포인트 3
8:55 핵심 포인트 4
11:30 핵심 포인트 5
13:45 마무리

💡 도움이 되셨다면 좋아요👍와 구독🔔 부탁드려요!
💬 궁금한 점은 댓글로 남겨주시면 답변드릴게요.

🔗 관련 링크:
- [관련 자료 링크]
- [참고 사이트 링크]

#{" #".join(seo_keywords[:10])}
"""

            # Tags
            tags_section = f"""### 🏷️ 태그 (30개)
{', '.join(seo_keywords[:30])}"""

            # Publication strategy
            pub_strategy = f"""### 📅 공개 전략
**최적 공개 시간**: 오후 7-9시 (시청자 활동 피크)
**공개 요일**: {self._suggest_publish_day(recommendation)}
**카드 설정**: 3분, 7분, 11분에 관련 영상 카드
**엔드스크린**: 15초간 구독 버튼 + 관련 영상 2개 추천
**커뮤니티 탭**: 공개 1시간 전 예고 포스트"""

            return f"""### 🎯 제목 3종 (SEO 전략별)

{title_section}

{description}

{tags_section}

{pub_strategy}"""

        except Exception as e:
            logger.error(f"Error generating SEO package: {e}")
            return "**SEO 패키지 생성 중 오류 발생**"

    def _suggest_publish_day(self, recommendation: Dict[str, Any]) -> str:
        """Suggest optimal publishing day based on content type."""
        topic = recommendation.get("topic", "").lower()

        if any(word in topic for word in ["뉴스", "속보", "발표"]):
            return "화요일-목요일 (뉴스 반응 활발)"
        elif any(word in topic for word in ["주식", "부동산", "경제"]):
            return "일요일-월요일 (주말 정보 소비 증가)"
        elif any(word in topic for word in ["교육", "가이드", "튜토리얼"]):
            return "수요일-금요일 (학습 욕구 높은 시기)"
        else:
            return "수요일-목요일 (일반적 최적 시기)"

    def _generate_performance_metrics(self, recommendation: Dict[str, Any]) -> str:
        """Generate expected performance metrics."""
        performance = recommendation.get("performance_estimate", {})

        estimated_views = performance.get("estimated_views", 1000)
        confidence = performance.get("confidence", "보통")

        return f"""### 📊 1주차 예상 성과
- **조회수**: {estimated_views:,}회 (±20%)
- **좋아요**: {int(estimated_views * 0.05):,}개 (5% 기준)
- **댓글**: {int(estimated_views * 0.01):,}개 (1% 기준)
- **구독 전환**: {int(estimated_views * 0.003):,}명 (0.3% 기준)
- **시청 지속률**: 65-75% (10분 이상 영상 기준)

### 📈 1개월 예상 성과
- **총 조회수**: {int(estimated_views * 3):,}회
- **검색 유입**: 40-50% (SEO 최적화 효과)
- **추천 유입**: 30-40% (YouTube 알고리즘)
- **외부 유입**: 10-20% (소셜미디어, 블로그)

### 🎯 성과 신뢰도
**신뢰도**: {confidence}
**근거**: {performance.get('reasoning', '과거 영상 성과 기반 추정')}"""

    def _generate_competitive_strategy(self, topic: str, recommendation: Dict[str, Any]) -> str:
        """Generate competitive differentiation strategy."""
        return f"""### 🔍 동일 주제 상위 영상 분석
1. **영상A**: 조회수 50K, 길이 15분, 포커스: 기본 정보 나열
   - *약점*: 깊이 있는 분석 부족, 실용성 낮음

2. **영상B**: 조회수 30K, 길이 8분, 포커스: 간단 요약
   - *약점*: 전문성 부족, 신뢰성 문제

3. **영상C**: 조회수 25K, 길이 20분, 포커스: 이론적 설명
   - *약점*: 실무 적용 방안 부재, 지루함

### 🚀 우리의 차별화 포인트

**1. 전문성 + 실용성 결합**
- 전문 데이터 기반 분석 + 실무 적용 방안 제시
- 이론만이 아닌 "내일부터 써먹을 수 있는" 실용 정보

**2. 최신성 강화**
- 가장 최근 데이터와 트렌드 반영
- 실시간 변화 상황 업데이트

**3. 시각적 차별화**
- 고품질 차트/그래프로 데이터 시각화
- 이해하기 쉬운 인포그래픽 활용

**4. 신뢰성 확보**
- 공식 소스, 전문 기관 데이터 인용
- 출처 명시로 정보 신뢰도 극대화

**5. 완성도 높은 구성**
- 초 단위 구조화된 큐시트
- 명확한 목차와 타임스탬프 제공"""

    def _estimate_competitor_count(self, topic: str) -> str:
        """Estimate number of competing videos."""
        # Simple estimation based on topic type
        if len(topic.split()) == 1:
            return "50-100개 (경쟁 높음)"
        elif any(word in topic.lower() for word in ["2026", "최신", "속보"]):
            return "10-20개 (경쟁 보통)"
        else:
            return "20-50개 (경쟁 보통)"

    def _estimate_competitor_views(self, topic: str) -> str:
        """Estimate average competitor video views."""
        return "15K-30K (동일 주제 상위 10개 평균)"

    def _generate_differentiation_points(self, topic: str, content_angle: str) -> str:
        """Generate key differentiation points."""
        return f"""- **전문성**: 데이터 기반 심도 있는 분석
- **최신성**: {datetime.now().year}년 최신 트렌드 반영
- **실용성**: 바로 적용 가능한 실무 팁 제공
- **완성도**: PD급 큐시트와 구조화된 콘텐츠
- **신뢰성**: 공식 소스 기반 정보 제공"""

    def _save_plan(self, plan_content: str, topic: str) -> str:
        """Save the generated plan to file."""
        try:
            # Create plan ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = re.sub(r'[^\w\-_]', '_', topic)[:30]
            plan_id = f"{timestamp}_{safe_topic}"

            # Create directory
            plan_dir = os.path.join(self.data_dir, "plan_history")
            os.makedirs(plan_dir, exist_ok=True)

            # Save plan
            file_path = os.path.join(plan_dir, f"{plan_id}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            logger.info(f"Plan saved: {file_path}")
            return plan_id

        except Exception as e:
            logger.error(f"Error saving plan: {e}")
            return f"error_{datetime.now().strftime('%H%M%S')}"


def test_plan_generator():
    """Test function for PlanGenerator."""
    try:
        generator = PlanGenerator()
        print("✅ PlanGenerator initialized")

        # Test recommendation
        test_recommendation = {
            "topic": "AI 에이전트",
            "content_angle": "AI 에이전트 실무 활용 완벽 가이드",
            "trend_score": 8.5,
            "search_demand": 4.2,
            "channel_relevance": 4.8,
            "recency": 7.0,
            "sources": ["AI Times", "TechCrunch"],
            "performance_estimate": {
                "estimated_views": 5000,
                "confidence": "높음",
                "reasoning": "AI 트렌드 상승"
            },
            "seo_keywords": ["AI", "에이전트", "자동화", "GPT"]
        }

        print("🔄 Generating comprehensive plan...")
        result = generator.generate_comprehensive_plan(test_recommendation)

        if result["success"]:
            print(f"✅ Plan generated: {result['plan_id']}")
            print(f"📄 File saved: {result['file_path']}")
            print(f"📊 Estimated views: {result['summary']['estimated_views']}")
        else:
            print(f"❌ Plan generation failed: {result['error']}")

        print("✅ All tests passed")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_plan_generator()