# STEP 0.3 V10 → STEP 0.4 V3 개선 사항

## 📋 목차
1. [개요](#개요)
2. [주요 변경 사항](#주요-변경-사항)
3. [데이터 구조 변경](#데이터-구조-변경)
4. [학습 설정 비교](#학습-설정-비교)
5. [코드 구조 개선](#코드-구조-개선)
6. [성능 예상](#성능-예상)
7. [마이그레이션 가이드](#마이그레이션-가이드)

---

## 개요

### STEP 0.3 V10
- **목적**: GPT-4 생성 고품질 요약으로 학습
- **데이터 형식**: V1 (gpt4_summary 컬럼)
- **데이터 소스**: `v10_training_data.csv`

### STEP 0.4 V3
- **목적**: 다양한 LLM 생성 고품질 요약으로 학습
- **데이터 형식**: V3 (llm_summary 컬럼)
- **데이터 소스**: `v3_merged_all_data.csv`

---

## 주요 변경 사항

### 1. 버전 업그레이드

| 항목 | V10 | V3 |
|------|-----|-----|
| 버전명 | STEP 0.3 V10 | STEP 0.4 V3 |
| 데이터 형식 | V1 (단일 LLM) | V3 (멀티 LLM) |
| 출력 디렉토리 | `arxiv-STEP0.3-V10-FINAL` | `arxiv-STEP0.4-V3-FINAL` |

### 2. 데이터 소스 다양화

#### V10 (단일 LLM)
```python
DATA_FILE = "v10_training_data.csv"
# 오직 GPT-4만 사용
```

#### V3 (멀티 LLM)
```python
DATA_FILE = "v3_merged_all_data.csv"
# 다양한 LLM 사용:
# - Google Gemini
# - OpenAI GPT-4
# - Anthropic Claude
# 등 여러 모델의 요약 통합
```

### 3. 데이터 품질 향상

#### V10 특징
- ✅ GPT-4 단일 모델
- ✅ 일관된 스타일
- ⚠️ 단일 관점

#### V3 특징
- ✅ 다양한 LLM 모델
- ✅ 여러 관점의 요약
- ✅ 더 풍부한 학습 데이터
- ✅ 모델 편향 감소

---

## 데이터 구조 변경

### 컬럼명 매핑

| V10 (V1 형식) | V3 형식 | 설명 |
|---------------|---------|------|
| `gpt4_summary` | `llm_summary` | 요약 텍스트 |
| `gpt4_success` | `llm_success` | 성공 여부 |
| `gpt4_words` | `llm_words` | 단어 수 |
| `gpt4_sentences` | `llm_sentences` | 문장 수 |
| - | `llm_name` | LLM 이름 (신규) |
| - | `llm_model` | 모델명 (신규) |
| - | `llm_mode` | 모드 (신규) |

### V10 데이터 구조
```csv
index,original_abstract,gpt4_summary,gpt4_words,gpt4_sentences,gpt4_success
0,"Abstract text...","Summary text...",42,2,True
```

### V3 데이터 구조
```csv
index,original_abstract,llm_summary,llm_words,llm_sentences,llm_success,llm_name,llm_model,llm_mode
0,"Abstract text...","Summary text...",42,2,True,"Google Gemini","gemini-pro-latest",1
1,"Abstract text...","Summary text...",45,2,True,"OpenAI GPT-4","gpt-4o-mini",0
```

### 데이터 검증 로직

#### V10
```python
# V1 형식 확인
required_columns = ['original_abstract', 'gpt4_summary', 'gpt4_success']
df_success = df[df['gpt4_success'] == True]
```

#### V3
```python
# V3 형식 확인
required_columns = ['original_abstract', 'llm_summary', 'llm_success']

# 형식 검증 추가
if missing_columns:
    raise ValueError(f"❌ V3 형식 오류! 필요 컬럼 없음: {missing_columns}")

df_success = df[df['llm_success'] == True]
```

---

## 학습 설정 비교

### 데이터 설정

| 설정 | V10 | V3 | 비고 |
|------|-----|-----|------|
| 기본 데이터량 | 100개 (테스트) | 1000개 | V3가 10배 많음 |
| 권장 데이터량 | 1000개 | 1000개 | 동일 |
| 최대 데이터량 | 2000개 | 제한 없음 | V3가 더 유연 |
| Train/Val 비율 | 90/10 | 90/10 | 동일 |

### 학습 하이퍼파라미터

| 파라미터 | V10 | V3 | 변경 여부 |
|----------|-----|-----|-----------|
| Epochs | 5 | 5 | 동일 |
| Batch Size | 1 | 1 | 동일 |
| Gradient Accumulation | 4 | 4 | 동일 |
| Learning Rate | 2e-4 | 2e-4 | 동일 |
| Max Length | 512 | 512 | 동일 |
| LoRA r | 16 | 16 | 동일 |
| LoRA alpha | 32 | 32 | 동일 |

### 프롬프트 구조

#### V10
```python
def formatting_prompts_func_v10(example):
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": example['abstract']},
        {"role": "assistant", "content": example['gpt4_summary']}  # V1
    ]
    return {"text": tokenizer.apply_chat_template(messages, ...)}
```

#### V3
```python
def formatting_prompts_func_v3(example):
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": example['original_abstract']},  # 명시적
        {"role": "assistant", "content": example['llm_summary']}  # V3
    ]
    return {"text": tokenizer.apply_chat_template(messages, ...)}
```

---

## 코드 구조 개선

### 1. 데이터 로드 개선

#### V10
```python
# 간단한 체크
if not data_path.exists():
    raise FileNotFoundError(f"❌ 데이터 파일 없음")

df = pd.read_csv(data_path)
df_success = df[df['gpt4_success'] == True]
```

#### V3
```python
# 강화된 검증
if not data_path.exists():
    raise FileNotFoundError(f"❌ 데이터 파일 없음: {data_path}\n"
                           f"→ V3 데이터를 먼저 생성하세요!")

df = pd.read_csv(data_path)

# V3 형식 검증 추가
required_columns = ['original_abstract', 'llm_summary', 'llm_success']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"❌ V3 형식 오류! 필요 컬럼 없음: {missing_columns}\n"
                    f"   현재 컬럼: {df.columns.tolist()}\n"
                    f"→ V3 형식 데이터인지 확인하세요!")

df_success = df[df['llm_success'] == True]
```

### 2. 통계 출력 개선

#### V10
```python
print(f"📊 GPT-4 요약 통계:")
print(f"  평균 단어: {train_df['gpt4_words'].mean():.1f}")
print(f"  평균 문장: {train_df['gpt4_sentences'].mean():.1f}")
```

#### V3
```python
print(f"📊 LLM 요약 통계:")
if 'llm_words' in train_df.columns:
    print(f"  평균 단어: {train_df['llm_words'].mean():.1f}")
if 'llm_sentences' in train_df.columns:
    print(f"  평균 문장: {train_df['llm_sentences'].mean():.1f}")
if 'llm_name' in train_df.columns:
    print(f"\n  LLM 분포:")
    for llm, count in train_df['llm_name'].value_counts().items():
        print(f"    {llm}: {count}개 ({count/len(train_df)*100:.1f}%)")
```

### 3. 메타데이터 저장 개선

#### V10
```python
metadata = {
    "model": BASE_MODEL,
    "version": "V10",
    "gpt4_avg_words": float(train_df['gpt4_words'].mean()),
    "gpt4_avg_sentences": float(train_df['gpt4_sentences'].mean()),
}
```

#### V3
```python
metadata = {
    "model": BASE_MODEL,
    "version": "V3",
    "train_samples": train_samples,
    "val_samples": val_samples,
}

# 조건부 추가 (안전성 향상)
if 'llm_words' in train_df.columns:
    metadata["llm_avg_words"] = float(train_df['llm_words'].mean())
if 'llm_sentences' in train_df.columns:
    metadata["llm_avg_sentences"] = float(train_df['llm_sentences'].mean())
```

### 4. 후처리 함수

#### 공통점
- 동일한 `clean_output` 로직
- 동일한 `detect_copy` 로직
- 동일한 복사 감지 임계값

#### 차이점

**V10**
```python
def clean_output_v10(raw_text, original_article=""):
    # V10 전용 후처리
    return processed_text
```

**V3**
```python
def clean_output_v3(raw_text, original_article=""):
    # V3 전용 후처리 (동일한 로직)
    return processed_text
```

---

## 성능 예상

### V10 예상 성능
- **데이터 품질**: 9/10 (GPT-4 단일 모델)
- **다양성**: 6/10 (단일 관점)
- **일관성**: 9/10 (높음)
- **예상 점수**: 7-8/10

### V3 예상 성능
- **데이터 품질**: 8/10 (다양한 LLM)
- **다양성**: 9/10 (여러 관점)
- **일관성**: 7/10 (다소 변동)
- **예상 점수**: 7.5-8.5/10

### 장단점 비교

#### V10 장점
✅ GPT-4 고품질 요약
✅ 일관된 스타일
✅ 단순한 데이터 구조

#### V10 단점
⚠️ 단일 모델 편향
⚠️ 제한된 다양성
⚠️ GPT-4 의존성

#### V3 장점
✅ 다양한 LLM 활용
✅ 모델 편향 감소
✅ 풍부한 학습 데이터
✅ 확장 가능한 구조

#### V3 단점
⚠️ 품질 일관성 다소 낮음
⚠️ 데이터 생성 복잡
⚠️ 여러 API 키 필요

---

## 마이그레이션 가이드

### 1. 데이터 준비

#### V10 → V3 변환
```python
# V1 데이터를 V3 형식으로 변환
df_v1 = pd.read_csv("v10_training_data.csv")

# 컬럼명 변경
df_v3 = df_v1.rename(columns={
    'gpt4_summary': 'llm_summary',
    'gpt4_words': 'llm_words',
    'gpt4_sentences': 'llm_sentences',
    'gpt4_success': 'llm_success'
})

# 추가 컬럼
df_v3['llm_name'] = 'GPT-4'
df_v3['llm_model'] = 'gpt-4o-mini'
df_v3['llm_mode'] = 0

# 저장
df_v3.to_csv("v3_converted_data.csv", index=False)
```

### 2. 설정 변경

#### Step 1: 데이터 파일 변경
```python
# V10
DATA_FILE = "v10_training_data.csv"

# V3
DATA_FILE = "v3_merged_all_data.csv"
```

#### Step 2: 출력 디렉토리 변경
```python
# V10
OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V10-FINAL"

# V3
OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL"
```

#### Step 3: 데이터량 확인
```python
# V10 기본값
MAX_DATA_TO_USE = 100

# V3 권장값
MAX_DATA_TO_USE = 1000
```

### 3. 코드 실행 순서
```bash
# 1. V3 데이터 생성 (이미 완료)
✅ v3_training_data_0.csv
✅ v3_training_data_1.csv
✅ ...

# 2. V3 데이터 병합 (이미 완료)
✅ v3_merged_all_data.csv

# 3. V3 학습 코드 실행
python step_0.4_v3.py

# 4. 결과 확인
📁 /content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL/
```

### 4. 호환성 체크리스트

- [ ] V3 데이터 파일 존재 확인
- [ ] 필수 컬럼 존재 확인 (`llm_summary`, `llm_success`)
- [ ] 데이터량 설정 (최소 100개, 권장 1000개)
- [ ] GPU 메모리 확인 (최소 15GB)
- [ ] Drive 마운트 확인
- [ ] API 키 필요 없음 (학습만 진행)

---

## 결론

### V10의 가치
- ✅ GPT-4 고품질 단일 모델 학습
- ✅ 일관된 품질 보장
- ✅ 간단한 데이터 구조

### V3의 개선점
- ✅ 다양한 LLM 활용으로 편향 감소
- ✅ 더 풍부한 학습 데이터
- ✅ 확장 가능한 아키텍처
- ✅ 1000개 데이터 기본 설정

### 권장 사항

**V10 사용 시나리오:**
- GPT-4 품질이 절대적으로 중요한 경우
- 일관된 스타일이 필요한 경우
- 단순한 파이프라인 선호

**V3 사용 시나리오:**
- 다양한 요약 스타일 학습 필요
- 모델 편향 최소화 중요
- 대규모 데이터 활용 가능
- **→ 대부분의 경우 V3 권장** ⭐

---

## 참고 자료

### 파일 위치
```
/content/drive/MyDrive/SummaryDataSet/
├── v10_training_data.csv          # V10 데이터
├── v3_merged_all_data.csv         # V3 병합 데이터
├── v3_training_data_0.csv         # V3 개별 데이터
├── v3_training_data_1.csv
└── ...

/content/drive/MyDrive/
├── arxiv-STEP0.3-V10-FINAL/       # V10 모델
└── arxiv-STEP0.4-V3-FINAL/        # V3 모델
```

### 다음 단계
1. ✅ V3 데이터 생성 완료
2. ✅ V3 데이터 병합 완료
3. 🔄 V3 모델 학습 (현재)
4. ⏳ V3 모델 평가
5. ⏳ V10 vs V3 A/B 테스트

---

**작성일**: 2026-01-05  
**버전**: 1.0  
**작성자**: AI Assistant