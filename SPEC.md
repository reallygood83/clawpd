---
title: YouTube PD Agent — OpenClaw 스킬 개발 스펙
date: 2026-03-08
type: spec
status: draft
tags:
  - openclaw
  - skill
  - youtube
  - agent
  - PD
  - SWOT
  - 기획
share_link: https://share.note.sx/a52xf1sg
share_updated: 2026-03-08T22:43:06+09:00
---

# 🎬 YouTube PD Agent — OpenClaw 스킬 개발 스펙

> 누구든 GitHub에서 설치하면 바로 사용 가능한 유튜브 전문 기획 에이전트

---

## 📌 프로젝트 개요

### 비전
"유튜브 기획 PD를 AI로 대체한다"
- OpenClaw 스킬로 패키징 → GitHub 공개 → `clawhub install` 한 줄로 설치
- vidIQ/Grok **없이도** 핵심 기능 동작 (있으면 강화)
- 사용자의 니치·소스·경쟁채널에 맞춤화된 PD급 기획안 자동 생성

### 2가지 핵심 기능
1. **🎯 PD급 유튜브 기획 에이전트** — 채널 분석 + 소스 크롤링 + 기획안 생성
2. **📊 경쟁채널 SWOT 분석** — 내 채널 vs 경쟁 3개 채널 비교 컨설팅

### 타겟 사용자
- 부동산·주식·교육·뷰티·테크 등 **전문 분야 유튜버**
- 유튜브 컨설턴트/에이전시
- 1인 기업가 크리에이터

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────┐
│           YouTube PD Agent (OpenClaw Skill)  │
│                                             │
│  [온보딩 모듈]                               │
│  ├─ 채널 URL 입력 → YouTube Data API 분석    │
│  ├─ 니치/타겟/톤 자동 감지                    │
│  ├─ 정보 소스 등록 (RSS, 웹사이트, 카페 등)   │
│  └─ 경쟁채널 등록 (최대 5개)                  │
│                                             │
│  [데이터 수집 엔진]                           │
│  ├─ YouTube Data API v3 (무료, 채널/영상 분석)│
│  ├─ RSS/Atom 피드 수집 (blogwatcher 연동)     │
│  ├─ 웹 크롤링 (web_fetch, 매경 등 뉴스사이트) │
│  ├─ 네이버 카페/블로그 (naver-search 스킬)    │
│  ├─ [선택] vidIQ 브라우저 자동화              │
│  ├─ [선택] Grok/X 검색 (xai-search 스킬)     │
│  └─ YouTube 자동완성 (suggestqueries API)     │
│                                             │
│  [분석 엔진]                                 │
│  ├─ 채널 DNA 분석 (업로드 패턴, 성과, 키워드) │
│  ├─ 트렌드 매칭 (소스 뉴스 ↔ 키워드 교차)    │
│  ├─ 경쟁 분석 (SWOT 매트릭스)                │
│  └─ 기획 전략 수립 (니치 × 트렌드 × 경쟁력)  │
│                                             │
│  [기획안 생성 엔진]                           │
│  ├─ PD급 큐시트 (초 단위)                     │
│  ├─ 전체 대본 초안                            │
│  ├─ 썸네일 시안 (텍스트 기반)                 │
│  ├─ SEO 패키지 (제목/설명/태그)              │
│  ├─ 촬영 가이드                              │
│  └─ 경쟁 차별화 전략                          │
│                                             │
│  [출력]                                      │
│  ├─ 마크다운 기획안 (옵시디언 호환)           │
│  ├─ 텔레그램/디스코드 브리핑                  │
│  └─ [선택] Share Note 링크                    │
└─────────────────────────────────────────────┘
```

---

## 📂 스킬 폴더 구조

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
│       ├── web_scraper.py      # 웹 크롤링 (web_fetch 기반)
│       ├── naver_fetcher.py    # 네이버 검색/카페 수집
│       └── keyword_suggest.py  # YouTube 자동완성 키워드
├── templates/
│   ├── pd_plan.md              # PD급 기획안 마크다운 템플릿
│   ├── swot_report.md          # SWOT 분석 리포트 템플릿
│   ├── onboard_questions.json  # 온보딩 질문 세트
│   └── niche_presets/          # 니치별 프리셋
│       ├── real_estate.json    # 부동산
│       ├── finance.json        # 주식/재테크
│       ├── education.json      # 교육
│       ├── tech_ai.json        # 테크/AI
│       └── custom.json         # 사용자 정의
├── data/
│   ├── channel_profile.json    # 채널 프로필 (온보딩 결과)
│   ├── sources.json            # 등록된 정보 소스
│   ├── competitors.json        # 경쟁채널 목록
│   ├── keyword_cache.json      # 키워드 캐시
│   └── plan_history/           # 기획안 이력
├── README.md                   # GitHub 설치 가이드
└── requirements.txt            # Python 의존성
```

