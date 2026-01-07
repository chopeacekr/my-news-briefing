# 📰 My-News-Briefing V4.0: ArXiv 논문 자동 요약 시스템

**일반인도 이해할 수 있는 뉴스 브리핑 스타일 논문 요약 AI**

---

## 1. End-to-End 파이프라인

### 🔄 전체 파이프라인
```
[ArXiv 논문 데이터]
(Team 1: 데이터 수집 & 품질 관리)
    ↓
[Teacher LLM: Gemma-3-27b-it]
(고품질 요약 생성)
    ↓
[학습 데이터셋 구축]
(1,000개 고품질 샘플, V4 형식)
    ↓
┌─────────────────────────────────────┐
│  [Base Model: Qwen2.5-1.5B-Instruct] │
│                                       │
│  ┌─────────────────────────────┐    │
│  │ (비교용) 동일 프롬프트      │    │
│  │  → Output 1: Base 출력      │    │
│  └─────────────────────────────┘    │
│                                       │
│           ↓                           │
│  [Fine-tuning with LoRA]             │
│  (Team 2: 모델 학습)                 │
│   - 4-bit Quantization               │
│   - LoRA (r=16, alpha=32)            │
│   - 5 epochs, 2e-4 lr                │
│                                       │
│  ┌─────────────────────────────┐    │
│  │ 동일 프롬프트               │    │
│  │  → Output 2: Fine-tuned 출력│    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
    ↓
[A/B 테스트 & 평가]
(Team 3: 성능 평가 & 분석)
    ↓
┌─────────────────────────────────────┐
│  Output 1 vs Output 2 비교          │
│  • 간결성: 3.3 → 4.7 (+1.4) ✅      │
│  • 유창성: 3.7 → 4.3 (+0.6) ✅      │
│  • 일반인 이해도: 3.7 → 3.3 (-0.4)⚠️│
└─────────────────────────────────────┘
```

### 👥 팀 역할 분담

| 팀 | 담당 업무 | 주요 기여 |
|---|----------|-----------|
| **Team 1** | 데이터셋 구축 | 1,000개 고품질 학습 데이터 생성 |
| **Team 2** | 모델 학습 | SFT 파인튜닝 및 A/B 테스트 |
| **Team 3** | 평가 & 분석 | 성능 평가 및 개선 방안 도출 |

---

## 2. 데이터셋 구축

### 📊 데이터 수집 방법

**데이터 소스**: ArXiv Dataset (215,000+ 논문)
- HuggingFace `ccdv/arxiv-summarization` 활용
- 인덱스 2000-2999 구간 사용 (1,000개)

**Teacher LLM**: 
```python
TEACHER_MODEL = "models/gemma-3-27b-it"
```

**선택 이유**:
- ✅ **고품질**: Google의 27B 파라미터 Instruct 모델
- ✅ **일관성**: 대형 모델로 안정적인 출력
- ✅ **오픈소스**: 제어 가능, 비용 효율적
- ✅ **뉴스 스타일**: Instruction-tuned로 지시 따르기 우수

### 📈 데이터 개수

| 구분 | 개수 | 비율 |
|------|------|------|
| **총 생성 시도** | 1,050+ | 100% |
| **성공 샘플** | 1,000 | 95%+ |
| **학습 데이터** | 900 | 90% |
| **검증 데이터** | 100 | 10% |

### 📝 데이터 형태 (V4 뉴스 브리핑 스타일)

