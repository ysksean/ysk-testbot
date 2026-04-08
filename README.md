# 🤖 AI 일정 비서 텔레그램 봇

텔레그램으로 대화하듯 Google 캘린더 일정을 관리하는 AI 비서입니다.

---

## ✨ 기능

| 기능 | 예시 |
|------|------|
| 📅 일정 조회 | "이번 주 일정 알려줘", "5월 일정 뭐 있어?" |
| ➕ 일정 추가 | "4월 10일 오후 6시 동대구역 미팅 추가해줘" |
| 🗑️ 일정 삭제 | "4월 15일 오후 4시 미팅 일정 지워줘" |
| ✏️ 일정 수정 | "기차타기 시간 오후 5시로 바꿔줘" |
| 💬 대화 기억 | 재시작해도 이전 대화 맥락 유지 |

---

## 🛠️ 기술 스택

- **Telegram Bot** — 채팅 인터페이스 (`python-telegram-bot`)
- **Groq API** — LLM 추론, Function Calling (`llama-3.3-70b-versatile`)
- **Google Calendar API** — 일정 CRUD
- **Redis** — 대화 히스토리 영구 저장
- **Railway** — 클라우드 배포 (24시간 운영)

---

## 🚀 배포 구조

```
텔레그램 메시지
      ↓
Railway (Python 서버)
      ├── Groq API (의도 파악 + 답변 생성)
      ├── Google Calendar API (일정 관리)
      └── Redis (대화 기록 저장)
      ↓
텔레그램 답장
```

---

## ⚙️ 환경변수

`.env.example` 참고:

```
TELEGRAM_TOKEN=        # @BotFather에서 발급
GROQ_API_KEY=          # console.groq.com
GOOGLE_CALENDAR_ID=primary
GOOGLE_TOKEN_JSON=     # Google OAuth token.json 내용
REDIS_URL=             # Railway Redis URL
```

---

## 🏃 로컬 실행

```bash
pip install -r requirements.txt
python main.py
```