---

## 🔄 기능 1: PD급 유튜브 기획 에이전트

### 1-1. 온보딩 플로우

사용자가 스킬 설치 후 처음 실행하면:

```
[Step 1] 채널 URL 입력
> "유튜브 채널 URL을 입력해주세요"
> 예: https://www.youtube.com/@배움의달인

[Step 2] 자동 분석 (YouTube Data API)
> 채널명: 배움의 달인
> 구독자: 10,500명
> 총 영상: 87개
> 평균 조회수: 3,200
> 상위 영상 TOP 5: ...
> 업로드 빈도: 주 2~3회
> 감지된 니치: AI 교육, 옵시디언, 생산성
> 감지된 타겟: 교사, 직장인, 1인 기업가
> "맞나요? 수정할 부분이 있으면 말씀해주세요"

[Step 3] 정보 소스 등록
> "주로 콘텐츠 소재를 어디서 찾으시나요? (여러 개 가능)"
> 예시:
>   - 매일경제 부동산 섹션 (https://www.mk.co.kr/news/realestate/)
>   - 네이버 카페 부동산스터디 (https://cafe.naver.com/jaegebal)
>   - 한경 부동산 (https://www.hankyung.com/realestate)
>   - 특정 RSS 피드
>   - X/트위터 계정

[Step 4] 경쟁채널 등록 (선택)
> "경쟁하거나 참고하는 채널 URL을 입력해주세요 (최대 5개)"
> 예: https://www.youtube.com/@부동산읽어주는남자

[Step 5] 설정 완료
> channel_profile.json + sources.json + competitors.json 저장
> "설정 완료! /기획 으로 기획안 생성, /swot 으로 경쟁 분석"
```

### 1-2. 소스 크롤링 엔진

**기본 소스 (API 키 불필요):**
| 소스 | 방법 | 데이터 |
|------|------|--------|
| YouTube 자동완성 | suggestqueries API | 트렌드 키워드 |
| YouTube Data API v3 | REST API (무료 할당량) | 채널/영상 분석 |
| RSS/Atom 피드 | blogwatcher / feedparser | 뉴스 헤드라인 |
| 웹사이트 크롤링 | web_fetch (readability) | 기사 본문 |
| 네이버 검색 | naver-search 스킬 | 뉴스/카페/블로그 |

**선택 소스 (API 키 있으면 강화):**
| 소스 | 조건 | 강화 내용 |
|------|------|-----------|
| vidIQ | 브라우저 로그인 | 키워드 점수, Outliers, Rising |
| Grok/X 검색 | XAI_API_KEY | 실시간 바이럴 트렌드 |
| 네이버 API | NAVER_CLIENT_ID | 정밀 검색 |

**부동산 전문 소스 (니치 프리셋):**
| 소스 | URL | 수집 내용 |
|------|-----|-----------|
| 매일경제 부동산 | mk.co.kr/news/realestate | 부동산 뉴스 헤드라인 |
| 한경 부동산 | hankyung.com/realestate | 시장 분석 |
| 국토교통부 보도자료 | molit.go.kr | 정책 발표 |
| 부동산114 | r114.com | 시세 데이터 |
| 네이버 부동산 | land.naver.com | 매물/시세 |
| 부동산스터디 카페 | cafe.naver.com/jaegebal | 커뮤니티 인사이트 |
| 청약홈 | applyhome.co.kr | 청약 일정 |
| 실거래가 공개시스템 | rt.molit.go.kr | 실거래 데이터 |
| DART | dart.fss.or.kr | 건설사 공시 |

