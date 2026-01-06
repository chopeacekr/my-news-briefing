"""
=================================================================
📰 ArXiv-NewsBrief-1.5B-1k-v4.0 - 뉴스 브리핑 스타일 모델 학습
=================================================================

🎯 모델명: ArXiv-NewsBrief-1.5B-1k-v4.0

📊 V4 핵심:
✅ 데이터: v4_training_data_all.csv (1000개)
✅ 스타일: 일반인도 이해 가능한 뉴스 브리핑
✅ 프롬프트: 단순하고 명확
✅ 모델: Qwen2.5-1.5B-Instruct + LoRA

🔄 버전 히스토리:
- V3.0: ArXiv-Academic-1.5B-600-v3.0 (학술 스타일, 600개)
- V4.0: ArXiv-NewsBrief-1.5B-1k-v4.0 (뉴스 스타일, 1000개) ⭐ NEW

=================================================================
"""

import subprocess
import sys
import os
import json
import re
import time
import random
import torch
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

print("\n" + "="*70)
print("🚀 ArXiv-NewsBrief-1.5B-1k-v4.0")
print("="*70)

# ================================================================
# ⭐⭐⭐ V4.0 설정 ⭐⭐⭐
# ================================================================

# 모델 정보
MODEL_VERSION = {
    'name': 'ArXiv-NewsBrief-1.5B-1k-v4.0',
    'major': 4,
    'minor': 0,
    'patch': 0,
    'base_model': 'Qwen/Qwen2.5-1.5B-Instruct',
    'base_size': '1.5B',
    'data_size': '1k',
    'style': 'News Briefing',
    'target': 'General Audience'
}

print(f"\n📦 모델 정보:")
print(f"   이름: {MODEL_VERSION['name']}")
print(f"   버전: v{MODEL_VERSION['major']}.{MODEL_VERSION['minor']}.{MODEL_VERSION['patch']}")
print(f"   베이스: {MODEL_VERSION['base_model']}")
print(f"   데이터: {MODEL_VERSION['data_size']}")
print(f"   스타일: {MODEL_VERSION['style']}")
print(f"   타겟: {MODEL_VERSION['target']}")

# 데이터 설정
DATA_CONFIG = {
    'source_file': 'v4_training_data_all.csv',
    'max_samples': 1000,
    'train_split': 0.9,
    'val_split': 0.1
}

# 학습 설정
TRAINING_CONFIG = {
    'num_epochs': 5,
    'learning_rate': 2e-4,
    'batch_size': 1,
    'gradient_accumulation_steps': 4,
    'max_length': 512,
    'warmup_steps': 10,
    'fp16': True
}

# LoRA 설정
LORA_CONFIG = {
    'r': 16,
    'alpha': 32,
    'dropout': 0.1,
    'target_modules': ["q_proj", "k_proj", "v_proj", "o_proj"]
}

# 생성 설정
GENERATION_CONFIG = {
    'temperature': 0.7,
    'top_p': 0.9,
    'max_new_tokens': 80,
    'do_sample': True
}

print("\n⚙️ 학습 설정:")
print(f"   에포크: {TRAINING_CONFIG['num_epochs']}")
print(f"   학습률: {TRAINING_CONFIG['learning_rate']}")
print(f"   LoRA r: {LORA_CONFIG['r']}")
print(f"   LoRA alpha: {LORA_CONFIG['alpha']}")
print("="*70)

# ================================================================
# STEP 1: 패키지 설치
# ================================================================

print("\n" + "="*70)
print("📦 STEP 1: 필수 패키지 설치")
print("="*70)

packages = [
    "transformers",
    "datasets", 
    "accelerate",
    "peft",
    "bitsandbytes",
    "trl",
    "pandas",
    "numpy",
    "torch"
]

print("📥 패키지 설치 중...")
for pkg in packages:
    print(f"  - {pkg}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
        capture_output=True,
        check=True
    )

print("✅ 모든 패키지 설치 완료!")

