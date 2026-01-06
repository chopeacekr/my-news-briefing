# 🔌 STEP 0.2 플러그인 버전 - 사용 가이드

## 🎯 플러그인 버전의 장점

### Before (일반 버전)
```python
# SimpleEvaluator 클래스가 코드에 직접 포함됨
class SimpleEvaluator:
    def evaluate(self, original, generated):
        ...

evaluator = SimpleEvaluator()
result = evaluator.evaluate(original, generated)

# 나중에 LLM 평가로 교체?
# → 코드 전체 수정 필요! 😰
```

### After (플러그인 버전) ⭐
```python
# 플러그인 시스템 사용!
from summary_evaluator_plugin import EvaluatorFactory

evaluator = EvaluatorFactory.create("keyword")
result = evaluator.evaluate(original, generated)

# 나중에 LLM 평가로 교체?
# → 단 1줄만 변경! 😎
evaluator = EvaluatorFactory.create("gpt4", {"api_key": "sk-..."})
```

---

## 📦 필요한 파일

### 1. STEP0_2_QWEN_COLAB_PLUGIN.py (실행 파일)
- 이미 다운로드했습니다! ✅

### 2. summary_evaluator_plugin.py (평가 시스템)
- 플러그인 평가 시스템 핵심 파일
- **Colab에 업로드 필요!** ⚠️

---

## 🚀 실행 방법

### Step 1: Colab에서 파일 준비

```
1. Google Colab 접속
   https://colab.research.google.com

2. 새 노트북 생성
   또는 기존 노트북 열기

3. 왼쪽 파일 탭 클릭 (폴더 아이콘)

4. 업로드 버튼 클릭 (파일 아이콘 ⬆️)

5. summary_evaluator_plugin.py 선택
   → 업로드 완료!

6. STEP0_2_QWEN_COLAB_PLUGIN.py 붙여넣기
   → Colab 셀에 코드 복사
```

---

### Step 2: 순서대로 실행

#### 섹션 1: 환경 설정
```python
# 실행
→ ✅ 패키지 설치 완료
→ 🔴 Runtime 재시작!
```

#### Runtime 재시작
```
Runtime → Restart runtime
또는 Ctrl+M .
```

#### 섹션 2: 데이터 준비
```python
# 실행
→ ✅ GPU 확인
→ ✅ Drive 마운트
→ ✅ 데이터 50개 로드
```

#### 섹션 3: 모델 학습
```python
# 실행
→ ✅ Qwen 모델 로딩
→ ✅ LoRA 적용
→ ✅ 학습 완료 (1-2분)
```

#### 섹션 4: A/B 테스트 (플러그인!)
```python
# 실행
→ 🔌 플러그인 로딩!
→ ✅ KeywordEvaluator 생성
→ ✅ 평가 완료
```

**여기서 플러그인 사용!** 🎉

#### 섹션 5: 결과 분석
```python
# 실행
→ ✅ 평균 계산
→ ✅ 그래프 생성
→ ✅ 파일 저장
```

---

## 🔌 플러그인 사용 확인

### 섹션 4 실행 시 출력

```
="=60
🔬 섹션 4: A/B 테스트 (플러그인 평가 시스템)
="=60

🔌 플러그인 평가 시스템 로딩 중...
✅ summary_evaluator_plugin.py 로드 성공!
✅ KeywordEvaluator 생성 완료
   평가기: KeywordEvaluator
   💡 나중에 LLM 평가로 즉시 교체 가능!
```

**이 메시지가 보이면 성공!** ✅

---

## ⚠️ 트러블슈팅

### Q1: summary_evaluator_plugin.py 로드 실패

```
❌ summary_evaluator_plugin.py 로드 실패!

해결 방법:
1. 왼쪽 파일 탭 클릭
2. 업로드 버튼 클릭
3. summary_evaluator_plugin.py 선택
4. 업로드 완료 후 섹션 4 재실행
```

**원인:**
- summary_evaluator_plugin.py 파일을 업로드하지 않음

**해결:**
1. 파일 탭 열기 (왼쪽)
2. 업로드 버튼 클릭
3. summary_evaluator_plugin.py 선택
4. 섹션 4 재실행

---

### Q2: ImportError: No module named 'summary_evaluator_plugin'

```python
ImportError: No module named 'summary_evaluator_plugin'
```

**원인:**
- Colab에 파일을 업로드하지 않음
- 또는 파일 이름이 다름

**해결:**
1. 파일 이름 확인: `summary_evaluator_plugin.py` (정확히)
2. Colab의 `/content/` 경로에 업로드되었는지 확인
3. 파일 탭에서 파일 보이는지 확인

---

### Q3: 업로드한 파일이 안 보임

**원인:**
- Runtime 재시작하면 업로드 파일 삭제됨