### 1-3. 트렌드 매칭 알고리즘

```python
def match_trends(sources_data, channel_keywords, youtube_suggest):
    """
    소스 뉴스 ↔ 채널 키워드 ↔ YouTube 트렌드 교차 분석
    
    1. 소스에서 오늘의 핫 토픽 추출 (TF-IDF or LLM 요약)
    2. YouTube 자동완성으로 검색 수요 확인
    3. 채널 기존 콘텐츠와 중복 체크
    4. 점수 산정:
       - 뉴스 시의성 (오늘 발행 = 높음)
       - 검색 수요 (자동완성 등장 = 높음)
       - 채널 적합도 (니치 매칭)
       - 경쟁도 (동일 주제 영상 수)
       - 미다룬 주제 보너스
    5. 상위 5개 주제 추천
    """
```

### 1-4. 기획안 생성 (PD급)

기획안에 포함되는 항목:

```markdown
# [PD급 기획안]

## 1. 기획 의도 + 데이터 근거
- 왜 지금 이 주제인지 (소스 뉴스 + 트렌드 데이터)
- 검색 수요 증거 (YouTube 자동완성 + [선택] vidIQ)
- 채널 적합도 분석

## 2. 초 단위 큐시트
- 00:00~00:15 훅, 00:15~00:45 문제제기, ...
- 각 구간: 카메라/샷, B-roll, 자막/그래픽, BGM/효과음

## 3. 전체 대본 초안
- 풀 스크립트 (러닝타임 전체)
- 구어체, 채널 톤 반영

## 4. 썸네일 시안 3종
- 텍스트 배치, 폰트, 컬러코드, 레이아웃, 인물 포즈

## 5. 촬영 가이드
- 카메라/렌즈, 조명, 배경, 소품, 마이크

## 6. SEO 패키지
- 제목 3안 (각각 SEO 전략 설명)
- 설명란 템플릿 (타임스탬프 포함)
- 태그 30개
- 카드/엔드스크린 설정
- 공개 시간 추천

## 7. 예상 성과
- RPM, 1주/1개월 조회수, 구독 전환율

## 8. 경쟁 차별화
- 동일 주제 상위 5개 영상 분석
- 차별화 포인트
```

### 1-5. 니치별 프리셋

스킬 설치 시 니치를 선택하면 자동 설정:

**부동산 프리셋 (real_estate.json):**
```json
{
  "niche": "부동산",
  "default_sources": [
    {"name": "매일경제 부동산", "url": "https://www.mk.co.kr/news/realestate/", "type": "web"},
    {"name": "한경 부동산", "url": "https://www.hankyung.com/realestate", "type": "web"},
    {"name": "국토부 보도자료", "url": "https://www.molit.go.kr/USR/NEWS/m_71/lst.jsp", "type": "web"},
    {"name": "부동산114", "url": "https://www.r114.com", "type": "web"},
    {"name": "부동산스터디", "url": "https://cafe.naver.com/jaegebal", "type": "naver_cafe"}
  ],
  "keywords_seed": ["부동산", "아파트", "재개발", "분양", "전세", "매매", "청약", "금리", "GTX"],
  "tone": "전문가 신뢰감 + 시의성 강조",
  "typical_length": "12~18분",
  "rpm_range": "3000~7000",
  "hook_style": "뉴스 속보 형태 ('오늘 나온 뉴스, 놓치면 큰일납니다')"
}
```

**테크/AI 프리셋 (tech_ai.json):**
```json
{
  "niche": "AI/테크",
  "default_sources": [
    {"name": "X AI 트렌드", "type": "x_search", "query": "AI agent, Claude, GPT"},
    {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "type": "rss"},
    {"name": "AI 타임스", "url": "https://www.aitimes.com", "type": "web"}
  ],
  "keywords_seed": ["AI", "ChatGPT", "Claude", "에이전트", "자동화", "옵시디언"],
  "tone": "친근한 교육자 + 실전 데모",
  "typical_length": "10~15분",
  "rpm_range": "5000~13000",
  "hook_style": "놀라운 발견 형태 ('이거 아직 모르시면 큰일입니다')"
}
```

