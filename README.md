# 📰 ArXiv-NewsBrief (V4.2)
## AI 논문 요약 + GGUF 웹 챗봇

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Model: Qwen2.5-1.5B](https://img.shields.io/badge/Model-Qwen2.5--1.5B-green.svg)](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)

> **학술 논문과 웹 텍스트를 30초 안에 이해할 수 있는 뉴스 브리핑으로 변환**  
> ArXiv 논문 초록을 일반인도 이해 가능한 뉴스 브리핑 톤으로 1-2문장, 최대 45단어 안에 요약하는 프로덕션 급 AI 시스템

---

## 📖 목차

- [프로젝트 목표](#-프로젝트-목표)
- [주요 기능](#-주요-기능)
- [빠른 시작](#-빠른-시작)
- [웹 챗봇 사용법](#-웹-챗봇-사용법)
- [모델 개발](#-모델-개발)
- [성능 지표](#-성능-지표)
- [문제 해결](#-문제-해결)

---

## 🎯 프로젝트 목표

본 프로젝트는 **데이터 생성 → 모델 학습 → 웹 챗봇(GGUF)**의 전체 파이프라인을 포함합니다.

### 핵심 목표

- ✅ 논문·웹 텍스트를 **뉴스처럼 짧고 명확하게 요약**
- ✅ **전문 용어 최소화**, 일반 독자 대상
- ✅ **출력 규격 고정**: 1-2문장 / 최대 45단어
- ✅ **환각 방지**: 입력에 없는 정보(숫자·사실) 생성 금지
- ✅ **TTS/STT**: 음성 입출력 지원

### 타겟 사용자

- **과학 커뮤니케이터**: 빠르고 정확한 요약 필요
- **언론인**: 연구 동향 취재
- **교육자**: 최신 발견 설명
- **일반 대중**: 과학 발전에 관심 있는 사람

---

## ✨ 주요 기능

### 🚀 성능

- **빠른 추론**: CPU 3-4초 / GPU 1초
- **높은 품질**: 98% 사실 정확도, 2% 환각
- **일관된 출력**: 94% 구조 준수
- **최적화 크기**: 0.9GB GGUF (70% 감소)

### 🎓 기술

- **모델**: Qwen2.5-1.5B + LoRA (r=16)
- **학습 데이터**: 2,000개 고품질 쌍 (v4.2)
- **Teacher**: Gemini-3-27b
- **추론**: PyTorch (GPU) / GGUF (CPU)
- **음성**: gTTS + Google SR
- **번역**: Gemini 2.5 Flash

### 🌐 웹 챗봇

- **텍스트 요약**: 논문/웹 텍스트 즉시 요약
- **📰 뉴스 브리프**: 최신 AI 논문 자동 요약
- **🎤 음성 입력**: STT → 요약
- **🔊 음성 출력**: TTS 자동재생
- **다국어**: 영어/한국어 UI

---

## ⚡ 빠른 시작

### 1. 설치

```bash
# Python 3.11+ 필요
# uv 설치 (권장)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 클론
git clone https://github.com/your-org/arxiv-newsbrief.git
cd arxiv-newsbrief

# 의존성 설치 (자동으로 가상환경 생성)
uv sync

# 또는 pip 사용
pip install -e .
```

### 2. 모델 다운로드

```bash
# GGUF 모델 다운로드 (0.9GB)
mkdir -p ArXiv-NewsBrief-1.5B-2k-v4.2
cd ArXiv-NewsBrief-1.5B-2k-v4.2
wget https://huggingface.co/your-org/arxiv-newsbrief/resolve/main/ArXiv-NewsBrief-Q4.2_K_M.gguf
cd ..
```

### 3. 웹 챗봇 실행

```bash
# Streamlit 실행
uv run streamlit run web_summary.py

# 또는
streamlit run web_summary.py

# 브라우저: http://localhost:8501
```

### 4. (선택) Gemini API 설정

```bash
# .env 파일 생성
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# 한국어 번역 기능 활성화됨
```

---

## 🌐 웹 챗봇 사용법

### 기본 사용

```yaml
텍스트 요약:
  1. 하단 채팅창에 논문 초록 입력
  2. Enter → 자동 요약
  3. (한국어 선택 시) 자동 번역
  4. (TTS 활성화 시) 음성 재생

음성 입력:
  1. "Voice Input" 섹션
  2. 오디오 파일 업로드 (WAV/MP3/M4A)
  3. STT → 요약 → TTS
```

### 📰 뉴스 브리프 (핵심 기능!)

**최신 AI 논문 3개 자동 요약 시스템**

```yaml
워크플로우:
  1. ArXiv API로 최근 논문 조회 (1-30일)
  2. Semantic Scholar로 인용수 조회
  3. 상위 3개 선택
  4. 각 논문 초록 GGUF 요약 (3회)
  5. 템플릿 스크립트 생성:
     - 오프닝 (1문장)
     - 논문 1/2/3 (각 1-2문장)
     - 클로징 (1문장)
  6. (한국어만) Gemini 번역
  7. (선택) TTS 자동재생

사용법:
  1. 사이드바 "Latest Papers" 설정
     - Lookback days: 7 (조회 기간)
     - How many papers: 3
     - Query: cs.AI OR cs.LG
  2. 버튼 클릭
     - 📌 Fetch: 논문 조회만
     - ➡️ Send: 채팅으로 전송
     - 📰 Make News Brief: 자동 요약 실행
```

**출력 예시:**

```
Here's your quick AI paper news brief with three highlights.

1) Attention Is All You Need
The paper introduces the Transformer architecture that relies 
entirely on attention mechanisms. This innovation became the 
foundation for modern language models.

2) BERT: Pre-training of Deep Transformers
Scientists created a new language model that understands context 
from both directions. BERT achieved state-of-the-art results.

3) GPT-3: Language Models are Few-Shot Learners
Researchers demonstrated that large language models can perform 
tasks without fine-tuning. The model showed impressive few-shot 
learning capabilities.

That's it for today—check the paper links for full details.
```

### 사이드바 설정

```yaml
Language:
  English: 영문 요약 + 영문 TTS
  Korean: 영문 요약 → 한국어 번역 + 한국어 TTS

Model Settings:
  Max tokens: 50-250 (기본 120)
  Temperature: 0.0-1.2 (기본 0.4)
  Top-p: 0.1-1.0 (기본 0.9)

GGUF Runtime:
  Context: 1024 / 2048 / 4096
  Threads: CPU 코어 수 (기본: 절반)
  Batch: 64 / 128 / 256 / 512

Audio:
  Enable TTS: 음성 출력
  Enable STT: 음성 입력

Translation:
  Enable Gemini: 한국어 번역 (API Key 필요)
```

---

## 🔬 모델 개발

### 학습 파이프라인

```
STEP 1: 데이터 생성 (dataset_generator.py)
  Teacher: Gemini-3-27b
  Input: ArXiv 초록 10,000개
  Output: 2,000개 고품질 쌍
  ↓
STEP 2: SFT 학습 (sft_train_data.py)
  Student: Qwen2.5-1.5B
  Method: LoRA (r=16, α=32)
  Epochs: 3, LR: 2e-4
  ↓
STEP 3: 모델 병합 (sft_merge_gguf.py)
  LoRA → 베이스 병합
  Output: 단독 모델 (3GB)
  ↓
STEP 4: GGUF 변환
  Quantization: Q4_K_M
  Size: 3GB → 0.9GB
  Target: CPU 최적화
```

### 새 버전 학습

```bash
# 1. 데이터 생성 (v4.3)
python dataset_generator.py

# 2. 모델 학습 (Colab 권장, T4 GPU)
python sft_train_data.py

# 3. 병합 + GGUF 변환
python sft_merge_gguf.py

# 4. 평가
python evaluate.py --mode ab_test --samples 100
```

### 핵심 설정

```python
# sft_train_data.py
MODEL_NAME = "ArXiv-NewsBrief-1.5B-2k-v4.2"
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

# LoRA
r = 16
lora_alpha = 32
target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]

# Training
epochs = 3
learning_rate = 2e-4
batch_size = 4
max_length = 512

# Generation
temperature = 0.3
top_k = 40
top_p = 0.9
max_tokens = 80
```

---

## 📊 성능 지표

### 모델 성능 (v4.2)

| 지표 | 값 | 목표 | 상태 |
|:----:|:--:|:----:|:----:|
| **평균 단어 수** | 43.2 | ≤45 | ✅ 96% |
| **2문장 비율** | 94% | >90% | ✅ Pass |
| **사실 정확도** | 98% | >95% | ✅ Pass |
| **환각 비율** | 2% | <5% | ✅ Pass |
| **ROUGE-L** | 0.42 | >0.35 | ✅ Pass |
| **BERTScore** | 0.88 | >0.85 | ✅ Pass |

### 추론 속도

| 환경 | 하드웨어 | 속도 | 처리량 |
|:----:|:--------:|:----:|:------:|
| **CPU** | 16 코어 | 3-4초 | 15-20/분 |
| **GPU** | T4 (16GB) | 1초 | 60/분 |
| **GPU** | A100 | 0.5초 | 120/분 |

### 모델 크기

| 포맷 | 크기 | 메모리 | 품질 | 용도 |
|:----:|:----:|:------:|:----:|:----:|
| **FP16** | 3.0GB | 6GB | 100% | 학습 |
| **Merged** | 3.0GB | 3GB | 100% | GPU |
| **Q4_K_M** | 0.9GB | 1GB | 98% | ⭐ CPU |

---

## 🔧 문제 해결

### 모델 로드 실패

```bash
# 경로 확인
ls -lh ArXiv-NewsBrief-1.5B-2k-v4.2/*.gguf

# 절대 경로 사용
GGUF_MODEL_PATH = "/absolute/path/to/model.gguf"
```

### 메모리 부족

```python
# Context 줄이기
n_ctx = 1024  # 2048 → 1024

# Batch 줄이기
n_batch = 64  # 256 → 64
```

### TTS 자동재생 안됨

```yaml
원인: 브라우저 자동재생 정책
해결: Chrome → 설정 → 사이트 설정 → 소리 → 허용
또는: 수동 재생 버튼 클릭
```

### Gemini 번역 실패

```bash
# API 키 확인
export GOOGLE_API_KEY=your_key

# 또는 사이드바에서 입력
Gemini API Key: [****]

# 할당량 확인
# https://console.cloud.google.com/apis/quotas
```

### 추론 속도 느림

```python
# 스레드 증가
n_threads = 16  # CPU 코어 수

# Batch 증가
n_batch = 512

# Max tokens 감소
max_new_tokens = 80
```

---

## 📂 프로젝트 구조

```
ArXiv-NewsBrief-1.5B-2k-v4.2/
│
├── data/                              # 학습 데이터
│   ├── teacher_prompt.md
│   └── v4.2_training_data_all.csv
│
├── reports/                           # 분석 보고서
│   ├── analysis/
│   ├── evaluation/
│   └── training/
│   └── REPORT.md                     # ArXiv-NewsBrief v4.2 프로젝트 발표자료
├── ArXiv-NewsBrief-Q4.2_K_M.gguf     # ⭐ CPU 모델
│
├── dataset_generator.py               # 데이터 생성
├── sft_train_data.py                 # 학습
├── sft_merge_gguf.py                 # 병합+GGUF
├── web.py                            # 🌐 웹 챗봇
│
├── pyproject.toml                     # 의존성
├── uv.lock                            # 버전 고정
└── README.md                          # 이 파일
```

---

## 🚀 로드맵

### V4.3 (개발 중)
- [ ] 학습 데이터 5,000개 확장
- [ ] 다중 도메인 (Physics, Biology, CS)
- [ ] 배치 추론 최적화

### V5.0 (계획)
- [ ] 다국어 (한국어, 스페인어, 프랑스어)
- [ ] Topic-aware briefing
- [ ] 모바일 앱

### V6.0 (비전)
- [ ] 실시간 ArXiv 통합
- [ ] 개인화 요약 스타일
- [ ] 멀티모달 (PDF, 이미지)

---

## 📝 주요 문서

### 핵심 문서
- **REPORT.md**: 종합 프로젝트 보고서
- **TEAM_WORKFLOW.md**: 협업 가이드
- **dataset_pipeline.md**: 데이터 파이프라인

### 분석 보고서
- **chatgpt_result_v4.2.md**: GPT-4 평가
- **claude_result_v4.2.md**: Claude 평가
- **LLM-as-a-Judge.md**: 평가 방법론

---

## 🙏 감사의 말

- **Qwen2.5-1.5B**: Alibaba Cloud
- **Gemini**: Google DeepMind
- **llama.cpp**: Georgi Gerganov
- **Transformers**: Hugging Face
- **ArXiv**: 논문 데이터

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 📮 연락처

- **GitHub Issues**: 버그 리포트
- **Discussions**: 질문 및 토론
- **Email**: contact@arxiv-newsbrief.com

---

## 📈 인용

```bibtex
@software{arxiv_newsbrief_2026,
  author = {ArXiv-NewsBrief Team},
  title = {ArXiv-NewsBrief: AI-Powered Research Paper Summarizer},
  year = {2026},
  version = {4.2},
  url = {https://github.com/your-org/arxiv-newsbrief}
}
```

---

<div align="center">

**ArXiv-NewsBrief 팀이 ❤️를 담아 만들었습니다**

[빠른 시작](#-빠른-시작) • [웹 챗봇](#-웹-챗봇-사용법) • [모델 개발](#-모델-개발) • [문제 해결](#-문제-해결)

</div>