"""
=================================================================
📰 ArXiv-NewsBrief-1.5B - 완전판 (CPU 지원) v2
=================================================================

🎯 실행 모드:
✅ MODE 0: 연습 모드 (50개 데이터, 빠른 검증)
✅ MODE 1: 전체 학습 모드 (1000개 데이터, 프로덕션) - GPU 필요
✅ MODE 2: 테스트 전용 (추론만) - CPU 가능! ⭐

📊 CPU 지원:
- MODE 2는 CPU에서도 실행 가능
- 속도는 느리지만 작동함 (샘플당 ~30-60초)
- 소량 테스트에 적합

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("🚀 ArXiv-NewsBrief - 완전판 (CPU 지원)")
print("="*70)

# ================================================================
# ⚙️ 실행 모드 설정 ⭐ 여기만 수정하세요!
# ================================================================

EXECUTION_MODE = 2  # ⭐ 여기를 바꾸세요!
# 0: 연습 모드 (50개, 3 epochs) - GPU 필요
# 1: 전체 모드 (1000개, 5 epochs) - GPU 필요
# 2: 테스트 모드 (추론만) - CPU 가능!

# ================================================================
# MODE 2 전용 설정 ⭐
# ================================================================

# 추론할 샘플 개수 설정
NUM_INFERENCE_SAMPLES = 100  # ⭐ CPU는 3-5개 추천 (많으면 오래 걸림)

# 사용할 모델 경로 (학습된 모델)
INFERENCE_MODEL_NAME = "ArXiv-NewsBrief-1.5B-1k-v4.0"  # ⭐ 실제 모델 이름으로 변경

# CPU 추론 설정
USE_CPU_FOR_INFERENCE = False  # ⭐ True면 GPU 없어도 실행됨

# ================================================================
# 모드별 자동 설정
# ================================================================

if EXECUTION_MODE == 0:
    # 연습 모드 ⭐
    MODE_NAME = "연습 (Practice)"
    DATA_FILE = "v4.1_training_data_all.csv"
    MAX_DATA_TO_USE = 50
    VAL_RATIO = 0.1
    NUM_EPOCHS = 3
    NUM_TEST_SAMPLES = 5
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = True
    MODEL_SUFFIX = "practice-50"
    REQUIRES_GPU = True

elif EXECUTION_MODE == 1:
    # 전체 모드
    MODE_NAME = "전체 (Full)"
    DATA_FILE = "v4_training_data_all.csv"
    MAX_DATA_TO_USE = 1000
    VAL_RATIO = 0.1
    NUM_EPOCHS = 5
    NUM_TEST_SAMPLES = 3
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = False
    MODEL_SUFFIX = "1k-v4.0"
    REQUIRES_GPU = True

else:  # MODE == 2
    # 테스트 모드 ⭐
    MODE_NAME = "추론 전용 (Inference Only)"
    DATA_FILE = "v4_training_data_all.csv"
    MAX_DATA_TO_USE = NUM_INFERENCE_SAMPLES
    NUM_TEST_SAMPLES = NUM_INFERENCE_SAMPLES
    ENABLE_FINETUNING = False
    DETAILED_LOGGING = True
    MODEL_SUFFIX = INFERENCE_MODEL_NAME
    REQUIRES_GPU = not USE_CPU_FOR_INFERENCE  # CPU 모드면 GPU 불필요

# 공통 설정
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
USE_CHAT_TEMPLATE = True
USE_SYSTEM_MESSAGE = True
SYSTEM_MESSAGE = "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."
TEMPERATURE = 0.7
ENABLE_COPY_DETECTION = True
COPY_DETECTION_THRESHOLD = 0.5

# 모델 정보
if EXECUTION_MODE == 2:
    MODEL_VERSION = {
        'name': INFERENCE_MODEL_NAME,
        'mode': MODE_NAME,
        'base_model': 'Qwen/Qwen2.5-1.5B-Instruct',
        'inference_samples': NUM_INFERENCE_SAMPLES,
        'style': 'News Briefing',
        'device': 'CPU' if USE_CPU_FOR_INFERENCE else 'GPU'
    }
else:
    MODEL_VERSION = {
        'name': f'ArXiv-NewsBrief-1.5B-{MODEL_SUFFIX}',
        'mode': MODE_NAME,
        'base_model': 'Qwen/Qwen2.5-1.5B-Instruct',
        'data_size': f'{MAX_DATA_TO_USE}',
        'style': 'News Briefing',
    }

print(f"\n🎯 실행 모드: {MODE_NAME}")
print(f"📦 모델: {MODEL_VERSION['name']}")
if EXECUTION_MODE == 2:
    print(f"💻 디바이스: {'CPU (느림)' if USE_CPU_FOR_INFERENCE else 'GPU (빠름)'}")
    print(f"🔬 추론 샘플: {NUM_INFERENCE_SAMPLES}개")
elif EXECUTION_MODE != 2:
    print(f"📊 데이터: {MAX_DATA_TO_USE}개")
    print(f"🔄 에포크: {NUM_EPOCHS}")
print(f"🧪 테스트: {NUM_TEST_SAMPLES}개")

# ================================================================
# 후처리 함수
# ================================================================

import re

def detect_copy(text, original_article, ngram_size=5):
    if not ENABLE_COPY_DETECTION:
        return False

    text_clean = re.sub(r'[^\w\s]', '', text.lower())
    article_clean = re.sub(r'[^\w\s]', '', original_article.lower())

    text_words = text_clean.split()
    article_words = article_clean.split()

    if len(text_words) < ngram_size:
        return False

    article_ngrams = set()
    for i in range(len(article_words) - ngram_size + 1):
        ngram = ' '.join(article_words[i:i+ngram_size])
        article_ngrams.add(ngram)

    copy_count = 0
    total_ngrams = 0

    for i in range(len(text_words) - ngram_size + 1):
        ngram = ' '.join(text_words[i:i+ngram_size])
        total_ngrams += 1
        if ngram in article_ngrams:
            copy_count += 1

    if total_ngrams == 0:
        return False

    copy_ratio = copy_count / total_ngrams
    return copy_ratio > COPY_DETECTION_THRESHOLD

def clean_output(raw_text, original_article=""):
    text = raw_text

    text = re.sub(r'\b(system|user|assistant)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou\s+are\s+(a|an)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'research\s+paper|always\s+respond|maximum\s+45', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()

    if "Summary:" in text:
        text = text.split("Summary:")[-1].strip()
    elif "Brief:" in text:
        text = text.split("Brief:")[-1].strip()
    elif "<|im_end|>" in text:
        text = text.split("<|im_end|>")[-1].strip()
    elif "<|im_start|>" in text:
        if "assistant" in text:
            text = text.split("assistant")[-1].strip()
        else:
            text = text.split("<|im_start|>")[-1].strip()

    text = re.sub(r'#{1,}|={3,}|-{3,}', '', text)

    prompt_patterns = [
        r'(?i)paper\s*:', r'(?i)summary\s*:', r'(?i)summarize',
        r'<\|im_start\|>', r'<\|im_end\|>',
    ]
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text)

    latex_patterns = [r'\$+', r'\\[a-zA-Z]+', r'@xmath\d+', r'@xcite']
    for pattern in latex_patterns:
        text = re.sub(pattern, '', text)

    text = re.sub(r'```', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    text = text.strip()

    if not text or len(text) < 20:
        return "[요약 생성 실패 - 출력 없음]"

    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 5]

    if not sentences:
        return "[요약 생성 실패 - 유효 문장 없음]"

    cleaned_sentences = []
    for s in sentences:
        if not s[-1] in '.!?':
            s += '.'
        cleaned_sentences.append(s)

    if len(cleaned_sentences) == 1:
        words = cleaned_sentences[0].split()
        if len(words) <= 45:
            return cleaned_sentences[0]
        else:
            return ' '.join(words[:45]) + '.'

    sentence1 = cleaned_sentences[0]
    sentence2 = cleaned_sentences[1]

    words1 = len(sentence1.split())
    words2 = len(sentence2.split())
    total = words1 + words2

    if total <= 45:
        return f"{sentence1} {sentence2}"
    elif words1 <= 45:
        return sentence1
    else:
        words = sentence1.split()
        return ' '.join(words[:45]) + '.'

print(f"\n✅ 후처리 함수 로드 완료")

# ================================================================
# MODE 2: 추론 전용 모드 (CPU 지원!) ⭐
# ================================================================

if EXECUTION_MODE == 2:

    print("\n" + "="*70)
    print("🔬 MODE 2: 추론 전용 모드 (CPU 지원)")
    print("="*70)

    if USE_CPU_FOR_INFERENCE:
        print(f"\n⚠️ CPU 모드 활성화!")
        print(f"  - GPU 없이도 실행 가능")
        print(f"  - 속도: 샘플당 약 30-60초 (GPU 대비 ~10배 느림)")
        print(f"  - 추천: 3-5개 샘플로 테스트")
        print(f"  - 현재 설정: {NUM_INFERENCE_SAMPLES}개 샘플")

    # ============================================================
    # STEP 1: 패키지 설치 (CPU용 간소화)
    # ============================================================

    print("\n" + "="*70)
    print("📦 STEP 1: 패키지 설치")
    print("="*70)

    if not USE_CPU_FOR_INFERENCE:
        # GPU 모드
        os.environ['BNB_CUDA_VERSION'] = '121'
        print("\n🔧 GPU 모드: bitsandbytes 설치...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "bitsandbytes"],
                       capture_output=True, check=False)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "bitsandbytes>=0.43.0"],
                       check=True)
    else:
        print("\n💻 CPU 모드: bitsandbytes 건너뜀")

    print("\n📥 필수 패키지 설치 중...")
    packages = ["transformers", "datasets", "accelerate", "peft", "pandas"]
    for pkg in packages:
        print(f"  - {pkg}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
                      capture_output=True, check=True)

    print("✅ 패키지 설치 완료!")

    # ============================================================
    # STEP 2: Import
    # ============================================================

    print("\n" + "="*70)
    print("📚 STEP 2: 라이브러리 Import")
    print("="*70)

    import torch
    import gc
    import json
    import time
    import pandas as pd
    from datetime import datetime
    from pathlib import Path
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM,
    )
    from peft import PeftModel
    from google.colab import drive

    # CPU 모드에서는 BitsAndBytesConfig 불필요
    if not USE_CPU_FOR_INFERENCE:
        from transformers import BitsAndBytesConfig

    print("✅ Import 완료")

    # 디바이스 확인
    print("\n🔍 디바이스 환경 확인...")

    if USE_CPU_FOR_INFERENCE:
        device = "cpu"
        print("✅ CPU 모드로 실행")
        print(f"⚠️ 예상 소요 시간: {NUM_INFERENCE_SAMPLES * 45 / 60:.1f}분 (샘플당 ~45초)")
    else:
        if not torch.cuda.is_available():
            print("⚠️ GPU 없음! CPU 모드로 전환합니다...")
            device = "cpu"
            USE_CPU_FOR_INFERENCE = True
        else:
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ GPU: {gpu_name}")
            print(f"✅ 메모리: {gpu_memory:.2f}GB")

    # Drive 마운트
    print("\n💾 Google Drive 마운트...")
    if not Path("/content/drive").exists():
        drive.mount('/content/drive')
    print("✅ 마운트 완료")

    # 경로 설정
    BASE_MODEL = MODEL_VERSION['base_model']
    MODEL_PATH = f"/content/drive/MyDrive/ArXiv-Models/{INFERENCE_MODEL_NAME}/final_model"
    RESULTS_DIR = Path(f"/content/drive/MyDrive/ArXiv-Models/{INFERENCE_MODEL_NAME}/inference_results")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n⚙️ 설정 확인:")
    print(f"  모드: {MODE_NAME}")
    print(f"  디바이스: {device.upper()}")
    print(f"  모델: {INFERENCE_MODEL_NAME}")
    print(f"  모델 경로: {MODEL_PATH}")
    print(f"  샘플 수: {NUM_INFERENCE_SAMPLES}개")

    # 모델 존재 확인
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"❌ 모델 없음: {MODEL_PATH}\n학습된 모델이 필요합니다!")

    # ============================================================
    # STEP 3: 데이터 로드
    # ============================================================

    print("\n" + "="*70)
    print("📂 STEP 3: 테스트 데이터 로드")
    print("="*70)

    data_path = Path(DATA_DIR) / DATA_FILE

    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 없음: {data_path}")

    print(f"📥 데이터 로딩: {DATA_FILE}")
    df = pd.read_csv(data_path)
    print(f"✅ 전체 데이터: {len(df)}개")

    # 필터링
    df_success = df[df['llm_success'] == True].copy()
    print(f"✅ 성공 데이터: {len(df_success)}개")

    # 샘플 선택
    if len(df_success) > NUM_INFERENCE_SAMPLES:
        df_test = df_success.sample(n=NUM_INFERENCE_SAMPLES, random_state=42)
    else:
        df_test = df_success.head(NUM_INFERENCE_SAMPLES)

    print(f"\n📊 테스트 데이터: {len(df_test)}개")

    # ============================================================
    # STEP 4: 모델 로딩 (CPU/GPU 자동 선택)
    # ============================================================

    print("\n" + "="*70)
    print("🚀 STEP 4: 모델 로딩")
    print("="*70)

    print(f"📥 토크나이저 로딩...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print("✅ 토크나이저 로드 완료")

    print(f"\n📥 베이스 모델 로딩...")

    if USE_CPU_FOR_INFERENCE:
        # CPU 모드 - 양자화 없이 로드
        print(f"💻 CPU 모드로 로딩 중... (2-3분 소요)")
        print(f"⚠️ 메모리 사용량: 약 6-8GB")

        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,  # CPU는 float32 사용
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
    else:
        # GPU 모드 - 4bit 양자화
        print(f"🚀 GPU 모드로 로딩 중... (1-2분 소요)")

        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True
            ),
            device_map="auto",
            trust_remote_code=True
        )

    print("✅ 베이스 모델 로드 완료")

    print(f"\n📥 LoRA 어댑터 로딩...")
    model = PeftModel.from_pretrained(model, MODEL_PATH)
    model.eval()
    print("✅ 학습된 모델 로드 완료")

    print("\n💡 모델 준비 완료!")

    # ============================================================
    # STEP 5: 추론 실행
    # ============================================================

    print("\n" + "="*70)
    print(f"🔬 STEP 5: 추론 실행 ({NUM_INFERENCE_SAMPLES}개)")
    print("="*70)

    if USE_CPU_FOR_INFERENCE:
        print(f"\n⏰ CPU 모드 예상 시간:")
        print(f"  - 샘플당: 약 30-60초")
        print(f"  - 전체: 약 {NUM_INFERENCE_SAMPLES * 45 / 60:.1f}분")
        print(f"  - 커피 한잔 하고 오세요! ☕")

    def make_prompt_v4(abstract):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": abstract})
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    all_results = []

    print(f"\n🧪 추론 시작...\n")

    overall_start = time.time()

    for i, (idx, row) in enumerate(df_test.iterrows()):
        sample_num = i + 1

        print(f"{'='*70}")
        print(f"샘플 {sample_num}/{len(df_test)}")
        print(f"{'='*70}")

        abstract = row['original_abstract']
        target = row['llm_summary']

        print(f"\n📄 초록:")
        print(f"{abstract[:200]}...")

        print(f"\n🎯 목표 요약 (V4.1):")
        print(f"{target}")

        # 추론
        prompt = make_prompt_v4(abstract)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

        # 디바이스로 이동
        if USE_CPU_FOR_INFERENCE:
            inputs = {k: v.to("cpu") for k, v in inputs.items()}
        else:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        print(f"\n⏳ 추론 중... ", end="")
        sample_start = time.time()

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                min_length=30,
                temperature=TEMPERATURE,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.pad_token_id
            )

        sample_time = time.time() - sample_start
        print(f"완료! ({sample_time:.1f}초)")

        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        raw_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        summary = clean_output(raw_output, abstract)

        print(f"\n✨ 생성된 요약:")
        print(f"{summary}")

        # 분석
        word_count = len(summary.split()) if '[' not in summary else 0
        sentence_count = len(re.split(r'[.!?]+', summary.strip())) - 1 if '[' not in summary else 0

        print(f"\n📊 분석:")
        print(f"  단어 수: {word_count}개 {'✅' if word_count <= 45 else '⚠️'}")
        print(f"  문장 수: {sentence_count}개 {'✅' if sentence_count == 2 else '⚠️'}")
        print(f"  소요 시간: {sample_time:.1f}초")

        # 진행 상황
        elapsed = time.time() - overall_start
        avg_time = elapsed / sample_num
        remaining = (len(df_test) - sample_num) * avg_time

        print(f"\n⏱️ 진행 상황:")
        print(f"  완료: {sample_num}/{len(df_test)} ({sample_num/len(df_test)*100:.1f}%)")
        print(f"  경과: {elapsed/60:.1f}분")
        print(f"  예상 남은 시간: {remaining/60:.1f}분")

        all_results.append({
            "sample_id": sample_num,
            "abstract": abstract,
            "target_summary": target,
            "generated_summary": summary,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "meets_word_limit": word_count <= 45 and word_count > 0,
            "meets_sentence_count": sentence_count == 2,
            "inference_time_seconds": round(sample_time, 2)
        })

        print()

    total_elapsed = time.time() - overall_start

    # ============================================================
    # STEP 6: 결과 저장 및 분석
    # ============================================================

    print("\n" + "="*70)
    print("📊 STEP 6: 결과 분석 및 저장")
    print("="*70)

    # 통계 계산
    valid_results = [r for r in all_results if r['word_count'] > 0]

    if valid_results:
        avg_words = sum(r['word_count'] for r in valid_results) / len(valid_results)
        word_compliant = sum(1 for r in valid_results if r['meets_word_limit'])
        sentence_compliant = sum(1 for r in all_results if r['meets_sentence_count'])
        avg_inference_time = sum(r['inference_time_seconds'] for r in all_results) / len(all_results)

        print(f"\n📈 전체 통계:")
        print(f"  총 샘플: {len(all_results)}개")
        print(f"  성공: {len(valid_results)}개 ({len(valid_results)/len(all_results)*100:.1f}%)")
        print(f"  평균 단어 수: {avg_words:.1f}개")
        print(f"  45단어 이하: {word_compliant}/{len(valid_results)} ({word_compliant/len(valid_results)*100:.1f}%)")
        print(f"  2문장 구조: {sentence_compliant}/{len(all_results)} ({sentence_compliant/len(all_results)*100:.1f}%)")
        print(f"  평균 추론 시간: {avg_inference_time:.1f}초/샘플")
        print(f"  총 소요 시간: {total_elapsed/60:.1f}분")
        print(f"  디바이스: {device.upper()}")

    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    device_suffix = "cpu" if USE_CPU_FOR_INFERENCE else "gpu"
    json_file = RESULTS_DIR / f"inference_{NUM_INFERENCE_SAMPLES}samples_{device_suffix}_{timestamp}.json"

    result_data = {
        "metadata": {
            "mode": "inference_only",
            "device": device.upper(),
            "model_name": INFERENCE_MODEL_NAME,
            "num_samples": NUM_INFERENCE_SAMPLES,
            "timestamp": datetime.now().isoformat(),
            "elapsed_time_seconds": round(total_elapsed, 2),
            "avg_inference_time_seconds": round(avg_inference_time, 2) if valid_results else 0,
        },
        "statistics": {
            "total_samples": len(all_results),
            "successful": len(valid_results),
            "avg_word_count": round(avg_words, 2) if valid_results else 0,
            "word_compliant_rate": round(word_compliant/len(valid_results)*100, 2) if valid_results else 0,
            "sentence_compliant_rate": round(sentence_compliant/len(all_results)*100, 2),
        },
        "results": all_results
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 결과 저장: {json_file.name}")

    # 마크다운 리포트 생성
    md_file = RESULTS_DIR / f"inference_report_{NUM_INFERENCE_SAMPLES}samples_{device_suffix}_{timestamp}.md"

    md_content = f"""# 추론 결과 리포트 ({device.upper()})