# ================================================================
# STEP 2: Import 및 기본 설정
# ================================================================

print("\n" + "="*70)
print("📚 STEP 2: Import 및 초기 설정")
print("="*70)

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
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
from datasets import Dataset
from google.colab import drive

print("✅ Import 완료")

# Drive 마운트
print("\n💾 Drive 마운트...")
if not Path("/content/drive").exists():
    drive.mount('/content/drive')
print("✅ Drive 마운트 완료")

# ================================================================
# STEP 3: V4 데이터 로드 및 검증
# ================================================================

print("\n" + "="*70)
print("📂 STEP 3: V4 데이터 로드 및 검증")
print("="*70)

# 데이터 경로
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
DATA_FILE = DATA_CONFIG['source_file']
data_path = Path(DATA_DIR) / DATA_FILE

# 데이터 로드
print(f"📥 데이터 로드 중...")
print(f"   파일: {DATA_FILE}")

if not data_path.exists():
    raise FileNotFoundError(f"❌ 데이터 파일 없음: {data_path}")

df = pd.read_csv(data_path)
print(f"✅ 로드 완료: {len(df)}개 샘플")

# V4 데이터 검증
print("\n🔍 V4.0 데이터 검증...")

# 필수 컬럼 확인
required_columns = ['original_abstract', 'llm_summary', 'llm_success']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"❌ 필수 컬럼 없음: {missing_columns}")

print("✅ 필수 컬럼 확인 완료")

# 성공한 데이터만 선택
df_success = df[df['llm_success'] == True].copy()
print(f"✅ 성공 데이터: {len(df_success)}개 (성공률: {len(df_success)/len(df)*100:.1f}%)")

# V4 버전 확인 (있으면)
if 'llm_version' in df_success.columns:
    v4_count = (df_success['llm_version'] == 'V4').sum()
    print(f"✅ V4 데이터: {v4_count}개")
    if v4_count > 0:
        df_success = df_success[df_success['llm_version'] == 'V4']
        print(f"   V4만 필터링: {len(df_success)}개")

# 테스트 데이터 제외 (있으면)
if 'test_mode' in df_success.columns:
    test_count = (df_success['test_mode'] == True).sum()
    if test_count > 0:
        df_success = df_success[df_success['test_mode'] == False]
        print(f"✅ 테스트 데이터 제외: {test_count}개 제거")

# 데이터 수 제한
max_samples = DATA_CONFIG['max_samples']
if len(df_success) > max_samples:
    print(f"\n⚠️ 데이터 제한: {len(df_success)}개 → {max_samples}개")
    df_success = df_success.head(max_samples)

print(f"\n📊 최종 데이터: {len(df_success)}개")

# 데이터 통계
print("\n📈 V4.0 데이터 통계:")
if 'llm_words' in df_success.columns:
    print(f"   평균 단어 수: {df_success['llm_words'].mean():.1f}")
    print(f"   범위: {df_success['llm_words'].min()}-{df_success['llm_words'].max()}")
    print(f"   45단어 이하: {(df_success['llm_words'] <= 45).sum()}개 ({(df_success['llm_words'] <= 45).sum()/len(df_success)*100:.1f}%)")

if 'llm_sentences' in df_success.columns:
    print(f"   평균 문장 수: {df_success['llm_sentences'].mean():.1f}")
    print(f"   2문장: {(df_success['llm_sentences'] == 2).sum()}개 ({(df_success['llm_sentences'] == 2).sum()/len(df_success)*100:.1f}%)")

if 'llm_name' in df_success.columns:
    print(f"\n   Teacher LLM 분포:")
    for llm, count in df_success['llm_name'].value_counts().items():
        print(f"     {llm}: {count}개")

# ================================================================
# STEP 4: Train/Val 분할
# ================================================================

print("\n" + "="*70)
print("✂️ STEP 4: Train/Val 분할")
print("="*70)

