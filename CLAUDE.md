# 텔레그램 AI 일정 비서

## 실행
```bash
python main.py
```

## 설치
```bash
pip install -r requirements.txt
```

## 프로젝트 구조
```
heritage/
├── main.py                 # 봇 실행 진입점
├── src/
│   ├── handlers.py         # 텔레그램 메시지 핸들러
│   ├── gemini_client.py    # Gemini API 래퍼
│   └── calendar_client.py  # Google Calendar API 래퍼
├── credentials/            # Google OAuth 파일 (git 제외)
└── .env                    # API 키 (git 제외)
```

## 환경변수 (.env)
- `TELEGRAM_TOKEN`: @BotFather에서 발급
- `GEMINI_API_KEY`: aistudio.google.com에서 발급
- `GOOGLE_CALENDAR_ID`: 보통 `primary`

## Google Calendar 인증
처음 실행 시 브라우저에서 OAuth 인증 필요.
`credentials/credentials.json` 파일이 있어야 함 (Google Cloud Console에서 다운로드).
인증 후 `credentials/token.json` 자동 생성됨.

## 규칙
- `.env` 절대 커밋하지 말 것
- `credentials/token.json` 절대 커밋하지 말 것
- 새 기능은 `src/` 안에 추가
- 포맷터: black
