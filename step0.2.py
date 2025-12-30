"""
=================================================================
📚 STEP 0.2: Qwen vs Mistral 비교 - 섹션별 실행 버전
=================================================================

섹션별로 독립 실행 가능합니다!

실행 순서:
1. 섹션 1: 환경 설정
2. Runtime 재시작 ⚠️
3. 섹션 2: 데이터 준비
4. 섹션 3: 모델 학습
5. 섹션 4: A/B 테스트
6. 섹션 5: 결과 분석

=================================================================
"""

# ================================================================
# 섹션 1: 환경 설정 (패키지 설치)
# ================================================================

print("="*60)
print("📦 섹션 1: 환경 설정")
print("="*60)

import sys
import subprocess
from pathlib import Path

INSTALL_FLAG = Path("/tmp/step0_2_qwen_installed.flag")

if INSTALL_FLAG.exists():
    print("✅ 패키지 이미 설치됨!")
    print("섹션 2로 이동하세요 →")
else:
    print("\n패키지 설치 중...")
    packages = ["transformers", "datasets", "accelerate", "peft", "bitsandbytes"]
    for package in packages:
        print(f"📥 {package} 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-U", package])
        print(f"   ✅ {package} 완료")
    
    INSTALL_FLAG.touch()
    
    print("\n" + "="*60)
    print("✅ 패키지 설치 완료!")
    print("="*60)
    print()
    print("🔴 중요: Runtime을 재시작해야 합니다!")
    print()
    print("방법:")
    print("1. 상단 메뉴: Runtime → Restart runtime")
    print("2. 또는 Ctrl+M . (점)")
    print()
    print("재시작 후 섹션 2부터 실행하세요!")
    print("="*60)


# ================================================================
# 섹션 2: 데이터 준비 및 전처리
# ================================================================

print("\n" + "="*60)
print("📚 섹션 2: 데이터 준비 및 전처리")
print("="*60)

try:
    import torch
    import gc
    import json
    import csv
    import re
    from datetime import datetime
    from datasets import load_dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from google.colab import drive
    print("✅ Import 성공!")
except ImportError as e:
    print(f"❌ Import 실패: {e}")
    print("섹션 1을 먼저 실행하고 Runtime을 재시작하세요!")
    raise

# GPU 확인
print("\n🔍 GPU 확인 중...")
if not torch.cuda.is_available():
    print("❌ GPU 없음!")
    print()
    print("GPU 설정 방법:")
    print("1. Runtime → Change runtime type")
    print("2. T4 GPU 선택")
    raise RuntimeError("GPU를 먼저 설정하세요!")

print(f"✅ GPU: {torch.cuda.get_device_name(0)}")

total_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
allocated_mem = torch.cuda.memory_allocated(0) / 1024**3
print(f"✅ GPU 메모리: {total_mem:.2f} GB (사용: {allocated_mem:.2f} GB)")

# GPU 메모리 정리
print("\n🧹 GPU 메모리 정리 중...")
torch.cuda.empty_cache()
gc.collect()
print("✅ 정리 완료")

# Google Drive 마운트
print("\n💾 Google Drive 마운트 중...")
if not Path("/content/drive").exists():
    drive.mount('/content/drive')
    print("✅ Drive 마운트 완료")
else:
    print("✅ Drive 이미 마운트됨")

# 설정
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.2-Qwen-GPU-Test"
RESULTS_DIR = Path(OUTPUT_DIR) / "ab_test_results"

TRAIN_SAMPLES = 40
VAL_SAMPLES = 10
NUM_SAMPLES = 50

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("\n⚙️ 설정:")
print(f"  모델: Qwen2.5-1.5B-Instruct (1.5B)")
print(f"  훈련 샘플: {TRAIN_SAMPLES}")
print(f"  검증 샘플: {VAL_SAMPLES}")
print(f"  출력 경로: {OUTPUT_DIR}")

# LaTeX 전처리 함수
print("\n🔧 전처리 함수 준비...")

