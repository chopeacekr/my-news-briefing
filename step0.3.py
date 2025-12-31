"""
=================================================================
📰 STEP 0.3: V10 Step 2 - 고품질 데이터로 모델 학습 (개선 버전)
=================================================================

🎯 V10 핵심 개선:
✅ 데이터 읽기: /SummaryDataSet/ 폴더에서 자동 로드
✅ 유연한 데이터량: 사용 가능한 데이터 자동 감지
✅ 학습 데이터: GPT-4 2문장 45단어 고품질 요약

📊 데이터 소스:
/content/drive/MyDrive/SummaryDataSet/v10_training_data.csv

📈 사용 시나리오:
- 200개 데이터: 180 train + 20 val
- 1000개 데이터: 900 train + 100 val
- 2000개 데이터: 1800 train + 200 val

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*60)
print("🚀 STEP 0.3 V10 - 고품질 학습 (개선)")
print("="*60)

# ================================================================
# ⚙️ 설정 - 여기만 수정하세요!
# ================================================================

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실행 모드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE = 0  # 0: 전체 실행 (학습+테스트), 1: 랜덤 테스트만
ENABLE_FINETUNING = True

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 설정 ⭐ V10 핵심!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
DATA_FILE = "v10_training_data.csv"

# 데이터 분할 비율 (자동 계산)
VAL_RATIO = 0.1  # 10%를 검증용으로

# 또는 직접 지정 (0으로 설정 시 자동 계산)
USE_TRAIN_SAMPLES = 0   # 0: 자동
USE_VAL_SAMPLES = 0     # 0: 자동

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 학습 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUM_EPOCHS = 5  # V10: 고품질 데이터로 5 에포크

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 챗 템플릿 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_CHAT_TEMPLATE = True
USE_SYSTEM_MESSAGE = True

SYSTEM_MESSAGE = "You are a research paper summarization expert. Always respond with exactly 2 sentences, maximum 45 words."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 생성 파라미터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEMPERATURE = 0.7

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 후처리 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST_PROCESS_MODE = "smart"
ENABLE_COPY_DETECTION = True
COPY_DETECTION_THRESHOLD = 0.5

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUM_RANDOM_TESTS = 3

# ================================================================

import re

# 후처리 함수
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

def clean_output_v10(raw_text, original_article=""):
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

def clean_output(raw_text, original_article=""):
    return clean_output_v10(raw_text, original_article)

print(f"\n✅ 후처리 함수 V10 로드 완료")

# ================================================================
# MODE 0: 전체 실행
# ================================================================

if MODE == 0:
    
    # ============================================================
    # STEP 1: 패키지 설치
    # ============================================================
    
    print("\n" + "="*60)
    print("📦 STEP 1: 패키지 설치")
    print("="*60)
    
    os.environ['BNB_CUDA_VERSION'] = '121'
    
    print("\n🔧 CUDA 호환 bitsandbytes 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "bitsandbytes"], 
                   capture_output=True, check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "bitsandbytes>=0.43.0"],
                   check=True)
    
    print("📥 나머지 패키지 설치 중...")
    packages = ["transformers", "datasets", "accelerate", "peft", "pandas"]
    for pkg in packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
                      capture_output=True, check=True)
    
    print("✅ 패키지 설치 완료!")
    
    # ============================================================
    # STEP 2: Import 및 설정
    # ============================================================
    
    print("\n" + "="*60)
    print("📚 STEP 2: Import 및 초기 설정")
    print("="*60)
    
    import torch
    import gc
    import json
    import csv
    import random
    import pandas as pd
    from datetime import datetime
    from pathlib import Path
    from datasets import Dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments, Trainer, DataCollatorForLanguageModeling
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
    from google.colab import drive
    
    print("✅ Import 완료")
    
    # GPU 확인
    print("\n🔍 GPU 확인...")
    if not torch.cuda.is_available():
        raise RuntimeError("❌ GPU 없음! Runtime → Change runtime type → T4 GPU")
    
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ 메모리: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    
    # bitsandbytes 확인
    print("\n🔍 bitsandbytes 확인...")
    import bitsandbytes as bnb
    print(f"✅ bitsandbytes {bnb.__version__}")
    
    # 메모리 정리
    gc.collect()
    torch.cuda.empty_cache()
    
    # Drive 마운트
    print("\n💾 Drive 마운트...")
    if not Path("/content/drive").exists():
        drive.mount('/content/drive')
    print("✅ 마운트 완료")
    
    # 설정
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V10-FINAL"
    RESULTS_DIR = Path(OUTPUT_DIR) / "results"
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n⚙️ 설정:")
    print(f"  모델: Qwen2.5-1.5B-Instruct")
    print(f"  버전: V10 (고품질 학습)")
    print(f"  데이터 소스: {DATA_DIR}")
    print(f"  출력: {OUTPUT_DIR}")
    
    # ============================================================
    # STEP 3: V10 데이터 로드 ⭐ 핵심!
    # ============================================================
    
    print("\n" + "="*60)
    print("📥 STEP 3: V10 데이터 로드 (SummaryDataSet)")
    print("="*60)
    
    data_path = Path(DATA_DIR) / DATA_FILE
    
    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 파일 없음: {data_path}\n"
                               f"→ Step 1을 먼저 실행하세요!")
    
    print(f"📥 데이터 로딩: {data_path}")
    df = pd.read_csv(data_path)
    
    # 성공한 샘플만 사용
    df_success = df[df['gpt4_success'] == True].copy()
    print(f"✅ 원본 데이터: {len(df)}개")
    print(f"✅ 성공 데이터: {len(df_success)}개")
    
    if len(df_success) == 0:
        raise ValueError(f"❌ 성공한 데이터 없음!\n"
                        f"→ Step 1을 다시 실행하세요!")
    
    # 데이터량 자동 계산
    total_available = len(df_success)
    
    if USE_VAL_SAMPLES == 0:
        # 자동 계산
        val_samples = max(10, int(total_available * VAL_RATIO))
        train_samples = total_available - val_samples
    else:
        # 직접 지정
        val_samples = USE_VAL_SAMPLES
        if USE_TRAIN_SAMPLES == 0:
            train_samples = total_available - val_samples
        else:
            train_samples = USE_TRAIN_SAMPLES
    
    # 검증
    if train_samples + val_samples > total_available:
        print(f"\n⚠️ 요청한 데이터량이 사용 가능한 양보다 많습니다!")
        print(f"  요청: {train_samples + val_samples}개")
        print(f"  가능: {total_available}개")
        print(f"\n자동으로 조정합니다...")
        val_samples = max(10, int(total_available * VAL_RATIO))
        train_samples = total_available - val_samples
    
    print(f"\n📊 데이터 분할:")
    print(f"  사용 가능: {total_available}개")
    print(f"  Train: {train_samples}개 ({train_samples/total_available*100:.1f}%)")
    print(f"  Val: {val_samples}개 ({val_samples/total_available*100:.1f}%)")
    print(f"  총 사용: {train_samples + val_samples}개")
    
    # Train/Val 분할
    df_success = df_success.sample(frac=1, random_state=42).reset_index(drop=True)
    
    train_df = df_success[:train_samples]
    val_df = df_success[train_samples:train_samples + val_samples]
    
    # Dataset 변환
    train_dataset = Dataset.from_pandas(train_df[['article', 'gpt4_summary']])
    val_dataset = Dataset.from_pandas(val_df[['article', 'gpt4_summary']])
    
    # 통계
    print(f"\n📊 GPT-4 요약 통계:")
    print(f"  평균 단어: {train_df['gpt4_words'].mean():.1f}")
    print(f"  평균 문장: {train_df['gpt4_sentences'].mean():.1f}")
    print(f"  45단어 이하: {(train_df['gpt4_words'] <= 45).sum()}/{len(train_df)} ({(train_df['gpt4_words'] <= 45).sum()/len(train_df)*100:.1f}%)")
    print(f"  2문장: {(train_df['gpt4_sentences'] == 2).sum()}/{len(train_df)} ({(train_df['gpt4_sentences'] == 2).sum()/len(train_df)*100:.1f}%)")
    
    print("\n📋 데이터 예시:")
    sample = train_df.iloc[0]
    print(f"{'='*60}")
    print(f"원본 초록 ({sample['original_words']}단어):")
    print(f"  {sample['original_abstract'][:150]}...")
    print()
    print(f"GPT-4 요약 ({sample['gpt4_words']}단어, {sample['gpt4_sentences']}문장):")
    print(f"  {sample['gpt4_summary']}")
    print(f"{'='*60}")
    
    # ============================================================
    # STEP 4: V10 프롬프트 적용
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 STEP 4: V10 프롬프트 적용")
    print("="*60)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("✅ 토크나이저 로드")
    
    def formatting_prompts_func_v10(example):
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        messages.append({
            "role": "user",
            "content": example['article']
        })
        
        messages.append({
            "role": "assistant",
            "content": example['gpt4_summary']
        })
        
        if USE_CHAT_TEMPLATE:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
        else:
            text = f"Summarize this paper in 2 sentences (max 45 words):\n\n{example['article']}\n\nSummary: {example['gpt4_summary']}"
        
        return {"text": text}
    
    print("🔄 V10 프롬프트 적용 중...")
    
    train_dataset = train_dataset.map(formatting_prompts_func_v10)
    val_dataset = val_dataset.map(formatting_prompts_func_v10)
    
    print("✅ 프롬프트 적용 완료")
    
    # ============================================================
    # STEP 5-8: 학습 (나머지는 동일)
    # ============================================================
    
    if ENABLE_FINETUNING:
        print("\n" + "="*60)
        print("🔤 STEP 5: 토크나이즈")
        print("="*60)
        
        def tokenize_function(example):
            result = tokenizer(example['text'], truncation=True, max_length=512, padding=False)
            result['labels'] = result['input_ids'].copy()
            return result
        
        print("🔄 토크나이즈 중...")
        train_dataset_tokenized = train_dataset.map(tokenize_function, remove_columns=train_dataset.column_names)
        val_dataset_tokenized = val_dataset.map(tokenize_function, remove_columns=val_dataset.column_names)
        print("✅ 토크나이즈 완료")
        
        print("\n" + "="*60)
        print("🚀 STEP 6: 모델 로딩 (4-bit)")
        print("="*60)
        
        print("📥 Qwen2.5-1.5B-Instruct 로딩 중...")
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
        
        print("\n🔧 LoRA 준비 중...")
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
        
        print("\n📊 학습 가능한 파라미터:")
        model.print_trainable_parameters()
        
        print("\n" + "="*60)
        print("🎯 STEP 7: 모델 학습 (V10)")
        print("="*60)
        
        training_args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            num_train_epochs=NUM_EPOCHS,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            logging_steps=10,
            save_steps=50,
            eval_strategy="steps",
            eval_steps=50,
            warmup_steps=10,
            fp16=True,
            report_to="none",
            max_grad_norm=1.0
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset_tokenized,
            eval_dataset=val_dataset_tokenized,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
        )
        
        print("\n🏋️ 학습 시작...")
        print(f"  데이터: {train_samples}개 (GPT-4 고품질)")
        print(f"  Epochs: {NUM_EPOCHS}")
        print(f"  예상 시간: ~{train_samples * NUM_EPOCHS // 3}분")
        print()
        
        trainer.train()
        
        print("\n✅ 학습 완료!")
        
        print("\n" + "="*60)
        print("💾 STEP 8: 모델 저장")
        print("="*60)
        
        final_model_path = Path(OUTPUT_DIR) / "final_model"
        trainer.model.save_pretrained(final_model_path)
        tokenizer.save_pretrained(final_model_path)
        
        print(f"✅ 저장 완료: {final_model_path}")
        
        # 메타데이터
        metadata = {
            "model": BASE_MODEL,
            "version": "V10",
            "data_source": f"{DATA_DIR}/{DATA_FILE}",
            "train_samples": train_samples,
            "val_samples": val_samples,
            "num_epochs": NUM_EPOCHS,
            "gpt4_avg_words": float(train_df['gpt4_words'].mean()),
            "gpt4_avg_sentences": float(train_df['gpt4_sentences'].mean()),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(final_model_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        del model, trainer
        gc.collect()
        torch.cuda.empty_cache()
        
        print("\n✅ STEP 1-8 완료!")
    
    else:
        print("\n⏭️  파인튜닝 건너뛰기")
        final_model_path = None
    
    # ============================================================
    # A/B 테스트
    # ============================================================
    
    print("\n" + "="*60)
    print("🔬 A/B 테스트 (V10)")
    print("="*60)
    
    def make_prompt_v10(article):
        """V10 프롬프트 생성"""
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        messages.append({
            "role": "user",
            "content": article
        })
        
        if USE_CHAT_TEMPLATE:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = f"Summarize this paper in 2 sentences (max 45 words):\n\n{article}\n\nSummary:"
        
        return prompt
    
    # 모델 로딩
    print("\n🤖 모델 로딩...")
    
    qwen_base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto", trust_remote_code=True
    )
    qwen_base.eval()
    print("  ✅ 베이스 모델")
    
    if ENABLE_FINETUNING and final_model_path:
        qwen_ft = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            device_map="auto", trust_remote_code=True
        )
        qwen_ft = PeftModel.from_pretrained(qwen_ft, final_model_path)
        qwen_ft.eval()
        print("  ✅ 파인튜닝 모델 (V10)")
    else:
        qwen_ft = None
        print("  ⏭️  파인튜닝 모델 없음")
    
    # 테스트 데이터
    print("\n📥 테스트용 논문 로딩...")
    
    tests = []
    for i in range(min(3, len(val_df))):
        paper = val_df.iloc[i]
        tests.append({
            "id": i + 1,
            "article": paper['article'],
            "original_abstract": paper['original_abstract'],
            "gpt4_summary": paper['gpt4_summary']
        })
    
    print(f"  ✅ {len(tests)}개 논문 로드")
    
    all_results = []
    
    print("\n🧪 테스트 실행...")
    
    for i, test in enumerate(tests):
        print(f"  Test {i+1}/3...", end=" ")
        
        prompt = make_prompt_v10(test['article'])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_base.device)
        
        # 베이스
        with torch.no_grad():
            outputs = qwen_base.generate(
                **inputs, max_new_tokens=80, min_length=30, 
                temperature=TEMPERATURE,
                do_sample=True, top_p=0.9, repetition_penalty=1.2,
                no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
            )
        
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        base_raw = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        base_summary = clean_output(base_raw, test['article'])
        base_is_copy = detect_copy(base_summary, test['article']) if base_summary and '[' not in base_summary else False
        
        # 파인튜닝
        if ENABLE_FINETUNING and qwen_ft:
            with torch.no_grad():
                outputs = qwen_ft.generate(
                    **inputs, max_new_tokens=80, min_length=30, 
                    temperature=TEMPERATURE,
                    do_sample=True, top_p=0.9, repetition_penalty=1.2,
                    no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
                )
            
            generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            ft_raw = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            ft_summary = clean_output(ft_raw, test['article'])
            ft_is_copy = detect_copy(ft_summary, test['article']) if ft_summary and '[' not in ft_summary else False
        else:
            ft_summary = "N/A (파인튜닝 미사용)"
            ft_is_copy = False
        
        all_results.append({
            "test_id": test['id'],
            "article": test['article'],
            "article_length": len(test['article']),
            "original_abstract": test['original_abstract'],
            "gpt4_target": test['gpt4_summary'],
            "base_summary": base_summary,
            "base_words": len(base_summary.split()) if '[' not in base_summary else 0,
            "base_copy_detected": base_is_copy,
            "ft_summary": ft_summary,
            "ft_words": len(ft_summary.split()) if '[' not in ft_summary and ft_summary != "N/A (파인튜닝 미사용)" else 0,
            "ft_copy_detected": ft_is_copy
        })
        
        print("✅")
    
    # 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = RESULTS_DIR / f"ab_test_v10_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "version": "V10",
                "data_source": f"{DATA_DIR}/{DATA_FILE}",
                "finetuning": ENABLE_FINETUNING,
                "train_samples": train_samples,
                "val_samples": val_samples,
                "num_epochs": NUM_EPOCHS,
                "gpt4_avg_words": float(train_df['gpt4_words'].mean()),
                "gpt4_avg_sentences": float(train_df['gpt4_sentences'].mean()),
                "temperature": TEMPERATURE,
                "timestamp": datetime.now().isoformat()
            },
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 저장: {json_file.name}")
    
    # 분석
    print("\n" + "="*60)
    print("📊 결과 분석")
    print("="*60)
    
    base_valid = [r for r in all_results if '[' not in r['base_summary']]
    base_copy = sum(1 for r in all_results if r['base_copy_detected'])
    
    if base_valid:
        avg_base = sum(r['base_words'] for r in base_valid) / len(base_valid)
        print(f"\n베이스: {avg_base:.1f}단어 ({len(base_valid)}/3 성공)")
        print(f"  복사 감지: {base_copy}건")
    else:
        print(f"\n베이스: 0/3 성공")
    
    if ENABLE_FINETUNING:
        ft_valid = [r for r in all_results if '[' not in r['ft_summary'] and r['ft_summary'] != "N/A (파인튜닝 미사용)"]
        ft_copy = sum(1 for r in all_results if r['ft_copy_detected'])
        
        if ft_valid:
            avg_ft = sum(r['ft_words'] for r in ft_valid) / len(ft_valid)
            print(f"V10 FT: {avg_ft:.1f}단어 ({len(ft_valid)}/3 성공)")
            print(f"  복사 감지: {ft_copy}건")
        else:
            print(f"V10 FT: 0/3 성공")
    
    print("\n샘플:")
    for r in all_results[:2]:
        print(f"\n논문 (길이: {r['article_length']}자):")
        print("-"*60)
        print(r['article'][:200] + "...")
        print("-"*60)
        print(f"GPT-4 타겟: {r['gpt4_target']}")
        print("-"*60)
        copy_flag_base = " ⚠️ 복사 감지" if r['base_copy_detected'] else ""
        print(f"베이스: {r['base_summary']}{copy_flag_base}")
        if ENABLE_FINETUNING:
            copy_flag_ft = " ⚠️ 복사 감지" if r['ft_copy_detected'] else ""
            print(f"V10 FT: {r['ft_summary']}{copy_flag_ft}")
    
    print("\n" + "="*60)
    print("✅ A/B 완료!")
    print("="*60)
    
    # LLM 분석용 프롬프트
    print("\n" + "="*60)
    print("📝 LLM 분석용 프롬프트 생성")
    print("="*60)
    
    analysis_prompt = f"""다음은 ArXiv 논문 요약 모델(V10)의 A/B 테스트 결과입니다.