# 인덱스 섞기 (재현성 위해 seed 고정)
df_shuffled = df_success.sample(frac=1, random_state=42).reset_index(drop=True)

# 분할
train_split = DATA_CONFIG['train_split']
train_size = int(len(df_shuffled) * train_split)
train_df = df_shuffled[:train_size]
val_df = df_shuffled[train_size:]

print(f"📊 데이터 분할 ({int(train_split*100)}/{int((1-train_split)*100)}):")
print(f"   Train: {len(train_df)}개 ({len(train_df)/len(df_shuffled)*100:.1f}%)")
print(f"   Val: {len(val_df)}개 ({len(val_df)/len(df_shuffled)*100:.1f}%)")

# Dataset 변환
train_dataset = Dataset.from_pandas(
    train_df[['original_abstract', 'llm_summary']].reset_index(drop=True)
)
val_dataset = Dataset.from_pandas(
    val_df[['original_abstract', 'llm_summary']].reset_index(drop=True)
)

print("✅ Dataset 변환 완료")

# 샘플 확인
print("\n📝 V4.0 샘플 확인:")
sample = train_dataset[0]
print(f"\n입력 (초록): {sample['original_abstract'][:200]}...")
print(f"\n출력 (V4 요약): {sample['llm_summary']}")

# ================================================================
# STEP 5: 모델 및 토크나이저 로드
# ================================================================

print("\n" + "="*70)
print("🤖 STEP 5: 모델 및 토크나이저 로드")
print("="*70)

BASE_MODEL = MODEL_VERSION['base_model']
print(f"📥 베이스 모델: {BASE_MODEL}")

# QLoRA 설정 (4-bit 양자화)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# 모델 로드
print("⏳ 모델 로딩 중...")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tokenizer.padding_side = "right"

print("✅ 모델 및 토크나이저 로드 완료")

# LoRA 준비
print("\n🔧 LoRA 설정 중...")
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=LORA_CONFIG['r'],
    lora_alpha=LORA_CONFIG['alpha'],
    target_modules=LORA_CONFIG['target_modules'],
    lora_dropout=LORA_CONFIG['dropout'],
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

print("📊 학습 가능한 파라미터:")
model.print_trainable_parameters()

# ================================================================
# STEP 6: V4 프롬프트 적용
# ================================================================

print("\n" + "="*70)
print("📝 STEP 6: V4.0 프롬프트 적용")
print("="*70)

# V4.0 System Message (뉴스 브리핑 스타일)
SYSTEM_MESSAGE_V4 = "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."

print("✨ V4.0 프롬프트:")
print(f"   \"{SYSTEM_MESSAGE_V4}\"")
print("\n특징:")
print("   - 매우 단순하고 직접적")
print("   - 일반인도 이해 가능")
print("   - 뉴스 브리핑 스타일")
print("   - V3 대비 90% 단순화")

def formatting_prompts_v4(example):
    """V4.0 프롬프트 포맷팅"""
    
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE_V4},
        {"role": "user", "content": example['original_abstract']},
        {"role": "assistant", "content": example['llm_summary']}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )
    
    return {"text": text}

def tokenize_function(example):
    """토크나이즈"""
    result = tokenizer(
        example['text'],
        truncation=True,
        max_length=TRAINING_CONFIG['max_length'],
        padding=False
    )
    result['labels'] = result['input_ids'].copy()
    return result

# 프롬프트 적용
print("\n🔄 V4.0 프롬프트 적용 중...")
train_dataset = train_dataset.map(formatting_prompts_v4)
val_dataset = val_dataset.map(formatting_prompts_v4)

print("🔄 토크나이즈 중...")
train_dataset_tokenized = train_dataset.map(
    tokenize_function,
    remove_columns=train_dataset.column_names
)
val_dataset_tokenized = val_dataset.map(
    tokenize_function,
    remove_columns=val_dataset.column_names
)

print("✅ V4.0 프롬프트 적용 완료")

