# My-News-Briefing

> ArXiv 논문을 일반인도 이해할 수 있는 뉴스 브리핑으로 자동 요약하는 AI 시스템

[![Version](https://img.shields.io/badge/version-4.0-blue.svg)](./VERSION_HISTORY.md)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Model](https://img.shields.io/badge/model-Qwen2.5--1.5B-orange.svg)]()
[![Data](https://img.shields.io/badge/data-1000_samples-brightgreen.svg)]()

---

## 🎯 프로젝트 소개

**My-News-Briefing**은 복잡한 학술 논문을 누구나 쉽게 이해할 수 있는 뉴스 브리핑 스타일로 자동 요약하는 AI 시스템입니다.

### 핵심 가치
````
"전문가의 연구를 대중의 언어로"
````

- 📰 **뉴스 브리핑 스타일**: 2문장, 45단어 이하
- 🌍 **일반인 대상**: 전문 지식 없이도 이해 가능
- ⚡ **빠른 처리**: 5초 이내 요약 생성
- 🎯 **고품질**: Teacher LLM 기반 학습

---

## ✨ 주요 특징

### 1. 뉴스 브리핑 스타일
````
AS-IS (학술):
"A novel transformer-based architecture combining self-attention 
with hierarchical representations achieves state-of-the-art..."

TO-BE (뉴스):
"Researchers developed a new AI system that better understands 
human language. The system performed better than previous methods."
````

### 2. 단순하고 명확한 프롬프트
````
"Summarize the following text in simple, clear English 
that anyone can understand. Use no more than two complete sentences."
````

### 3. 고품질 데이터
- **Teacher LLM**: Gemini Pro, GPT-4
- **데이터 크기**: 1,000 samples (V4.0)
- **성공률**: 95%+
- **품질 관리**: 환각 방지, 복사 감지

---

## 🚀 빠른 시작

### 요구사항
````yaml
Python: 3.8+
GPU: T4 / A100 (권장)
메모리: 16GB+ GPU RAM
````

### 설치
````bash
# 저장소 클론
git clone https://github.com/your-org/my-news-briefing.git
cd my-news-briefing

# 의존성 설치
pip install -r requirements.txt
````

### 데이터 생성 (팀1)
````bash
cd ArXiv-NewsBrief-1.5B-1k-v4.0
python dataset_generator.py
````

### 모델 학습 (팀2)
````bash
python sft_train_data.py --config configs/training_v4.yaml
````

### 평가 (팀3)
````bash
# evaluation 디렉토리 참고
cd reports/evaluation/
# llm_prompt_request.md 사용
````

---

## 📊 현재 버전 (V4.0)

### 사양
````yaml
버전: ArXiv-NewsBrief-1.5B-1k-v4.0
날짜: 2026-01-06
상태: ✅ 학습 완료, 평가 진행 중

데이터: 1,000 samples
모델: Qwen2.5-1.5B-Instruct + LoRA
스타일: 뉴스 브리핑
타겟: 일반 대중

성능: 7.2/10 (예상)
V3 대비: +1.2점
````

### 예시

#### 입력
````
This paper proposes a novel deep learning architecture for natural 
language understanding. We introduce a transformer-based model that 
achieves state-of-the-art results on multiple benchmarks including 
GLUE and SuperGLUE. Our approach combines self-attention mechanisms 
with hierarchical representations to capture both local and global 
context. Experimental results demonstrate significant improvements 
over previous methods, with an average score increase of 5.2% across 
all tasks...
````

#### 출력 (V4.0)
````
Researchers developed a new AI system that better understands human 
language by combining different learning techniques. The system 
performed better than previous methods on major language tests.
````

---

## 📁 프로젝트 구조
````
My-News-Briefing/
│
├── ArXiv-NewsBrief-1.5B-1k-v3.0/    # V3 (학술 스타일)
├── ArXiv-NewsBrief-1.5B-1k-v4.0/    # V4 (뉴스 스타일) ⭐
│   ├── data/
│   ├── reports/
│   │   ├── training/
│   │   ├── evaluation/
│   │   └── analysis/
│   └── scripts/
│
├── TEAM_WORKFLOW.md                  # 팀 워크플로우
├── VERSION_HISTORY.md                # 버전 히스토리
└── README.md                         # 이 파일
````

---

## 🔄 버전 히스토리

### 버전 로드맵
````
✅ V3.0: ArXiv-Academic-1.5B-600-v3.0 (학술, 6.0/10)
✅ V4.0: ArXiv-NewsBrief-1.5B-1k-v4.0 (뉴스, 7.2/10) ⭐ 현재
⏳ V5.0: ArXiv-NewsBrief-1.5B-4k-v5.0 (개선, 8.5/10)
🎯 V6.0: ArXiv-NewsBrief-3B-4k-v6.0 (스케일업, 9.0/10)
````

### 주요 개선사항

#### V3.0 → V4.0
- 🎯 타겟: 전문가 → 일반인
- 📝 프롬프트: 90% 단순화
- 📊 데이터: 600 → 1,000 samples
- 🛡️ 환각 방지 강화
- 🔧 전처리 개선

자세한 내용은 [VERSION_HISTORY.md](./VERSION_HISTORY.md) 참고

---

## 👥 팀 구성

### 팀1: 데이터셋 구축
- **담당**: 고품질 학습 데이터 생성
- **도구**: ArXiv API, Gemini, GPT-4
- **산출물**: v4_training_data_all.csv

### 팀2: 모델 학습
- **담당**: SFT 파인튜닝
- **도구**: LoRA, Qwen2.5, A/B Testing
- **산출물**: ab_test_v4.0.json

### 팀3: 평가 & 분석
- **담당**: 성능 평가 및 개선 제안
- **도구**: ChatGPT, Claude, Gemini
- **산출물**: performance_report, improvement_research

자세한 내용은 [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) 참고

---

## 📊 성능

### V4.0 평가 결과 (예상)

| 평가 항목 | 점수 | 가중치 |
|----------|------|--------|
| 형식 준수 | 2.0/2 | 20% |
| 내용 정확성 | 2.3/3 | 30% |
| 일반인 이해도 | 1.8/2.5 | 25% |
| 가독성 | 1.0/1.5 | 15% |
| 환각 방지 | 0.7/1 | 10% |
| **총점** | **7.2/10** | 100% |

### V3 vs V4 비교

| 항목 | V3.0 | V4.0 | 개선 |
|------|------|------|------|
| 점수 | 6.0 | 7.2 | +1.2 |
| 일반인 이해도 | 40% | 72% | +32% |
| 활용 범위 | 학술 | 뉴스/블로그 | 확대 |
| 프롬프트 길이 | 200단어 | 20단어 | -90% |

---

## 🛠️ 기술 스택

### 데이터 생성
- **ArXiv API**: 논문 수집
- **HuggingFace Datasets**: 데이터 관리
- **Gemini Pro**: Teacher LLM (무료)
- **GPT-4o-mini**: Teacher LLM (고품질)

### 모델 학습
- **Qwen2.5-1.5B-Instruct**: 베이스 모델
- **LoRA**: 효율적 파인튜닝
- **Transformers**: Hugging Face
- **PEFT**: Parameter-Efficient Fine-Tuning

### 평가
- **ChatGPT-4**: 평가 LLM
- **Claude 3.5**: 평가 LLM
- **Gemini 1.5 Pro**: 평가 LLM

---

## 📈 로드맵

### 단기 (1개월)
- [x] V3.0 완료 (학술 스타일)
- [x] V4.0 완료 (뉴스 스타일) ⭐
- [ ] V4.0 평가 완료
- [ ] V5.0 데이터 생성 (4k)

### 중기 (3개월)
- [ ] V5.0 학습 및 평가 (8.5/10 목표)
- [ ] 다국어 지원 검토 (한국어, 일본어)
- [ ] API 서비스 개발 시작

### 장기 (6개월)
- [ ] V6.0 스케일업 (3B 모델)
- [ ] 프로덕션 서비스 런칭
- [ ] 실시간 뉴스 브리핑 서비스

---

## 🤝 기여 방법

### 버그 리포트
Issues 탭에서 버그 리포트 제출

### 기능 제안
Issues 탭에서 "enhancement" 라벨로 제안

### Pull Request
1. Fork the repository
2. Create feature branch
3. Commit your changes
4. Push to the branch
5. Create Pull Request

---

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](./LICENSE) 참고

---

## 📞 연락처

- **프로젝트 리드**: 조화평
- **이메일**: [email@example.com]
- **GitHub**: [https://github.com/your-org/my-news-briefing](https://github.com/your-org/my-news-briefing)
- **문서**: [https://docs.your-org.com/news-briefing](https://docs.your-org.com/news-briefing)

---

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들을 기반으로 합니다:

- **Qwen2.5** by Alibaba Cloud
- **Transformers** by Hugging Face
- **PEFT** by Hugging Face
- **ArXiv Dataset** by Cornell University

---

## 📚 참고 문서

- [TEAM_WORKFLOW.md](./TEAM_WORKFLOW.md) - 팀 워크플로우 상세
- [VERSION_HISTORY.md](./VERSION_HISTORY.md) - 버전별 변경사항
- [dataset_pipeline.md](./ArXiv-NewsBrief-1.5B-1k-v4.0/dataset_pipeline.md) - 데이터 파이프라인
- [update.md](./ArXiv-NewsBrief-1.5B-1k-v4.0/update.md) - V3→V4 개선사항

---

**최종 수정일**: 2026-01-06  
**버전**: V4.0  
**상태**: 학습 완료, 평가 진행 중

⭐ Star this repository if you find it helpful!