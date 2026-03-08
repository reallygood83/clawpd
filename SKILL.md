# YouTube PD Agent

AI 기반 유튜브 콘텐츠 기획 전문 에이전트

## 📝 설명

YouTube PD Agent는 전문 PD 수준의 유튜브 콘텐츠 기획안을 자동 생성하는 AI 에이전트입니다. 실시간 트렌드 분석, 채널별 맞춤 기획, 경쟁사 SWOT 분석을 통해 데이터 기반의 콘텐츠 전략을 제공합니다.

## 🎯 주요 기능

### 1. 🎬 PD급 콘텐츠 기획
- **실시간 트렌드 분석**: RSS/웹 크롤링을 통한 최신 이슈 수집
- **초 단위 큐시트**: 전문 PD 수준의 세밀한 영상 구성안
- **완전한 대본**: 채널 톤에 맞는 풀스크립트 생성
- **썸네일 시안**: 3종 디자인 가이드 (레이아웃, 컬러, 텍스트)
- **SEO 패키지**: 제목 3안, 설명란, 태그 30개, 공개 전략

### 2. 📊 경쟁 채널 SWOT 분석
- **정량적 비교**: YouTube API 기반 채널 성과 분석
- **정성적 분석**: 콘텐츠 전략, 포지셔닝 차이점 도출
- **실행 가능한 전략**: 즉시/중기/장기 단계별 액션플랜
- **차별화 포인트**: 경쟁사 약점 기반 공략 전략

### 3. 🔧 스마트 소스 관리
- **다채널 수집**: RSS, 웹사이트, 네이버 카페/블로그
- **자동 필터링**: 채널 니치에 맞는 콘텐츠만 선별
- **트렌드 매칭**: 소스 데이터와 YouTube 검색 수요 교차 분석

## 🚀 트리거 (사용법)

### 기본 명령어
- **`/온보딩`** - 채널 설정 및 초기 분석 (최초 1회)
- **`/기획`** - 이번 주 추천 콘텐츠 기획안 생성
- **`/swot [경쟁채널URL]`** - 경쟁 채널 SWOT 분석
- **`/소스관리`** - 정보 소스 추가/삭제/테스트

### 고급 명령어
- **`/기획 [주제]`** - 특정 주제로 기획안 생성
- **`/분석 [채널URL]`** - 특정 채널 성과 분석
- **`/트렌드 [키워드]`** - 키워드 트렌드 분석
- **`/히스토리`** - 과거 기획안 목록 조회

## ⚙️ 설치 및 설정

### 필수 요구사항
```bash
# Python 버전
Python 3.10 이상

# API 키 설정 (환경변수)
export YOUTUBE_API_KEY="your_youtube_api_key"
```

### 설치 방법
```bash
# 1. ClawHub에서 설치 (권장)
clawhub install youtube-pd-agent

# 2. GitHub에서 직접 설치
git clone https://github.com/reallygood83/youtube-pd-agent
cd youtube-pd-agent
pip install -r requirements.txt
```

### 초기 설정
```bash
# 1. 온보딩 실행
/온보딩

# 2. YouTube API 키 설정 확인
# Google Cloud Console에서 YouTube Data API v3 활성화 필요
# https://console.cloud.google.com/apis/library/youtube.googleapis.com
```

## 🔑 API 키 및 선택 강화