## 📊 기본 정보
- **모델**: {INFERENCE_MODEL_NAME}
- **디바이스**: {device.upper()}
- **샘플 수**: {NUM_INFERENCE_SAMPLES}개
- **실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **소요 시간**: {total_elapsed/60:.1f}분

## 📈 성능 통계
- **총 샘플**: {len(all_results)}개
- **성공률**: {len(valid_results)}/{len(all_results)} ({len(valid_results)/len(all_results)*100:.1f}%)
- **평균 단어 수**: {avg_words:.1f}개
- **45단어 이하 준수율**: {word_compliant}/{len(valid_results)} ({word_compliant/len(valid_results)*100:.1f}%)
- **2문장 구조 준수율**: {sentence_compliant}/{len(all_results)} ({sentence_compliant/len(all_results)*100:.1f}%)
- **평균 추론 시간**: {avg_inference_time:.1f}초/샘플

## 📝 샘플 결과

"""

    for r in all_results[:min(3, len(all_results))]:
        md_content += f"""
### 샘플 {r['sample_id']}

**초록** (요약):
> {r['abstract'][:150]}...

**목표 요약**:
> {r['target_summary']}

**생성된 요약**:
> {r['generated_summary']}

**분석**:
- 단어 수: {r['word_count']}개 {'✅' if r['meets_word_limit'] else '⚠️'}
- 문장 수: {r['sentence_count']}개 {'✅' if r['meets_sentence_count'] else '⚠️'}
- 추론 시간: {r['inference_time_seconds']}초