def clean_arxiv_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'@xmath\d+', '', text)
    text = re.sub(r'@xcite', '', text)
    text = re.sub(r'@xref', '', text)
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r'--+', '-', text)
    return text.strip()

print("✅ 전처리 함수 준비 완료")

# 데이터 로딩
print("\n📥 ArXiv 데이터 로딩 중...")
print(f"로딩할 샘플: {NUM_SAMPLES}개")

dataset = load_dataset("ccdv/arxiv-summarization", split=f"train[:{NUM_SAMPLES}]")
print(f"✅ {len(dataset)}개 로드 완료")

# 전처리 적용
print("\n🔄 전처리 적용 중...")
dataset = dataset.map(
    lambda x: {
        'article': clean_arxiv_text(x['article']),
        'abstract': clean_arxiv_text(x['abstract'])
    },
    desc="전처리"
)
print("✅ 전처리 완료")

# 데이터 분할 (STEP 0와 동일한 seed)
print("\n✂️ Train/Val 분할 중...")
dataset = dataset.train_test_split(test_size=VAL_SAMPLES, seed=42)
train_dataset = dataset['train']
val_dataset = dataset['test']

print(f"✅ Train: {len(train_dataset)}개")
print(f"✅ Val: {len(val_dataset)}개")
print(f"💡 STEP 0와 동일한 데이터 (seed=42)")

print("\n" + "="*60)
print("✅ 섹션 2 완료!")
print("다음: 섹션 3 실행 →")
print("="*60)


# ================================================================
# 섹션 3: 모델 학습
# ================================================================

print("\n" + "="*60)
print("🤖 섹션 3: 모델 학습")
print("="*60)

from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Qwen 프롬프트 함수
def formatting_prompts_func(example):
    text = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nSummarize this academic paper in 1-2 sentences (under 50 words):\n\n{example['article']}<|im_end|>\n<|im_start|>assistant\n{example['abstract']}<|im_end|>"
    return {"text": text}

print("\n📝 프롬프트 적용 중...")
train_dataset = train_dataset.map(formatting_prompts_func, desc="프롬프트")
val_dataset = val_dataset.map(formatting_prompts_func, desc="프롬프트")
print("✅ Qwen 프롬프트 적용 완료")

# 토크나이저 로딩
print("\n🔤 토크나이저 로딩 중...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"
print("✅ 토크나이저 완료")

# 토크나이즈 함수
def tokenize_function(example):
    result = tokenizer(
        example['text'],
        truncation=True,
        max_length=512,
        padding=False
    )
    result['labels'] = result['input_ids'].copy()
    return result

print("\n🔄 데이터 토크나이즈 중...")
train_dataset = train_dataset.map(
    tokenize_function,
    remove_columns=train_dataset.column_names,
    desc="토크나이즈"
)
val_dataset = val_dataset.map(
    tokenize_function,
    remove_columns=val_dataset.column_names,
    desc="토크나이즈"
)
print("✅ 토크나이즈 완료")

# 모델 로딩
print("\n🚀 모델 로딩 중...")
print("   Qwen2.5-1.5B-Instruct + 4-bit")
print("   예상 메모리: ~1.5GB")

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

model = prepare_model_for_kbit_training(model)
print("✅ 모델 로딩 완료 (~1.5GB)")

# LoRA 설정
print("\n🔧 LoRA 설정 중...")
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
print("✅ LoRA 적용 완료")
model.print_trainable_parameters()

# 학습 설정
print("\n⚙️ 학습 설정...")
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    learning_rate=2e-4,
    logging_steps=10,
    save_steps=20,
    save_total_limit=2,
    eval_strategy="steps",
    eval_steps=20,
    warmup_steps=2,
    fp16=True,
    report_to="none"
)

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator
)

print("✅ Trainer 준비 완료")
print()
print("🎯 학습 시작!")
print("   예상 시간: 1-2분")
print()

# 학습 실행
trainer.train()

