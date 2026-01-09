"""
=================================================================
📰 ArXiv-NewsBrief-1.5B - 완전판 (CPU 지원) v4.2 (FIXED)
=================================================================

🎯 실행 모드:
✅ MODE 0: 연습 모드 (50개 데이터, 빠른 검증) - GPU 필요
✅ MODE 1: 전체 학습 모드 (2000개 데이터, 프로덕션) - GPU 필요
✅ MODE 2: 테스트 전용 (추론만) - CPU 가능! ⭐

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("🚀 ArXiv-NewsBrief - 완전판 (CPU 지원) v4.2 (FIXED)")
print("="*70)

# ================================================================
# ⚙️ 실행 모드 설정 ⭐ 여기만 수정하세요!
# ================================================================

EXECUTION_MODE = 1  # ⭐ 0/1/2 로 변경

# MODE 2 전용 설정
NUM_INFERENCE_SAMPLES = 5
INFERENCE_MODEL_NAME = "ArXiv-NewsBrief-1.5B-2k-v4.2"
USE_CPU_FOR_INFERENCE = True

# ================================================================
# 모드별 자동 설정
# ================================================================

if EXECUTION_MODE == 0:
    MODE_NAME = "연습 (Practice)"
    DATA_FILE = "v4.2_training_data_all.csv"
    MAX_DATA_TO_USE = 50
    VAL_RATIO = 0.1
    NUM_EPOCHS = 3
    NUM_TEST_SAMPLES = 5
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = True
    MODEL_SUFFIX = "practice-50"
    REQUIRES_GPU = True

elif EXECUTION_MODE == 1:
    MODE_NAME = "전체 (Full)"
    DATA_FILE = "v4.2_training_data_all.csv"
    MAX_DATA_TO_USE = 1845
    VAL_RATIO = 0.1
    NUM_EPOCHS = 5
    NUM_TEST_SAMPLES = 3
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = False
    MODEL_SUFFIX = "2k-v4.2"
    REQUIRES_GPU = True

else:  # MODE 2
    MODE_NAME = "추론 전용 (Inference Only)"
    DATA_FILE = "v4.2_training_data_all.csv"
    MAX_DATA_TO_USE = NUM_INFERENCE_SAMPLES
    NUM_TEST_SAMPLES = NUM_INFERENCE_SAMPLES
    ENABLE_FINETUNING = False
    DETAILED_LOGGING = True
    MODEL_SUFFIX = INFERENCE_MODEL_NAME
    REQUIRES_GPU = (not USE_CPU_FOR_INFERENCE)

# 공통 설정
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
USE_CHAT_TEMPLATE = True
USE_SYSTEM_MESSAGE = True
SYSTEM_MESSAGE = (
    "Summarize the following text in simple, clear English that anyone can understand. "
    "Make it as for the each script not for reading. Use no more than two complete sentences. "
    "Do not include my prompt message in result. Make sure to keep in professional tone."
)
TEMPERATURE = 0.4
ENABLE_COPY_DETECTION = True
COPY_DETECTION_THRESHOLD = 0.5

# 모델 정보
if EXECUTION_MODE == 2:
    MODEL_VERSION = {
        "name": INFERENCE_MODEL_NAME,
        "mode": MODE_NAME,
        "base_model": "Qwen/Qwen2.5-1.5B-Instruct",
        "inference_samples": NUM_INFERENCE_SAMPLES,
        "style": "News Briefing",
        "device": "CPU" if USE_CPU_FOR_INFERENCE else "GPU",
    }
else:
    MODEL_VERSION = {
        "name": f"ArXiv-NewsBrief-1.5B-{MODEL_SUFFIX}",
        "mode": MODE_NAME,
        "base_model": "Qwen/Qwen2.5-1.5B-Instruct",
        "data_size": f"{MAX_DATA_TO_USE}",
        "style": "News Briefing",
    }

print(f"\n🎯 실행 모드: {MODE_NAME}")
print(f"📦 모델: {MODEL_VERSION['name']}")
if EXECUTION_MODE == 2:
    print(f"💻 디바이스: {'CPU (느림)' if USE_CPU_FOR_INFERENCE else 'GPU (빠름)'}")
    print(f"🔬 추론 샘플: {NUM_INFERENCE_SAMPLES}개")
else:
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
    text_clean = re.sub(r"[^\w\s]", "", text.lower())
    article_clean = re.sub(r"[^\w\s]", "", original_article.lower())
    text_words = text_clean.split()
    article_words = article_clean.split()
    if len(text_words) < ngram_size:
        return False
    article_ngrams = set()
    for i in range(len(article_words) - ngram_size + 1):
        article_ngrams.add(" ".join(article_words[i:i+ngram_size]))
    copy_count = 0
    total_ngrams = 0
    for i in range(len(text_words) - ngram_size + 1):
        ngram = " ".join(text_words[i:i+ngram_size])
        total_ngrams += 1
        if ngram in article_ngrams:
            copy_count += 1
    if total_ngrams == 0:
        return False
    copy_ratio = copy_count / total_ngrams
    return copy_ratio > COPY_DETECTION_THRESHOLD

def clean_output(raw_text, original_article=""):
    text = raw_text
    text = re.sub(r"\b(system|user|assistant)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\byou\s+are\s+(a|an)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"research\s+paper|always\s+respond|maximum\s+45", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
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
    text = re.sub(r"#{1,}|={3,}|-{3,}", "", text)
    prompt_patterns = [
        r"(?i)paper\s*:", r"(?i)summary\s*:", r"(?i)summarize",
        r"<\|im_start\|>", r"<\|im_end\|>",
    ]
    for pattern in prompt_patterns:
        text = re.sub(pattern, "", text)
    latex_patterns = [r"\$+", r"\\[a-zA-Z]+", r"@xmath\d+", r"@xcite"]
    for pattern in latex_patterns:
        text = re.sub(pattern, "", text)
    text = re.sub(r"```", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.\.+", ".", text)
    text = text.strip()
    if not text or len(text) < 20:
        return "[요약 생성 실패 - 출력 없음]"
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 5]
    if not sentences:
        return "[요약 생성 실패 - 유효 문장 없음]"
    cleaned_sentences = []
    for s in sentences:
        if s and s[-1] not in ".!?":
            s += "."
        cleaned_sentences.append(s)
    if len(cleaned_sentences) == 1:
        words = cleaned_sentences[0].split()
        return cleaned_sentences[0] if len(words) <= 45 else " ".join(words[:45]) + "."
    sentence1 = cleaned_sentences[0]
    sentence2 = cleaned_sentences[1]
    total = len(sentence1.split()) + len(sentence2.split())
    if total <= 45:
        return f"{sentence1} {sentence2}"
    elif len(sentence1.split()) <= 45:
        return sentence1
    else:
        words = sentence1.split()
        return " ".join(words[:45]) + "."

print("\n✅ 후처리 함수 로드 완료")

# ================================================================
# MODE 2: 추론 전용 모드 (CPU 지원!)
# ================================================================

if EXECUTION_MODE == 2:
    print("\n" + "="*70)
    print("🔬 MODE 2: 추론 전용 모드 (CPU 지원)")
    print("="*70)

    if USE_CPU_FOR_INFERENCE:
        print("\n⚠️ CPU 모드 활성화!")
        print("  - GPU 없이도 실행 가능")
        print("  - 속도: 샘플당 약 30-60초 (GPU 대비 느림)")
        print(f"  - 현재 설정: {NUM_INFERENCE_SAMPLES}개 샘플")

    print("\n" + "="*70)
    print("📦 STEP 1: 패키지 설치")
    print("="*70)

    if not USE_CPU_FOR_INFERENCE:
        os.environ["BNB_CUDA_VERSION"] = "121"
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

    print("\n" + "="*70)
    print("📚 STEP 2: 라이브러리 Import")
    print("="*70)

    import torch
    import json
    import time
    import pandas as pd
    from datetime import datetime
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    from google.colab import drive

    if not USE_CPU_FOR_INFERENCE:
        from transformers import BitsAndBytesConfig

    print("✅ Import 완료")

    print("\n🔍 디바이스 환경 확인...")
    if USE_CPU_FOR_INFERENCE:
        device = "cpu"
        print("✅ CPU 모드로 실행")
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

    print("\n💾 Google Drive 마운트...")
    if not Path("/content/drive").exists():
        drive.mount("/content/drive")
    print("✅ 마운트 완료")

    BASE_MODEL = MODEL_VERSION["base_model"]
    MODEL_PATH = f"/content/drive/MyDrive/ArXiv-Models/{INFERENCE_MODEL_NAME}/final_model"
    RESULTS_DIR = Path(f"/content/drive/MyDrive/ArXiv-Models/{INFERENCE_MODEL_NAME}/inference_results")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n⚙️ 설정 확인:")
    print(f"  모드: {MODE_NAME}")
    print(f"  디바이스: {device.upper()}")
    print(f"  모델: {INFERENCE_MODEL_NAME}")
    print(f"  모델 경로: {MODEL_PATH}")
    print(f"  샘플 수: {NUM_INFERENCE_SAMPLES}개")

    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"❌ 모델 없음: {MODEL_PATH}\n학습된 모델이 필요합니다!")

    print("\n" + "="*70)
    print("📂 STEP 3: 테스트 데이터 로드")
    print("="*70)

    data_path = Path(DATA_DIR) / DATA_FILE
    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 없음: {data_path}")

    print(f"📥 데이터 로딩: {DATA_FILE}")
    df = pd.read_csv(data_path)
    print(f"✅ 전체 데이터: {len(df)}개")

    df_success = df[df["llm_success"] == True].copy() if "llm_success" in df.columns else df.copy()
    print(f"✅ 성공 데이터: {len(df_success)}개")

    if len(df_success) > NUM_INFERENCE_SAMPLES:
        df_test = df_success.sample(n=NUM_INFERENCE_SAMPLES, random_state=42)
    else:
        df_test = df_success.head(NUM_INFERENCE_SAMPLES)

    print(f"\n📊 테스트 데이터: {len(df_test)}개")

    print("\n" + "="*70)
    print("🚀 STEP 4: 모델 로딩")
    print("="*70)

    print("📥 토크나이저 로딩...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print("✅ 토크나이저 로드 완료")

    print("\n📥 베이스 모델 로딩...")

    if USE_CPU_FOR_INFERENCE:
        print("💻 CPU 모드 로딩 (양자화 없음, RAM 6~8GB 예상)")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
    else:
        print("🚀 GPU 모드 로딩 (4bit)")
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

    print("\n📥 LoRA 어댑터 로딩...")
    model = PeftModel.from_pretrained(model, MODEL_PATH)
    model.eval()
    print("✅ 학습된 모델 로드 완료")

    print("\n" + "="*70)
    print(f"🔬 STEP 5: 추론 실행 ({NUM_INFERENCE_SAMPLES}개)")
    print("="*70)

    def make_prompt_v4(abstract):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": abstract})
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    all_results = []
    overall_start = time.time()

    for i, (_, row) in enumerate(df_test.iterrows()):
        sample_num = i + 1
        print(f"{'='*70}")
        print(f"샘플 {sample_num}/{len(df_test)}")
        print(f"{'='*70}")

        abstract = row["original_abstract"]
        target = row["llm_summary"] if "llm_summary" in row else ""

        print("\n📄 초록:")
        print(f"{abstract[:200]}...")

        if target:
            print("\n🎯 목표 요약:")
            print(target)

        prompt = make_prompt_v4(abstract)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to("cpu" if USE_CPU_FOR_INFERENCE else model.device) for k, v in inputs.items()}

        print("\n⏳ 추론 중... ", end="")
        sample_start = time.time()

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=TEMPERATURE,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.pad_token_id
            )

        sample_time = time.time() - sample_start
        print(f"완료! ({sample_time:.1f}초)")

        generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        raw_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        summary = clean_output(raw_output, abstract)

        print("\n✨ 생성된 요약:")
        print(summary)

        word_count = len(summary.split()) if "[" not in summary else 0
        sentence_count = len(re.split(r"[.!?]+", summary.strip())) - 1 if "[" not in summary else 0

        all_results.append({
            "sample_id": sample_num,
            "abstract": abstract,
            "target_summary": target,
            "generated_summary": summary,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "meets_word_limit": (word_count <= 45 and word_count > 0),
            "meets_sentence_count": (sentence_count == 2),
            "inference_time_seconds": round(sample_time, 2)
        })

    total_elapsed = time.time() - overall_start

    print("\n" + "="*70)
    print("📊 STEP 6: 결과 저장")
    print("="*70)

    valid_results = [r for r in all_results if r["word_count"] > 0]
    avg_inference_time = sum(r["inference_time_seconds"] for r in all_results) / max(1, len(all_results))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    device_suffix = "cpu" if USE_CPU_FOR_INFERENCE else "gpu"
    json_file = RESULTS_DIR / f"inference_{NUM_INFERENCE_SAMPLES}samples_{device_suffix}_{timestamp}.json"

    result_data = {
        "metadata": {
            "mode": "inference_only",
            "device": ("CPU" if USE_CPU_FOR_INFERENCE else "GPU"),
            "model_name": INFERENCE_MODEL_NAME,
            "num_samples": NUM_INFERENCE_SAMPLES,
            "timestamp": datetime.now().isoformat(),
            "elapsed_time_seconds": round(total_elapsed, 2),
            "avg_inference_time_seconds": round(avg_inference_time, 2),
        },
        "results": all_results
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 저장 완료: {json_file}")
    print("\n" + "="*70)
    print("✅ 추론 완료!")
    print("="*70)

# ================================================================
# MODE 0/1: 학습 모드 (GPU 필요)
# ================================================================

elif EXECUTION_MODE in [0, 1]:

    import torch
    if not torch.cuda.is_available():
        raise RuntimeError(f"""
