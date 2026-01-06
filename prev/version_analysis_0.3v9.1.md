# V9.1 A/B 테스트 결과 상세 분석

## 📊 총평

**결론: V9.1은 V9보다 크게 개선되었으나, 여전히 목표에 미달합니다.**

---

## 🎯 형식 준수 분석

### Test 1

| 모델 | 출력 | 문장 수 | 단어 수 | 형식 점수 |
|------|------|---------|---------|-----------|
| **베이스** | "our study confirms previous results on irac colors and sizes from recent survey data using both ground-based telescopes and space observatories like wfcam, speclensat, faradis, cfa-8m, ftsr16, harpsn, gta12, nircollima, ndsirp, nsiai, ngasim,." | 1문장 | 33 | ❌ 1/10 |
| **V9.1 FT** | "]) and pipe nebulosity does indeed seem inconsistent with our model ( figs. {fig:msflimit_orion } and { fig:msfringpipe_nebula })." | 1문장 | 19 | ❌ 2/10 |

**문제점:**
- ❌ 2문장 요구사항 미충족 (둘 다 1문장)
- ✅ 45단어 이하 충족 (33, 19)
- ❌ 베이스: 문장 끝이 쉼표로 끝남 (비정상)
- ❌ V9.1: 괄호와 LaTeX 코드로 시작 (비정상)

---

### Test 2

| 모델 | 출력 | 문장 수 | 단어 수 | 형식 점수 |
|------|------|---------|---------|-----------|
| **베이스** | "could possibly help achieve faster processing times by using multiple input channels simultaneously rather than relying solely upon spike channeling alone ." | 1문장 | 22 | ❌ 3/10 |
| **V9.1 FT** | "can also help in simulating cognitive processes which require shortterm adaptation including perception , decision making , attention control , motor planning , visual tracking & object detection among others ." | 1문장 | 31 | ❌ 3/10 |

**문제점:**
- ❌ 2문장 요구사항 미충족 (둘 다 1문장)
- ✅ 45단어 이하 충족 (22, 31)
- ❌ 소문자로 시작 (주어 없음)
- ❌ 문장이 불완전함

---

### Test 3

| 모델 | 출력 | 문장 수 | 단어 수 | 형식 점수 |
|------|------|---------|---------|-----------|
| **베이스** | "this suggests that these sources can emit significant amounts of gamma rays ; however, no evidence has yet been obtained ." | 1문장 | 21 | ❌ 4/10 |
| **V9.1 FT** | "to that of an unobscured quasar . therefore this object seems promising for studying rl - ng1s through its intrinsic properties such as optical spectrum ." | 2문장 | 26 | ⚠️ 5/10 |

**문제점:**
- ✅ V9.1: 2문장 충족!
- ✅ 45단어 이하 충족 (21, 26)
- ❌ 베이스: 세미콜론 사용 (2문장 아님)
- ⚠️ V9.1: 첫 문장이 "to that of"로 시작 (불완전)

---

### 형식 종합

| 항목 | 목표 | 베이스 평균 | V9.1 평균 | 개선 |
|------|------|-------------|-----------|------|
| **문장 수** | 2문장 | 1.0문장 | 1.3문장 | +0.3 |
| **단어 수** | ≤45 | 25.3 | 25.3 | 동일 |
| **2문장 비율** | 100% | 0% (0/3) | 33% (1/3) | +33%p |
| **45단어 비율** | 100% | 100% (3/3) | 100% (3/3) | 동일 |
| **완전한 문장** | 100% | 33% (1/3) | 33% (1/3) | 동일 |

**결론:** V9.1이 베이스보다 약간 나아졌으나, 여전히 2문장 요구사항을 크게 미충족합니다.

---

## 💡 내용 품질 분석

### Test 1: IRDCs (적외선 암흑 구름)

**원본 초록 핵심:**
- IRDCs의 대규모 별 형성 능력 평가
- 질량-크기 임계값 기준으로 구분
- 대부분 IRDCs는 임계값 미달 (대규모 별 형성 불가)

---

**베이스 모델:**
```
"our study confirms previous results on irac colors and sizes from recent survey data using both ground-based telescopes and space observatories like wfcam, speclensat, faradis, cfa-8m, ftsr16, harpsn, gta12, nircollima, ndsirp, nsiai, ngasim,."
```

**분석:**
- ❌ 논문과 무관한 내용 (망원경 이름 나열)
- ❌ 핵심 내용 누락 (IRDCs, 별 형성, 임계값)
- ❌ 의미 없는 약어들 (speclensat, faradis 등 - 존재하지 않는 망원경)
- ❌ 완전 실패

**내용 점수: 0/10** (환각)

---

