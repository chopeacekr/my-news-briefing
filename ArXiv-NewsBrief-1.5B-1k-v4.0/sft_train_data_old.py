"""
=================================================================
📰 ArXiv-NewsBrief-1.5B-1k-v4.0 - 뉴스 브리핑 스타일 모델 학습 v1
=================================================================

🎯 모델명: ArXiv-NewsBrief-1.5B-1k-v4.0

📊 V4 핵심:
✅ 데이터: v4_training_data_all.csv (1000개)
✅ 스타일: 일반인도 이해 가능한 뉴스 브리핑
✅ 프롬프트: 단순하고 명확
✅ 모델: Qwen2.5-1.5B-Instruct + LoRA

🔄 실행 방법:
1. 이 셀 한 번 실행
2. 런타임 자동 재시작 대기 (10초)
3. 자동으로 학습 시작! 🚀

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("🚀 ArXiv-NewsBrief-1.5B-1k-v4.0 - 자동 설치 및 학습")
print("="*70)

# ================================================================
# PHASE 1: 패키지 설치 체크 및 재설치
# ================================================================

def check_packages_installed():
    """필수 패키지가 제대로 설치되었는지 확인"""
    try:
        import transformers
        import torch
        import peft
        import datasets
        import bitsandbytes
        import accelerate

        # transformers import 테스트
        from transformers.cache_utils import Cache
        from transformers import AutoModelForCausalLM

        # bitsandbytes import 테스트
        from bitsandbytes.nn import Linear4bit

        print(f"✅ transformers: {transformers.__version__}")
        print(f"✅ torch: {torch.__version__}")
        print(f"✅ peft: {peft.__version__}")
        print(f"✅ datasets: {datasets.__version__}")
        print(f"✅ bitsandbytes: {bitsandbytes.__version__}")
        print(f"✅ accelerate: {accelerate.__version__}")

        return True
    except (ImportError, AttributeError) as e:
        print(f"⚠️ 패키지 문제 감지: {e}")
        return False

# 패키지 상태 확인
need_install = not check_packages_installed()

if need_install:
    print("\n" + "="*70)
    print("📦 PHASE 1: 패키지 설치 (첫 실행)")
    print("="*70)

    # 기존 패키지 완전 제거
    print("\n🗑️ 기존 패키지 제거...")
    packages_to_remove = ["transformers", "accelerate", "peft", "trl", "bitsandbytes"]
    for pkg in packages_to_remove:
        print(f"  - 제거: {pkg}")
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", pkg],
            capture_output=True
        )

    print("✅ 제거 완료")

    # 캐시 정리
    print("\n🧹 pip 캐시 정리...")
    subprocess.run(
        [sys.executable, "-m", "pip", "cache", "purge"],
        capture_output=True
    )

    # 새 패키지 설치 (순서 중요!)
    packages = [
        "torch",  # 먼저 torch
        "bitsandbytes==0.45.0",  # bitsandbytes
        "transformers==4.46.3",
        "datasets==3.2.0",
        "accelerate==1.2.1",
        "peft==0.13.2",
        "trl==0.12.2"
    ]

    print("\n📥 패키지 설치 중...")
    for pkg in packages:
        print(f"  - 설치: {pkg}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"    ⚠️ 경고: {result.stderr[:200]}")

    print("\n✅ 설치 완료!")
    print("\n" + "="*70)
    print("🔄 런타임 자동 재시작 중...")
    print("="*70)
    print("\n⏳ 10초 후 자동으로 학습이 시작됩니다...")
    print("   (수동 작업 필요 없음)")

    # 런타임 재시작
    os.kill(os.getpid(), 9)

# ================================================================
# PHASE 2: 메인 학습 파이프라인 (재시작 후 자동 실행)
# ================================================================

print("\n" + "="*70)
print("✅ PHASE 2: 메인 학습 시작")
print("="*70)

# Import
import json
import re
import time
import pandas as pd
import numpy as np
from datetime import datetime
import torch

print("\n🔍 최종 패키지 버전 확인...")
import transformers
import peft
import datasets
import bitsandbytes
import accelerate

print(f"✅ transformers: {transformers.__version__}")
print(f"✅ torch: {torch.__version__}")
print(f"✅ peft: {peft.__version__}")
print(f"✅ datasets: {datasets.__version__}")
print(f"✅ bitsandbytes: {bitsandbytes.__version__}")
print(f"✅ accelerate: {accelerate.__version__}")

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

print("✅ Import 완료!")

# ================================================================
# 설정
# ================================================================

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

DATA_CONFIG = {
    'source_file': 'v4_training_data_all.csv',
    'max_samples': 1000,
    'train_split': 0.9,
    'val_split': 0.1
}

TRAINING_CONFIG = {
    'num_epochs': 5,
    'learning_rate': 2e-4,
    'batch_size': 1,
    'gradient_accumulation_steps': 4,
    'max_length': 512,
    'warmup_steps': 10,
    'fp16': True
}

LORA_CONFIG = {
    'r': 16,
    'alpha': 32,
    'dropout': 0.1,
    'target_modules': ["q_proj", "k_proj", "v_proj", "o_proj"]
}

GENERATION_CONFIG = {
    'temperature': 0.7,
    'top_p': 0.9,
    'max_new_tokens': 80,
    'do_sample': True
}

SYSTEM_MESSAGE_V4 = "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."

print(f"\n📦 모델: {MODEL_VERSION['name']}")
print(f"🎯 스타일: {MODEL_VERSION['style']}")
print(f"⚙️ 에포크: {TRAINING_CONFIG['num_epochs']}")

# ================================================================
# Drive 마운트
# ================================================================

print("\n" + "="*70)
print("💾 Drive 마운트")
print("="*70)

if not Path("/content/drive").exists():
    drive.mount('/content/drive')
print("✅ Drive 마운트 완료")

# ================================================================
# 데이터 로드
# ================================================================

print("\n" + "="*70)
print("📂 데이터 로드")
print("="*70)

DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"
data_path = Path(DATA_DIR) / DATA_CONFIG['source_file']

print(f"📥 {DATA_CONFIG['source_file']} 로딩...")
df = pd.read_csv(data_path)
print(f"✅ 총 {len(df)}개 로드")

# 성공 데이터만
df_success = df[df['llm_success'] == True].copy()
print(f"✅ 성공: {len(df_success)}개 ({len(df_success)/len(df)*100:.1f}%)")

# V4 필터링
if 'llm_version' in df_success.columns:
    v4_count = (df_success['llm_version'] == 'V4').sum()
    if v4_count > 0:
        df_success = df_success[df_success['llm_version'] == 'V4']
        print(f"✅ V4: {len(df_success)}개")

# 테스트 제외
if 'test_mode' in df_success.columns:
    df_success = df_success[df_success['test_mode'] == False]

# 제한
if len(df_success) > DATA_CONFIG['max_samples']:
    df_success = df_success.head(DATA_CONFIG['max_samples'])
    print(f"✅ 제한: {len(df_success)}개")

# 통계
if 'llm_words' in df_success.columns:
    print(f"\n📊 평균 단어: {df_success['llm_words'].mean():.1f}")
if 'llm_name' in df_success.columns:
    print(f"📊 Teacher LLM:")
    for llm, cnt in df_success['llm_name'].value_counts().head(3).items():
        print(f"   {llm}: {cnt}개")

# ================================================================
# Train/Val 분할
# ================================================================

print("\n" + "="*70)
print("✂️ Train/Val 분할")
print("="*70)

df_shuffled = df_success.sample(frac=1, random_state=42).reset_index(drop=True)
train_size = int(len(df_shuffled) * DATA_CONFIG['train_split'])
train_df = df_shuffled[:train_size]
val_df = df_shuffled[train_size:]

print(f"📊 Train: {len(train_df)}개")
print(f"📊 Val: {len(val_df)}개")

train_dataset = Dataset.from_pandas(
    train_df[['original_abstract', 'llm_summary']].reset_index(drop=True)
)
val_dataset = Dataset.from_pandas(
    val_df[['original_abstract', 'llm_summary']].reset_index(drop=True)
)

print("✅ Dataset 변환 완료")

# 샘플 확인
print(f"\n📝 샘플:")
sample = train_dataset[0]
print(f"입력: {sample['original_abstract'][:150]}...")
print(f"출력: {sample['llm_summary']}")

# ================================================================
# 모델 로드
# ================================================================

print("\n" + "="*70)
print("🤖 모델 로드")
print("="*70)

BASE_MODEL = MODEL_VERSION['base_model']
print(f"📥 베이스: {BASE_MODEL}")

# 4-bit 양자화 설정
print("\n🔧 4-bit 양자화 설정 중...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)
print("✅ 양자화 설정 완료")

print("\n⏳ 모델 로딩 중... (1-2분 소요)")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
print("✅ 모델 로드 완료")

print("\n⏳ 토크나이저 로딩...")
tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    trust_remote_code=True
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

tokenizer.padding_side = "right"
print("✅ 토크나이저 로드 완료")

# LoRA
print("\n🔧 LoRA 설정...")
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
print("📊 학습 가능 파라미터:")
model.print_trainable_parameters()

# ================================================================
# 프롬프트 적용
# ================================================================

print("\n" + "="*70)
print("📝 프롬프트 적용")
print("="*70)

print(f"✨ V4 프롬프트:")
print(f'   "{SYSTEM_MESSAGE_V4}"')

def formatting_prompts_v4(example):
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
    result = tokenizer(
        example['text'],
        truncation=True,
        max_length=TRAINING_CONFIG['max_length'],
        padding=False
    )
    result['labels'] = result['input_ids'].copy()
    return result

print("🔄 프롬프트 적용 중...")
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

print("✅ 준비 완료")

# ================================================================
# 학습
# ================================================================

print("\n" + "="*70)
print("🏋️ 모델 학습")
print("="*70)

OUTPUT_DIR = f"/content/drive/MyDrive/ArXiv-Models/{MODEL_VERSION['name']}"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
print(f"📁 출력: {OUTPUT_DIR}")

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=TRAINING_CONFIG['num_epochs'],
    per_device_train_batch_size=TRAINING_CONFIG['batch_size'],
    per_device_eval_batch_size=TRAINING_CONFIG['batch_size'],
    gradient_accumulation_steps=TRAINING_CONFIG['gradient_accumulation_steps'],
    eval_accumulation_steps=TRAINING_CONFIG['gradient_accumulation_steps'],
    learning_rate=TRAINING_CONFIG['learning_rate'],
    warmup_steps=TRAINING_CONFIG['warmup_steps'],
    max_grad_norm=1.0,
    logging_steps=10,
    save_steps=50,
    eval_strategy="steps",
    eval_steps=50,
    save_total_limit=3,
    fp16=TRAINING_CONFIG['fp16'],
    report_to="none",
    dataloader_num_workers=0,
    remove_unused_columns=False
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
    pad_to_multiple_of=8,
    return_tensors="pt"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset_tokenized,
    eval_dataset=val_dataset_tokenized,
    data_collator=data_collator
)

print(f"\n⚙️ 설정:")
print(f"   모델: {MODEL_VERSION['name']}")
print(f"   Train: {len(train_dataset_tokenized)}개")
print(f"   Val: {len(val_dataset_tokenized)}개")
print(f"   에포크: {TRAINING_CONFIG['num_epochs']}")
print(f"   배치: {TRAINING_CONFIG['batch_size']}")
print(f"   학습률: {TRAINING_CONFIG['learning_rate']}")

total_steps = len(train_dataset_tokenized) * TRAINING_CONFIG['num_epochs'] / (TRAINING_CONFIG['batch_size'] * TRAINING_CONFIG['gradient_accumulation_steps'])
print(f"\n⏱️ 예상:")
print(f"   스텝: ~{total_steps:.0f}")
print(f"   시간: ~{total_steps * 3 / 60:.0f}분")
print("="*70)

start_time = time.time()
trainer.train()
elapsed_time = time.time() - start_time

print("\n" + "="*70)
print(f"✅ 학습 완료!")
print(f"⏱️ 소요: {elapsed_time/60:.1f}분")
print("="*70)

# 저장
print("\n💾 모델 저장...")
final_model_path = Path(OUTPUT_DIR) / "final_model"
trainer.model.save_pretrained(final_model_path)
tokenizer.save_pretrained(final_model_path)
print(f"✅ 저장: {final_model_path}")

# ================================================================
# 메타데이터
# ================================================================

print("\n" + "="*70)
print("📋 메타데이터 저장")
print("="*70)

metadata = {
    "model_info": MODEL_VERSION,
    "dataset": {
        "source": DATA_CONFIG['source_file'],
        "train_size": len(train_df),
        "val_size": len(val_df),
    },
    "training": {
        "config": TRAINING_CONFIG,
        "lora": LORA_CONFIG,
        "elapsed_time_minutes": round(elapsed_time / 60, 2),
    },
    "prompt": {
        "system_message": SYSTEM_MESSAGE_V4,
    },
    "created_at": datetime.now().isoformat(),
}

metadata_path = Path(OUTPUT_DIR) / "metadata.json"
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"✅ 메타데이터: {metadata_path}")

# README
readme_content = f"""# {MODEL_VERSION['name']}