---
"""

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"📄 리포트 저장: {md_file.name}")

    print("\n" + "="*70)
    print("✅ 추론 완료!")
    print("="*70)

    print(f"\n📁 저장 위치:")
    print(f"  결과: {json_file}")
    print(f"  리포트: {md_file}")

    print(f"\n💡 다음 단계:")
    print(f"  - 결과 파일 확인 및 분석")
    print(f"  - 샘플 개수 조정: NUM_INFERENCE_SAMPLES 변경")
    if USE_CPU_FOR_INFERENCE:
        print(f"  - GPU 사용 시 USE_CPU_FOR_INFERENCE = False로 변경")
        print(f"  - CPU는 느리므로 5개 이하 추천")

# ================================================================
# 전체 실행 (MODE 0, 1) - GPU 필요
# ================================================================

elif EXECUTION_MODE in [0, 1]:

    # GPU 체크
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError(f"""
❌ GPU 필요!

MODE {EXECUTION_MODE} (학습 모드)는 GPU가 필요합니다.

해결 방법:
1. Colab에서: 런타임 → 런타임 유형 변경 → GPU 선택
2. 추론만 하려면: MODE = 2로 변경 (CPU에서도 가능)
""")

    # [나머지 MODE 0, 1 코드는 동일...]
    print("\n⚠️ MODE 0, 1은 GPU가 필요합니다.")
    print("이 코드는 CPU 추론 지원을 위해 MODE 2만 수정되었습니다.")

print("\n" + "="*70)
print("🎉 프로그램 종료")
print("="*70)