**V9.1 파인튜닝:**
```
"]) and pipe nebulosity does indeed seem inconsistent with our model ( figs. {fig:msflimit_orion } and { fig:msfringpipe_nebula })."
```

**분석:**
- ⚠️ 일부 관련 내용 (pipe nebula는 논문에 언급됨)
- ❌ 괄호로 시작 (문장 조각)
- ❌ LaTeX 코드 그대로 출력
- ❌ 핵심 결론 누락
- ⚠️ 약간의 관련성은 있으나 매우 불완전

**내용 점수: 2/10** (불완전한 조각)

---

### Test 2: MTJ Synapse (자기 터널 접합 시냅스)

**원본 초록 핵심:**
- MTJ의 자화 동역학이 생물학적 시냅스와 유사
- 단기 가소성(STP)과 장기 강화(LTP) 구현
- 자극 빈도가 핵심 역할

---

**베이스 모델:**
```
"could possibly help achieve faster processing times by using multiple input channels simultaneously rather than relying solely upon spike channeling alone ."
```

**분석:**
- ⚠️ "faster processing" - 일반적 관련성
- ❌ MTJ, 시냅스, STP/LTP 언급 없음
- ❌ 핵심 기여 누락
- ❌ 너무 추상적

**내용 점수: 1/10** (관련성 희박)

---

**V9.1 파인튜닝:**
```
"can also help in simulating cognitive processes which require shortterm adaptation including perception , decision making , attention control , motor planning , visual tracking & object detection among others ."
```

**분석:**
- ⚠️ "cognitive processes" - 신경형 컴퓨팅과 관련
- ⚠️ "shortterm adaptation" - 단기 가소성과 유사
- ❌ MTJ, 시냅스 메커니즘 미언급
- ❌ 핵심 기술 내용 누락
- ⚠️ 응용 분야만 언급, 기술 자체는 미언급

**내용 점수: 3/10** (관련 있으나 핵심 누락)

---

### Test 3: RL-NLS1 Galaxy (전파 큰 협선 세이퍼트 1형 은하)

**원본 초록 핵심:**
- SDSSJ094857.3+002225의 intranight 광학 변동성 발견
- B, R 밴드에서 수 시간 내 0.5 mag 변동
- 상대론적 제트 존재 증거

---

**베이스 모델:**
```
"this suggests that these sources can emit significant amounts of gamma rays ; however, no evidence has yet been obtained ."
```

**분석:**
- ⚠️ "gamma rays" - 고에너지 천문학 관련
- ⚠️ 일부 관련성 (Fermi 위성 관측)
- ❌ 광학 변동성, 제트 미언급
- ❌ 핵심 발견 누락

**내용 점수: 2/10** (약한 관련성)

---

**V9.1 파인튜닝:**
```
"to that of an unobscured quasar . therefore this object seems promising for studying rl - ng1s through its intrinsic properties such as optical spectrum ."
```

**분석:**
- ✅ "quasar" - 관련 천체
- ✅ "rl-ng1s" (rl-nls1s의 오타) - 정확한 대상!
- ✅ "optical spectrum" - 광학 관측 언급
- ⚠️ "promising for studying" - 일부 맥락 있음
- ❌ 핵심 발견(intranight variability, 제트) 누락
- ❌ 첫 문장이 불완전 ("to that of"로 시작)

**내용 점수: 5/10** (관련성 높으나 불완전)

---

### 내용 종합

| Test | 논문 주제 | 베이스 점수 | V9.1 점수 | 차이 |
|------|----------|-------------|-----------|------|
| 1 | IRDCs | 0/10 (환각) | 2/10 (조각) | +2 |
| 2 | MTJ Synapse | 1/10 (희박) | 3/10 (누락) | +2 |
| 3 | RL-NLS1 | 2/10 (약함) | 5/10 (불완전) | +3 |
| **평균** | - | **1.0/10** | **3.3/10** | **+2.3** |

**결론:** V9.1이 베이스보다 내용 품질이 2.3점 향상되었으나, 여전히 목표(7-8점)에 크게 미달합니다.

---

## 🔍 V9 vs V9.1 비교

### V9 결과 (이전 테스트)

```
Test 1 FT: ") with k = h / cm s^(-1) ."
Test 2 FT: "modifications following shortterm stimulation..."
Test 3 FT: "ed as an rllagga source..."
```

**특징:**
- 괄호/불완전 단어로 시작
- 의미 없는 조각
- 품질: 0-1/10

---

### V9.1 결과 (현재 테스트)

```
Test 1 FT: "]) and pipe nebulosity does indeed seem inconsistent..."
Test 2 FT: "can also help in simulating cognitive processes..."
Test 3 FT: "to that of an unobscured quasar . therefore this object..."
```

**특징:**
- 여전히 불완전하지만 더 긴 문장
- 일부 관련 내용 포함
- 품질: 2-5/10

