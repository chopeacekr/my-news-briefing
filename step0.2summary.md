# 📚 STEP 0.2 실험 코드 요약 설명  
**Qwen LoRA 학습 + A/B 테스트 (Qwen vs Mistral)**

---

## 🎯 이 코드의 목적

이 스크립트는 **Qwen 1.5B 모델을 소규모 SFT(50개 논문)로 학습**한 뒤,  
그 결과를 **A/B 테스트로 비교·분석**하고 **JSON/CSV로 저장**하는  
**단일 실행형 실험 파이프라인**이다.

---

## 🔄 전체 실행 흐름

### 1️⃣ 환경 준비
- `transformers`, `datasets`, `peft`, `bitsandbytes` 등 필수 패키지 설치
- 설치 여부를 flag 파일로 관리해 **중복 설치 방지**
- GPU 존재 여부를 검사하고 없으면 즉시 중단

---

### 2️⃣ 데이터 로딩 & 전처리
- HuggingFace `ccdv/arxiv-summarization` 데이터셋에서 **총 50개 논문** 로딩  
  - Train 40 / Validation 10
- arXiv 논문에 포함된 LaTeX 토큰과 특수 기호를 제거하는 전처리 수행
- **중요:**  
  - 학습용 토큰화 데이터와 별도로  
    **원본 텍스트(train_raw / val_raw)를 그대로 보관**
  - A/B 테스트 시 `original_article`이 **실제 논문 본문**이 되도록 설계

---

### 3️⃣ 학습 데이터 포맷 구성 (Qwen Instruct 형식)
- Qwen Instruct 모델에 맞는 Chat 포맷 사용
  - `system`: 도움 역할 지정
  - `user`: “50단어 이하 요약” + 논문 본문
  - `assistant`: 정답 abstract
- CausalLM 방식으로 학습 (`labels = input_ids`)

---

### 4️⃣ Qwen 1.5B + 4-bit LoRA 학습
- Qwen 1.5B 모델을 **4-bit 양자화**로 로드해 GPU 메모리 절약
- LoRA를 Attention projection 모듈에만 적용
- `TrainingArguments`에서 발생할 수 있는
  - `evaluation_strategy` / `eval_strategy` 버전 충돌을 자동 처리
- 학습 결과를 Drive에 저장