# ================================================================
# STEP 7: V4.0 학습 설정 및 실행
# ================================================================

print("\n" + "="*70)
print("🏋️ STEP 7: V4.0 모델 학습")
print("="*70)

# 출력 디렉토리 (V4.0 네이밍)
OUTPUT_DIR = f"/content/drive/MyDrive/ArXiv-Models/{MODEL_VERSION['name']}"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

print(f"📁 출력 디렉토리: {OUTPUT_DIR}")

# 학습 설정
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    
    # 에포크 및 배치
    num_train_epochs=TRAINING_CONFIG['num_epochs'],
    per_device_train_batch_size=TRAINING_CONFIG['batch_size'],
    per_device_eval_batch_size=TRAINING_CONFIG['batch_size'],
    gradient_accumulation_steps=TRAINING_CONFIG['gradient_accumulation_steps'],
    eval_accumulation_steps=TRAINING_CONFIG['gradient_accumulation_steps'],
    
    # 옵티마이저
    learning_rate=TRAINING_CONFIG['learning_rate'],
    warmup_steps=TRAINING_CONFIG['warmup_steps'],
    max_grad_norm=1.0,
    
    # 로깅 및 저장
    logging_steps=10,
    save_steps=50,
    eval_strategy="steps",
    eval_steps=50,
    save_total_limit=3,
    
    # 정밀도
    fp16=TRAINING_CONFIG['fp16'],
    
    # 기타
    report_to="none",
    dataloader_num_workers=0,
    remove_unused_columns=False
)

# Data Collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
    pad_to_multiple_of=8,
    return_tensors="pt"
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset_tokenized,
    eval_dataset=val_dataset_tokenized,
    data_collator=data_collator
)

# 학습 시작
print("\n" + "="*70)
print(f"🏋️ {MODEL_VERSION['name']} 학습 시작!")
print("="*70)
print(f"\n⚙️ 설정:")
print(f"   모델: {MODEL_VERSION['name']}")
print(f"   버전: v{MODEL_VERSION['major']}.{MODEL_VERSION['minor']}.{MODEL_VERSION['patch']}")
print(f"   스타일: {MODEL_VERSION['style']}")
print(f"   데이터: {len(train_dataset_tokenized)}개 (train)")
print(f"   검증: {len(val_dataset_tokenized)}개 (val)")
print(f"   에포크: {TRAINING_CONFIG['num_epochs']}")
print(f"   배치 크기: {TRAINING_CONFIG['batch_size']}")
print(f"   Gradient Accumulation: {TRAINING_CONFIG['gradient_accumulation_steps']}")
print(f"   학습률: {TRAINING_CONFIG['learning_rate']}")
print(f"\n⏱️ 예상 시간:")
total_steps = len(train_dataset_tokenized) * TRAINING_CONFIG['num_epochs'] / (TRAINING_CONFIG['batch_size'] * TRAINING_CONFIG['gradient_accumulation_steps'])
print(f"   총 스텝: ~{total_steps:.0f}")
print(f"   예상 시간: ~{total_steps * 3 / 60:.0f}분 (T4 GPU)")
print("="*70)

start_time = time.time()
trainer.train()
elapsed_time = time.time() - start_time

print("\n" + "="*70)
print(f"✅ {MODEL_VERSION['name']} 학습 완료!")
print("="*70)
print(f"⏱️ 소요 시간: {elapsed_time/60:.1f}분")

# 모델 저장
print("\n💾 모델 저장 중...")
final_model_path = Path(OUTPUT_DIR) / "final_model"
trainer.model.save_pretrained(final_model_path)
tokenizer.save_pretrained(final_model_path)
print(f"✅ 모델 저장 완료: {final_model_path}")

# ================================================================
# STEP 8: V4.0 메타데이터 저장
# ================================================================

print("\n" + "="*70)
print("📋 STEP 8: V4.0 메타데이터 저장")
print("="*70)

