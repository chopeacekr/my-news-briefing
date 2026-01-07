# ArXiv-NewsBrief v4.1 학습 로그

## 🎯 실행 정보

- **실행 모드**: 전체 (Full)
- **모델**: ArXiv-NewsBrief-1.5B-1k-v4.1
- **베이스 모델**: Qwen/Qwen2.5-1.5B-Instruct
- **데이터셋**: v4.1_training_data_all.csv
- **샘플 수**: 1000개
- **에포크**: 5
- **테스트 샘플**: 3개

---

## 📦 STEP 1: 패키지 설치

- ✅ bitsandbytes 설치
- ✅ 나머지 패키지 설치 완료

---

## 📚 STEP 2: 라이브러리 Import

### GPU 환경
- **GPU**: NVIDIA A100-SXM4-80GB
- **메모리**: 85.17GB
- **bitsandbytes 버전**: 0.49.0

### 설정 요약
- 모드: 전체 (Full)
- 모델: ArXiv-NewsBrief-1.5B-1k-v4.1
- 베이스: Qwen/Qwen2.5-1.5B-Instruct
- 데이터: v4.1_training_data_all.csv
- 샘플 수: 1000개
- 에포크: 5
- 저장 위치: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.1`

---

## 📂 STEP 3: 데이터 로드 및 준비

### 데이터 통계
- **전체 데이터**: 941개
- **성공 데이터**: 941개
- **V4 필터**: 941개
- **최종 데이터**: 941개

### 데이터 분할
- **Train**: 847개 (90.0%)
- **Validation**: 94개 (10.0%)

### 데이터 품질 통계
- **평균 단어 수**: 52.4
- **45단어 이하**: 91/847 (10.7%)
- **평균 문장 수**: 2.0
- **2문장**: 833/847 (98.3%)

### 샘플 예시 (1/847)

**초록:**
```
localized states of harper s equation correspond to strange nonchaotic attractors ( snas ) in the related harper mapping. in parameter space. , these fractal attractors with nonpositive lyapunov expon...
```

**V4.1 요약 (영문):**
```
This research explores how energy behaves in a specific physics equation (the Harper equation) when things get "stuck" in certain patterns, revealing complex and organized structures. By studying these patterns, scientists can better understand and categorize the different energy levels and how they change with varying conditions.
```

**V4.1 요약 (한글):**
```
이 연구는 특정 물리학 방정식(Harper 방정식)에서 에너지가 특정 패턴에 "갇힐" 때 어떻게 행동하는지 탐구하여 복잡하고 조직화된 구조를 드러냅니다. 이러한 패턴을 연구함으로써 과학자들은 다양한 에너지 레벨과 조건 변화에 따라 어떻게 변하는지 더 잘 이해하고 분류할 수 있습니다.
```

- 47단어, 2문장

---

## 📝 STEP 4: 프롬프트 생성

### 시스템 프롬프트
```
Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences.
```

- ✅ 토크나이저 로드 완료
- ✅ 프롬프트 적용 완료

---

## 🔤 STEP 5: 토크나이즈

- ✅ 텍스트를 숫자로 변환 완료

---

## 🚀 STEP 6: 모델 로딩

- ✅ Qwen/Qwen2.5-1.5B-Instruct 로드 완료
- ✅ 4-bit 양자화 적용
- ✅ LoRA 어댑터 설정

### 학습 파라미터
- **학습 가능 파라미터**: 4,358,144 (0.49%)
- **전체 파라미터**: 892,974,592

---

## 🏋️ STEP 7: 모델 학습

### 학습 정보
- **모드**: 전체 (Full)
- **데이터**: 847개
- **에포크**: 5
- **총 스텝**: 1060
- **실제 소요 시간**: 36.3분
- **평균 속도**: 29.1 스텝/분

### 학습 진행 결과

| Step | Training Loss | Validation Loss |
|------|---------------|-----------------|
| 50   | 2.195800      | 2.149481        |
| 100  | 2.119100      | 2.068999        |
| 150  | 1.991500      | 2.049902        |
| 200  | 2.058600      | 2.035104        |
| 250  | 1.954200      | 2.027742        |
| 300  | 1.996800      | 2.031657        |
| 350  | 1.936200      | 2.021293        |
| 400  | 1.959900      | 2.019362        |
| 450  | 1.923100      | 2.021418        |
| 500  | 1.868200      | 2.024808        |
| 550  | 1.892700      | 2.027371        |
| 600  | 1.926900      | 2.020732        |
| 650  | 1.819200      | 2.026111        |
| 700  | 1.774000      | 2.037507        |
| 750  | 1.811600      | 2.036982        |
| 800  | 1.817100      | 2.038425        |
| 850  | 1.899500      | 2.039688        |
| 900  | 1.821400      | 2.055198        |
| 950  | 1.719800      | 2.057278        |
| 1000 | 1.810500      | 2.056664        |
| 1050 | 1.775100      | 2.056681        |

---

## 💾 STEP 8: 모델 저장

- ✅ 모델 저장 완료
- ✅ 메타데이터 저장 완료
- ✅ README 저장 완료

**저장 위치**: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.1/final_model`