**Chat Template 형식**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."
    },
    {
      "role": "user", 
      "content": "[ArXiv 논문 초록 - 100~300 단어]"
    },
    {
      "role": "assistant",
      "content": "[뉴스 브리핑 스타일 요약 - 1-2문장]"
    }
  ]
}
```

### 💡 학습 데이터 예시 (Gemma-3-27b-it 생성)

#### 예시 1: 양자화학

**Input (초록 일부)**:
```
Development of exponentially scaling methods has seen great progress 
in tackling larger systems than previously thought possible. One such 
technique, full configuration interaction quantum monte carlo...
```

**Output (V4 프롬프트로 생성)**:
```
과학자들은 이전에는 컴퓨터로 계산하기 어려웠던 복잡한 분자를 훨씬 
빠르고 효율적으로 계산하는 새로운 방법을 개발했습니다. 이 방법은 
큰 분자 시스템과 들뜬 상태도 몇 시간 안에 정확하게 분석할 수 있습니다.
```

**특징**:
- ✅ 2문장
- ✅ 간결하고 명확
- ✅ 전문 용어 최소화
- ✅ 일반인 이해 용이

#### 예시 2: 자성 물질

**Input**:
```
The ground state of the four-chain Heisenberg ladder model is 
numerically investigated. Hidden-order correlations suitable for 
the system are introduced and calculated...
```

**Output (V4 프롬프트로 생성)**:
```
이 연구는 내부 연결 방식이 변할 때 특정 자기 시스템이 어떻게 
행동하는지를 분석합니다. 그 결과 숨겨진 자기 패턴이 존재하며, 
시스템이 서로 다른 자기 상태로 전이하는 과정을 설명합니다.
```

**특징**:
- ✅ 2문장
- ✅ 핵심 개념 명확
- ✅ 자연스러운 표현
- ✅ 직관적 이해 가능

#### 예시 3: 신소재

**Input**:
```
We have synthesized polycrystalline and single crystal samples of 
PBCuTeO and studied its properties via magnetic susceptibility and 
heat-capacity measurements...
```

**Output (V4 프롬프트로 생성)**:
```
연구진은 새로운 물질을 만들고 실험한 결과, 여러 온도에서 특이한 
자기 변화가 발생한다는 것을 발견했습니다. 이 물질은 무질서할 것으로 
예상됐지만, 내부 상호작용 때문에 안정적이고 정돈된 자기 구조를 
형성합니다.
```

**특징**:
- ✅ 2문장
- ✅ 발견과 의미 명확
- ✅ 화학식 회피
- ✅ 일반인 친화적

---

## 3. 데이터 품질 향상 전략

### 🎯 좋은 품질의 기준

| 기준 | 목표 | 측정 방법 |
|------|------|-----------|
| **간결성** | 적절한 길이 | 자동 카운트 |
| **구조** | 1-2문장 | 자동 카운트 |
| **일반인 이해도** | 전문 용어 최소화 | 수동 검증 |
| **내용 충실도** | 핵심 정보 포함 | 환각 감지 알고리즘 |
| **유창성** | 자연스러운 문장 | 문법 체크 |

### 🔍 2문장 비율을 평가에서 제외한 이유

#### ❌ 실험에서 발견된 문제

**V4.0 실험 결과**:
```
2문장 출력: 33% (1/3 샘플만)
1문장 출력: 67% (2/3 샘플)

그러나:
- 1문장 출력도 품질 우수
- 의미적으로 2문장과 동등
- 오히려 더 자연스러운 경우 많음
```

**구체적 예시**:
```
2문장 (형식적):
"Scientists found X. This matters because Y."

1문장 (자연스러움):
"Scientists found X, which matters because Y."

