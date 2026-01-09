# ArXiv-NewsBrief v4.0 학습 로그

## 🎯 실행 정보

- **실행 모드**: 전체 (Full)
- **모델**: ArXiv-NewsBrief-1.5B-1k-v4.0
- **베이스 모델**: Qwen/Qwen2.5-1.5B-Instruct
- **데이터셋**: v4_training_data_all.csv
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
- 모델: ArXiv-NewsBrief-1.5B-1k-v4.0
- 베이스: Qwen/Qwen2.5-1.5B-Instruct
- 데이터: v4_training_data_all.csv
- 샘플 수: 1000개
- 에포크: 5
- 저장 위치: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0`

---

## 📂 STEP 3: 데이터 로드 및 준비

### 데이터 통계
- **전체 데이터**: 782개
- **성공 데이터**: 782개
- **V4 필터**: 782개
- **최종 데이터**: 782개

### 데이터 분할
- **Train**: 704개 (90.0%)
- **Validation**: 78개 (10.0%)

### 데이터 품질 통계
- **평균 단어 수**: 52.1
- **45단어 이하**: 89/704 (12.6%)
- **평균 문장 수**: 2.0
- **2문장**: 696/704 (98.9%)

### 샘플 예시 (1/704)

**초록:**
```
we present an analysis of the two - point angular correlation function of the elais s1 survey. the survey covers 4 deg and contains 462 sources detected at 15 m to a 5 flux limit of 0.45 mjy. using th...
```

**V4 요약 (영문):**
```
This study looked at how galaxies are spread out in the sky using infrared light, finding that they tend to cluster together, but not as much as galaxies seen with regular light. This suggests that galaxies identified by their infrared glow are less grouped than those seen in visible light, especially at greater distances.
```

**V4 요약 (한글):**
```
이 연구는 적외선을 사용하여 하늘에 은하들이 어떻게 분포되어 있는지 조사했으며, 은하들이 함께 모여 있는 경향이 있지만 일반 빛으로 관측되는 은하들만큼은 아니라는 것을 발견했습니다. 이는 적외선으로 식별된 은하들이 가시광선으로 보이는 은하들보다, 특히 더 먼 거리에서 덜 밀집되어 있음을 시사합니다.
```

- 54단어, 2문장

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
- **데이터**: 704개
- **에포크**: 5
- **총 스텝**: 880
- **실제 소요 시간**: 29.7분
- **평균 속도**: 29.7 스텝/분

### 학습 진행 결과

| Step | Training Loss | Validation Loss |
|------|---------------|-----------------|
| 50   | 2.179600      | 2.099127        |
| 100  | 2.081200      | 2.028833        |
| 150  | 2.139100      | 2.013743        |
| 200  | 1.982800      | 2.003889        |
| 250  | 1.997700      | 1.999719        |
| 300  | 1.989200      | 1.995565        |
| 350  | 1.927800      | 1.990512        |
| 400  | 1.904400      | 1.996075        |
| 450  | 1.810900      | 1.996067        |
| 500  | 1.901800      | 1.995227        |
| 550  | 1.834800      | 2.010142        |
| 600  | 1.911700      | 2.011550        |
| 650  | 1.843400      | 2.012139        |
| 700  | 1.825300      | 2.011491        |
| 750  | 1.728800      | 2.027000        |
| 800  | 1.679400      | 2.033656        |
| 850  | 1.738000      | 2.032377        |

---

## 💾 STEP 8: 모델 저장

- ✅ 모델 저장 완료
- ✅ 메타데이터 저장 완료
- ✅ README 저장 완료

**저장 위치**: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/final_model`

---

## 🔬 STEP 9: A/B 테스트

### 테스트 설정
- **테스트 샘플**: 3개
- **결과 저장**: `test_전체_(Full)_20260106_043702.json`

### 결과 분석

| 모델 | 평균 단어 수 | 성공률 |
|------|-------------|--------|
| 베이스 모델 | 29.7단어 | 3/3 (100%) |
| 학습된 모델 | 23.0단어 | 3/3 (100%) |

### 샘플 비교 (1/3)

**초록:**
```
development of exponentially scaling methods has seen great progress in tackling larger systems than previously thought possible. one such technique ,...
```

**목표 (Ground Truth - 영문):**
```
Scientists have developed a new, faster way to solve complex quantum chemistry problems that were previously too difficult for computers. This improved method allows for accurate calculations on larger systems, like the chromium dimer, in a fraction of the time compared to older techniques, and can also efficiently calculate excited state energies.
```

**목표 (Ground Truth - 한글):**
```
과학자들은 이전에 컴퓨터로 풀기에 너무 어려웠던 복잡한 양자화학 문제를 해결하는 새롭고 빠른 방법을 개발했습니다. 이 개선된 방법은 크롬 이량체와 같은 더 큰 시스템에 대해 기존 기술보다 훨씬 짧은 시간에 정확한 계산을 수행할 수 있으며, 들뜬 상태 에너지도 효율적으로 계산할 수 있습니다.
```

**베이스 모델 출력 (영문):**
```
Exponential growth of computational complexity means only very large molecular systems have been feasible before. Researchers developed algorithms capable of handling bigger systems thanks to their ability to sample determinant combinations randomly rather than exhaustively calculate all possibilities.
```

**베이스 모델 출력 (한글):**
```
계산 복잡도의 기하급수적 증가는 이전에는 매우 큰 분자 시스템만 실현 가능했음을 의미합니다. 연구자들은 모든 가능성을 완전히 계산하는 대신 무작위로 행렬식 조합을 샘플링하는 능력 덕분에 더 큰 시스템을 처리할 수 있는 알고리즘을 개발했습니다.
```

**학습된 모델 출력 (영문):**
```
Scientists have developed faster computer algorithms—like Full Configuration Interaction Quantum Monte Carlo—to solve complex molecular problems that were too hard before.
```

**학습된 모델 출력 (한글):**
```
과학자들은 이전에는 너무 어려웠던 복잡한 분자 문제를 해결하기 위해 Full Configuration Interaction Quantum Monte Carlo와 같은 더 빠른 컴퓨터 알고리즘을 개발했습니다.
```

---

## ✅ 완료

### 최종 저장 위치
- **모델**: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/final_model`
- **테스트 결과**: `/content/drive/MyDrive/ArXiv-Models/ArXiv-NewsBrief-1.5B-1k-v4.0/results/test_전체_(Full)_20260106_043702.json`

### 주요 성과
- ✅ 782개 데이터로 5 에포크 학습 완료
- ✅ Training Loss: 2.180 → 1.738 (20.3% 감소)
- ✅ Validation Loss: 2.099 → 2.032 (3.2% 감소)
- ✅ 29.7분 만에 학습 완료
- ✅ 학습된 모델이 베이스 모델보다 간결한 요약 생성 (23.0 vs 29.7 단어)