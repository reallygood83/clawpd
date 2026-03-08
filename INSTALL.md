# ClawPD 설치 가이드 (OpenClaw 사용자용)

## 1단계: 클론
```bash
cd ~/Projects  
git clone https://github.com/reallygood83/clawpd.git
cd clawpd
pip install -r requirements.txt
```

## 2단계: 환경변수
```bash
# YouTube API 키 (필수, 무료)
export YOUTUBE_API_KEY="your-key-here"

# 선택
export XAI_API_KEY="..."          # Grok/X 검색
export NAVER_CLIENT_ID="..."      # 네이버 검색
export NAVER_CLIENT_SECRET="..."
```

## 3단계: 온보딩 설정
OpenClaw에서:
```
/온보딩
```
→ 채널 URL, 소스, 경쟁채널, 옵시디언 볼트 경로 설정

## 4단계: 사용
```
/기획          → PD급 기획안 생성 + 옵시디언 저장
/기획 [주제]    → 특정 주제 기획안
/swot [URL]    → SWOT 분석
/소스관리       → 소스 추가/삭제
```