**해결:**
- Runtime 재시작 **후**에 파일 업로드!
- 순서:
  1. 섹션 1 실행
  2. Runtime 재시작
  3. summary_evaluator_plugin.py 업로드 ⚠️
  4. 섹션 2-5 실행

---

## 💡 플러그인 vs 일반 버전 비교

| 항목 | 일반 버전 | 플러그인 버전 |
|------|----------|--------------|
| **평가 시스템** | SimpleEvaluator (코드 내장) | KeywordEvaluator (플러그인) |
| **파일 필요** | 1개 | 2개 (+ plugin) |
| **업로드 필요** | ❌ 없음 | ✅ plugin 파일 |
| **LLM 교체** | 어려움 (코드 수정) | 쉬움 (1줄 변경) |
| **확장성** | 낮음 | 높음 |

---

## 🔄 나중에 LLM 평가로 교체하는 방법

### 현재 (Keyword 평가)

```python
# 섹션 4
from summary_evaluator_plugin import EvaluatorFactory

evaluator = EvaluatorFactory.create("keyword")
```

### 향후 (GPT-4 평가)

```python
# 섹션 4 - 단 1줄만 변경!
from summary_evaluator_plugin import EvaluatorFactory

evaluator = EvaluatorFactory.create("gpt4", config={
    "api_key": "sk-...",  # OpenAI API 키
    "model": "gpt-4"
})
```

**나머지 코드는 그대로!** ✨

---

## 📊 결과 파일에 평가기 정보 포함

### JSON 결과

```json
{
  "metadata": {
    "qwen_model": "Qwen2.5-1.5B-Instruct",
    "mistral_model": "Mistral-7B-v0.1",
    "evaluator": {
      "name": "KeywordEvaluator",
      "version": "1.0.0",
      "type": "KeywordEvaluator"
    }
  },
  ...
}
```

**평가기 정보가 자동으로 저장됨!** 📝

---

## ✅ 체크리스트

### 실행 전
- [ ] step0.2.py 다운로드
- [ ] summary_evaluator_plugin.py 다운로드
- [ ] Colab 접속
- [ ] GPU 설정 (T4)

### 파일 준비
- [ ] 섹션 1 실행 (패키지 설치)
- [ ] Runtime 재시작 ⚠️
- [ ] summary_evaluator_plugin.py 업로드 ⚠️
- [ ] 파일 탭에서 파일 확인

### 실행
- [ ] 섹션 2 실행 (데이터 준비)
- [ ] 섹션 3 실행 (모델 학습)
- [ ] 섹션 4 실행 (플러그인 평가!)
- [ ] 섹션 5 실행 (결과 분석)

### 확인
- [ ] 섹션 4에서 "플러그인 로드 성공" 메시지 확인
- [ ] 평가기 이름 확인: KeywordEvaluator
- [ ] 결과 파일에 평가기 정보 포함 확인

---

## 🎯 권장 사항

### 지금 (학습 단계)
```python
# KeywordEvaluator 사용 (빠르고 무료)
evaluator = EvaluatorFactory.create("keyword")
```

**장점:**
- ⚡ 빠름 (밀리초)
- 💰 무료
- 🎯 일관성 있음

---

### 향후 (프로덕션)
```python
# GPT-4 또는 Claude 사용 (최고 품질)
evaluator = EvaluatorFactory.create("gpt4", {...})
```

**장점:**
- ⭐ 최고 품질
- 🧠 사람처럼 평가
- 📊 세밀한 분석

**단점:**
- 💰 비용 발생
- ⏱️ 느림 (초 단위)

---

### 절충안 (Hybrid)
```python
# Keyword 70% + GPT-4 30%
evaluator = EvaluatorFactory.create("hybrid", {
    "evaluators": [
        {"type": "keyword", "weight": 0.7},
        {"type": "gpt4", "weight": 0.3, "api_key": "..."}
    ]
})
```

**장점:**
- ⚖️ 균형잡힌 선택
- 💰 비용 절감
- 🎯 품질 향상

---

## 🎉 요약

**플러그인 버전의 핵심:**

```
✅ 파일 2개 필요
   - STEP0_2_QWEN_COLAB_PLUGIN.py
   - summary_evaluator_plugin.py

✅ summary_evaluator_plugin.py 업로드 필수!

✅ KeywordEvaluator 사용

✅ 나중에 LLM 평가로 즉시 교체 가능
   → 단 1줄만 변경!

✅ 확장성 높음
   → 새로운 평가기 쉽게 추가
```

---

**Peace님, 플러그인 버전 준비 완료!** 🎉

**지금:**
1. summary_evaluator_plugin.py 다운로드
2. Colab에 업로드
3. STEP0_2_QWEN_COLAB_PLUGIN.py 실행
4. 플러그인 평가 체험!

**나중에:**
- create("gpt4") → LLM 평가 즉시 전환!

**화이팅!** 💪🔥