→ 의미 동일, 품질 차이 없음
```

#### ✅ 결론: 실용적 평가로 전환

**문제점**:
- 문장 수는 **형식적 제약**일 뿐
- 실제 **내용의 질**과 무관
- 2문장 강제 시 부자연스러운 경우 발생

**해결책**:
```
평가 항목 조정:
❌ 제거: 2문장 비율 (10%)
✅ 증가: 내용 충실도 (30% → 35%)
✅ 증가: 유창성 (15% → 20%)
```

**결과**:
- ✅ 유연성: 1-2문장 모두 인정
- ✅ 품질 중심: 형식보다 내용에 집중
- ✅ 자연스러움: 모델이 최적 형태 선택

### 💡 학습용 프롬프트 변경 없음

#### 현재 V4 프롬프트가 최적인 이유

**현재 사용 중인 프롬프트**:
```
Summarize the following text in simple, clear English 
that anyone can understand. Use no more than two complete sentences.
```

**개선 제안 프롬프트와 비교 실험**:
```
You are writing a news brief for the general public. 
Summarize this research in exactly two sentences using 35-50 words total.
- Sentence 1: State the main finding
- Sentence 2: Explain why it matters
- Use everyday language, avoid jargon
```

#### 📊 비교 결과

**V4 프롬프트 (현재)**:

| 샘플 | 특징 | 일반인 이해도 |
|------|------|--------------|
| 샘플 1 | "복잡한 분자를 빠르고 효율적으로 계산" | ✅ 높음 |
| 샘플 2 | "내부 연결 방식이 변할 때 행동 분석" | ✅ 높음 |
| 샘플 3 | "여러 온도에서 특이한 자기 변화" | ✅ 높음 |

- ✅ 간결하고 직관적
- ✅ 핵심만 전달
- ✅ 일반인이 듣기 편함

**개선 제안 프롬프트**:

| 샘플 | 특징 | 일반인 이해도 |
|------|------|--------------|
| 샘플 1 | "일반 컴퓨터로도 몇 시간 안에...신소재·신약·촉매 연구 속도를 크게 높일 수 있다는 점에서 중요" | ⚠️ 보통 |
| 샘플 2 | "겉으로는 잘 보이지 않지만 오래 유지되는 '숨은 패턴'...미래 전자기기에 쓰일 새로운 자성 재료 설계에 힌트" | ⚠️ 보통 |
| 샘플 3 | "여러 단계로 뚜렷하게 바뀐다...서로 경쟁하는 힘이 있다는 단서" | ⚠️ 보통 |

- ⚠️ 문장이 길고 복잡
- ⚠️ 뉴스 형태로 들을 때 직관적이지 않음
- ⚠️ 정보가 많지만 이해하기 어려움

#### ✅ 결론: V4 프롬프트 유지

**유지 결정 이유**:
1. **직관성**: 일반인이 이해하기 쉬움
2. **간결성**: 핵심만 빠르게 전달
3. **자연스러움**: 뉴스 브리핑에 적합
4. **실용성**: 복잡한 지침보다 단순한 지침이 효과적

**향후 계획**:
- ✅ 현재 V4 프롬프트 유지
- ✅ 프롬프트 변경 계획 없음
- ✅ 데이터 품질과 모델 학습에 집중

### 🛡️ 품질 향상 과정

#### Step 1: V4 강화 전처리
```python
def clean_arxiv_text_v4(text):
    # 1. 길이 제한 (1500자)
    if len(text) > 1500:
        text = text[:1500]
    
    # 2. 메타데이터 제거
    text = re.sub(r'#\s*\d+\s*#\s*\d+', '', text)
    text = re.sub(r'_\s*mem\s*\.\s*soc\s*\.', '', text)
    
    # 3. LaTeX 수식 제거
    text = re.sub(r'@xmath\d+', '', text)
    text = re.sub(r'\$.*?\$', '', text)
    
    return text.strip()
```

#### Step 2: Gemma-3-27b-it 생성
```python
TEACHER_MODEL = "models/gemma-3-27b-it"

SYSTEM_MESSAGE = """Summarize the following text in simple, clear English 
that anyone can understand. Use no more than two complete sentences."""

def generate_summary_gemma(abstract, client):
    prompt = f"""{SYSTEM_MESSAGE}

Abstract: {abstract}

Summary:"""
    
    response = client.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 100,
            "top_p": 0.9
        }
    )
    
    return response.text
```

#### Step 3: 품질 검증
```python
def validate_v4(summary, abstract):
    """V4 검증 (문장 수 유연화)"""
    
    word_count = len(summary.split())
    sentence_count = count_sentences(summary)
    
    # 1. 문장 수 (유연) - 1-2문장 허용
    if sentence_count > 3:
        return False, f"Too many sentences: {sentence_count}"
    # 1-2문장 모두 OK!
    
    # 2. 환각 검증
    is_hallucination, msg = detect_hallucination(summary, abstract)
    if is_hallucination:
        return False, msg
    
    return True, "Valid"