metadata = {
    "model_info": MODEL_VERSION,
    "dataset": {
        "source": DATA_CONFIG['source_file'],
        "total_size": len(df_success),
        "train_size": len(train_df),
        "val_size": len(val_df),
        "train_split": DATA_CONFIG['train_split'],
        "statistics": {
            "avg_words": float(df_success['llm_words'].mean()) if 'llm_words' in df_success.columns else None,
            "avg_sentences": float(df_success['llm_sentences'].mean()) if 'llm_sentences' in df_success.columns else None,
            "teacher_llm": df_success['llm_name'].value_counts().to_dict() if 'llm_name' in df_success.columns else None
        }
    },
    "training": {
        "config": TRAINING_CONFIG,
        "lora": LORA_CONFIG,
        "generation": GENERATION_CONFIG,
        "elapsed_time_minutes": round(elapsed_time / 60, 2),
        "total_steps": int(total_steps)
    },
    "prompt": {
        "system_message": SYSTEM_MESSAGE_V4,
        "style": "Simple and direct",
        "comparison_to_v3": "90% simpler than V3"
    },
    "changelog": [
        "Initial V4.0 release with news briefing style",
        "Simplified prompt from V3 (complex academic → simple news)",
        "Enhanced hallucination prevention",
        "Improved preprocessing for metadata filtering",
        "Target audience: General public"
    ],
    "status": "experimental",
    "created_at": datetime.now().isoformat(),
    "next_version": "v4.1 (2k samples expansion planned)"
}

metadata_path = Path(OUTPUT_DIR) / "metadata.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✅ 메타데이터 저장: {metadata_path}")

# README 생성
readme_content = f"""# {MODEL_VERSION['name']}

## 📋 Model Information

- **Version**: v{MODEL_VERSION['major']}.{MODEL_VERSION['minor']}.{MODEL_VERSION['patch']}
- **Base Model**: {MODEL_VERSION['base_model']}
- **Style**: {MODEL_VERSION['style']}
- **Target Audience**: {MODEL_VERSION['target']}
- **Data Size**: {MODEL_VERSION['data_size']} samples
- **Status**: {metadata['status']}
- **Created**: {datetime.now().strftime('%Y-%m-%d')}

## 🎯 Purpose

Generate news-style briefings of ArXiv papers that anyone can understand.

## 📊 Training Data

- **Source**: {DATA_CONFIG['source_file']}
- **Train**: {len(train_df)} samples
- **Validation**: {len(val_df)} samples
- **Teacher LLM**: {list(df_success['llm_name'].unique()) if 'llm_name' in df_success.columns else 'Unknown'}

## ⚙️ Training Configuration

- **Epochs**: {TRAINING_CONFIG['num_epochs']}
- **Learning Rate**: {TRAINING_CONFIG['learning_rate']}
- **LoRA r**: {LORA_CONFIG['r']}
- **LoRA alpha**: {LORA_CONFIG['alpha']}
- **Training Time**: {elapsed_time/60:.1f} minutes

## 📝 System Prompt
```
{SYSTEM_MESSAGE_V4}
```

## 🔄 Version History

- **V3.0**: Academic style (600 samples)
- **V4.0**: News briefing style (1000 samples) ⭐ Current

## 🚀 Next Steps

- Expand to 2k samples (v4.1)
- Improve quality metrics
- A/B testing with V3.0

## 📁 Directory Structure
```
{MODEL_VERSION['name']}/
├── final_model/       # Trained model weights
├── checkpoint-*/      # Training checkpoints
├── results/          # Evaluation results
├── metadata.json     # Complete metadata
└── README.md         # This file
```

## 📧 Contact

For questions about this model, please refer to the training logs and metadata.
"""

readme_path = Path(OUTPUT_DIR) / "README.md"
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"✅ README 생성: {readme_path}")

# ================================================================
# STEP 9: V4.0 모델 테스트 (A/B 비교)
# ================================================================

print("\n" + "="*70)
print("🧪 STEP 9: V4.0 모델 테스트 (A/B 비교)")
print("="*70)