### 필수 (무료)
- **YouTube Data API v3**: 채널/영상 분석 (무료 10,000 units/일)
  - 발급: [Google Cloud Console](https://console.cloud.google.com/)

### 선택 강화 (더 나은 성능)
- **XAI_API_KEY**: Grok/X 검색으로 실시간 바이럴 트렌드 수집
- **NAVER_CLIENT_ID + NAVER_CLIENT_SECRET**: 네이버 검색 API로 정밀 카페/뉴스 검색
- **CEREBRAS_API_KEY**: 무료 전처리/요약으로 성능 향상

```bash
# 선택 API 키 설정
export XAI_API_KEY="your_xai_key"
export NAVER_CLIENT_ID="your_naver_client_id"
export NAVER_CLIENT_SECRET="your_naver_client_secret"
export CEREBRAS_API_KEY="your_cerebras_key"
```

## 📂 프로젝트 구조

```
youtube-pd-agent/
├── SKILL.md                    # OpenClaw 스킬 정의
├── scripts/
│   ├── onboard.py              # 온보딩 (채널 분석 + 소스 등록)
│   ├── channel_analyzer.py     # 채널 DNA 분석
│   ├── source_collector.py     # 정보 소스 크롤링 엔진
│   ├── trend_matcher.py        # 트렌드 매칭 (소스 ↔ 키워드)
│   ├── plan_generator.py       # PD급 기획안 생성
│   ├── swot_analyzer.py        # SWOT 분석 엔진
│   └── utils/
│       ├── youtube_api.py      # YouTube Data API v3 래퍼
│       ├── rss_fetcher.py      # RSS/Atom 수집
│       ├── web_scraper.py      # 웹 크롤링
│       ├── naver_fetcher.py    # 네이버 검색/카페 수집
│       └── keyword_suggest.py  # YouTube 자동완성 키워드
├── templates/
│   ├── pd_plan.md              # PD급 기획안 마크다운 템플릿
│   ├── swot_report.md          # SWOT 분석 리포트 템플릿
│   └── onboard_questions.json  # 온보딩 질문 세트
├── presets/
│   ├── real_estate.json        # 부동산 니치 프리셋
│   ├── tech_ai.json           # 테크/AI 니치 프리셋
│   ├── education.json         # 교육 니치 프리셋
│   └── custom.json            # 사용자 정의 프리셋
└── data/
    ├── channel_profile.json    # 채널 프로필 (온보딩 결과)
    ├── sources.json           # 등록된 정보 소스
    ├── plan_history/          # 기획안 이력
    └── swot_reports/          # SWOT 분석 리포트
```

## 🎯 니치별 특화 기능

### 🏠 부동산 채널
- **전문 소스**: 매경, 한경, 국토부, 부동산114, 청약홈
- **키워드**: 재개발, 분양, 전세, 금리, GTX, 투자 등
- **특화 기획**: 정책 해설, 지역 분석, 시세 전망

### 🤖 테크/AI 채널
- **전문 소스**: Hacker News, TechCrunch, GitHub, OpenAI Blog
- **키워드**: AI, GPT, 자동화, 프로그래밍, 생산성
- **특화 기획**: 실습 튜토리얼, 도구 리뷰, 트렌드 분석

### 📚 교육 채널
- **전문 소스**: 교육부, 에듀테크, Coursera, 학습법 커뮤니티
- **키워드**: 학습법, 공부법, 자기계발, 효율성, 습관
- **특화 기획**: 단계별 가이드, 사례 연구, 동기부여

## 📊 성과 예측

### 기획안 성과 지표
- **조회수 예측**: 과거 데이터 + 트렌드 스코어 기반
- **참여율 예측**: 키워드 검색 수요 + 채널 적합도
- **신뢰도**: 높음/보통/낮음 + 근거 제시

### SWOT 분석 지표
- **정량 비교**: 구독자, 조회수, 참여율, 업로드 빈도
- **정성 분석**: 콘텐츠 전략, 포지셔닝, 차별화 요소
- **전략 제안**: 데이터 기반 3단계 실행 계획

## 🔄 자동화 및 스케줄링

### 주간 자동 기획
```bash
# 매주 월요일 오전 9시 자동 실행 (cron)
0 9 * * 1 cd /path/to/youtube-pd-agent && python -m scripts.plan_generator --auto

# 또는 OpenClaw 스케줄러 사용
/스케줄 add "매주 월요일 09:00" "/기획"
```

### 실시간 트렌드 모니터링
```bash
# 매 6시간마다 소스 수집 및 트렌드 업데이트
0 */6 * * * cd /path/to/youtube-pd-agent && python -m scripts.source_collector --collect
```

## 🛠️ 커스터마이징

### 새로운 소스 추가
```python
# 커스텀 소스 크롤러 추가
from scripts.source_collector import SourceCollector

collector = SourceCollector()
collector.add_source(
    name="나만의 소스",
    url="https://example.com/feed",
    source_type="rss",
    keywords=["키워드1", "키워드2"]
)
```

### 템플릿 수정
```markdown
# templates/pd_plan.md 파일 수정으로 기획안 형식 변경
# templates/swot_report.md 파일 수정으로 SWOT 리포트 형식 변경
```

## 📈 성능 최적화

### 비용 효율성
- **무료 운영**: YouTube API 무료 할당량만으로도 기본 기능 완전 동작
- **선택 강화**: API 키 추가 시에만 고급 기능 활성화
- **로컬 처리**: 모든 분석이 로컬에서 실행되어 외부 의존성 최소

### 속도 최적화
- **병렬 처리**: 멀티스레딩으로 여러 소스 동시 수집
- **캐싱**: 분석 결과 캐시로 중복 API 호출 방지
- **점진적 로딩**: 필요한 데이터만 단계별 로딩

## 🤝 기여 및 확장

### 새로운 니치 추가
```json
# presets/new_niche.json 파일 생성
{
  "niche": "새로운_니치",
  "default_sources": [...],
  "keywords_seed": [...],
  "content_characteristics": {...}
}
```

### 분석 엔진 확장
```python
# custom_analyzer.py 추가로 새로운 분석 기능 구현
class CustomAnalyzer:
    def analyze(self, data):
        # 커스텀 분석 로직
        return results
```

## 🐛 문제 해결

### 자주 발생하는 오류
1. **YouTube API 할당량 초과**: 내일까지 대기 또는 API 키 추가
2. **채널 URL 인식 실패**: @username 또는 /channel/ 형식 사용
3. **소스 수집 실패**: 네트워크 연결 및 URL 유효성 확인

### 로그 확인
```bash
# 상세 로그 활성화
export PYTHONPATH=.
python -m scripts.plan_generator --verbose
```

## 📞 지원

- **GitHub Issues**: [문제 신고](https://github.com/reallygood83/youtube-pd-agent/issues)
- **Discussion**: [기능 제안 및 질문](https://github.com/reallygood83/youtube-pd-agent/discussions)
- **Wiki**: [상세 가이드](https://github.com/reallygood83/youtube-pd-agent/wiki)

## 📜 라이센스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 🎉 크레딧

- **개발자**: [배움의달인](https://youtube.com/@배움의달인)
- **OpenClaw 스킬**: AI 에이전트 생태계 기여
- **커뮤니티**: 사용자 피드백과 기여로 지속 발전

---

*YouTube PD Agent v1.0 - AI가 만드는 전문 PD급 콘텐츠 기획*