---

### V9 → V9.1 개선 효과

| 지표 | V9 | V9.1 | 개선 |
|------|----|----|------|
| **평균 단어 수** | 9-16 | 19-31 | +10~15 단어 |
| **문장 완성도** | 조각 | 불완전한 문장 | ⚠️ 개선 |
| **내용 관련성** | 없음 | 약함~중간 | ✅ 개선 |
| **평균 점수** | 0.5/10 | 3.3/10 | **+2.8점** |
| **형식(2문장)** | 0% | 33% | +33%p |

**결론:** V9.1이 V9보다 크게 개선되었으나, 실용 수준에는 미달합니다.

---

## 🎯 V9.1 개선사항 효과 분석

### System Message 간결화

**V9:**
```
"You are a research paper summarization expert. Summarize papers concisely and accurately in exactly 2 sentences, maximum 45 words. Focus on the main contribution and key results."
```
→ 50단어, 장황

**V9.1:**
```
"You are a research paper summarization expert. Always respond with exactly 2 sentences, maximum 45 words."
```
→ 20단어, 간결

**효과:**
- ✅ 중복 제거
- ✅ 명확성 향상
- ⚠️ 실제 성능: 2문장 33% (목표 100%)

---

### User 프롬프트 제거

**V9:**
```python
{"role": "user", "content": "Summarize this paper in 2 sentences (max 45 words):\n\n{article}"}
```

**V9.1:**
```python
{"role": "user", "content": article}  # 논문만!
```

**효과:**
- ✅ 중복 지시사항 제거
- ✅ 프롬프트 간결화
- ⚠️ 실제 성능: 여전히 불완전

---

### 개선사항 평가

| 개선사항 | 이론적 효과 | 실제 효과 | 평가 |
|----------|-------------|-----------|------|
| System 간결화 | 혼란 감소 | 약간 개선 | ⚠️ |
| User 프롬프트 제거 | 중복 제거 | 약간 개선 | ⚠️ |
| 전체 최적화 | 성능 향상 | 미미한 개선 | ❌ |

**결론:** 개선사항이 이론적으로는 올바르나, 실제 성능 향상은 미미합니다.

---

## 🔬 근본 원인 분석

### 왜 V9.1도 실패했는가?

#### 1. 학습 데이터 문제 ⭐⭐⭐

**가설:** ArXiv 초록이 2문장이 아님

```python
# 실제 ArXiv 초록 예시
"we present a new assessment... (40 words)
this is done by comparison... (35 words)
we establish as a novel... (30 words)
many irdcs, if not most... (25 words)
..." 
```
→ 4-6문장, 총 100-150 단어!

**문제:**
- 모델이 학습한 데이터: 다문장 초록
- 요구사항: 2문장, 45단어
- 결과: 모델이 학습과 다른 형식 요구받음

---

#### 2. 학습 방법 문제 ⭐⭐

**현재 방식:**
```python
# 전체 초록을 타겟으로
{"role": "assistant", "content": full_abstract}  # 100단어
```

**필요한 방식:**
```python
# 2문장 45단어 요약을 타겟으로
{"role": "assistant", "content": two_sentence_summary}  # 45단어
```

**문제:** 학습 데이터와 출력 요구사항 불일치!

---

#### 3. 프롬프트 문제 ⭐

**System Message가 무시됨:**
```
System: "Always respond with exactly 2 sentences, maximum 45 words."
모델: "음... 학습 때는 6문장 쓰라고 배웠는데? 무시하자"
```

**이유:**
- System message는 "힌트"일 뿐
- 실제 학습 데이터가 더 강력함
- 모델은 학습 패턴을 따름

---

#### 4. 모델 크기 문제 ⭐

**Qwen2.5-1.5B:**
- 너무 작아서 복잡한 지시 이해 어려움
- Instruction following 능력 제한적
- 200개 데이터로는 부족

---

## 📊 최종 점수

### Test 1 (IRDCs)

| 모델 | 형식 | 내용 | 복사 | 총점 |
|------|------|------|------|------|
| 베이스 | 1/10 | 0/10 | ✅ | **0.5/10** |
| V9.1 FT | 2/10 | 2/10 | ✅ | **2/10** |

---

### Test 2 (MTJ Synapse)

| 모델 | 형식 | 내용 | 복사 | 총점 |
|------|------|------|------|------|
| 베이스 | 3/10 | 1/10 | ✅ | **2/10** |
| V9.1 FT | 3/10 | 3/10 | ✅ | **3/10** |

---

### Test 3 (RL-NLS1)

| 모델 | 형식 | 내용 | 복사 | 총점 |
|------|------|------|------|------|
| 베이스 | 4/10 | 2/10 | ✅ | **3/10** |
| V9.1 FT | 5/10 | 5/10 | ✅ | **5/10** |