# 베이스 모델 로드 (비교용)
print("\n📥 베이스 모델 로드 (비교용)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
print("✅ 베이스 모델 로드 완료")

# 테스트 샘플 선택
print("\n📊 테스트 샘플 선택 (3개)...")
test_samples = val_df.sample(n=min(3, len(val_df)), random_state=42)

# 생성 설정
generation_config = {
    "max_new_tokens": GENERATION_CONFIG['max_new_tokens'],
    "temperature": GENERATION_CONFIG['temperature'],
    "top_p": GENERATION_CONFIG['top_p'],
    "do_sample": GENERATION_CONFIG['do_sample'],
    "pad_token_id": tokenizer.pad_token_id,
    "eos_token_id": tokenizer.eos_token_id,
}

def generate_summary(model, abstract, is_finetuned=False):
    """요약 생성"""
    
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE_V4},
        {"role": "user", "content": abstract}
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(**inputs, **generation_config)
    
    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Assistant 응답만 추출
    if "<|im_start|>assistant" in full_output:
        summary = full_output.split("<|im_start|>assistant")[-1].strip()
    elif "assistant" in full_output.lower():
        summary = full_output.split("assistant")[-1].strip()
    else:
        summary = full_output
    
    # 정리
    summary = summary.replace("<|im_end|>", "").strip()
    
    return summary

