# TTS 뉴스 브리핑 평가 결과 (재평가)

**평가 모델**: ArXiv-NewsBrief-1.5B-1k-v4.2  
**평가 샘플**: 3개  
**평가 관점**: 일반 청중 대상 TTS 뉴스 브리핑 (출퇴근길에 들을 수 있는 수준)

---

## 🎙️ 개별 평가 (TTS 관점)

### Sample 1: 광학 장치 내 빛의 움직임 연구

**생성된 요약**:
> This research details how changes in light waves affect the movement and characteristics of tiny structures called domain walls within a specific optical setup. By studying this relationship, scientists were able to measure the direction (chirality) of these movements using visible light signals.

#### 점수: ⭐⭐⭐⭐ (4/5)

**✅ Clarity for General Audience (9/10)**
- "tiny structures called domain walls" - 훌륭한 설명 방식
- "changes in light waves" - 이해 가능한 표현
- 전반적으로 과학 배경 없어도 이해 가능
- **단 하나의 문제**: "chirality" - 괄호 안에 있어도 설명 없음

**✅ TTS Script Quality (9/10)**
- 문장 흐름 자연스러움
- 읽었을 때: "This research details... tiny structures called domain walls... optical setup."
- 호흡 구간 적절, 리듬감 좋음
- "within a specific optical setup" - 약간 서면체지만 허용 가능

**✅ Professional Tone (9/10)**
- NPR Science Friday 스타일에 근접
- 권위 있지만 접근 가능한 톤
- 과하지 않은 전문성

**✅ Length Compliance (8/10)**
- ✅ 정확히 2문장
- ✅ 단어 수: 44단어 (이상적 범위 내)
- 첫 문장이 약간 긴 편 (26단어)

**주요 문제점**:
- "chirality" 용어가 설명 없이 등장 (일반인은 모름)

**개선안**:
> This research details how changes in light waves affect the movement and characteristics of tiny structures called domain walls within a specific optical setup. By studying this relationship, scientists were able to measure the rotation direction of these movements using visible light signals.

("chirality" → "rotation direction"으로 대체)

---

### Sample 2: 입자 상호작용 모델링 연구

**생성된 요약**:
> This research explores how particles called mesons interact with each other using mathematical tools called form factors. The study presents two different ways to model these interactions and demonstrates their usefulness in calculations involving mesons and their associated particles.

#### 점수: ⭐⭐⭐⭐½ (4.5/5)

**✅ Clarity for General Audience (10/10)**
- "particles called mesons" - 완벽한 도입
- "mathematical tools" - 구체적이면서 이해 가능
- "form factors" - 약간 전문적이지만 "mathematical tools"로 맥락 제공
- **전문용어 최소화**: Non-local Lagrangians 같은 어려운 용어 생략 (TTS 관점에서는 오히려 장점!)

**✅ TTS Script Quality (10/10)**
- 매우 자연스러운 뉴스 스크립트
- 읽기 쉬운 리듬: "explores... interact... using mathematical tools"
- 문장 간 연결 부드러움
- 아나운서가 편하게 읽을 수 있는 구조

**✅ Professional Tone (10/10)**
- 완벽한 뉴스 브리핑 톤
- "explores", "demonstrates their usefulness" - 전문적이지만 접근 가능
- 과도한 단순화 없음

**✅ Length Compliance (9/10)**
- ✅ 정확히 2문장
- ✅ 단어 수: 41단어 (완벽)
- 문장 길이 균형 잘 맞음 (19 + 22)

**주요 문제점**:
- 거의 없음! 가장 TTS 친화적인 샘플

**미세 개선 여지**:
- "form factors" 대신 "mathematical formulas" 고려 가능 (더 일반적)
- 하지만 현재 상태도 충분히 우수

---

### Sample 3: 우주의 물질 생성 연구

