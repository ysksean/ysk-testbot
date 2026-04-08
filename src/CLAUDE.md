# src/ 폴더 가이드

## 파일 역할

| 파일 | 역할 |
|------|------|
| `handlers.py` | 텔레그램 메시지 수신 → 처리 → 응답 전송 |
| `gemini_client.py` | Groq LLM 호출, 대화 히스토리 관리, Function Calling |
| `calendar_client.py` | Google Calendar API CRUD (조회/추가/수정/삭제) |

## 주요 흐름

```
handlers.py
  ├── calendar.get_events()       # 항상 60일치 일정 조회
  ├── gemini.chat()               # LLM에 메시지 + 일정 컨텍스트 전달
  │     └── Function Calling      # LLM이 직접 판단해서 함수 호출
  └── calendar.create/delete/update_event()  # 툴 호출 결과에 따라 실행
```

## 규칙

- 새 기능은 이 폴더 안에 추가
- 외부 API 호출은 각 client 파일에서만
- handlers.py는 라우팅만 담당, 비즈니스 로직은 client에
- 환경변수는 항상 `os.getenv()`로 읽기, 하드코딩 금지