def clean_output(text, original_abstract):
    """출력 정리"""
    
    # 프롬프트 누출 제거
    patterns = [
        r"Summarize.*?sentences?\.",
        r"Use no more than.*?sentences?\.",
        r"simple, clear English",
        r"anyone can understand"
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # 초록 일부가 포함된 경우 제거
    abstract_start = original_abstract[:50].lower()
    if abstract_start in text.lower():
        return "[ERROR: Contains original text]"
    
    # 짧은 답변 체크
    if len(text.split()) < 10:
        return "[ERROR: Too short]"
    
    # 메타 표현 제거
    text = re.sub(r"Here('s| is) (the|a) summary:?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(The )?(summary|abstract):?", "", text, flags=re.IGNORECASE)
    
    return text.strip()

# A/B 테스트 실행
print("\n" + "="*70)
print("🔬 A/B 테스트 시작")
print("="*70)

ab_test_results = []

for idx, (_, row) in enumerate(test_samples.iterrows(), 1):
    print(f"\n{'='*70}")
    print(f"테스트 {idx}/3")
    print(f"{'='*70}")
    
    abstract = row['original_abstract']
    target = row['llm_summary']
    
    print(f"\n📄 초록 (입력):")
    print(f"{abstract[:300]}...")
    
    print(f"\n🎯 목표 (V4 Teacher):")
    print(f"{target}")
    
    # 베이스 모델
    print(f"\n⏳ 베이스 모델 생성 중...")
    base_output = generate_summary(base_model, abstract, is_finetuned=False)
    base_summary = clean_output(base_output, abstract)
    
    print(f"\n📝 베이스 모델 출력:")
    print(f"{base_summary}")
    
    # 파인튜닝 모델
    print(f"\n⏳ V4.0 파인튜닝 모델 생성 중...")
    ft_output = generate_summary(trainer.model, abstract, is_finetuned=True)
    ft_summary = clean_output(ft_output, abstract)
    
    print(f"\n✨ V4.0 파인튜닝 출력:")
    print(f"{ft_summary}")
    
    # 결과 저장
    result = {
        "test_id": idx,
        "abstract": abstract,
        "abstract_length": len(abstract),
        "target_v4": target,
        "base_output": base_summary,
        "base_words": len(base_summary.split()) if "[ERROR" not in base_summary else 0,
        "ft_output_v4": ft_summary,
        "ft_words": len(ft_summary.split()) if "[ERROR" not in ft_summary else 0,
    }
    
    ab_test_results.append(result)

# 결과 저장
results_path = Path(OUTPUT_DIR) / "results"
results_path.mkdir(exist_ok=True)

ab_test_file = results_path / f"ab_test_{MODEL_VERSION['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

test_metadata = {
    "metadata": {
        "model": MODEL_VERSION,
        "test_config": GENERATION_CONFIG,
        "prompt": SYSTEM_MESSAGE_V4,
        "timestamp": datetime.now().isoformat()
    },
    "results": ab_test_results
}

with open(ab_test_file, 'w', encoding='utf-8') as f:
    json.dump(test_metadata, f, indent=2, ensure_ascii=False)

print(f"\n💾 A/B 테스트 결과 저장: {ab_test_file}")

# ================================================================
# STEP 10: 최종 통계 및 요약
# ================================================================

print("\n" + "="*70)
print("📊 STEP 10: 최종 통계 및 요약")
print("="*70)

print(f"\n✨ {MODEL_VERSION['name']} 학습 완료!")
print(f"\n📦 저장 위치:")
print(f"   모델: {final_model_path}")
print(f"   메타데이터: {metadata_path}")
print(f"   README: {readme_path}")
print(f"   결과: {ab_test_file}")

print(f"\n📊 학습 통계:")
print(f"   모델명: {MODEL_VERSION['name']}")
print(f"   버전: v{MODEL_VERSION['major']}.{MODEL_VERSION['minor']}.{MODEL_VERSION['patch']}")
print(f"   스타일: {MODEL_VERSION['style']}")
print(f"   타겟: {MODEL_VERSION['target']}")
print(f"   데이터: {DATA_CONFIG['source_file']}")
print(f"   Train: {len(train_df)}개")
print(f"   Val: {len(val_df)}개")
print(f"   에포크: {TRAINING_CONFIG['num_epochs']}")
print(f"   소요 시간: {elapsed_time/60:.1f}분")

# A/B 테스트 간단 통계
base_avg = np.mean([r['base_words'] for r in ab_test_results if r['base_words'] > 0])
ft_avg = np.mean([r['ft_words'] for r in ab_test_results if r['ft_words'] > 0])

print(f"\n🔬 A/B 테스트 통계:")
print(f"   테스트: {len(ab_test_results)}개")
print(f"   베이스 평균: {base_avg:.1f}단어")
print(f"   V4.0 FT 평균: {ft_avg:.1f}단어")

print(f"\n💡 다음 단계:")
print(f"   1. A/B 테스트 결과 검토")
print(f"   2. 일반인 이해도 평가")
print(f"   3. V3.0 vs V4.0 비교 분석")
print(f"   4. V4.1 (2k) 확장 계획")

print(f"\n🔄 버전 로드맵:")
print(f"   ✅ V3.0: ArXiv-Academic-1.5B-600-v3.0 (학술)")
print(f"   ✅ V4.0: ArXiv-NewsBrief-1.5B-1k-v4.0 (뉴스) ⭐ 현재")
print(f"   ⏳ V4.1: ArXiv-NewsBrief-1.5B-2k-v4.1 (계획)")
print(f"   ⏳ V4.2: ArXiv-NewsBrief-1.5B-3k-v4.2 (계획)")
print(f"   🎯 V4.3: ArXiv-NewsBrief-1.5B-5k-v4.3 (목표)")

print("\n" + "="*70)
print(f"🎉 {MODEL_VERSION['name']} 파이프라인 완료!")
print("="*70)

print(f"\n✨ V4.0 특징:")
print(f"   - 일반인도 이해 가능")
print(f"   - 뉴스 브리핑 스타일")
print(f"   - 단순하고 명확한 언어")
print(f"   - V3 대비 프롬프트 90% 단순화")
print(f"   - 활용: 뉴스, 블로그, 대중 강연")

print(f"\n📚 평가 프롬프트:")
print(f"   V4.0 결과를 다른 LLM에 넣어 평가받으세요:")
print(f"   파일: {ab_test_file}")

print("\n" + "="*70)