## 모델 설정

**버전:** V10 (GPT-4 고품질 학습)
**데이터 소스:** {DATA_DIR}/{DATA_FILE}
**학습 데이터:** {train_samples}개
**검증 데이터:** {val_samples}개
**에포크:** {NUM_EPOCHS}
**GPT-4 품질:** {train_df['gpt4_words'].mean():.1f}단어, {train_df['gpt4_sentences'].mean():.1f}문장

## 테스트 결과

"""
    
    for i, r in enumerate(all_results, 1):
        analysis_prompt += f"""
### Test {i}

**논문 원문 (전체):**
```
{r['article']}
```

**GPT-4 타겟 요약:**
```
{r['gpt4_target']}
```

**베이스:**
```
{r['base_summary']}
```
- 단어: {r['base_words']}
- 복사: {'⚠️ 예' if r['base_copy_detected'] else '아니오'}

"""
        
        if ENABLE_FINETUNING and r['ft_summary'] != "N/A (파인튜닝 미사용)":
            analysis_prompt += f"""**V10 파인튜닝:**
```
{r['ft_summary']}
```
- 단어: {r['ft_words']}
- 복사: {'⚠️ 예' if r['ft_copy_detected'] else '아니오'}

"""
    
    analysis_prompt += """
## 분석 요청