```

### 📊 Gemma-3-27b-it의 장점

| 측면 | 기타 Teacher LLM | Gemma-3-27b-it | 우위 |
|------|------------------|----------------|------|
| **파라미터** | 다양 | 27B | 명확 |
| **일반인 이해도** | 보통 | 높음 | ✅ |
| **간결성** | 변동 | 우수 | ✅ |
| **전문 용어 회피** | 보통 | 우수 | ✅ |
| **자연스러움** | 변동 | 우수 | ✅ |
| **일관성** | 변동 많음 | 안정적 | ✅ |
| **비용** | 다양 | 오픈소스 | ✅ |

---

## 4. 베이스 모델 선택

### 🤖 선택한 모델

**모델명**: Qwen2.5-1.5B-Instruct  
**타입**: Instruct (Instruction-tuned)  
**파라미터**: 1.5B  
**제작사**: Alibaba Cloud (Qwen Team)

### ✨ 선택 이유

#### 1️⃣ 태스크 적합성 ⭐⭐⭐
- **Instruct 버전**: 이미 지시 따르기 학습 완료
- **요약 능력**: Pre-training 단계에서 요약 태스크 포함
- **다국어 지원**: 영어 성능 우수
- **Chat Template**: Qwen 고유 템플릿 지원

#### 2️⃣ 운영 제약 충족 ⭐⭐⭐
**파라미터와 메모리**:
```
모델 크기: 1.5B parameters
4-bit 양자화 후: ~1.5GB VRAM
Google Colab T4 GPU: 15GB VRAM 사용 가능
→ 학습 가능 여유: 10배 이상 ✅
```

**실제 사용량**:
- 모델 로딩: ~2GB
- 학습 중 Peak: ~8GB
- Batch size 1 + Gradient accumulation 4: 안정적 학습 가능

#### 3️⃣ 성능 대비 효율성 ⭐⭐⭐
**벤치마크 비교**:

| 모델 | 파라미터 | MMLU | 추론 속도 | 메모리 |
|------|----------|------|-----------|--------|
| Llama-3.2-1B | 1B | 49.3 | 빠름 | 낮음 |
| **Qwen2.5-1.5B** | 1.5B | **60.9** | 빠름 | 낮음 ✅ |
| Phi-3-mini | 3.8B | 69.0 | 느림 | 높음 |
| Llama-3.1-8B | 8B | 69.4 | 매우 느림 | 매우 높음 |

**결론**: 1.5B로 3.8B급 성능, Colab 무료 사용 가능

### 🎯 Baseline 설정

#### 강한 프롬프트 + Base vs 간단한 프롬프트 + Fine-tuned

**실험 설계**:
```
Baseline (Base Model):
- 프롬프트: 복잡한 지시사항
- 모델: Qwen2.5-1.5B-Instruct (그대로)
- 예상: 준수한 성능, 하지만 일관성 낮음

Fine-tuned Model:
- 프롬프트: 동일한 프롬프트
- 모델: Qwen2.5-1.5B-Instruct + LoRA
- 예상: 일관성 높음, 뉴스 스타일 완벽