# 모델 저장
print("\n💾 모델 저장 중...")
final_model_path = Path(OUTPUT_DIR) / "checkpoints" / "final_model"
trainer.model.save_pretrained(final_model_path)
tokenizer.save_pretrained(final_model_path)
print(f"✅ 모델 저장: {final_model_path}")

# 메모리 정리
print("\n🧹 메모리 정리 중...")
del model, trainer
gc.collect()
torch.cuda.empty_cache()
print("✅ 정리 완료")

print("\n" + "="*60)
print("✅ 섹션 3 완료!")
print("다음: 섹션 4 실행 →")
print("="*60)


# ================================================================
# 섹션 4: A/B 테스트 (Mistral vs Qwen)
# ================================================================

print("\n" + "="*60)
print("🔬 섹션 4: A/B 테스트")
print("="*60)

from peft import PeftModel

# 평가 함수
def evaluate_summary_detailed(original, generated):
    orig_words = set(original.lower().split())
    gen_words = set(generated.lower().split())
    utility = len(orig_words & gen_words) / max(len(orig_words), 1) * 100
    
    word_count = len(generated.split())
    rule1 = 100 if word_count <= 50 else max(0, 100 - (word_count - 50) * 2)
    rule2 = 100 if any(kw in generated.lower() for kw in ["novel", "new", "achieve", "improve", "propose"]) else 50
    tech_terms = [w for w in generated.split() if w and (w[0].isupper() or len(w) > 15)]
    rule3 = 100 if len(tech_terms) >= 4 else (75 if len(tech_terms) >= 2 else max(0, len(tech_terms) * 25))
    rule4 = 100 if not any(sw in generated.lower() for sw in ["amazing", "wonderful", "terrible"]) else 50
    rule5 = 100 if any(kw in generated.lower() for kw in ["application", "use", "practical"]) else 50
    style = (rule1 + rule2 + rule3 + rule4 + rule5) / 5
    
    return {"utility": utility, "style": style, "word_count": word_count,
            "rules": {"rule1": rule1, "rule2": rule2, "rule3": rule3, "rule4": rule4, "rule5": rule5}}

# 모델 로딩
print("\n🤖 모델 로딩 중...")

# 1. Qwen 베이스 모델
print("1️⃣ Qwen 베이스 모델...")
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
print("   ✅ Qwen 베이스 로드")

# 2. STEP 0 Mistral 파인튜닝 모델 (있으면)
step0_model = None
step0_tokenizer = None

print("2️⃣ STEP 0 (Mistral) 모델...")
step0_model_path = "/content/drive/MyDrive/arxiv-STEP0-Mistral-7B-GPU-Test/checkpoints/final_model"

if Path(step0_model_path).exists():
    step0_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
    step0_tokenizer.pad_token = step0_tokenizer.eos_token
    
    step0_model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-v0.1",
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    step0_model = PeftModel.from_pretrained(step0_model, step0_model_path)
    step0_model.eval()
    print("   ✅ STEP 0 Mistral 로드")
else:
    print("   ⚠️ STEP 0 모델 없음 (비교 생략)")

# 3. STEP 0.2 Qwen 파인튜닝 모델
print("3️⃣ STEP 0.2 (Qwen) 모델...")
qwen_finetuned = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    ),
    device_map="auto",
    trust_remote_code=True
)
qwen_finetuned = PeftModel.from_pretrained(qwen_finetuned, final_model_path)
qwen_finetuned.eval()
print("   ✅ STEP 0.2 Qwen 로드")

print("\n✅ 모든 모델 로드 완료")

# 테스트 데이터
tests = [
    {
        "id": 1,
        "article": "We present a novel deep learning approach for natural language processing tasks. Our method achieves state-of-the-art results on multiple benchmarks.",
        "abstract": "Novel deep learning approach achieving state-of-the-art NLP results."
    },
    {
        "id": 2,
        "article": "This paper investigates the impact of climate change on Arctic ecosystems through extensive five-year field studies.",
        "abstract": "Five-year field study reveals climate change impacts Arctic ecosystems."
    },
    {
        "id": 3,
        "article": "We introduce a new quantum computing algorithm achieving 100x speedup for optimization problems.",
        "abstract": "New quantum algorithm achieves 100x speedup for optimization."
    }
]

