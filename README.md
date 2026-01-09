# 📰 ArXiv-NewsBrief (V4.2)
## Paper & Web News Briefing + GGUF Web Chatbot

**ArXiv-NewsBrief**는 ArXiv 논문 초록과 웹 텍스트를  
👉 **일반인도 이해 가능한 뉴스 브리핑 톤**으로 **1–2문장, 최대 45단어** 안에 요약하는 LLM 프로젝트입니다.

본 프로젝트는 **데이터 생성 → 모델 학습 → 웹 챗봇(GGUF)**의 전체 파이프라인을 포함합니다.

---

## 🎯 Project Goals

- 논문·웹 텍스트를 **뉴스처럼 짧고 명확하게 요약**
- **전문 용어 최소화**, 일반 독자 대상
- **출력 규격 고정**: 1–2문장 / 최대 45단어
- **환각 방지**: 입력에 없는 정보(숫자·사실·추정) 생성 금지
- **TTS(음성 브리핑)** 및 모바일/웹 UI에 바로 사용 가능

---

## 🧬 Base Model & Fine-tuning

- **Base Model**: `Qwen/Qwen2.5-1.5B-Instruct`
- **Fine-tuning**: LoRA + 4-bit quantization (NF4)
- **Inference**
  - GPU: Transformers + bitsandbytes
  - CPU: **GGUF(Q4_K_M)** + llama.cpp

---

## ⭐ Current Stable Version

### V4.2 — Hallucination-Reduced News Briefing (Current)

- **Model**: `ArXiv-NewsBrief-1.5B-2k-v4.2`
- **특징**
  - 뉴스 브리핑 스타일 고정
  - 환각 방지 규칙 강화
  - 숫자·사실 검증
  - LaTeX / 메타데이터 / 참고문헌 제거 전처리
  - 병렬 데이터 생성(GROUP_ID) 지원

### Output Constraints
- 1–2 complete sentences  
- Max 45 words  
- Professional / neutral tone  
- Prompt 재출력 금지  
- 추측성 표현(approximately, around 등) 지양  

---

## 📖 Version History

| Version | Model Name | Description |
|------|-----------|------------|
| V3.0 | ArXiv-Academic-1.5B-600-v3.0 | Academic baseline |
| V4.0 | ArXiv-NewsBrief-1.5B-1k-v4.0 | News briefing 첫 프로덕션 |
| V4.1 | ArXiv-NewsBrief-1.5B-2k-v4.1 | **AI 데이터셋 기반 실험 단계** |
| ⭐ V4.2 | ArXiv-NewsBrief-1.5B-2k-v4.2 | **환각 방지 강화 (현재)** |
| 🎯 V4.3 | ArXiv-NewsBrief-1.5B-5k-v4.3 | 대규모 확장 (계획) |

---

## 📁 Directory Structure

/content/drive/MyDrive/ArXiv-Models/
│
├── ArXiv-Academic-1.5B-600-v3.0/
│
├── ArXiv-NewsBrief-1.5B-1k-v4.0/
│
├── ArXiv-NewsBrief-1.5B-2k-v4.1/
│ └── (experimental)
│
└── ArXiv-NewsBrief-1.5B-2k-v4.2/
├── final_model/
├── results/
│ ├── ab_test_.json
│ └── inference_.json
├── metadata.json
├── README.md
└── ArXiv-NewsBrief-Q4_K_M.gguf



---

## 🧱 Core Prompt (Teacher & Inference 동일)


---

## 🌐 Web Summarization

논문 초록 외에도 다음 입력을 동일한 규칙으로 요약합니다.

- 뉴스 기사
- 블로그 글
- 리서치 리포트
- 긴 웹 텍스트(복사/붙여넣기)

**규칙**
- 핵심 결론·의미 중심
- 입력에 없는 숫자/사실 사용 금지
- 항상 1–2문장 / 45단어 이하 유지

> Streamlit 챗봇의 **Text Input**에 웹 본문을 그대로 붙여넣으면 웹 요약으로 동작합니다.

---

## 🤖 GGUF Web Chatbot (Streamlit)

### ArXiv-NewsBrief v0.1 Summarization Chatbot (GGUF)

- **Model**: Qwen2.5-1.5B-Instruct → GGUF(Q4_K_M)
- **Inference**: llama-cpp-python (CPU)
- **TTS**: Google gTTS
- **STT**: Google Speech Recognition
- **Translation (Korean UI)**: Google Gemini 2.5 Flash

### GGUF Model Path

./ArXiv-NewsBrief-1.5B-2k-v4.2/ArXiv-NewsBrief-Q4_K_M.gguf


### Chatbot Features

- 텍스트 입력 요약 (논문 / 웹)
- 음성 입력(STT) → 요약 → 음성 출력(TTS)
- 한국어 UI: GGUF 요약 → Gemini 번역 → TTS
- ChatML 기반 Teacher 프롬프트 구조 재현
- TTS **자동 재생(autoplay)** 지원

---

## 🧪 Evaluation & A/B Test

- Base vs Fine-tuned 모델 비교
- Validation 샘플 랜덤 추출
- 체크 항목
  - 45단어 이하
  - 1–2문장
  - 환각 여부
  - 프롬프트 잔존 여부


### Chatbot Features

- 텍스트 입력 요약 (논문 / 웹)
- 음성 입력(STT) → 요약 → 음성 출력(TTS)
- 한국어 UI: GGUF 요약 → Gemini 번역 → TTS
- ChatML 기반 Teacher 프롬프트 구조 재현
- TTS **자동 재생(autoplay)** 지원

---

## 🧪 Evaluation & A/B Test

- Base vs Fine-tuned 모델 비교
- Validation 샘플 랜덤 추출
- 체크 항목
  - 45단어 이하
  - 1–2문장
  - 환각 여부
  - 프롬프트 잔존 여부
results/
├── ab_test_5samples_YYYYMMDD.json
└── val_test_5samples_YYYYMMDD.json



---

## ⚙️ Execution Modes

| Mode | Purpose | GPU | CPU |
|---|---|---:|---:|
| MODE 0 | Practice (50 samples) | ✅ | ❌ |
| MODE 1 | Full Training (1k–2k) | ✅ | ❌ |
| MODE 2 | Inference Only | 선택 | ✅ |

---

## 🔊 TTS / STT / Translation

- **TTS(gTTS)**: 뉴스 브리핑에 최적
- **STT(Google SR)**: 언어 설정 중요
- **Korean UI 번역**: Gemini API Key 필요

---

## 🚀 Roadmap

- **V4.3**: 5k 데이터 확장, 안정성 강화
- **V5.x**
  - 다국어 요약(EN/KO)
  - Topic-aware briefing
  - Streaming TTS

---

## 📌 Notes

- **V4.1은 실험 단계**
- **V4.2가 기준 모델**
- 모든 버전은 뉴스·음성 친화 포맷 유지 필수

---

## 🙌 Acknowledgements

- ArXiv summarization datasets  
- Hugging Face ecosystem  
- Qwen model family  
- OpenAI / Google Gemini / Anthropic  
- llama.cpp / Streamlit community


