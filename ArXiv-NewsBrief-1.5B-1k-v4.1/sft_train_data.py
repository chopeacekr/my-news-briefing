"""
=================================================================
📰 ArXiv-NewsBrief-1.5B - 완전판 (연습 모드 포함)
=================================================================

🎯 실행 모드:
✅ MODE 0: 연습 모드 (50개 데이터, 빠른 검증) ⭐ NEW!
✅ MODE 1: 전체 학습 모드 (1000개 데이터, 프로덕션)
✅ MODE 2: 테스트 전용 (추론만)

📊 연습 모드 특징:
- 50개 데이터 (45 train + 5 val)
- 3 에포크 (빠른 학습)
- 5개 테스트 샘플
- 상세한 진행 상황 출력
- 팀원 교육용 최적화

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("🚀 ArXiv-NewsBrief - 완전판")
print("="*70)

# ================================================================
# ⚙️ 실행 모드 설정 ⭐ 여기만 수정하세요!
# ================================================================

EXECUTION_MODE = 0  # ⭐ 여기를 바꾸세요!
# 0: 연습 모드 (50개, 3 epochs) - 팀원 교육용
# 1: 전체 모드 (1000개, 5 epochs) - 프로덕션
# 2: 테스트 모드 (추론만)

# ================================================================
# 모드별 자동 설정
# ================================================================

if EXECUTION_MODE == 0:
    # 연습 모드 ⭐
    MODE_NAME = "연습 (Practice)"
    DATA_FILE = "v4.1_training_data_all.csv"
    MAX_DATA_TO_USE = 50  # 50개만
    VAL_RATIO = 0.1  # 45 train + 5 val
    NUM_EPOCHS = 3  # 빠른 학습
    NUM_TEST_SAMPLES = 5  # 5개 테스트
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = True  # 상세 로그
    MODEL_SUFFIX = "practice-50"
    
elif EXECUTION_MODE == 1:
    # 전체 모드
    MODE_NAME = "전체 (Full)"
    DATA_FILE = "v4.1_training_data_all.csv"
    MAX_DATA_TO_USE = 1000
    VAL_RATIO = 0.1  # 900 train + 100 val
    NUM_EPOCHS = 5
    NUM_TEST_SAMPLES = 3
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = False
    MODEL_SUFFIX = "1k-v4.1"
    
else:  # MODE == 2
    # 테스트 모드
    MODE_NAME = "테스트 (Test Only)"
    DATA_FILE = "v4.1_training_data_all.csv"
    MAX_DATA_TO_USE = 50
    NUM_TEST_SAMPLES = 5
    ENABLE_FINETUNING = False
    DETAILED_LOGGING = True
    MODEL_SUFFIX = "test"

# 공통 설정
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
USE_CHAT_TEMPLATE = True
USE_SYSTEM_MESSAGE = True
SYSTEM_MESSAGE = "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."
TEMPERATURE = 0.7
ENABLE_COPY_DETECTION = True
COPY_DETECTION_THRESHOLD = 0.5

# 모델 정보
MODEL_VERSION = {
    'name': f'ArXiv-NewsBrief-1.5B-{MODEL_SUFFIX}',
    'mode': MODE_NAME,
    'base_model': 'Qwen/Qwen2.5-1.5B-Instruct',
    'data_size': f'{MAX_DATA_TO_USE if EXECUTION_MODE != 2 else "N/A"}',
    'style': 'News Briefing',
}

print(f"\n🎯 실행 모드: {MODE_NAME}")
print(f"📦 모델: {MODEL_VERSION['name']}")
if EXECUTION_MODE != 2:
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
# 전체 실행 (MODE 0, 1)
# ================================================================

if EXECUTION_MODE in [0, 1]:
    
    # ============================================================
    # STEP 1: 패키지 설치
    # ============================================================
    
    print("\n" + "="*70)
    print("📦 STEP 1: 패키지 설치")
    print("="*70)
    
    if DETAILED_LOGGING:
        print("\n💡 연습 모드: 패키지 설치 과정을 보여드립니다")
    
    os.environ['BNB_CUDA_VERSION'] = '121'
    
    print("\n🔧 bitsandbytes 설치...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "bitsandbytes"], 
                   capture_output=True, check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "bitsandbytes>=0.43.0"],
                   check=True)
    
    print("📥 나머지 패키지...")
    packages = ["transformers", "datasets", "accelerate", "peft", "pandas"]
    for pkg in packages:
        if DETAILED_LOGGING:
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
    from datasets import Dataset
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, 
        BitsAndBytesConfig, TrainingArguments, 
        Trainer, DataCollatorForLanguageModeling
    )
    from peft import (
        LoraConfig, get_peft_model, 
        prepare_model_for_kbit_training, PeftModel
    )
    from google.colab import drive
    
    print("✅ Import 완료")
    
    # GPU 확인
    print("\n🔍 GPU 환경 확인...")
    if not torch.cuda.is_available():
        raise RuntimeError("❌ GPU 없음!")
    
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    print(f"✅ GPU: {gpu_name}")
    print(f"✅ 메모리: {gpu_memory:.2f}GB")
    
    if DETAILED_LOGGING:
        print(f"\n💡 연습 모드: {gpu_name}는 충분합니다!")
    
    # bitsandbytes
    import bitsandbytes as bnb
    print(f"✅ bitsandbytes: {bnb.__version__}")
    
    # 메모리 정리
    gc.collect()
    torch.cuda.empty_cache()
    
    # Drive 마운트
    print("\n💾 Google Drive 마운트...")
    if not Path("/content/drive").exists():
        drive.mount('/content/drive')
    print("✅ 마운트 완료")
    
    # 출력 디렉토리
    BASE_MODEL = MODEL_VERSION['base_model']
    OUTPUT_DIR = f"/content/drive/MyDrive/ArXiv-Models/{MODEL_VERSION['name']}"
    RESULTS_DIR = Path(OUTPUT_DIR) / "results"
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n⚙️ 설정 요약:")
    print(f"  모드: {MODE_NAME}")
    print(f"  모델: {MODEL_VERSION['name']}")
    print(f"  베이스: {BASE_MODEL}")
    print(f"  데이터: {DATA_FILE}")
    print(f"  샘플 수: {MAX_DATA_TO_USE}개")
    print(f"  에포크: {NUM_EPOCHS}")
    print(f"  저장 위치: {OUTPUT_DIR}")
    
    if DETAILED_LOGGING:
        print(f"\n💡 연습 모드 팁:")
        print(f"  - 50개 데이터로 전체 파이프라인 경험")
        print(f"  - 약 10-15분 소요 예상")
        print(f"  - 실제 프로덕션과 동일한 구조")
    
    # ============================================================
    # STEP 3: 데이터 로드
    # ============================================================
    
    print("\n" + "="*70)
    print("📂 STEP 3: 데이터 로드 및 준비")
    print("="*70)
    
    data_path = Path(DATA_DIR) / DATA_FILE
    
    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 없음: {data_path}")
    
    print(f"📥 데이터 로딩: {DATA_FILE}")
    df = pd.read_csv(data_path)
    print(f"✅ 전체 데이터: {len(df)}개")
    
    # 검증
    required_columns = ['original_abstract', 'llm_summary', 'llm_success']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        raise ValueError(f"❌ 필수 컬럼 없음: {missing}")
    
    # 필터링
    df_success = df[df['llm_success'] == True].copy()
    print(f"✅ 성공 데이터: {len(df_success)}개")
    
    if 'llm_version' in df_success.columns:
        v4_count = (df_success['llm_version'] == 'V4.1').sum()
        if v4_count > 0:
            df_success = df_success[df_success['llm_version'] == 'V4.1']
            print(f"✅ V4 필터: {len(df_success)}개")
    
    if 'test_mode' in df_success.columns:
        df_success = df_success[df_success['test_mode'] == False]
    
    # 데이터 제한
    if len(df_success) > MAX_DATA_TO_USE:
        if DETAILED_LOGGING:
            print(f"\n⚙️ 데이터 샘플링:")
            print(f"  전체: {len(df_success)}개")
            print(f"  사용: {MAX_DATA_TO_USE}개")
        df_success = df_success.head(MAX_DATA_TO_USE)
    
    print(f"\n📊 최종 데이터: {len(df_success)}개")
    
    # Train/Val 분할
    total = len(df_success)
    val_samples = max(5, int(total * VAL_RATIO))
    train_samples = total - val_samples
    
    print(f"\n📊 데이터 분할:")
    print(f"  Train: {train_samples}개 ({train_samples/total*100:.1f}%)")
    print(f"  Val: {val_samples}개 ({val_samples/total*100:.1f}%)")
    
    if DETAILED_LOGGING:
        print(f"\n💡 연습 모드:")
        print(f"  - Train {train_samples}개로 모델 학습")
        print(f"  - Val {val_samples}개로 성능 검증")
        print(f"  - 실제 프로덕션과 동일한 비율")
    
    df_success = df_success.sample(frac=1, random_state=42).reset_index(drop=True)
    train_df = df_success[:train_samples]
    val_df = df_success[train_samples:train_samples + val_samples]
    
    # Dataset 생성
    train_dataset = Dataset.from_pandas(
        train_df[['original_abstract', 'llm_summary']].reset_index(drop=True)
    )
    val_dataset = Dataset.from_pandas(
        val_df[['original_abstract', 'llm_summary']].reset_index(drop=True)
    )
    
    # 통계
    print(f"\n📊 데이터 통계:")
    if 'llm_words' in train_df.columns:
        avg_words = train_df['llm_words'].mean()
        under_45 = (train_df['llm_words'] <= 45).sum()
        print(f"  평균 단어: {avg_words:.1f}")
        print(f"  45단어 이하: {under_45}/{len(train_df)} ({under_45/len(train_df)*100:.1f}%)")
    
    if 'llm_sentences' in train_df.columns:
        avg_sent = train_df['llm_sentences'].mean()
        two_sent = (train_df['llm_sentences'] == 2).sum()
        print(f"  평균 문장: {avg_sent:.1f}")
        print(f"  2문장: {two_sent}/{len(train_df)} ({two_sent/len(train_df)*100:.1f}%)")
    
    # 샘플 출력
    print(f"\n📝 데이터 샘플 (1/{len(train_df)}):")
    sample = train_df.iloc[0]
    print("="*70)
    print(f"📖 초록:")
    print(f"{sample['original_abstract'][:200]}...")
    print(f"\n✨ V4.1 요약:")
    print(f"{sample['llm_summary']}")
    if 'llm_words' in sample:
        print(f"\n📊 {sample['llm_words']}단어, {sample.get('llm_sentences', '?')}문장")
    print("="*70)
    
    if DETAILED_LOGGING:
        print(f"\n💡 이해하기:")
        print(f"  - 초록(abstract)을 입력으로")
        print(f"  - V4.1 요약을 목표로 학습")
        print(f"  - 2문장, 45단어 이하가 목표")
    
    # ============================================================
    # STEP 4: 프롬프트 적용
    # ============================================================
    
    print("\n" + "="*70)
    print("📝 STEP 4: 프롬프트 생성")
    print("="*70)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("✅ 토크나이저 로드")
    
    print(f"\n✨ 시스템 프롬프트:")
    print(f'"{SYSTEM_MESSAGE}"')
    
    if DETAILED_LOGGING:
        print(f"\n💡 프롬프트 역할:")
        print(f"  - 모델에게 작업 지시")
        print(f"  - 일반인도 이해 가능한 문장")
        print(f"  - 2문장 제한 명시")
    
    def formatting_prompts_v4(example):
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        messages.append({
            "role": "user",
            "content": example['original_abstract']
        })
        
        messages.append({
            "role": "assistant",
            "content": example['llm_summary']
        })
        
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        
        return {"text": text}
    
    print("\n🔄 프롬프트 적용 중...")
    train_dataset = train_dataset.map(formatting_prompts_v4)
    val_dataset = val_dataset.map(formatting_prompts_v4)
    print("✅ 완료")
    
    if DETAILED_LOGGING:
        print(f"\n💡 다음 단계:")
        print(f"  - 프롬프트를 토큰으로 변환")
        print(f"  - 모델이 학습 가능한 형태로 변환")
    
    # ============================================================
    # STEP 5: 토크나이즈
    # ============================================================
    
    print("\n" + "="*70)
    print("🔤 STEP 5: 토크나이즈 (텍스트→숫자)")
    print("="*70)
    
    def tokenize_function(example):
        result = tokenizer(
            example['text'],
            truncation=True,
            max_length=512,
            padding=False
        )
        result['labels'] = result['input_ids'].copy()
        return result
    
    print("🔄 토크나이즈 중...")
    train_dataset_tokenized = train_dataset.map(
        tokenize_function,
        remove_columns=train_dataset.column_names
    )
    val_dataset_tokenized = val_dataset.map(
        tokenize_function,
        remove_columns=val_dataset.column_names
    )
    print("✅ 완료")
    
    if DETAILED_LOGGING:
        print(f"\n💡 토크나이즈란?")
        print(f"  - 텍스트를 숫자(토큰)로 변환")
        print(f"  - 모델은 숫자로 학습합니다")
        print(f"  - 예: 'Hello' → [123, 456]")
    
    # ============================================================
    # STEP 6: 모델 로딩
    # ============================================================
    
    print("\n" + "="*70)
    print("🚀 STEP 6: 모델 로딩 (4-bit 양자화)")
    print("="*70)
    
    print(f"📥 {BASE_MODEL} 로딩 중...")
    
    if DETAILED_LOGGING:
        print(f"\n💡 4-bit 양자화:")
        print(f"  - 메모리 사용량 1/4로 감소")
        print(f"  - T4 GPU(15GB)에서 실행 가능")
        print(f"  - 성능은 거의 동일")
        print(f"\n⏳ 로딩 중... (1-2분 소요)")
    
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
    print("✅ 모델 로드 완료")
    
    print("\n🔧 LoRA 어댑터 설정...")
    
    if DETAILED_LOGGING:
        print(f"\n💡 LoRA란?")
        print(f"  - 전체 모델이 아닌 일부만 학습")
        print(f"  - 메모리 효율적")
        print(f"  - 빠른 학습 가능")
    
    model = prepare_model_for_kbit_training(model)
    
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    
    print("\n📊 학습 파라미터:")
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"  학습 가능: {trainable:,} ({100 * trainable / total:.2f}%)")
    print(f"  전체: {total:,}")
    
    if DETAILED_LOGGING:
        print(f"\n💡 의미:")
        print(f"  - 전체의 {100 * trainable / total:.1f}%만 학습")
        print(f"  - 나머지는 고정 (효율적)")
    
    # ============================================================
    # STEP 7: 학습
    # ============================================================
    
    print("\n" + "="*70)
    print(f"🏋️ STEP 7: 모델 학습 ({NUM_EPOCHS} 에포크)")
    print("="*70)
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        eval_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=5 if DETAILED_LOGGING else 10,
        save_steps=25 if DETAILED_LOGGING else 50,
        eval_strategy="steps",
        eval_steps=25 if DETAILED_LOGGING else 50,
        warmup_steps=5 if DETAILED_LOGGING else 10,
        fp16=True,
        report_to="none",
        max_grad_norm=1.0,
        dataloader_num_workers=0,
        save_total_limit=2,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset_tokenized,
        eval_dataset=val_dataset_tokenized,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8,
            return_tensors="pt"
        )
    )
    
    # 예상 시간 계산
    steps_per_epoch = len(train_dataset_tokenized) // 4  # gradient_accumulation
    total_steps = steps_per_epoch * NUM_EPOCHS
    estimated_minutes = total_steps * 3 / 60  # 스텝당 ~3초
    
    print(f"\n📊 학습 정보:")
    print(f"  모드: {MODE_NAME}")
    print(f"  데이터: {train_samples}개")
    print(f"  에포크: {NUM_EPOCHS}")
    print(f"  총 스텝: ~{total_steps}")
    print(f"  예상 시간: ~{estimated_minutes:.0f}분")
    
    if DETAILED_LOGGING:
        print(f"\n💡 학습 과정:")
        print(f"  - 에포크: 전체 데이터를 한 번 보는 것")
        print(f"  - {NUM_EPOCHS}번 반복 = 데이터를 {NUM_EPOCHS}번 봄")
        print(f"  - 로그가 {5 if DETAILED_LOGGING else 10}스텝마다 출력")
        print(f"\n⏳ 학습 시작... (진행 상황을 관찰하세요!)")
    
    print("="*70)
    
    start_time = time.time()
    trainer.train()
    elapsed_time = time.time() - start_time
    
    print("\n" + "="*70)
    print(f"✅ 학습 완료!")
    print("="*70)
    print(f"⏱️ 소요 시간: {elapsed_time/60:.1f}분")
    print(f"⚡ 평균 속도: {total_steps/(elapsed_time/60):.1f} 스텝/분")
    
    if DETAILED_LOGGING:
        print(f"\n💡 학습 결과:")
        print(f"  - 모델이 {train_samples}개 예시 학습 완료")
        print(f"  - 이제 새로운 초록도 요약 가능")
        print(f"  - 다음: 모델 저장 및 테스트")
    
    # ============================================================
    # STEP 8: 저장
    # ============================================================
    
    print("\n" + "="*70)
    print("💾 STEP 8: 모델 저장")
    print("="*70)
    
    final_model_path = Path(OUTPUT_DIR) / "final_model"
    trainer.model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    
    print(f"✅ 모델 저장: {final_model_path}")
    
    # 메타데이터
    metadata = {
        "model_info": MODEL_VERSION,
        "mode": MODE_NAME,
        "dataset": {
            "source": f"{DATA_DIR}/{DATA_FILE}",
            "total_used": len(df_success),
            "train_size": train_samples,
            "val_size": val_samples,
        },
        "training": {
            "num_epochs": NUM_EPOCHS,
            "learning_rate": 2e-4,
            "elapsed_time_minutes": round(elapsed_time / 60, 2),
        },
        "created_at": datetime.now().isoformat(),
    }
    
    with open(final_model_path / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 메타데이터 저장")
    
    # README
    readme_content = f"""# {MODEL_VERSION['name']}