# 결과 저장 구조
all_results = {
    "metadata": {
        "qwen_model": "Qwen2.5-1.5B-Instruct",
        "mistral_model": "Mistral-7B-v0.1",
        "step": "STEP 0.2",
        "training_samples": TRAIN_SAMPLES,
        "timestamp": datetime.now().isoformat()
    },
    "tests": []
}

# 테스트 실행
print("\n" + "-"*60)
print("🧪 A/B 테스트 실행 중...")
print("-"*60)

for i, test in enumerate(tests):
    print(f"\n📝 테스트 {i+1}/3...")
    
    # Qwen 프롬프트
    qwen_prompt = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nSummarize this academic paper in 1-2 sentences (under 50 words):\n\n{test['article']}<|im_end|>\n<|im_start|>assistant\n"
    qwen_inputs = tokenizer(qwen_prompt, return_tensors="pt", truncation=True, max_length=400).to(qwen_base.device)
    
    # 1. Qwen 베이스 평가
    with torch.no_grad():
        qwen_base_outputs = qwen_base.generate(
            **qwen_inputs,
            max_new_tokens=60,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.pad_token_id
        )
    qwen_base_summary = tokenizer.decode(qwen_base_outputs[0], skip_special_tokens=True).split("<|im_start|>assistant\n")[-1].strip()
    qwen_base_result = evaluate_summary_detailed(test['abstract'], qwen_base_summary)
    
    # 2. STEP 0 Mistral 평가 (있으면)
    if step0_model and step0_tokenizer:
        step0_prompt = f"<s>[INST] Summarize this academic paper in 1-2 sentences (under 50 words):\n\n{test['article']}\n\n[/INST]"
        step0_inputs = step0_tokenizer(step0_prompt, return_tensors="pt", truncation=True, max_length=400).to(step0_model.device)
        
        with torch.no_grad():
            step0_outputs = step0_model.generate(
                **step0_inputs,
                max_new_tokens=60,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=step0_tokenizer.pad_token_id
            )
        step0_summary = step0_tokenizer.decode(step0_outputs[0], skip_special_tokens=True).split("[/INST]")[-1].strip()
        step0_result = evaluate_summary_detailed(test['abstract'], step0_summary)
    else:
        step0_summary = "N/A"
        step0_result = {"utility": 0, "style": 0, "word_count": 0, "rules": {}}
    
    # 3. STEP 0.2 Qwen 파인튜닝 평가
    with torch.no_grad():
        qwen_ft_outputs = qwen_finetuned.generate(
            **qwen_inputs,
            max_new_tokens=60,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.pad_token_id
        )
    qwen_ft_summary = tokenizer.decode(qwen_ft_outputs[0], skip_special_tokens=True).split("<|im_start|>assistant\n")[-1].strip()
    qwen_ft_result = evaluate_summary_detailed(test['abstract'], qwen_ft_summary)
    
    # 결과 출력
    print(f"  Qwen 베이스: 유용성 {qwen_base_result['utility']:.1f}%, 스타일 {qwen_base_result['style']:.1f}%")
    if step0_model:
        print(f"  STEP 0 (Mistral): 유용성 {step0_result['utility']:.1f}%, 스타일 {step0_result['style']:.1f}%")
    print(f"  STEP 0.2 (Qwen): 유용성 {qwen_ft_result['utility']:.1f}%, 스타일 {qwen_ft_result['style']:.1f}%")
    
    # 결과 저장
    all_results["tests"].append({
        "test_id": test['id'],
        "original_article": test['article'],
        "target_abstract": test['abstract'],
        "qwen_base": {
            "summary": qwen_base_summary,
            "utility": qwen_base_result['utility'],
            "style": qwen_base_result['style'],
            "word_count": qwen_base_result['word_count']
        },
        "step0_mistral_ft": {
            "summary": step0_summary,
            "utility": step0_result['utility'],
            "style": step0_result['style'],
            "word_count": step0_result['word_count']
        } if step0_model else None,
        "step0_2_qwen_ft": {
            "summary": qwen_ft_summary,
            "utility": qwen_ft_result['utility'],
            "style": qwen_ft_result['style'],
            "word_count": qwen_ft_result['word_count']
        }
    })