## 📋 Model Information
- **Version**: v{MODEL_VERSION['major']}.{MODEL_VERSION['minor']}.{MODEL_VERSION['patch']}
- **Base**: {MODEL_VERSION['base_model']}
- **Style**: {MODEL_VERSION['style']}
- **Data**: {MODEL_VERSION['data_size']} samples
- **Created**: {datetime.now().strftime('%Y-%m-%d')}

## 📊 Training
- **Train**: {len(train_df)} samples
- **Val**: {len(val_df)} samples
- **Epochs**: {TRAINING_CONFIG['num_epochs']}
- **Time**: {elapsed_time/60:.1f} minutes

## 📝 Prompt
```
{SYSTEM_MESSAGE_V4}
```
"""

readme_path = Path(OUTPUT_DIR) / "README.md"
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"✅ README: {readme_path}")

# ================================================================
# 테스트
# ================================================================

print("\n" + "="*70)
print("🧪 모델 테스트")
print("="*70)

print("📥 베이스 모델 로드...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
print("✅ 베이스 로드 완료")

test_samples = val_df.sample(n=min(3, len(val_df)), random_state=42)

generation_config = {
    "max_new_tokens": GENERATION_CONFIG['max_new_tokens'],
    "temperature": GENERATION_CONFIG['temperature'],
    "top_p": GENERATION_CONFIG['top_p'],
    "do_sample": GENERATION_CONFIG['do_sample'],
    "pad_token_id": tokenizer.pad_token_id,
    "eos_token_id": tokenizer.eos_token_id,
}

def generate_summary(model, abstract):
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

    if "<|im_start|>assistant" in full_output:
        summary = full_output.split("<|im_start|>assistant")[-1].strip()
    elif "assistant" in full_output.lower():
        summary = full_output.split("assistant")[-1].strip()
    else:
        summary = full_output

    summary = summary.replace("<|im_end|>", "").strip()
    return summary

ab_test_results = []

for idx, (_, row) in enumerate(test_samples.iterrows(), 1):
    print(f"\n{'='*70}")
    print(f"테스트 {idx}/3")
    print(f"{'='*70}")

    abstract = row['original_abstract']
    target = row['llm_summary']

    print(f"\n📄 초록: {abstract[:200]}...")
    print(f"\n🎯 목표: {target}")

    base_summary = generate_summary(base_model, abstract)
    print(f"\n📝 베이스: {base_summary}")

    ft_summary = generate_summary(trainer.model, abstract)
    print(f"\n✨ V4.0 FT: {ft_summary}")

    ab_test_results.append({
        "test_id": idx,
        "target": target,
        "base": base_summary,
        "ft_v4": ft_summary,
    })

# 결과 저장
results_path = Path(OUTPUT_DIR) / "results"
results_path.mkdir(exist_ok=True)

ab_test_file = results_path / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(ab_test_file, 'w', encoding='utf-8') as f:
    json.dump({
        "metadata": MODEL_VERSION,
        "results": ab_test_results
    }, f, indent=2, ensure_ascii=False)

print(f"\n💾 결과 저장: {ab_test_file}")

# ================================================================
# 완료
# ================================================================

print("\n" + "="*70)
print(f"🎉 {MODEL_VERSION['name']} 완료!")
print("="*70)
print(f"\n✨ 저장 위치:")
print(f"   📁 모델: {final_model_path}")
print(f"   📁 메타: {metadata_path}")
print(f"   📁 README: {readme_path}")
print(f"   📁 결과: {ab_test_file}")
print(f"\n📊 통계:")
print(f"   Train: {len(train_df)}개")
print(f"   Val: {len(val_df)}개")
print(f"   시간: {elapsed_time/60:.1f}분")
print(f"\n🎯 다음 단계:")
print(f"   1. 결과 파일 확인")
print(f"   2. V3.0 vs V4.0 비교")
print(f"   3. V4.1 (2k) 확장")
print("\n" + "="*70)