---

## 📊 기능 2: 경쟁채널 SWOT 분석

### 2-1. 입력

```
/swot
> "경쟁채널 URL을 입력해주세요 (최대 3~5개)"
> 1. https://www.youtube.com/@부동산읽어주는남자
> 2. https://www.youtube.com/@월급쟁이부동산
> 3. https://www.youtube.com/@집코노미
```

### 2-2. 데이터 수집 (YouTube Data API v3)

각 채널에서 수집하는 데이터:

| 데이터 | API 엔드포인트 | 분석 용도 |
|--------|---------------|-----------|
| 구독자 수 | channels.list | 규모 비교 |
| 총 조회수 | channels.list | 성장 속도 |
| 영상 수 | channels.list | 업로드 빈도 |
| 최근 30개 영상 | search.list | 성과 분석 |
| 각 영상 조회수/좋아요 | videos.list | 평균 성과 |
| 영상 제목/설명/태그 | videos.list | 키워드 전략 |
| 업로드 시간 패턴 | videos.list | 업로드 전략 |
| 댓글 수 | videos.list | 참여도 |
| Shorts vs Long | videos.list | 포맷 전략 |

### 2-3. SWOT 분석 프레임워크

```markdown
# 📊 SWOT 분석 리포트

## 채널 비교 대시보드
| 지표 | 내 채널 | 경쟁A | 경쟁B | 경쟁C |
|------|---------|-------|-------|-------|
| 구독자 | 10.5K | 50K | 120K | 30K |
| 월 평균 조회수 | 25K | 150K | 400K | 80K |
| 평균 조회수/영상 | 3.2K | 8K | 15K | 5K |
| 업로드 빈도 | 주 2회 | 주 5회 | 주 3회 | 주 1회 |
| 평균 영상 길이 | 12분 | 8분 | 18분 | 25분 |
| 참여율 (좋아요/조회) | 4.2% | 3.1% | 5.5% | 2.8% |
| Shorts 비율 | 10% | 40% | 5% | 0% |
| 성장률 (최근 3개월) | +15% | +8% | +12% | +3% |

## S (Strengths) — 강점
- 참여율 4.2%로 경쟁 대비 높음 (충성 시청자)
- AI 교육 니치에서 독보적 포지셔닝
- ...

## W (Weaknesses) — 약점
- 구독자 규모 경쟁 대비 소규모
- Shorts 콘텐츠 부족
- ...

## O (Opportunities) — 기회
- 경쟁A는 Shorts 중심 → 장편 시장 공백
- 경쟁B의 부동산 + AI 교차 영역 미진입
- ...

## T (Threats) — 위협
- 경쟁A의 빠른 업로드 빈도 (주 5회)
- ...

## 🎯 전략 제안
### 즉시 실행 (1주 내)
1. ...

### 중기 전략 (1개월)
1. ...

### 장기 방향 (3개월)
1. ...

## 📈 경쟁 채널별 상세 분석
### 경쟁A: 부동산읽어주는남자
- 상위 영상 TOP 5 (제목, 조회수, 키워드)
- 콘텐츠 전략: ...
- 약점/공략 포인트: ...
```

### 2-4. 분석 엔진 로직

```python
def swot_analysis(my_channel, competitors):
    """
    1. 정량 분석 (YouTube API 데이터)
       - 구독자, 조회수, 참여율, 성장률 비교
       - 키워드 오버랩/갭 분석
       - 업로드 패턴 비교
    
    2. 정성 분석 (LLM)
       - 상위 영상 제목/썸네일 패턴
       - 콘텐츠 포지셔닝 차이
       - 톤/스타일 차별점
       - 댓글 감성 분석 (샘플)
    
    3. SWOT 매트릭스 생성
       - S: 내가 경쟁보다 나은 지표 + 고유 강점
       - W: 내가 경쟁보다 약한 지표 + 개선 필요
       - O: 경쟁이 안 하는 영역 + 트렌드 기회
       - T: 경쟁 우위 + 시장 위협
    
    4. 전략 제안 (LLM)
       - 데이터 기반 액셔너블 전략 3단계
    """
```