print("\n" + "="*60)
print("✅ 섹션 4 완료!")
print("다음: 섹션 5 실행 →")
print("="*60)


# ================================================================
# 섹션 5: 결과 분석 및 시각화
# ================================================================

print("\n" + "="*60)
print("📊 섹션 5: 결과 분석")
print("="*60)

# 변수 존재 확인
try:
    all_results
    step0_model
except NameError:
    print("❌ 섹션 4를 먼저 실행해야 합니다!")
    print("섹션 4에서 모델과 결과 데이터가 생성됩니다.")
    raise NameError("섹션 4를 먼저 실행하세요!")

# 평균 계산
avg_qwen_base_u = sum(t['qwen_base']['utility'] for t in all_results['tests']) / 3
avg_qwen_base_s = sum(t['qwen_base']['style'] for t in all_results['tests']) / 3

if step0_model:
    avg_step0_u = sum(t['step0_mistral_ft']['utility'] for t in all_results['tests']) / 3
    avg_step0_s = sum(t['step0_mistral_ft']['style'] for t in all_results['tests']) / 3
else:
    avg_step0_u = 0
    avg_step0_s = 0

avg_qwen_ft_u = sum(t['step0_2_qwen_ft']['utility'] for t in all_results['tests']) / 3
avg_qwen_ft_s = sum(t['step0_2_qwen_ft']['style'] for t in all_results['tests']) / 3

# 요약 추가
all_results["summary"] = {
    "qwen_base": {"utility": avg_qwen_base_u, "style": avg_qwen_base_s},
    "step0_mistral_ft": {"utility": avg_step0_u, "style": avg_step0_s} if step0_model else None,
    "step0_2_qwen_ft": {"utility": avg_qwen_ft_u, "style": avg_qwen_ft_s},
    "qwen_improvement": {
        "utility": avg_qwen_ft_u - avg_qwen_base_u,
        "style": avg_qwen_ft_s - avg_qwen_base_s
    }
}

if step0_model:
    all_results["summary"]["mistral_vs_qwen"] = {
        "utility_diff": avg_step0_u - avg_qwen_ft_u,
        "style_diff": avg_step0_s - avg_qwen_ft_s,
        "qwen_quality_ratio": (avg_qwen_ft_u / avg_step0_u * 100) if avg_step0_u > 0 else 0,
        "winner": "Mistral" if avg_step0_u > avg_qwen_ft_u else "Qwen"
    }

# 결과 출력
print("\n" + "="*60)
print("📈 평균 점수")
print("="*60)

print(f"\nQwen 베이스 (파인튜닝 전):")
print(f"  유용성: {avg_qwen_base_u:.1f}%")
print(f"  스타일: {avg_qwen_base_s:.1f}%")

if step0_model:
    print(f"\nSTEP 0 (Mistral 7B):")
    print(f"  유용성: {avg_step0_u:.1f}%")
    print(f"  스타일: {avg_step0_s:.1f}%")

print(f"\nSTEP 0.2 (Qwen 1.5B):")
print(f"  유용성: {avg_qwen_ft_u:.1f}%")
print(f"  스타일: {avg_qwen_ft_s:.1f}%")

print(f"\n" + "="*60)
print("📊 Qwen 개선도")
print("="*60)
print(f"  유용성: {avg_qwen_ft_u - avg_qwen_base_u:+.1f}%p")
print(f"  스타일: {avg_qwen_ft_s - avg_qwen_base_s:+.1f}%p")

