# LLM-as-a-Judge 평가 시스템 설계 리포트

**프로젝트**: ArXiv-NewsBrief  
**문서 버전**: 1.0  
**작성일**: 2026-01-09  
**목적**: TTS 뉴스 브리핑용 과학 논문 요약 평가 시스템 설계

---

## 📋 목차

1. [배경 및 문제 인식](#1-배경-및-문제-인식)
2. [평가 시스템 설계 원칙](#2-평가-시스템-설계-원칙)
3. [100점 체계 전환 근거](#3-100점-체계-전환-근거)
4. [형식-내용 분리 전략](#4-형식-내용-분리-전략)
5. [평가 스키마 상세 설명](#5-평가-스키마-상세-설명)
6. [버전 비교 분리 전략](#6-버전-비교-분리-전략)
7. [모델 진화 과정: v4.0 → v4.2](#7-모델-진화-과정-v40--v42)
8. [구현 가이드](#8-구현-가이드)

---

## 1. 배경 및 문제 인식

### 1.1 기존 평가 방식의 한계

#### 문제 1: 10점 척도의 해상도 부족
```
10점 척도 예시:
- Sample A: 7/10 (70%)
- Sample B: 7/10 (70%)

실제 품질 차이:
- Sample A: 형식 완벽(100%), 내용 보통(40%) → 평균 70%
- Sample B: 형식 부족(40%), 내용 우수(100%) → 평균 70%

문제: 같은 점수이지만 개선 방향이 완전히 다름!
```

**의사결정 영향**:
- 7점 vs 8점 차이가 실제 10%인지 30%인지 불명확
- 개선 우선순위 판단 불가
- A/B 테스트 시 통계적 유의성 검증 어려움

#### 문제 2: 버전 비교의 컨텍스트 의존성
```yaml
V9 프롬프트에 포함:
  "V8 대비 개선도 평가"
  "V7 템플릿 변경 효과 분석"
  
문제점:
  - LLM이 V7, V8 결과를 기억해야 함
  - 컨텍스트 길이 증가 (토큰 낭비)
  - 평가 일관성 저하 (이전 버전 정보 변동 시)
  - 새로운 LLM으로 재평가 시 불가능
```

**실제 사례**:
```
V8 평가 시: "V7 대비 10% 개선"
V9 평가 시: "V8 대비 5% 개선"

문제: V7 평가 기준이 달랐다면?
→ V9의 "절대적" 품질을 알 수 없음
```

#### 문제 3: 형식과 내용의 혼재
```
기존 평가 항목:
- 명확성 (30점)
- 전문성 (25점)
- TTS 친화성 (25점)
- 길이 준수 (20점)

문제:
- "길이 준수"는 자동 측정 가능 (문자 수 세기)
- LLM이 판단할 필요 없음
- LLM 판단 비용 낭비
```

---

## 2. 평가 시스템 설계 원칙

### 2.1 핵심 설계 철학

#### 원칙 1: Separation of Concerns (관심사 분리)
```
형식 평가 (Code-based)
├─ 측정 가능한 객관적 지표
├─ 규칙 기반 자동 산출
└─ 빠르고 일관된 평가

내용 평가 (LLM-based)
├─ 의미론적 판단 필요
├─ 인간의 전문성 모방
└─ 고비용이지만 필수적
```

**장점**:
- LLM 비용 50% 절감 (형식 평가 제외)
- 평가 속도 3배 향상
- 일관성 증가 (형식은 100% 재현)

#### 원칙 2: Absolute Evaluation (절대 평가)
```
각 샘플 독립적으로 평가
→ 이전 버전과 무관
→ 언제든 재평가 가능
→ 다른 LLM으로도 평가 가능
```

#### 원칙 3: Actionable Metrics (실행 가능한 지표)
```
Bad: "전반적으로 좋음" (7/10)
Good: "형식 95/100, 내용 65/100
      → 내용 품질 개선 필요
      → 구체적으로: 핵심 결과 누락"
```

---

## 3. 100점 체계 전환 근거

### 3.1 해상도 비교

#### 10점 척도의 문제
```
가능한 점수: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
실제 사용: 5, 6, 7, 8, 9 (극단값 회피 경향)

유효 해상도: 5단계
→ 샘플 간 미세한 차이 구분 불가
```

#### 100점 척도의 장점
```
가능한 점수: 1-100
실제 사용: 40-95 (극단값 회피해도 55단계)

유효 해상도: 55단계
→ 샘플 간 미세한 차이 포착 가능
```

### 3.2 통계적 검증력

#### A/B 테스트 시나리오
```python
# 10점 척도
model_a_scores = [7, 7, 8, 7, 8]  # 평균 7.4
model_b_scores = [7, 8, 7, 8, 8]  # 평균 7.6

차이: 0.2점 (2.7%)
→ 통계적 유의성 검증 어려움 (p > 0.05)

# 100점 척도
model_a_scores = [72, 68, 75, 70, 74]  # 평균 71.8
model_b_scores = [78, 80, 76, 79, 77]  # 평균 78.0

차이: 6.2점 (8.6%)
→ 통계적 유의성 검증 가능 (p < 0.01)
```

### 3.3 실무 의사결정 개선

#### 시나리오: 프로덕션 배포 결정
```yaml
10점 척도:
  평균 점수: 7.2/10 (72%)
  판단: "괜찮은데... 배포할까?"
  문제: 구체적 개선점 불명확

100점 척도:
  형식 점수: 88/100
  내용 점수: 56/100
  판단: "형식은 우수, 내용 개선 후 배포"
  조치: 내용 품질 집중 개선
```

---

## 4. 형식-내용 분리 전략

### 4.1 형식 평가 (50점) - Code-based

#### 평가 항목 및 배점

| 항목 | 배점 | 측정 방법 | 통과 기준 |
|------|------|-----------|----------|
| **문장 수 준수** | 20점 | `len(re.split(r'[.!?]+', text))` | 정확히 2문장 |
| **단어 수 제한** | 15점 | `len(text.split())` | 30-45단어 |
| **특수문자 누출** | 10점 | Regex 패턴 매칭 | `<\|im_start\|>`, `###` 등 0개 |
| **프롬프트 누출** | 5점 | 키워드 검색 | "summarize", "system" 등 0개 |

#### 채점 알고리즘 (Python)

```python
def evaluate_format(summary: str) -> dict:
    """
    형식 평가 (50점 만점)
    
    Returns:
        {
            'total': int (0-50),
            'breakdown': {
                'sentence_count': int (0-20),
                'word_count': int (0-15),
                'special_chars': int (0-10),
                'prompt_leakage': int (0-5)
            },
            'details': dict
        }
    """
    score = 0
    breakdown = {}
    details = {}
    
    # 1. 문장 수 (20점)
    sentences = [s.strip() for s in re.split(r'[.!?]+', summary) if s.strip()]
    sentence_count = len(sentences)
    
    if sentence_count == 2:
        breakdown['sentence_count'] = 20
        details['sentence_count'] = "✅ 정확히 2문장"
    elif sentence_count == 1:
        breakdown['sentence_count'] = 10
        details['sentence_count'] = "⚠️ 1문장 (목표: 2문장)"
    elif sentence_count == 3:
        breakdown['sentence_count'] = 15
        details['sentence_count'] = "⚠️ 3문장 (목표: 2문장)"
    else:
        breakdown['sentence_count'] = 0
        details['sentence_count'] = f"❌ {sentence_count}문장 (목표: 2문장)"
    
    # 2. 단어 수 (15점)
    word_count = len(summary.split())
    
    if 30 <= word_count <= 45:
        breakdown['word_count'] = 15
        details['word_count'] = f"✅ {word_count}단어 (이상적)"
    elif 25 <= word_count < 30 or 45 < word_count <= 50:
        breakdown['word_count'] = 10
        details['word_count'] = f"⚠️ {word_count}단어 (허용 범위)"
    elif 20 <= word_count < 25 or 50 < word_count <= 55:
        breakdown['word_count'] = 5
        details['word_count'] = f"⚠️ {word_count}단어 (개선 필요)"
    else:
        breakdown['word_count'] = 0
        details['word_count'] = f"❌ {word_count}단어 (부적합)"
    
    # 3. 특수문자 (10점)
    special_patterns = [
        r'<\|im_start\|>',
        r'<\|im_end\|>',
        r'###',
        r'```',
        r'\*\*\*',
        r'---',
    ]
    
    found_specials = []
    for pattern in special_patterns:
        if re.search(pattern, summary):
            found_specials.append(pattern)
    
    if not found_specials:
        breakdown['special_chars'] = 10
        details['special_chars'] = "✅ 특수문자 없음"
    else:
        breakdown['special_chars'] = max(0, 10 - len(found_specials) * 3)
        details['special_chars'] = f"❌ 발견: {', '.join(found_specials)}"
    
    # 4. 프롬프트 누출 (5점)
    prompt_keywords = [
        'summarize', 'summary', 'brief', 'system', 'user', 'assistant',
        'prompt', 'instruction', 'following text'
    ]
    
    found_keywords = [kw for kw in prompt_keywords if kw.lower() in summary.lower()]
    
    if not found_keywords:
        breakdown['prompt_leakage'] = 5
        details['prompt_leakage'] = "✅ 프롬프트 누출 없음"
    else:
        breakdown['prompt_leakage'] = 0
        details['prompt_leakage'] = f"❌ 발견: {', '.join(found_keywords)}"
    
    # 총점 계산
    total = sum(breakdown.values())
    
    return {
        'total': total,
        'breakdown': breakdown,
        'details': details
    }
```

#### 출력 예시
```json
{
  "total": 45,
  "breakdown": {
    "sentence_count": 20,
    "word_count": 10,
    "special_chars": 10,
    "prompt_leakage": 5
  },
  "details": {
    "sentence_count": "✅ 정확히 2문장",
    "word_count": "⚠️ 48단어 (허용 범위)",
    "special_chars": "✅ 특수문자 없음",
    "prompt_leakage": "✅ 프롬프트 누출 없음"
  }
}
```

### 4.2 내용 평가 (50점) - LLM-based

#### 평가 항목 및 배점

| 항목 | 배점 | 평가 대상 | 핵심 질문 |
|------|------|-----------|----------|
| **핵심 기여도 포함** | 20점 | 논문의 주요 발견/기여 | "논문의 핵심 결과가 포함되었는가?" |
| **초록 대비 정확성** | 15점 | 사실관계 정확성 | "초록 내용과 일치하는가? 환각은 없는가?" |
| **일반인 명료성** | 10점 | 이해 난이도 | "과학 배경 없이 이해 가능한가?" |
| **TTS 자연스러움** | 5점 | 구어체 적합성 | "읽었을 때 자연스러운가?" |

**총 50점** (형식 50점 + 내용 50점 = **100점 만점**)

---

## 5. 평가 스키마 상세 설명

### 5.1 LLM-as-a-Judge 프롬프트 설계

#### System Prompt

```markdown
# Scientific Summary Evaluator for TTS News Briefing

You are an expert evaluator for AI-generated scientific summaries.

## Your Role
- Science communication expert
- Academic paper reviewer
- TTS news script editor

## Evaluation Focus
Evaluate ONLY the **content quality** of summaries.
Format aspects (sentence count, word count, special characters) 
are handled separately by automated scripts.

## Scoring Scale
- Total: 50 points (content only)
- Be precise: use full range (0-50)
- Avoid clustering around 35-40

## Evaluation Criteria (50 points)

###