---

### 전체 평균

| 모델 | 평균 점수 |
|------|-----------|
| 베이스 | **1.8/10** |
| V9.1 FT | **3.3/10** |
| **개선** | **+1.5점** |

---

## 💡 권장 조치

### 즉시 조치 (V10)

#### Option 1: 학습 데이터 수정 ⭐⭐⭐ 권장!

```python
# GPT-4로 ArXiv 초록을 2문장으로 요약
original_abstract = "we present... (150 words)"
two_sentence = gpt4_summarize(original_abstract, max_words=45)

# 이것으로 학습!
{"role": "assistant", "content": two_sentence}
```

**장점:**
- 학습 데이터 = 출력 요구사항
- 모델이 올바른 형식 학습
- 성공 가능성 높음

---

#### Option 2: 더 큰 모델 ⭐⭐

```python
BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"  # 1.5B → 7B
```

**장점:**
- Instruction following 능력 향상
- System message 이해 가능
- 복잡한 요구사항 처리

**단점:**
- 추론 속도 느림
- 메모리 많이 필요

---

#### Option 3: Few-shot 학습 ⭐

```python
messages = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    
    # Example 1
    {"role": "user", "content": "{논문1}"},
    {"role": "assistant", "content": "{2문장 요약1}"},
    
    # Example 2
    {"role": "user", "content": "{논문2}"},
    {"role": "assistant", "content": "{2문장 요약2}"},
    
    # Actual
    {"role": "user", "content": article}
]
```

**장점:**
- 명확한 예시 제공
- 형식 학습 강화

**단점:**
- 프롬프트 매우 길어짐

---

#### Option 4: 후처리 강화 ⭐

```python
def post_process_to_two_sentences(text):
    # 1. 모든 문장 추출
    sentences = split_sentences(text)
    
    # 2. 가장 중요한 2문장 선택 (TF-IDF)
    top_2 = select_top_k_sentences(sentences, k=2)
    
    # 3. 45단어로 압축
    summary = truncate_to_45_words(top_2)
    
    return summary
```

**장점:**
- 즉시 적용 가능
- 추가 학습 불필요

**단점:**
- 품질 보장 어려움

---

### V10 최종 권장안

```python
# 1단계: 학습 데이터 생성 (GPT-4)
train_data = []
for paper in arxiv_papers:
    two_sent = gpt4.summarize(
        paper['abstract'],
        instruction="Summarize in exactly 2 sentences, max 45 words"
    )
    train_data.append({
        "article": paper['article'],
        "summary": two_sent  # 2문장 45단어!
    })

# 2단계: V10 학습
SYSTEM_MESSAGE = "You are a research paper summarization expert. Always respond with exactly 2 sentences, maximum 45 words."

messages = [
    {"role": "system", "content": SYSTEM_MESSAGE},
    {"role": "user", "content": article},
    {"role": "assistant", "content": two_sent}  # ⭐ 핵심!
]

# 3단계: Few-shot 추가 (선택)
# 4단계: 후처리 강화 (보험)
```

---

## 📈 예상 결과

### V9.1 → V10

| 지표 | V9.1 | V10 (예상) | 개선 |
|------|------|------------|------|
| 평균 점수 | 3.3/10 | **7-8/10** | +4점 |
| 2문장 비율 | 33% | **90%** | +57%p |
| 내용 품질 | 3.3/10 | **7/10** | +3.7점 |
| 실용성 | ❌ | ✅ | 성공 |

---

## 🎯 결론

### V9.1 평가

**긍정적:**
- ✅ V9보다 1.5점 향상
- ✅ Chat template 최적화 효과 있음
- ✅ 복사 감지 정상 작동
- ✅ 개선 방향 올바름

**부정적:**
- ❌ 목표(7-8/10)에 크게 미달
- ❌ 2문장 요구사항 대부분 실패
- ❌ 실용성 없음
- ❌ 근본 문제 미해결

---

### 근본 원인

```
1. 학습 데이터 ≠ 출력 요구사항
   ArXiv 초록 (6문장, 150단어) ≠ 목표 (2문장, 45단어)

2. 모델 크기 부족
   1.5B는 복잡한 instruction following 어려움

3. 프롬프트만으로는 한계
   System message < 학습 데이터의 패턴
```

---

### V10 권장 방향

```
⭐⭐⭐ 필수: 학습 데이터를 2문장 45단어로 재구성
⭐⭐ 권장: 7B 모델 사용
⭐ 선택: Few-shot 예시 추가

예상 성능: 7-8/10 (실용 가능)
```

---

**Peace님, V9.1은 개선되었으나 아직 부족합니다.**

**V10에서 학습 데이터를 반드시 수정해야 합니다!** 🎯