**생성된 요약**:
> This research explores how the universe initially created matter by studying a specific theoretical process called electroweak baryogenesis. Researchers analyze existing theories to clarify their predictions and align them with experimental possibilities, focusing on scenarios involving supersymmetry and a precise Higgs particle mass.

#### 점수: ⭐⭐⭐ (3/5)

**⚠️ Clarity for General Audience (5/10)**
- ✅ "how the universe initially created matter" - 훌륭한 시작!
- ❌ "electroweak baryogenesis" - 설명 없는 전문용어 (일반인 이해 불가)
- ❌ "supersymmetry" - 괄호에 있어도 설명 없음
- ❌ "Higgs particle mass" - 과학 뉴스 팔로우하는 사람만 이해
- **문제**: 첫 문장 후 급격히 전문화됨

**⚠️ TTS Script Quality (6/10)**
- 첫 문장: 자연스러움
- 두 번째 문장: 너무 복잡하고 길음 (30단어!)
- "to clarify their predictions and align them with experimental possibilities, focusing on..." - 읽기 힘든 구조
- 호흡 부족, 리듬 끊김

**✅ Professional Tone (8/10)**
- 권위 있는 톤은 유지
- 너무 학술적으로 치우침

**⚠️ Length Compliance (7/10)**
- ✅ 정확히 2문장
- ⚠️ 단어 수: 51단어 (이상적 범위 초과)
- 두 번째 문장이 과도하게 김

**주요 문제점**:
1. "electroweak baryogenesis" 일반인 이해 불가
2. 두 번째 문장 너무 복잡 (3개 절 연결)
3. 전문용어 과다 (supersymmetry, Higgs)

**개선안**:
> This research explores how the universe initially created more matter than antimatter, a mystery scientists are still trying to solve. Researchers refined existing calculations to better understand this process, focusing on conditions that can be tested in particle accelerators.

(전문용어 제거, 실험 가능성을 일반인이 이해하는 방식으로 전환)

---

## 🏆 최종 순위 (TTS 뉴스 브리핑 관점)

### 1위: Sample 2 (Mesons) ⭐⭐⭐⭐½ (4.5/5)
**"출퇴근길에 듣기 완벽"**

**선정 이유**:
- 일반 청중이 100% 이해 가능
- 뉴스 아나운서가 가장 편하게 읽을 수 있는 구조
- 전문성 유지하면서도 접근성 최고
- 문장 길이와 리듬 완벽

**강점**:
- "particles called X" 패턴으로 친절한 설명
- 복잡한 수학적 내용을 "mathematical tools"로 적절히 추상화
- 두 가지 방법 비교라는 핵심만 전달

---

### 2위: Sample 1 (Domain Walls) ⭐⭐⭐⭐ (4/5)
**"거의 완벽, 단어 하나만 수정하면 완성"**

**선정 이유**:
- 매우 자연스러운 TTS 스크립트
- "tiny structures called domain walls" - 모범 사례
- 전반적으로 일반인 이해 가능

**단점**:
- "chirality" 하나만이 유일한 문제
- 이 단어만 "rotation direction"으로 바꾸면 1위 가능

---

### 3위: Sample 3 (Baryogenesis) ⭐⭐⭐ (3/5)
**"과학자용 요약, 일반인용 아님"**

**선정 이유**:
- 첫 문장은 훌륭하나 두 번째 문장이 문제
- 전문용어 과다 (electroweak baryogenesis, supersymmetry)
- 문장 구조 복잡 → 읽기 힘듦
- 일반인이 차 안에서 듣기엔 너무 어려움

**치명적 문제**:
- "electroweak baryogenesis"를 그대로 사용 (일반인 이해 불가)
- Teacher 프롬프트 "simple, clear English that anyone can understand" 위배

---

## 📊 종합 분석

### 점수 비교표

