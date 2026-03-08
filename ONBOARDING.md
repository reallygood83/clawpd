# 🚀 ClawPD 온보딩 가이드

## 설치 필요 조건

### 1. OpenClaw 실행 환경
- OpenClaw가 설치되어 있어야 합니다
- 텔레그램 또는 디스코드 채널 연동

### 2. YouTube Data API 키 (필수, 무료)
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성
3. YouTube Data API v3 활성화
4. API 키 생성
5. 환경변수 설정: `export YOUTUBE_API_KEY="발급받은키"`

### 3. Python 3.10+ 및 의존성
```bash
pip install google-api-python-client feedparser beautifulsoup4 lxml requests python-dateutil python-dotenv
```

### 4. 옵시디언 볼트 (선택, 권장)
- 기획안이 자동으로 옵시디언 노트로 저장됩니다
- 볼트 경로를 온보딩 시 설정

## 설치

```bash
cd ~/Projects  # 또는 원하는 위치
git clone https://github.com/reallygood83/clawpd.git
cd clawpd
pip install -r requirements.txt
```

## 온보딩 (최초 1회)

OpenClaw에서 `/온보딩` 실행하면:
1. 채널 URL 입력 → YouTube API로 자동 분석
2. 정보 소스 등록 (매경, 네이버 카페 등)
3. 경쟁채널 등록 (최대 5개)
4. 옵시디언 볼트 경로 설정
5. 설정 완료!

## 사용

- `/기획` — PD급 기획안 생성 (소스 크롤링 → 트렌드 매칭 → LLM 기획안)
- `/기획 [주제]` — 특정 주제로 기획안 생성
- `/swot [경쟁채널URL]` — SWOT 분석
- `/소스관리` — 소스 추가/삭제

## 선택 강화 (없어도 동작)
- vidIQ 계정 → 키워드 점수, Outliers
- Grok API (XAI_API_KEY) → X 실시간 트렌드
- 네이버 API (NAVER_CLIENT_ID) → 정밀 카페 검색