if step0_model:
    quality_ratio = all_results["summary"]["mistral_vs_qwen"]["qwen_quality_ratio"]
    
    print(f"\n" + "="*60)
    print("🏆 Mistral vs Qwen 비교")
    print("="*60)
    print(f"  유용성: Mistral {avg_step0_u:.1f}% vs Qwen {avg_qwen_ft_u:.1f}%")
    print(f"  스타일: Mistral {avg_step0_s:.1f}% vs Qwen {avg_qwen_ft_s:.1f}%")
    print(f"\n  Qwen 품질: Mistral 대비 {quality_ratio:.1f}%")
    print(f"  승자: {all_results['summary']['mistral_vs_qwen']['winner']}")
    
    print(f"\n" + "="*60)
    print("🎯 권장사항")
    print("="*60)
    
    if quality_ratio >= 90:
        print("  ✅ Qwen 성공! (품질 90% 이상)")
        print("     → STEP 2A에서 Qwen 사용 추천")
        print("     → 크기 1/5, 속도 3배!")
    elif quality_ratio >= 85:
        print("  💡 Qwen 양호 (품질 85-90%)")
        print("     → 속도 우선: Qwen")
        print("     → 품질 우선: Mistral")
    else:
        print("  ⚠️ Qwen 부족 (품질 85% 미만)")
        print("     → Mistral 사용 추천")

# 결과 저장
print("\n" + "="*60)
print("💾 결과 저장")
print("="*60)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# JSON
json_file = RESULTS_DIR / f"results_{timestamp}.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)
print(f"✅ JSON: {json_file}")

# CSV
csv_file = RESULTS_DIR / f"results_{timestamp}.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    
    if step0_model:
        writer.writerow(['Test', 'Qwen Base U', 'Qwen Base S', 
                        'Mistral U', 'Mistral S', 'Qwen FT U', 'Qwen FT S'])
        for t in all_results['tests']:
            writer.writerow([
                t['test_id'],
                f"{t['qwen_base']['utility']:.1f}",
                f"{t['qwen_base']['style']:.1f}",
                f"{t['step0_mistral_ft']['utility']:.1f}",
                f"{t['step0_mistral_ft']['style']:.1f}",
                f"{t['step0_2_qwen_ft']['utility']:.1f}",
                f"{t['step0_2_qwen_ft']['style']:.1f}"
            ])
        writer.writerow(['Average', 
                        f"{avg_qwen_base_u:.1f}", f"{avg_qwen_base_s:.1f}",
                        f"{avg_step0_u:.1f}", f"{avg_step0_s:.1f}",
                        f"{avg_qwen_ft_u:.1f}", f"{avg_qwen_ft_s:.1f}"])
    else:
        writer.writerow(['Test', 'Qwen Base U', 'Qwen Base S', 'Qwen FT U', 'Qwen FT S'])
        for t in all_results['tests']:
            writer.writerow([
                t['test_id'],
                f"{t['qwen_base']['utility']:.1f}",
                f"{t['qwen_base']['style']:.1f}",
                f"{t['step0_2_qwen_ft']['utility']:.1f}",
                f"{t['step0_2_qwen_ft']['style']:.1f}"
            ])
        writer.writerow(['Average', 
                        f"{avg_qwen_base_u:.1f}", f"{avg_qwen_base_s:.1f}",
                        f"{avg_qwen_ft_u:.1f}", f"{avg_qwen_ft_s:.1f}"])

print(f"✅ CSV: {csv_file}")

# 메모리 정리
print("\n🧹 메모리 정리...")
del qwen_base, qwen_finetuned
if step0_model:
    del step0_model
gc.collect()
torch.cuda.empty_cache()
print("✅ 정리 완료")

print("\n" + "="*60)
print("🎉 STEP 0.2 완료!")
print("="*60)

if step0_model:
    print(f"\n🏆 최종 결과:")
    print(f"  Qwen 품질: Mistral 대비 {quality_ratio:.1f}%")
    print(f"  승자: {all_results['summary']['mistral_vs_qwen']['winner']}")

print(f"\n📁 결과 파일:")
print(f"  {json_file.name}")
print(f"  {csv_file.name}")