## 🎯 모드: {MODE_NAME}

이 모델은 **{MODE_NAME}**으로 학습되었습니다.

## 📊 학습 정보

- **데이터**: {train_samples} train + {val_samples} val
- **에포크**: {NUM_EPOCHS}
- **시간**: {elapsed_time/60:.1f}분
- **날짜**: {datetime.now().strftime('%Y-%m-%d')}

## 💡 목적

{'팀원 교육 및 파이프라인 검증용' if EXECUTION_MODE == 0 else '프로덕션 품질 모델'}

## 📝 시스템 프롬프트
```
{SYSTEM_MESSAGE}
```

## 🚀 사용 방법

이 모델은 ArXiv 논문 초록을 일반인도 이해 가능한 2문장 요약으로 변환합니다.
"""
    
    with open(final_model_path / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ README 저장")
    
    # 메모리 정리
    del model, trainer
    gc.collect()
    torch.cuda.empty_cache()
    
    print("\n✅ STEP 1-8 완료!")
    
    # ============================================================
    # STEP 9: A/B 테스트
    # ============================================================
    
    print("\n" + "="*70)
    print(f"🔬 STEP 9: A/B 테스트 ({NUM_TEST_SAMPLES}개 샘플)")
    print("="*70)
    
    if DETAILED_LOGGING:
        print(f"\n💡 A/B 테스트란?")
        print(f"  - 베이스 모델 vs 학습된 모델 비교")
        print(f"  - {NUM_TEST_SAMPLES}개 논문으로 테스트")
        print(f"  - 품질 개선 확인")
    
    def make_prompt_v4(abstract):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": abstract})
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # 모델 로딩
    print("\n🤖 모델 로딩...")
    
    qwen_base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    qwen_base.eval()
    print("  ✅ 베이스 모델")
    
    qwen_ft = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    qwen_ft = PeftModel.from_pretrained(qwen_ft, final_model_path)
    qwen_ft.eval()
    print("  ✅ 학습된 모델")
    
    # 테스트 데이터
    print(f"\n📥 테스트 데이터 선택...")
    tests = []
    for i in range(min(NUM_TEST_SAMPLES, len(val_df))):
        paper = val_df.iloc[i]
        tests.append({
            "id": i + 1,
            "abstract": paper['original_abstract'],
            "llm_summary": paper['llm_summary']
        })
    print(f"  ✅ {len(tests)}개 선택")
    
    all_results = []
    
    print(f"\n🧪 테스트 실행 중...")
    
    for i, test in enumerate(tests):
        if DETAILED_LOGGING:
            print(f"\n{'='*70}")
            print(f"테스트 {i+1}/{len(tests)}")
            print(f"{'='*70}")
        else:
            print(f"  {i+1}/{len(tests)}...", end=" ")
        
        prompt = make_prompt_v4(test['abstract'])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_base.device)
        
        # 베이스
        with torch.no_grad():
            outputs = qwen_base.generate(
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
        
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        base_raw = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        base_summary = clean_output(base_raw, test['abstract'])
        
        # 학습된 모델
        with torch.no_grad():
            outputs = qwen_ft.generate(
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
        
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        ft_raw = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        ft_summary = clean_output(ft_raw, test['abstract'])
        
        all_results.append({
            "test_id": test['id'],
            "abstract": test['abstract'],
            "target": test['llm_summary'],
            "base": base_summary,
            "base_words": len(base_summary.split()) if '[' not in base_summary else 0,
            "trained": ft_summary,
            "trained_words": len(ft_summary.split()) if '[' not in ft_summary else 0,
        })
        
        if DETAILED_LOGGING:
            print(f"\n📄 초록:")
            print(f"{test['abstract'][:150]}...")
            print(f"\n🎯 목표:")
            print(f"{test['llm_summary']}")
            print(f"\n📝 베이스:")
            print(f"{base_summary}")
            print(f"\n✨ 학습된 모델:")
            print(f"{ft_summary}")
        else:
            print("✅")
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = RESULTS_DIR / f"test_{MODE_NAME.replace(' ', '_')}_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "mode": MODE_NAME,
                "model": MODEL_VERSION,
                "timestamp": datetime.now().isoformat()
            },
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 결과 저장: {json_file.name}")
    
    # 분석
    print("\n" + "="*70)
    print("📊 결과 분석")
    print("="*70)
    
    base_valid = [r for r in all_results if '[' not in r['base']]
    trained_valid = [r for r in all_results if '[' not in r['trained']]
    
    if base_valid:
        avg_base = sum(r['base_words'] for r in base_valid) / len(base_valid)
        print(f"\n베이스 모델: {avg_base:.1f}단어 ({len(base_valid)}/{len(all_results)} 성공)")
    
    if trained_valid:
        avg_trained = sum(r['trained_words'] for r in trained_valid) / len(trained_valid)
        print(f"학습된 모델: {avg_trained:.1f}단어 ({len(trained_valid)}/{len(all_results)} 성공)")
    
    if DETAILED_LOGGING:
        print(f"\n💡 결과 해석:")
        print(f"  - 성공률: 요약 생성 여부")
        print(f"  - 단어 수: 45단어 이하가 목표")
        print(f"  - 학습 효과 확인")
    
    # 샘플 출력
    print(f"\n📋 샘플 비교 (1/{len(all_results)}):")
    r = all_results[0]
    print("="*70)
    print(f"초록: {r['abstract'][:150]}...")
    print(f"\n목표: {r['target']}")
    print(f"\n베이스: {r['base']}")
    print(f"학습: {r['trained']}")
    print("="*70)
    
    print("\n" + "="*70)
    print("✅ 전체 파이프라인 완료!")
    print("="*70)
    
    print(f"\n📁 저장 위치:")
    print(f"  모델: {final_model_path}")
    print(f"  결과: {json_file}")
    
    if DETAILED_LOGGING:
        print(f"\n🎓 학습 완료!")
        print(f"  - 전체 파이프라인 경험 ✅")
        print(f"  - 데이터 로드부터 테스트까지 ✅")
        print(f"  - 다음: MODE=1로 전체 학습 시도")
        print(f"\n💡 팀 공유:")
        print(f"  - 결과 파일을 팀원들과 공유")
        print(f"  - 각 단계별 로그 검토")
        print(f"  - 질문사항 정리")

# ================================================================
# 테스트 전용 모드 (MODE 2)
# ================================================================

elif EXECUTION_MODE == 2:
    print("\n⚠️ 테스트 전용 모드는 별도 구현 필요")
    print("MODE=0 또는 MODE=1을 사용하세요")

print("\n" + "="*70)
print("🎉 프로그램 종료")
print("="*70)