---

## 🔧 기술 스택

### 필수 (API 키 불필요)
| 기술 | 용도 | 비용 |
|------|------|------|
| YouTube Data API v3 | 채널/영상 분석 | 무료 (10,000 units/일) |
| YouTube suggestqueries | 트렌드 키워드 | 무료 |
| web_fetch (OpenClaw 내장) | 웹 크롤링 | 무료 |
| feedparser (Python) | RSS 수집 | 무료 |
| OpenClaw LLM | 기획안/SWOT 생성 | 사용자 모델 |

### 선택 (있으면 강화)
| 기술 | 용도 | 조건 |
|------|------|------|
| vidIQ (브라우저) | 키워드 점수, Outliers | vidIQ 계정 + 브라우저 로그인 |
| Grok/X 검색 | 실시간 바이럴 | XAI_API_KEY |
| 네이버 검색 API | 정밀 카페/뉴스 검색 | NAVER_CLIENT_ID |
| Cerebras | 무료 전처리/요약 | CEREBRAS_API_KEY |

### 의존성
```
# requirements.txt
feedparser>=6.0
google-api-python-client>=2.0  # YouTube Data API
beautifulsoup4>=4.12            # 웹 파싱 보조
```

---

## 🚀 개발 로드맵

### Phase 1: 핵심 엔진 (1주, 3/9~3/15)
- [ ] 프로젝트 구조 생성 (`youtube-pd-agent/`)
- [ ] `youtube_api.py` — YouTube Data API v3 래퍼
  - 채널 정보 조회
  - 최근 영상 목록 + 통계
  - 키워드/태그 추출
- [ ] `keyword_suggest.py` — YouTube 자동완성 키워드 수집
- [ ] `web_scraper.py` — web_fetch 기반 뉴스 크롤링
- [ ] `channel_analyzer.py` — 채널 DNA 분석 (니치 감지, 성과 통계)
- [ ] SKILL.md 작성 (OpenClaw 스킬 정의)

### Phase 2: 온보딩 + 기획 생성 (1주, 3/16~3/22)
- [ ] `onboard.py` — 대화형 온보딩 플로우
  - 채널 URL → 자동 분석 → 확인
  - 정보 소스 등록 (URL 입력 → 타입 자동 감지)
  - 경쟁채널 등록
  - `channel_profile.json` + `sources.json` 저장
- [ ] `source_collector.py` — 등록된 소스 일괄 크롤링
  - RSS, 웹, 네이버 카페 통합 수집
  - 중복 제거 + 날짜 필터
- [ ] `trend_matcher.py` — 소스 뉴스 ↔ 키워드 교차 분석
- [ ] `plan_generator.py` — PD급 기획안 생성
  - 큐시트, 대본, 썸네일, SEO 전부 포함
  - 마크다운 템플릿 기반 출력
- [ ] 니치 프리셋 3개 (부동산, AI/테크, 범용)

### Phase 3: SWOT + 고도화 (1주, 3/23~3/29)
- [ ] `swot_analyzer.py` — 경쟁채널 SWOT 분석
  - 정량 비교 (API 데이터)
  - 정성 분석 (LLM)
  - 전략 제안
- [ ] vidIQ 브라우저 연동 (선택 모듈)
  - 로그인 감지 → 키워드 데이터 자동 수집
- [ ] Grok/X 검색 연동 (선택 모듈)
- [ ] 크론잡 연동 — 주간 자동 기획안 생성

### Phase 4: 공개 + 문서화 (3일, 3/30~4/1)
- [ ] GitHub 리포지토리 생성
- [ ] README.md (설치 가이드, 스크린샷, 데모)
- [ ] ClawHub 등록 (`clawhub publish`)
- [ ] 유튜브 영상 제작 (배움의 달인 채널)

---

## 📋 커맨드 설계