1. **형식**: 2문장, 45단어 이하?
2. **내용**: GPT-4 타겟과 비교했을 때 품질은?
3. **V10 개선 효과**: GPT-4 고품질 학습이 효과있었나?
4. **점수**: 각 출력에 10점 만점 점수
5. **V9.1 대비**: V9.1(3.3/10) 대비 얼마나 개선되었나?

---

**상세 분석 부탁드립니다!**
"""
    
    prompt_file = RESULTS_DIR / f"analysis_prompt_v10_{timestamp}.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(analysis_prompt)
    
    print(f"✅ 분석 프롬프트 저장: {prompt_file.name}")
    
    print("\n" + "="*60)
    print("✅ 완료!")
    print("="*60)
    
    print(f"\n📁 저장 위치:")
    print(f"  모델: {OUTPUT_DIR}/final_model/")
    print(f"  결과: {json_file}")
    print(f"  프롬프트: {prompt_file}")
    print(f"  데이터: {DATA_DIR}/{DATA_FILE}")

# ================================================================
# MODE 1: 랜덤 테스트
# ================================================================

if MODE == 1:
    print("\n" + "="*60)
    print("🎲 랜덤 테스트 (V10)")
    print("="*60)
    
    import torch, gc, json, random
    from datetime import datetime
    from pathlib import Path
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    import pandas as pd
    
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V10-FINAL"
    final_model_path = Path(OUTPUT_DIR) / "final_model"
    
    # 토크나이저
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 모델 로드
    if ENABLE_FINETUNING:
        if not final_model_path.exists():
            raise FileNotFoundError(f"모델 없음: {final_model_path}")
        
        qwen_ft = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            device_map="auto", trust_remote_code=True
        )
        qwen_ft = PeftModel.from_pretrained(qwen_ft, final_model_path)
        qwen_ft.eval()
        print("✅ V10 모델 로드")
    else:
        qwen_ft = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            device_map="auto", trust_remote_code=True
        )
        qwen_ft.eval()
        print("✅ 베이스 모델 로드")
    
    # 데이터 로드
    data_path = Path(DATA_DIR) / DATA_FILE
    if not data_path.exists():
        raise FileNotFoundError(f"데이터 없음: {data_path}")
    
    df = pd.read_csv(data_path)
    df_success = df[df['gpt4_success'] == True]
    
    print(f"✅ {len(df_success)}개 로드")
    
    random_indices = random.sample(range(len(df_success)), min(NUM_RANDOM_TESTS, len(df_success)))
    print(f"인덱스: {random_indices}")
    
    def make_prompt_v10(article):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": article})
        if USE_CHAT_TEMPLATE:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            return f"Summarize this paper in 2 sentences (max 45 words):\n\n{article}\n\nSummary:"
    
    print("\n🔮 추론 시작...")
    
    for i, idx in enumerate(random_indices):
        paper = df_success.iloc[idx]
        
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📄 테스트 {i+1}/{len(random_indices)} (인덱스: {idx})")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        print(f"\n📖 논문 (처음 300자):")
        print("-"*60)
        print(paper['article'][:300] + "...")
        print("-"*60)
        
        print(f"\n📌 GPT-4 타겟 요약:")
        print("-"*60)
        print(paper['gpt4_summary'])
        print(f"({paper['gpt4_words']}단어, {paper['gpt4_sentences']}문장)")
        print("-"*60)
        
        print(f"\n🔮 V10 추론 중...")
        
        prompt = make_prompt_v10(paper['article'])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_ft.device)
        
        with torch.no_grad():
            outputs = qwen_ft.generate(
                **inputs, max_new_tokens=80, min_length=30, 
                temperature=TEMPERATURE,
                do_sample=True, top_p=0.9, repetition_penalty=1.2,
                no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
            )
        
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        raw_output = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        clean = clean_output(raw_output, paper['article'])
        
        is_copy = detect_copy(clean, paper['article']) if clean and '[' not in clean else False
        
        print(f"\n📰 V10 요약:")
        print("="*60)
        print(clean)
        if is_copy:
            print("\n⚠️ 복사 경고: 5-gram 분석 결과 논문과 겹침 감지")
        print("="*60)
        
        is_failed = '[' in clean
        word_count = 0 if is_failed else len(clean.split())
        sentence_count = 0 if is_failed else len([s for s in re.split(r'[.!?]+', clean) if s.strip()])
        
        print(f"\n📊 통계:")
        print(f"  성공: {'❌' if is_failed else '✅'}")
        if is_copy:
            print(f"  복사 경고: ⚠️")
        if not is_failed:
            print(f"  단어: {word_count}")
            print(f"  문장: {sentence_count}")
            print(f"  45단어: {'✅' if word_count <= 45 else '❌'}")
            print(f"  2문장: {'✅' if sentence_count == 2 else '⚠️ ' + str(sentence_count)}")

print("\n" + "="*60)
print("🎉 V10 완료!")
print("="*60)

print("\n✨ V10 핵심 개선:")
print("  ✅ 데이터: /SummaryDataSet/ 자동 로드")
print("  ✅ GPT-4 고품질 2문장 요약으로 학습")
print("  ✅ 자동 데이터 분할")
print("  ✅ 예상 성능: 7-8/10")
print(f"\n📁 결과: {OUTPUT_DIR}")
print(f"📁 데이터: {DATA_DIR}")

print("\n🚀 V10 완성!")
print("="*60)