| Sample | Clarity | TTS Quality | Professional Tone | Length | **Total** |
|--------|---------|-------------|-------------------|--------|-----------|
| 2 (Mesons) | 10/10 | 10/10 | 10/10 | 9/10 | **4.5/5** |
| 1 (Domain Walls) | 9/10 | 9/10 | 9/10 | 8/10 | **4.0/5** |
| 3 (Baryogenesis) | 5/10 | 6/10 | 8/10 | 7/10 | **3.0/5** |

**평균**: 3.83/5

---

## 💪 모델 강점

✅ **"called X" 패턴 탁월**: "particles called mesons", "structures called domain walls"  
✅ **문장 길이 준수**: 모든 샘플이 2문장 규칙 준수  
✅ **자연스러운 문장 흐름**: 대부분 읽기 쉬운 리듬  
✅ **전문성과 접근성 균형**: Sample 1, 2에서 우수한 균형감

---

## ⚠️ 모델 약점

❌ **전문용어 과다 사용**: "electroweak baryogenesis", "chirality", "supersymmetry"  
❌ **일반화 실패**: 복잡한 주제(Sample 3)를 일반인 수준으로 변환 실패  
❌ **두 번째 문장 복잡도 증가 경향**: Sample 3에서 명확히 드러남  
❌ **괄호 속 용어를 설명으로 착각**: "chirality", "supersymmetry"를 그대로 사용

---

## 🎯 Training 개선 제안

### 1. 전문용어 필터링 강화
**현재 문제**: "electroweak baryogenesis" 같은 고급 용어를 그대로 사용

**개선 방법**:
```
Bad: "electroweak baryogenesis"
Good: "a process that created matter in the early universe"

Bad: "chirality"
Good: "rotation direction" or "handedness"

Bad: "supersymmetry"
Good: "a theoretical framework" or "advanced physics theories"
```

**Training 데이터 추가**:
- 전문용어 → 일반 언어 변환 예시 100개 추가
- "Avoid these terms: [list of academic jargon]" 명시적 지시

---

### 2. TTS 읽기 테스트 도입
**현재 문제**: 두 번째 문장이 너무 길거나 복잡 (Sample 3)

**개선 방법**:
- 문장당 최대 25단어 제한 (현재 30단어 발생)
- 절(clause) 개수 제한: 문장당 최대 2개 절
- "and"로 3개 이상 연결 금지

**Training 지시 추가**:
```
"Each sentence should be readable in ONE breath. 
Avoid: 'A, B, and C' structures with 3+ clauses."
```

---

### 3. "Anyone Can Understand" 체크리스트
**Training 프롬프트에 추가**:
```
Before finishing, check:
□ Would a high school student understand every word?
□ Can you explain this to someone while they're driving?
□ Are there any words that need a science degree?
□ If you say it out loud, does it sound like news or a textbook?

If any answer is NO → rewrite using simpler terms.
```

---

### 4. 구체적 예시 Few-Shot 추가

**나쁜 예**:
> "This research explores electroweak baryogenesis in the minimal supersymmetric standard model..."

**좋은 예**:
> "This research explores how the early universe created more matter than antimatter, a puzzle scientists are still solving..."

**Training 데이터에 10-20개 Before/After 쌍 추가**

---

## 🎬 최종 판정

**모델 현황**: TTS 스크립트 기본기는 우수하나, 복잡한 주제에서 일반화 실패

**즉시 개선 가능한 부분**:
1. 전문용어 블랙리스트 작성 및 필터링
2. 문장당 단어 수 hard limit (25단어)
3. Few-shot 예시에 "나쁜 전문용어 사용 예시" 포함

**장기 개선 방향**:
1. "고등학생이 이해 가능한가?" 테스트 단계 추가
2. TTS 음성 출력 후 명확성 평가 시스템 구축
3. 일반인 청취자 피드백 수집 후 fine-tuning

---

**결론**: Sample 2는 방송 준비 완료, Sample 1은 단어 하나만 수정, Sample 3은 전면 재작성 필요.