❌ GPU 필요!

MODE {EXECUTION_MODE} (학습 모드)는 GPU가 필요합니다.

해결 방법:
1. Colab에서: 런타임 → 런타임 유형 변경 → GPU 선택
2. 추론만 하려면: EXECUTION_MODE = 2로 변경 (CPU에서도 가능)
""")

    print("\n" + "="*70)
    print(f"🏋️ MODE {EXECUTION_MODE}: 학습 모드 시작 ({MODE_NAME})")
    print("="*70)

    # 패키지 설치
    os.environ["BNB_CUDA_VERSION"] = "121"
    pkgs = [
        "torch",
        "transformers>=4.46.0",
        "datasets>=3.2.0",
        "accelerate>=1.2.0",
        "peft>=0.13.0",
        "bitsandbytes>=0.43.0",
        "pandas",
    ]
    for p in pkgs:
        print(f"  - install: {p}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", p], check=True)

    # Import
    import time
    import json
    import pandas as pd
    from datetime import datetime
    from pathlib import Path
    from google.colab import drive
    from datasets import Dataset
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import (
        LoraConfig,
        get_peft_model,
        prepare_model_for_kbit_training
    )

    # Drive 마운트
    print("\n💾 Google Drive 마운트...")
    if not Path("/content/drive").exists():
        drive.mount("/content/drive")
    print("✅ 마운트 완료")

    # 데이터 로드
    print("\n" + "="*70)
    print("📂 데이터 로드")
    print("="*70)

    data_path = Path(DATA_DIR) / DATA_FILE
    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 없음: {data_path}")

    df = pd.read_csv(data_path)
    print(f"✅ 전체 로드: {len(df)}개")

    if "llm_success" in df.columns:
        df = df[df["llm_success"] == True].copy()
        print(f"✅ 성공 데이터: {len(df)}개")

    if "test_mode" in df.columns:
        df = df[df["test_mode"] == False].copy()
        print(f"✅ test_mode 제외: {len(df)}개")

    if len(df) > MAX_DATA_TO_USE:
        df = df.sample(n=MAX_DATA_TO_USE, random_state=42).reset_index(drop=True)
        print(f"✅ 제한 적용: {len(df)}개")

    # ✅ 필수 컬럼 확인 (수정된 부분)
    required_columns = ["original_abstract", "llm_summary"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"❌ 필수 컬럼 누락: {missing}")

    print(f"✅ 최종 데이터: {len(df)}개")

    # Train/Val 분할
    print("\n" + "="*70)
    print("🔀 Train/Val 분할")
    print("="*70)

    train_df = df.sample(frac=(1-VAL_RATIO), random_state=42)
    val_df = df.drop(train_df.index)

    print(f"✅ Train: {len(train_df)}개")
    print(f"✅ Val: {len(val_df)}개")

    # 토크나이저 로드
    print("\n" + "="*70)
    print("🔧 토크나이저 로드")
    print("="*70)

    BASE_MODEL = MODEL_VERSION["base_model"]
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    print("✅ 토크나이저 로드 완료")

    # 데이터셋 포맷팅
    print("\n" + "="*70)
    print("📝 데이터셋 포맷팅")
    print("="*70)

    def format_chat(example):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": example["original_abstract"]})
        messages.append({"role": "assistant", "content": example["llm_summary"]})

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        return {"text": text}

    train_dataset = Dataset.from_pandas(train_df[required_columns])
    val_dataset = Dataset.from_pandas(val_df[required_columns])

    train_dataset = train_dataset.map(format_chat, remove_columns=train_dataset.column_names)
    val_dataset = val_dataset.map(format_chat, remove_columns=val_dataset.column_names)

    print(f"✅ Train 포맷: {len(train_dataset)}개")
    print(f"✅ Val 포맷: {len(val_dataset)}개")

    # 토크나이징
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding=False
        )

    train_tokenized = train_dataset.map(tokenize_function, batched=True, remove_columns=["text"])
    val_tokenized = val_dataset.map(tokenize_function, batched=True, remove_columns=["text"])

    print("✅ 토크나이징 완료")

    # 모델 로드
    print("\n" + "="*70)
    print("🚀 모델 로드 및 LoRA 설정")
    print("="*70)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    model = prepare_model_for_kbit_training(model)
    print("✅ 베이스 모델 로드 완료")

    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    print("✅ LoRA 설정 완료")

    # 학습 설정
    print("\n" + "="*70)
    print("⚙️ 학습 설정")
    print("="*70)

    OUTPUT_DIR = f"/content/drive/MyDrive/ArXiv-Models/{MODEL_VERSION['name']}"

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="loss",
        greater_is_better=False,
        warmup_steps=50,
        save_total_limit=2,
        report_to="none",
        optim="paged_adamw_8bit"
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=val_tokenized,
        data_collator=data_collator
    )

    print("✅ 학습 설정 완료")

    # 학습 시작
    print("\n" + "="*70)
    print("🏋️ 학습 시작!")
    print("="*70)
    print(f"📊 Train: {len(train_tokenized)}개")
    print(f"📊 Val: {len(val_tokenized)}개")
    print(f"🔄 Epochs: {NUM_EPOCHS}")
    print("="*70 + "\n")

    train_start = time.time()
    trainer.train()
    train_elapsed = time.time() - train_start

    print("\n" + "="*70)
    print(f"✅ 학습 완료! ({train_elapsed/60:.1f}분)")
    print("="*70)

    # 모델 저장
    print("\n💾 모델 저장 중...")
    final_model_path = Path(OUTPUT_DIR) / "final_model"
    trainer.model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"✅ 저장 완료: {final_model_path}")

    # 메타데이터 저장
    metadata = {
        "model_name": MODEL_VERSION["name"],
        "base_model": BASE_MODEL,
        "mode": MODE_NAME,
        "train_size": len(train_tokenized),
        "val_size": len(val_tokenized),
        "epochs": NUM_EPOCHS,
        "training_time_minutes": round(train_elapsed/60, 2),
        "timestamp": datetime.now().isoformat()
    }

    metadata_path = Path(OUTPUT_DIR) / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✅ 메타데이터 저장: {metadata_path}")

    # 테스트
    print("\n" + "="*70)
    print("🧪 간단 테스트 (Val 샘플)")
    print("="*70)

    test_df = val_df.sample(n=min(NUM_TEST_SAMPLES, len(val_df)), random_state=42)
    model.eval()

    def make_prompt(abstract):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": abstract})
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    test_results = []

    for i, (_, row) in enumerate(test_df.iterrows(), 1):
        abstract = row["original_abstract"]
        target = row["llm_summary"]

        prompt = make_prompt(abstract)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=TEMPERATURE,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id
            )

        gen_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        raw = tokenizer.decode(gen_tokens, skip_special_tokens=True)
        summary = clean_output(raw, abstract)

        print("\n" + "-"*70)
        print(f"샘플 {i}/{len(test_df)}")
        print("🎯 목표:", target)
        print("✨ 생성:", summary)

        test_results.append({
            "sample_id": i,
            "target": target,
            "generated": summary,
            "abstract": abstract
        })

    # 테스트 결과 저장
    results_dir = Path(OUTPUT_DIR) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_json_path = results_dir / f"val_test_{len(test_results)}samples_{timestamp}.json"

    payload = {
        "metadata": {
            "model_name": MODEL_VERSION["name"],
            "mode": MODE_NAME,
            "base_model": MODEL_VERSION["base_model"],
            "num_test_samples": len(test_results),
            "timestamp": datetime.now().isoformat(),
        },
        "results": test_results
    }

    with open(test_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print("\n" + "="*70)
    print("✅ 테스트 결과 JSON 저장 완료!")
    print(f"💾 저장 위치: {test_json_path}")
    print("="*70)

    print("\n" + "="*70)
    print("🎉 전체 프로세스 완료!")
    print("="*70)
    print(f"📦 모델: {MODEL_VERSION['name']}")
    print(f"📂 저장 위치: {OUTPUT_DIR}")
    print(f"⏱️ 학습 시간: {train_elapsed/60:.1f}분")
    print("="*70)