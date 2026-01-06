"""
=================================================================
📰 STEP 0.4: V3 - 고품질 데이터로 모델 학습 (V3 데이터 버전)
=================================================================

🎯 V3 핵심 개선:
✅ 데이터 셋: input(초록) -> output(LLM 요약 - 2문장 45단어)
✅ 데이터 읽기: /SummaryDataSet/ 폴더에서 자동 로드
✅ V3 형식: llm_summary 컬럼 사용 (V1의 gpt4_summary → V3의 llm_summary)
✅ 유연한 데이터량: 사용 가능한 데이터 자동 감지
✅ 학습 데이터: 고품질 2문장 45단어 요약

📊 데이터 소스:
/content/drive/MyDrive/SummaryDataSet/v3_merged_all_data.csv
(또는 v3_training_data.csv)

📈 사용 시나리오:
- 200개 데이터: 180 train + 20 val
- 1000개 데이터: 900 train + 100 val ⭐ 기본값
- 2000개 데이터: 1800 train + 200 val

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*60)
print("🚀 STEP 0.4 V3 - 고품질 학습 (V3 데이터)")
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
# 데이터 설정 ⭐ V3 핵심!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
DATA_FILE = "v3_merged_all_data.csv"  # ⭐ V3 병합 데이터
# 다른 옵션: "v3_training_data.csv", "v3_training_data_0.csv" 등

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 사용량 설정 ⭐ 여기만 수정하세요!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAX_DATA_TO_USE = 1000  # ⭐ 1000개 사용
# 예시:
#   100: 빠른 테스트 (90 train + 10 val)
#   200: 빠른 검증 (180 train + 20 val)
#   1000: 목표 품질 (900 train + 100 val) ⭐ 기본값
#   2000: 최고 품질 (1800 train + 200 val)
#   0 또는 None: 전체 데이터 사용 (자동)

# 데이터 분할 비율
VAL_RATIO = 0.1  # 10%를 검증용으로

# 또는 직접 지정 (고급 설정, 보통은 0으로 두세요)
USE_TRAIN_SAMPLES = 0   # 0: 자동 계산
USE_VAL_SAMPLES = 0     # 0: 자동 계산

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 학습 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUM_EPOCHS = 5  # V3: 고품질 데이터로 5 에포크

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

def clean_output_v3(raw_text, original_article=""):
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
    return clean_output_v3(raw_text, original_article)

print(f"\n✅ 후처리 함수 V3 로드 완료")

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
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL"
    RESULTS_DIR = Path(OUTPUT_DIR) / "results"
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n⚙️ 설정:")
    print(f"  모델: Qwen2.5-1.5B-Instruct")
    print(f"  버전: V3 (고품질 학습)")
    print(f"  데이터 소스: {DATA_DIR}")
    print(f"  데이터 파일: {DATA_FILE}")
    print(f"  데이터 제한: {MAX_DATA_TO_USE if MAX_DATA_TO_USE and MAX_DATA_TO_USE > 0 else '없음 (전체 사용)'}")
    print(f"  출력: {OUTPUT_DIR}")
    
    # ============================================================
    # STEP 3: V3 데이터 로드 ⭐ 핵심!
    # ============================================================
    
    print("\n" + "="*60)
    print("📥 STEP 3: V3 데이터 로드 (SummaryDataSet)")
    print("="*60)
    
    data_path = Path(DATA_DIR) / DATA_FILE
    
    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 파일 없음: {data_path}\n"
                               f"→ V3 데이터를 먼저 생성하세요!")
    
    print(f"📥 데이터 로딩: {data_path}")
    df = pd.read_csv(data_path)
    
    print(f"✅ 원본 데이터: {len(df)}개")
    
    # V3 형식 확인
    required_columns = ['original_abstract', 'llm_summary', 'llm_success']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"❌ V3 형식 오류! 필요 컬럼 없음: {missing_columns}\n"
                        f"   현재 컬럼: {df.columns.tolist()}\n"
                        f"→ V3 형식 데이터인지 확인하세요!")
    
    # 성공한 샘플만 사용 (llm_success == True)
    df_success = df[df['llm_success'] == True].copy()
    print(f"✅ 성공 데이터: {len(df_success)}개")
    
    if len(df_success) == 0:
        raise ValueError(f"❌ 성공한 데이터 없음!\n"
                        f"→ V3 데이터를 다시 생성하세요!")
    
    # MAX_DATA_TO_USE 적용 ⭐ 핵심!
    if MAX_DATA_TO_USE and MAX_DATA_TO_USE > 0:
        if len(df_success) > MAX_DATA_TO_USE:
            print(f"\n⚙️ 데이터 제한 적용:")
            print(f"  사용 가능: {len(df_success)}개")
            print(f"  설정 제한: {MAX_DATA_TO_USE}개")
            print(f"  → {MAX_DATA_TO_USE}개만 사용합니다")
            df_success = df_success.head(MAX_DATA_TO_USE)
        else:
            print(f"\n✅ 전체 데이터 사용:")
            print(f"  사용 가능: {len(df_success)}개")
            print(f"  설정 제한: {MAX_DATA_TO_USE}개")
            print(f"  → 전체 {len(df_success)}개 사용")
    else:
        print(f"\n✅ 전체 데이터 사용: {len(df_success)}개")
    
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
    
    # Dataset 변환 ⭐ original_abstract, llm_summary 사용
    train_dataset = Dataset.from_pandas(train_df[['original_abstract', 'llm_summary']])
    val_dataset = Dataset.from_pandas(val_df[['original_abstract', 'llm_summary']])
    
    # 통계
    print(f"\n📊 LLM 요약 통계:")
    if 'llm_words' in train_df.columns:
        print(f"  평균 단어: {train_df['llm_words'].mean():.1f}")
        print(f"  45단어 이하: {(train_df['llm_words'] <= 45).sum()}/{len(train_df)} ({(train_df['llm_words'] <= 45).sum()/len(train_df)*100:.1f}%)")
    if 'llm_sentences' in train_df.columns:
        print(f"  평균 문장: {train_df['llm_sentences'].mean():.1f}")
        print(f"  2문장: {(train_df['llm_sentences'] == 2).sum()}/{len(train_df)} ({(train_df['llm_sentences'] == 2).sum()/len(train_df)*100:.1f}%)")
    if 'llm_name' in train_df.columns:
        print(f"\n  LLM 분포:")
        for llm, count in train_df['llm_name'].value_counts().items():
            print(f"    {llm}: {count}개 ({count/len(train_df)*100:.1f}%)")
    
    print("\n📋 데이터 예시:")
    sample = train_df.iloc[0]
    print(f"{'='*60}")
    print(f"원본 초록 ({sample.get('original_words', 'N/A')}단어):")
    print(f"  {sample['original_abstract'][:150]}...")
    print()
    print(f"LLM 요약 ({sample.get('llm_words', 'N/A')}단어, {sample.get('llm_sentences', 'N/A')}문장):")
    print(f"  {sample['llm_summary']}")
    if 'llm_name' in sample:
        print(f"  (생성: {sample['llm_name']})")
    print(f"{'='*60}")
    
    # ============================================================
    # STEP 4: V3 프롬프트 적용
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 STEP 4: V3 프롬프트 적용")
    print("="*60)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("✅ 토크나이저 로드")
    
    def formatting_prompts_func_v3(example):
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        messages.append({
            "role": "user",
            "content": example['original_abstract']  # ⭐ V3: original_abstract
        })
        
        messages.append({
            "role": "assistant",
            "content": example['llm_summary']  # ⭐ V3: llm_summary
        })
        
        if USE_CHAT_TEMPLATE:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False
            )
        else:
            text = f"Summarize this abstract in 2 sentences (max 45 words):\n\n{example['original_abstract']}\n\nSummary: {example['llm_summary']}"
        
        return {"text": text}
    
    print("🔄 V3 프롬프트 적용 중...")
    
    train_dataset = train_dataset.map(formatting_prompts_func_v3)
    val_dataset = val_dataset.map(formatting_prompts_func_v3)
    
    print("✅ 프롬프트 적용 완료")
    
    # ============================================================
    # STEP 5-8: 학습
    # ============================================================
    
    if ENABLE_FINETUNING:
        print("\n" + "="*60)
        print("🔤 STEP 5: 토크나이즈")
        print("="*60)
        
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
        print("🎯 STEP 7: 모델 학습 (V3)")
        print("="*60)
        
        training_args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            num_train_epochs=NUM_EPOCHS,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=4,
            eval_accumulation_steps=4,
            learning_rate=2e-4,
            logging_steps=10,
            save_steps=50,
            eval_strategy="steps",
            eval_steps=50,
            warmup_steps=10,
            fp16=True,
            report_to="none",
            max_grad_norm=1.0,
            dataloader_num_workers=0
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
        
        print("\n🏋️ 학습 시작...")
        print(f"  데이터: {train_samples}개 (V3 고품질)")
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
            "version": "V3",
            "data_source": f"{DATA_DIR}/{DATA_FILE}",
            "train_samples": train_samples,
            "val_samples": val_samples,
            "num_epochs": NUM_EPOCHS,
            "timestamp": datetime.now().isoformat()
        }
        
        if 'llm_words' in train_df.columns:
            metadata["llm_avg_words"] = float(train_df['llm_words'].mean())
        if 'llm_sentences' in train_df.columns:
            metadata["llm_avg_sentences"] = float(train_df['llm_sentences'].mean())
        
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
    print("🔬 A/B 테스트 (V3)")
    print("="*60)
    
    def make_prompt_v3(abstract):
        """V3 프롬프트 생성"""
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        messages.append({
            "role": "user",
            "content": abstract
        })
        
        if USE_CHAT_TEMPLATE:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = f"Summarize this abstract in 2 sentences (max 45 words):\n\n{abstract}\n\nSummary:"
        
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
        print("  ✅ 파인튜닝 모델 (V3)")
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
            "abstract": paper['original_abstract'],
            "llm_summary": paper['llm_summary']
        })
    
    print(f"  ✅ {len(tests)}개 논문 로드")
    
    all_results = []
    
    print("\n🧪 테스트 실행...")
    
    for i, test in enumerate(tests):
        print(f"  Test {i+1}/3...", end=" ")
        
        prompt = make_prompt_v3(test['abstract'])
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
        base_summary = clean_output(base_raw, test['abstract'])
        base_is_copy = detect_copy(base_summary, test['abstract']) if base_summary and '[' not in base_summary else False
        
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
            ft_summary = clean_output(ft_raw, test['abstract'])
            ft_is_copy = detect_copy(ft_summary, test['abstract']) if ft_summary and '[' not in ft_summary else False
        else:
            ft_summary = "N/A (파인튜닝 미사용)"
            ft_is_copy = False
        
        all_results.append({
            "test_id": test['id'],
            "abstract": test['abstract'],
            "abstract_length": len(test['abstract']),
            "llm_target": test['llm_summary'],
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
    json_file = RESULTS_DIR / f"ab_test_v3_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "version": "V3",
                "data_source": f"{DATA_DIR}/{DATA_FILE}",
                "finetuning": ENABLE_FINETUNING,
                "train_samples": train_samples,
                "val_samples": val_samples,
                "num_epochs": NUM_EPOCHS,
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
            print(f"V3 FT: {avg_ft:.1f}단어 ({len(ft_valid)}/3 성공)")
            print(f"  복사 감지: {ft_copy}건")
        else:
            print(f"V3 FT: 0/3 성공")
    
    print("\n샘플:")
    for r in all_results[:2]:
        print(f"\n초록 (길이: {r['abstract_length']}자):")
        print("-"*60)
        print(r['abstract'][:200] + "...")
        print("-"*60)
        print(f"LLM 타겟: {r['llm_target']}")
        print("-"*60)
        copy_flag_base = " ⚠️ 복사 감지" if r['base_copy_detected'] else ""
        print(f"베이스: {r['base_summary']}{copy_flag_base}")
        if ENABLE_FINETUNING:
            copy_flag_ft = " ⚠️ 복사 감지" if r['ft_copy_detected'] else ""
            print(f"V3 FT: {r['ft_summary']}{copy_flag_ft}")
    
    print("\n" + "="*60)
    print("✅ A/B 완료!")
    print("="*60)
    
    print("\n" + "="*60)
    print("✅ 완료!")
    print("="*60)
    
    print(f"\n📁 저장 위치:")
    print(f"  모델: {OUTPUT_DIR}/final_model/")
    print(f"  결과: {json_file}")
    print(f"  데이터: {DATA_DIR}/{DATA_FILE}")

# ================================================================
# MODE 1: 랜덤 테스트
# ================================================================

if MODE == 1:
    print("\n" + "="*60)
    print("🎲 랜덤 테스트 (V3)")
    print("="*60)
    
    import torch, gc, json, random
    from datetime import datetime
    from pathlib import Path
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    import pandas as pd
    
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.4-V3-FINAL"
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
        print("✅ V3 모델 로드")
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
    df_success = df[df['llm_success'] == True]
    
    print(f"✅ {len(df_success)}개 로드")
    
    random_indices = random.sample(range(len(df_success)), min(NUM_RANDOM_TESTS, len(df_success)))
    print(f"인덱스: {random_indices}")
    
    def make_prompt_v3(abstract):
        messages = []
        if USE_SYSTEM_MESSAGE:
            messages.append({"role": "system", "content": SYSTEM_MESSAGE})
        messages.append({"role": "user", "content": abstract})
        if USE_CHAT_TEMPLATE:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            return f"Summarize this abstract in 2 sentences (max 45 words):\n\n{abstract}\n\nSummary:"
    
    print("\n🔮 추론 시작...")
    
    for i, idx in enumerate(random_indices):
        paper = df_success.iloc[idx]
        
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📄 테스트 {i+1}/{len(random_indices)} (인덱스: {idx})")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        print(f"\n📖 초록 (처음 300자):")
        print("-"*60)
        print(paper['original_abstract'][:300] + "...")
        print("-"*60)
        
        print(f"\n📌 LLM 타겟 요약:")
        print("-"*60)
        print(paper['llm_summary'])
        if 'llm_words' in paper and 'llm_sentences' in paper:
            print(f"({paper['llm_words']}단어, {paper['llm_sentences']}문장)")
        if 'llm_name' in paper:
            print(f"(생성: {paper['llm_name']})")
        print("-"*60)
        
        print(f"\n🔮 V3 추론 중...")
        
        prompt = make_prompt_v3(paper['original_abstract'])
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
        clean = clean_output(raw_output, paper['original_abstract'])
        
        is_copy = detect_copy(clean, paper['original_abstract']) if clean and '[' not in clean else False
        
        print(f"\n📰 V3 요약:")
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
print("🎉 V3 완료!")
print("="*60)

print("\n✨ V3 핵심 개선:")
print("  ✅ 데이터: V3 형식 (llm_summary)")
print("  ✅ 1000개 데이터로 학습")
print("  ✅ 다양한 LLM 생성 요약")
print("  ✅ 자동 데이터 분할")
print(f"\n📁 결과: {OUTPUT_DIR}")
print(f"📁 데이터: {DATA_DIR}/{DATA_FILE}")

print("\n🚀 V3 완성!")
print("="*60)