### /기획 (또는 /plan)
```
/기획
> 소스 크롤링 중... (매경 부동산 5건, 부동산스터디 3건, YouTube 트렌드 15개)
> 트렌드 매칭 중... (상위 5개 주제 선정)
> PD급 기획안 생성 중...

📋 이번 주 기획안 TOP 3:
1. "강남 재개발 초읽기! 2026 투자 지도" (시의성 ⭐⭐⭐)
2. "전세 사기 방지법 총정리" (검색 수요 ⭐⭐⭐)
3. "금리 인하 후 부동산 전망" (트렌드 ⭐⭐)

> 어떤 주제로 기획안 작성할까요? (번호 선택)
> 1

[PD급 기획안 생성 → 마크다운 저장 → 링크 제공]
```

### /swot (또는 /경쟁분석)
```
/swot
> 경쟁채널 URL 입력 (최대 5개, 쉼표 구분):
> https://youtube.com/@A, https://youtube.com/@B, https://youtube.com/@C

> 데이터 수집 중... (내 채널 + 경쟁 3개)
> SWOT 분석 중...

📊 SWOT 리포트 생성 완료!
[마크다운 저장 → 링크 제공]
```

### /소스관리 (또는 /sources)
```
/소스관리
> 현재 등록된 소스:
> 1. 매일경제 부동산 (web)
> 2. 부동산스터디 카페 (naver_cafe)
> 3. 한경 부동산 (web)
>
> [추가] [삭제] [테스트]
```

---

## ⚙️ SKILL.md 초안

```markdown
# YouTube PD Agent

유튜브 채널 분석 + PD급 기획안 자동 생성 + 경쟁채널 SWOT 분석

## 트리거
- `/기획` — 이번 주 콘텐츠 기획안 생성
- `/swot [경쟁채널URL]` — 경쟁채널 SWOT 분석
- `/소스관리` — 정보 소스 추가/삭제
- `/온보딩` — 채널 설정 (최초 1회)

## 필수 조건
- YouTube Data API v3 키 (YOUTUBE_API_KEY)
- Python 3.10+

## 선택 강화
- vidIQ 계정 (브라우저 로그인 시 자동 연동)
- XAI_API_KEY (Grok/X 검색)
- NAVER_CLIENT_ID + NAVER_CLIENT_SECRET (네이버 검색)

## 설치
clawhub install youtube-pd-agent
또는
git clone https://github.com/reallygood83/youtube-pd-agent
```

---

## 💰 비용 분석

| 항목 | 비용 | 비고 |
|------|------|------|
| YouTube Data API | 무료 | 10,000 units/일 (충분) |
| OpenClaw LLM | 사용자 기존 모델 | Haiku $0.002/기획안 |
| vidIQ (선택) | $0~39/월 | 무료 플랜으로도 기본 가능 |
| Grok (선택) | 사용자 API | 없어도 동작 |
| **합계** | **$0 (기본)** | 선택 강화 시 ~$40/월 |

---

## 🎯 차별화 포인트

기존 유튜브 기획 도구 대비:

| 항목 | 기존 도구 (vidIQ/TubeBuddy) | YouTube PD Agent |
|------|----------------------------|------------------|
| 기획 수준 | 키워드 추천 | **PD급 큐시트 + 풀 대본** |
| 소스 크롤링 | ❌ | **사용자 맞춤 소스 자동 수집** |
| 니치 특화 | 범용 | **부동산/AI/교육 등 프리셋** |
| SWOT 분석 | 제한적 | **컨설턴트급 SWOT 리포트** |
| 가격 | $9~49/월 | **무료 (OpenClaw 스킬)** |
| 커스터마이징 | ❌ | **오픈소스, 완전 커스텀** |

---

## 📹 콘텐츠 시너지

이 에이전트 자체가 "배움의 달인" 콘텐츠가 됨:
1. **개발 과정 영상** — "AI 유튜브 PD 에이전트 만드는 과정"
2. **데모 영상** — "이 AI가 내 유튜브를 기획합니다"
3. **클라이언트 사례** — 김기원 대표 채널에 실제 적용
4. **GitHub 공개** — 개발자 커뮤니티 트래픽
5. **ClawHub 등록** — OpenClaw 생태계 기여

---

*작성: Jarvis (OpenClaw) | 2026-03-08*
*의뢰: 김문정 (배움의 달인)*
*첫 번째 클라이언트: 김기원 대표 (부동산 유튜버)*