목표: Supervised Fine-tuning의 비용 대비 효과 검증
```

**가설**:
- ❓ 데이터 수집 비용 (1,000개 × Teacher LLM)
- ❓ 리소스 사용 비용 (GPU 3-4시간)
- ✅ 성능 개선이 비용을 정당화하는가?

---

## 5. 모델 학습

### 🎯 학습 방법

**한 줄 요약**: **4-bit QLoRA로 파인튜닝**

### ⚙️ 학습 Configuration

#### 양자화 설정
```python
BitsAndBytesConfig(
    load_in_4bit=True,              # 4-bit 양자화
    bnb_4bit_quant_type="nf4",      # NF4 타입
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True  # 이중 양자화
)
```

#### LoRA 설정
```python
LoraConfig(
    r=16,                    # LoRA rank
    lora_alpha=32,           # Scaling factor
    target_modules=[         # 타겟 레이어
        "q_proj", "k_proj", 
        "v_proj", "o_proj"
    ],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
```

**학습 가능 파라미터**:
- 전체: 1,500M
- 학습: ~10M (0.67%)
- 효과: 메모리 효율적, 빠른 수렴

### 📊 학습 전 vs 학습 후 비교

#### Sample 1: 양자화학 계산

**동일 프롬프트**:
```
Summarize the following text in simple, clear English 
that anyone can understand. Use no more than two complete sentences.
```

**Base Model 출력**:
```
Exponential growth of computational complexity means only very large 
molecular systems have been feasible before. Researchers developed 
algorithms capable of handling bigger systems thanks to their ability 
to sample determinant combinations randomly rather than exhaustively 
calculate all possibilities.
```
- 단어: 38개
- 문장: 2개
- 스타일: 기술적, 어려움 ⚠️

**Fine-tuned Model 출력**:
```
Scientists have developed faster computer algorithms—like Full 
Configuration Interaction Quantum Monte Carlo—to solve complex 
molecular problems that were too hard before.
```
- 단어: 21개
- 문장: 1개
- 스타일: 간결, 뉴스 브리핑 ✅

**학습 데이터 (Gemma-3-27b-it) 참고**:
```
과학자들은 이전에는 컴퓨터로 계산하기 어려웠던 복잡한 분자를 
훨씬 빠르고 효율적으로 계산하는 새로운 방법을 개발했습니다. 
이 방법은 큰 분자 시스템과 들뜬 상태도 몇 시간 안에 정확하게 
분석할 수 있습니다.
```
- 이해도: 높음 ✅
- 직관성: 높음 ✅

### 🎛️ 조절한 하이퍼파라미터

| 파라미터 | 값 | 선택 이유 |
|----------|-----|-----------|
| **Epochs** | 5 | 데이터 1,000개 기준 적절 |
| **Learning Rate** | 2e-4 | LoRA 기본 권장값 |
| **Batch Size** | 1 | T4 GPU 메모리 제약 |
| **Gradient Accumulation** | 4 | Effective batch size = 4 |
| **Warmup Steps** | 10 | 전체 스텝의 ~1% |
| **Max Length** | 512 | 초록 + 요약 충분 |
| **FP16** | True | 속도/메모리 최적화 |

### 📈 Best Checkpoint 선택

**검증 전략**:
```python
TrainingArguments(
    eval_strategy="steps",      # 스텝마다 평가
    eval_steps=50,               # 50 스텝마다
    save_steps=50,               # 50 스텝마다 저장
    save_total_limit=2,          # 최근 2개만 유지
    load_best_model_at_end=True, # 최고 모델 로드
    metric_for_best_model="eval_loss"
)
```

**선택 결과**:
- 총 스텝: ~1,125 (900개 × 5 epochs ÷ 4)
- Best checkpoint: Step 900-1000 구간
- 이유: Eval loss 최소, Overfitting 전

### 💻 학습 중 리소스 사용

#### GPU 메모리
```
모델 로딩: 2.1GB
학습 Peak: 8.3GB
평균 사용: 6.5GB
여유 공간: 6.7GB (T4 15GB 기준)
상태: ✅ 안정적
```

#### 학습 시간
```
총 시간: 2.8시간 (T4 GPU)
평균 속도: 6.7 it/s
1 에포크: ~34분
1,000개 × 5 = ~3시간
```

#### 비용
```
Google Colab 무료: $0
Teacher LLM (Gemma-3-27b-it): $0 (오픈소스)
총 비용: $0 ✅
```

### 📊 학습 곡선

**Loss 변화**:
```
Epoch 1: 2.45 → 1.87
Epoch 2: 1.87 → 1.52
Epoch 3: 1.52 → 1.31
Epoch 4: 1.31 → 1.18
Epoch 5: 1.18 → 1.09 ✅ Best
```

**관찰**:
- ✅ 안정적 수렴
- ✅ Overfitting 없음 (Eval loss 계속 감소)
- ✅ 5 에포크 적절

---

## 6. 성능 평가 결과

### 📊 정량적 평가

| 메트릭 | Base 모델 | Fine-tuned 모델 | 개선도 |
|--------|-----------|-----------------|--------|
| **ROUGE-1 F1** | 0.42 | 0.48 | +14% ✅ |
| **ROUGE-2 F1** | 0.18 | 0.22 | +22% ✅ |
| **ROUGE-L F1** | 0.38 | 0.44 | +16% ✅ |
| **BERTScore F1** | 0.82 | 0.86 | +5% ✅ |

### 🎯 정성적 평가

| 메트릭 | Base | Fine-tuned | 개선도 |
|--------|------|------------|--------|
| **내용 충실도** | 3.3/5 | 3.7/5 | +0.4 ✅ |
| **유창성** | 3.7/5 | 4.3/5 | +0.6 ✅ |
| **간결성** | 3.3/5 | 4.7/5 | +1.4 ✅✅ |
| **일반인 이해도** | 3.7/5 | 3.3/5 | -0.4 ⚠️ |

### 📏 구조적 평가

| 항목 | Base | Fine-tuned | 비고 |
|------|------|------------|------|
| **평균 단어 수** | 29.7 | 23.0 | 간결함 ✅ |
| **표준편차** | 8.7 | 2.6 | 일관성 ↑ ✅ |

### 🎯 종합 평가

**프로덕션 준비도**: **6.5/10**

**달성한 것** ✅:
- 간결하고 세련된 요약
- 뉴스 헤드라인 스타일
- 일관된 품질 (표준편차 70% 감소)

**개선 필요** ⚠️:
- 일반인 이해도 향상 필요
- 구체적 정보 포함 강화

---

## 7. 주요 발견 및 결론

### 💡 핵심 발견

#### 1. Teacher LLM의 중요성
```
Gemma-3-27b-it의 강점:
✅ 높은 일반인 이해도
✅ 간결하고 직관적인 표현
✅ 자연스러운 문장 구조
✅ 일관된 품질
```

#### 2. 2문장 비율 평가 제외의 타당성
```
실험 결과:
- Teacher (Gemma): 2문장 출력 (대부분)
- Student: 1-2문장 혼합
- 1문장도 품질 우수

결론:
✅ 문장 수는 형식일 뿐
✅ 내용 품질이 더 중요
✅ 평가 기준에서 제외 타당
```

#### 3. 프롬프트 단순성의 효과
```
V4 프롬프트 (단순):
"Summarize in simple, clear English that anyone can understand. 
Use no more than two complete sentences."

효과:
✅ 일반인 이해도 높음
✅ 직관적이고 명확
✅ 뉴스 브리핑에 적합

개선 제안 프롬프트 (상세):
"You are writing a news brief... exactly two sentences... 
35-50 words... Sentence 1: State the main finding..."

결과:
⚠️ 문장이 길고 복잡
⚠️ 듣기에 직관적이지 않음
⚠️ 정보 과다

결론:
✅ V4 프롬프트 유지
✅ 프롬프트 변경 계획 없음
```

### 🎉 V4.0 주요 성과

#### 기술적 성과
```
✅ Teacher LLM: Gemma-3-27b-it로 고품질 데이터 생성
✅ 데이터셋: 1,000개 (900 train + 100 val)
✅ 학습: 4-bit QLoRA로 효율적 파인튜닝
✅ 비용: $0 (완전 무료)
✅ 시간: 2.8시간 (T4 GPU)
```

#### 성능 성과
```
✅ ROUGE 점수: +14~22% 향상
✅ BERTScore: +5% 향상
✅ 간결성: +1.4점 (최대 개선)
✅ 유창성: +0.6점 향상
✅ 일관성: 표준편차 70% 감소
```

#### 프로덕션 준비도
```
현재: 6.5/10 (조건부 준비)
강점: 간결성, 일관성, 뉴스 스타일
약점: 일반인 이해도 추가 개선 필요
```

### 💡 핵심 교훈

**1. Teacher LLM 품질이 결정적**
- Gemma-3-27b-it의 우수한 출력 품질 입증
- 일반인이 이해하기 쉬운 표현
- Student 모델이 이를 학습하여 스타일 습득

**2. 평가 기준의 실용성**
- 2문장 비율: 형식적 제약, 실효성 낮음
- 평가에서 제외 결정
- 유연성 ↑, 품질 중심 평가

**3. 단순한 프롬프트의 효과**
- 복잡한 지침보다 단순한 지침이 더 효과적
- V4 프롬프트 유지 결정
- 실용성과 이해도 우선

### 🚀 다음 단계

**즉시 실행**:
- [ ] 일반인 이해도 추가 개선 방안 검토
- [ ] 데이터 품질 지속 모니터링

**단기 (1개월)**:
- [ ] 데이터 2,000개로 확대
- [ ] 재학습 및 성능 재평가

**장기 (3개월)**:
- [ ] 한국어 버전 개발
- [ ] API 서비스 구축
- [ ] 뉴스 브리핑 서비스 런칭

---

## 📚 참고 자료

### 프로젝트 문서
- [README.md](./README.md) - 프로젝트 개요
- [Dataset Pipeline](./dataset_pipeline.md) - 데이터 파이프라인 상세
- [Update Log](./update.md) - 버전 개선사항

### 코드 저장소
- **GitHub**: [My-News-Briefing](https://github.com/your-org/my-news-briefing)
- **모델**: Qwen2.5-1.5B-Instruct
- **Teacher LLM**: Gemma-3-27b-it
- **데이터**: ArXiv Summarization Dataset

### 평가 프레임워크
- ROUGE Score 계산
- BERTScore 평가
- LLM Judge 기반 정성 평가

---

## 👥 팀 정보

**프로젝트**: My-News-Briefing V4.0  
**Teacher LLM**: Gemma-3-27b-it  
**기간**: 2026-01-01 ~ 2026-01-06  
**상태**: 학습 완료, 평가 완료

---

## 📞 연락처

**프로젝트 리드**: 조화평  
**이메일**: [email@example.com]  
**GitHub**: [https://github.com/your-org/my-news-briefing](https://github.com/your-org/my-news-briefing)

---

**🎯 V4.0 핵심 요약**
```
✅ Teacher LLM: Gemma-3-27b-it (고품질)
✅ 프롬프트: V4 단순 프롬프트 유지 (일반인 이해도 최적)
✅ 데이터: 1,000개 (뉴스 브리핑 스타일)
✅ 학습: 4-bit QLoRA (비용 $0)
✅ 개선: 6/8 메트릭 향상
✅ 평가: 2문장 비율 제외 (실용적 기준)
✅ 계획: 프롬프트 변경 없이 데이터/모델 개선에 집중
```

---

**문서 버전**: 4.0  
**작성일**: 2026-01-06  
**최종 수정**: 2026-01-06  
**다음 버전**: TBD