---

## 🔬 STEP 9: A/B 테스트

### 테스트 설정
- **테스트 샘플**: 3개
- **결과 저장**: `test_전체_(Full)_20260107_033148.json`

### 결과 분석

| 모델 | 평균 단어 수 | 성공률 |
|------|-------------|--------|
| 베이스 모델 | 25.7단어 | 3/3 (100%) |
| 학습된 모델 | 34.3단어 | 3/3 (100%) |

### 샘플 비교 (1/3)

**초록:**
```
we present a search for the standard model higgs boson produced in association with a boson. this search uses data corresponding to an integrated lumi...
```

**목표 (Ground Truth - 영문):**
```
Scientists looked for a specific particle called the Higgs boson using data from a powerful machine called the Tevatron, but they didn't find enough evidence to confirm it exists. They were able to rule out certain possibilities for how often this particle *could* be created, setting limits on its potential behavior based on their observations.
```

**목표 (Ground Truth - 한글):**
```
과학자들은 Tevatron이라는 강력한 기계의 데이터를 사용하여 힉스 보손이라는 특정 입자를 찾았지만, 그것이 존재한다는 것을 확인할 만큼 충분한 증거를 찾지 못했습니다. 그들은 이 입자가 얼마나 자주 생성될 *수 있는지*에 대한 특정 가능성을 배제할 수 있었으며, 관측을 바탕으로 잠재적 행동에 대한 한계를 설정했습니다.
```

**베이스 모델 출력 (영문):**
```
A team looked for tiny particles called Higgs Bosons using special machines. They found out there's not enough information yet about these Higgs particles.
```

**베이스 모델 출력 (한글):**
```
한 팀이 특수 기계를 사용하여 힉스 보손이라는 작은 입자를 찾았습니다. 그들은 이 힉스 입자에 대한 정보가 아직 충분하지 않다는 것을 발견했습니다.
```

**학습된 모델 출력 (영문):**
```
Scientists used powerful equipment to look for signs of a special particle called the Higgs bosoon created when other particles collide—specifically searching for it *in* those collisions rather than after they happen.
```

**학습된 모델 출력 (한글):**
```
과학자들은 다른 입자들이 충돌할 때 생성되는 힉스 보손이라는 특별한 입자의 흔적을 찾기 위해 강력한 장비를 사용했습니다—특히 충돌이 일어난 후가 아니라 충돌 *중에* 그것을 찾았습니다.
```

---

## ✅ 완료

### 최종 저장 위치
- **모델**: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.1/final_model`
- **테스트 결과**: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.1/results/test_전체_(Full)_20260107_033148.json`

### 주요 성과
- ✅ 941개 데이터로 5 에포크 학습 완료
- ✅ Training Loss: 2.196 → 1.775 (19.2% 감소)
- ✅ Validation Loss: 2.149 → 2.057 (4.3% 감소)
- ✅ 36.3분 만에 학습 완료
- ✅ 학습된 모델이 베이스 모델보다 더 상세한 요약 생성 (34.3 vs 25.7 단어)