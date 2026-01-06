# 📊 ArXiv-NewsBrief-1.5B-1k-v4.0 평가 보고서

---

## 1. 전체 점수 요약표

| 메트릭 | 베이스 모델 | Fine-tuned 모델 | 개선도 (△) |
|---|---:|---:|---:|
| **정량 평가** ||||
| ROUGE-1 F1 | 0.42 | **0.48** | **+0.06** |
| ROUGE-2 F1 | 0.18 | **0.21** | **+0.03** |
| ROUGE-L F1 | 0.39 | **0.44** | **+0.05** |
| BERTScore F1 | 0.86 | **0.89** | **+0.03** |
| **정성 평가** ||||
| 내용 충실도 (/5) | 3.7 | **3.9** | **+0.2** |
| 유창성 (/5) | 4.2 | **4.6** | **+0.4** |
| 간결성 (/5) | 3.5 | **4.4** | **+0.9** |
| 일반인 이해도 (/5) | 3.9 | **4.6** | **+0.7** |
| **구조적 평가** ||||
| 평균 단어 수 | 29.7 | **23.0** | **-6.7** |
| 2문장 비율 (%) | 67% | **33%** | **-34%p** |

---

## 2. 강점 분석

### 강점 1: 뉴스 브리핑에 최적화된 간결성
- **근거**: 평균 단어 수 감소(29.7 → 23.0), 불필요한 배경 제거
- **예시**: 결과 중심의 단문 요약으로 핵심만 전달

### 강점 2: 높은 사실 충실도 (Low Hallucination)
- **근거**: 3개 샘플 모두 허위 정보/과장 없음
- **예시**: 불확실한 세부 성과(예: excited state)는 안전하게 생략

### 강점 3: 일반인 친화적 문체
- **근거**: 전문 용어 최소화, 단순·능동 문장
- **예시**: “This research studied how magnets arrange themselves…”

---

## 3. 약점 분석

### 약점 1: 핵심 과학적 기여 축약 과도
- **문제점**: ‘무엇이 새롭다’는 남고 ‘왜 중요한가’가 사라짐
- **영향**: 전문가 독자 정보 부족
- **개선 방향**: *결과 + 구체 성과 1개* 포함 강제

### 약점 2: Target Summary와의 의미 거리
- **문제점**: 추상화 수준 과도
- **영향**: ROUGE/Alignment 정체
- **개선 방향**: Target 문장 패턴 학습 강화

### 약점 3: 물리·재료 도메인에서 성능 저하
- **문제점**: 개념 손실(특히 이론 물리)
- **영향**: 도메인 신뢰도 하락
- **개선 방향**: Physics/Materials 전용 데이터 보강

---

## 4. V4.1 개선 제안

### 4.1 데이터 측면
- **현재 문제**: 과도한 요약(정보 누락)
- **개선 방안**: 1문장에도 핵심 결과 2개 포함 샘플 추가
- **예상 효과**: Coverage 및 ROUGE-2 상승

### 4.2 프롬프트 측면
- **현재 프롬프트**  
  "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."
- **문제점**: ‘simple’이 과도한 일반화 유도
- **개선 프롬프트 제안**
```text
Summarize the following scientific text for a general news audience.
Include:
1) the main scientific contribution
2) one concrete result or implication
Use 1–2 concise sentences.
```
