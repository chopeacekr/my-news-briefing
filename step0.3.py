"""
=================================================================
📰 STEP 0.3: V6 최종 버전 (Few-shot + 초강화)
=================================================================

🆕 V6 개선 사항:
✅ Few-shot 프롬프트 (예시 기반 학습)
✅ 초강화 후처리 (패턴 3배 확장)
✅ 논문 첫 부분 스킵
✅ "Brief:" 기준 추출
✅ 프롬프트 완전 차단

🎯 MODE 설정

MODE = 0  ← 여기를 변경하세요!

0: 전체 실행 (STEP 1-8 + A/B + 분석 + 랜덤)
1: 랜덤 테스트만

🎯 후처리 모드 설정

POST_PROCESS_MODE = "smart"  ← 여기를 변경하세요!

"smart": 완결된 문장만 (안전, 추천)
"aggressive": 항상 2문장 시도 (적극적)

=================================================================
"""

# ================================================================
# ⚙️ 설정
# ================================================================

MODE = 0  # 0: 전체, 1: 랜덤 테스트만
POST_PROCESS_MODE = "smart"  # "smart" 또는 "aggressive"
NUM_RANDOM_TESTS = 3  # 랜덤 테스트 개수 (1-10)

# ================================================================

import subprocess
import sys
import os
from pathlib import Path

print("="*60)
print("🚀 STEP 0.3 V6 - Few-shot + 초강화")
print("="*60)
print(f"\nMODE: {MODE}")
print(f"후처리 모드: {POST_PROCESS_MODE}")

if MODE == 0:
    print("→ 전체 실행 (STEP 1-8 + A/B + 분석 + 랜덤)")
elif MODE == 1:
    print("→ 랜덤 테스트만")
else:
    raise ValueError(f"❌ 잘못된 MODE: {MODE}")

print("="*60)


# ================================================================
# 🔧 V6 후처리 함수 (초강화!) ⭐⭐⭐
# ================================================================

import re

def clean_output_v6(raw_text, original_article=""):
    """
    V6 초강화 후처리
    
    개선:
    - Brief: 기준 추출
    - 프롬프트 패턴 3배 확장
    - 논문 첫 부분 스킵
    - 더 공격적인 정제
    """
    
    # STEP 1: "Brief:" 이후만 추출
    if "Brief:" in raw_text:
        text = raw_text.split("Brief:")[-1].strip()
    elif "Summary:" in raw_text:
        text = raw_text.split("Summary:")[-1].strip()
    else:
        text = raw_text.strip()
    
    # STEP 2: 모든 ### 및 특수 구분자 제거
    text = re.sub(r'#{1,}', '', text)
    text = re.sub(r'={3,}', '', text)
    text = re.sub(r'-{3,}', '', text)
    
    # STEP 3: 프롬프트 패턴 제거 (대폭 확장!)
    prompt_patterns = [
        # Write 시리즈
        r'(?i)write\s+a\s+.*?brief',
        r'(?i)write\s+exactly',
        r'(?i)write.*?sentence',
        
        # 숫자 관련
        r'(?i)max\s+\d+\s+words?',
        r'(?i)\d+-sentence',
        r'(?i)2-sentence',
        r'(?i)45\s+words?',
        
        # Brief/Summary 관련
        r'(?i)research\s+news\s+brief',
        r'(?i)news\s+brief',
        r'(?i)brief\s*:',
        r'(?i)summary\s*:',
        
        # For this 시리즈
        r'(?i)for\s+this\s+paper',
        r'(?i)for\s+this\s+research',
        
        # Paper 관련
        r'(?i)paper\s*:',
        r'(?i)the\s+paper',
        r'(?i)this\s+paper',
        
        # 기타 프롬프트
        r'(?i)system\s*',
        r'(?i)task\s*:',
        r'(?i)requirements?\s*:',
        r'(?i)summarize',
        r'(?i)scientific\s+editor',
        r'(?i)academic\s+audience',
    ]
    
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text)
    
    # STEP 4: 논문 첫 문장 패턴 제거
    paper_start_patterns = [
        r'(?i)^information-theoretic\s+research.*?\.',
        r'(?i)^it\s+is\s+believed\s+that.*?\.',
        r'(?i)^semiconductor\s+devices\s+have.*?\.',
        r'(?i)^we\s+present\s+a\s+novel.*?\.',
        r'(?i)^this\s+paper\s+investigates.*?\.',
        r'(?i)^in\s+this\s+paper.*?\.',
        r'(?i)^the\s+authors?\s+consider.*?\.',
    ]
    
    for pattern in paper_start_patterns:
        text = re.sub(pattern, '', text, count=1)
    
    # STEP 5: 논문과 동일한 시작 부분 제거
    if original_article and len(original_article) > 100:
        article_start = original_article[:100].lower()
        text_start = text[:100].lower()
        
        # 유사도 체크 (단순 버전)
        common_words = set(article_start.split()) & set(text_start.split())
        if len(common_words) > 10:  # 10개 이상 공통 단어
            # 첫 50단어 스킵
            words = text.split()
            if len(words) > 50:
                text = ' '.join(words[50:])
    
    # STEP 6: LaTeX 제거
    latex_patterns = [r'\$+', r'\\[a-zA-Z]+', r'@xmath\d+', r'@xcite']
    for pattern in latex_patterns:
        text = re.sub(pattern, '', text)
    
    # STEP 7: 정리
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    text = text.strip()
    
    # STEP 8: 빈 텍스트 체크
    if not text or len(text) < 20:
        return "[요약 생성 실패 - 출력 없음]"
    
    # STEP 9: 금지 키워드 체크
    forbidden_in_output = [
        'write', 'brief', 'paper:', 'summary:', 'max', 'words',
        '2-sentence', 'sentence', 'task', 'requirements'
    ]
    
    # 첫 20단어에 금지 키워드가 있으면 제거
    first_words = ' '.join(text.split()[:20]).lower()
    if any(kw in first_words for kw in forbidden_in_output):
        # 금지 키워드 이후부터 시작
        sentences = re.split(r'[.!?]+', text)
        clean_sentences = []
        for s in sentences:
            if not any(kw in s.lower() for kw in forbidden_in_output):
                if len(s.split()) >= 5:
                    clean_sentences.append(s.strip())
        
        if clean_sentences:
            text = '. '.join(clean_sentences)
        else:
            return "[요약 생성 실패 - 프롬프트 포함]"
    
    # STEP 10: 문장 분리 및 선택
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 5]
    
    if not sentences:
        return "[요약 생성 실패 - 유효 문장 없음]"
    
    # 마침표 추가
    cleaned_sentences = []
    for s in sentences:
        if not s[-1] in '.!?':
            s += '.'
        cleaned_sentences.append(s)
    
    # STEP 11: Smart 선택
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


def clean_output_aggressive_v6(raw_text, original_article=""):
    """V6 Aggressive: 2문장 강제"""
    
    # STEP 1-9: Smart와 동일
    if "Brief:" in raw_text:
        text = raw_text.split("Brief:")[-1].strip()
    elif "Summary:" in raw_text:
        text = raw_text.split("Summary:")[-1].strip()
    else:
        text = raw_text.strip()
    
    text = re.sub(r'#{1,}', '', text)
    
    prompt_patterns = [
        r'(?i)write\s+a\s+.*?brief', r'(?i)max\s+\d+\s+words?',
        r'(?i)2-sentence', r'(?i)for\s+this\s+paper',
        r'(?i)brief\s*:', r'(?i)paper\s*:',
    ]
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text)
    
    paper_patterns = [
        r'(?i)^information-theoretic\s+research.*?\.',
        r'(?i)^it\s+is\s+believed.*?\.',
    ]
    for pattern in paper_patterns:
        text = re.sub(pattern, '', text, count=1)
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text or len(text) < 20:
        return "[요약 생성 실패]"
    
    # 금지 키워드 체크
    forbidden = ['write', 'brief', 'max', 'words', 'sentence']
    first_words = ' '.join(text.split()[:20]).lower()
    if any(kw in first_words for kw in forbidden):
        sentences = re.split(r'[.!?]+', text)
        clean_sentences = [s.strip() for s in sentences 
                          if not any(kw in s.lower() for kw in forbidden) 
                          and len(s.split()) >= 5]
        if clean_sentences:
            text = '. '.join(clean_sentences)
        else:
            return "[요약 생성 실패]"
    
    # 문장 분리
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 5]
    
    if not sentences:
        return "[요약 생성 실패]"
    
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
    
    # Aggressive: 2문장 강제
    sentence1 = cleaned_sentences[0]
    sentence2 = cleaned_sentences[1]
    
    words1 = sentence1.split()
    words2 = sentence2.split()
    total = len(words1) + len(words2)
    
    if total <= 45:
        return f"{sentence1} {sentence2}"
    
    # 비율 배분
    target1 = min(27, len(words1))
    target2 = min(18, len(words2))
    
    truncated1 = ' '.join(words1[:target1])
    truncated2 = ' '.join(words2[:target2])
    
    if not truncated1.endswith('.'):
        truncated1 += '.'
    if not truncated2.endswith('.'):
        truncated2 += '.'
    
    return f"{truncated1} {truncated2}"


def clean_output(raw_text, original_article=""):
    """선택된 POST_PROCESS_MODE로 후처리"""
    if POST_PROCESS_MODE == "aggressive":
        return clean_output_aggressive_v6(raw_text, original_article)
    else:
        return clean_output_v6(raw_text, original_article)


print(f"\n✅ 후처리 함수 V6 로드 완료 ({POST_PROCESS_MODE} 모드)")


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
    packages = ["transformers", "datasets", "accelerate", "peft"]
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
    from datetime import datetime
    from pathlib import Path
    from datasets import load_dataset
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
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V6-FINAL"
    RESULTS_DIR = Path(OUTPUT_DIR) / "results"
    
    TRAIN_SAMPLES = 40
    VAL_SAMPLES = 10
    NUM_SAMPLES = 50
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n⚙️ 설정:")
    print(f"  모델: Qwen2.5-1.5B-Instruct")
    print(f"  프롬프트: V6 (Few-shot)")
    print(f"  후처리: {POST_PROCESS_MODE} V6 (초강화)")
    print(f"  샘플: Train {TRAIN_SAMPLES}, Val {VAL_SAMPLES}")
    print(f"  출력: {OUTPUT_DIR}")
    
    # ============================================================
    # STEP 3: 데이터 준비
    # ============================================================
    
    print("\n" + "="*60)
    print("📥 STEP 3: 데이터 준비")
    print("="*60)
    
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
    
    print("📥 ArXiv 데이터 로딩...")
    dataset = load_dataset("ccdv/arxiv-summarization", split=f"train[:{NUM_SAMPLES}]")
    print(f"✅ {len(dataset)}개 로드")
    
    print("🔄 전처리 중...")
    dataset = dataset.map(lambda x: {
        'article': clean_arxiv_text(x['article']),
        'abstract': clean_arxiv_text(x['abstract'])
    })
    
    print("✂️ Train/Val 분할...")
    dataset = dataset.train_test_split(test_size=VAL_SAMPLES, seed=42)
    train_dataset = dataset['train']
    val_dataset = dataset['test']
    
    print(f"✅ Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    
    # ============================================================
    # STEP 4: 프롬프트 적용 (V6 - Few-shot!) ⭐⭐⭐
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 STEP 4: V6 Few-shot 프롬프트 적용")
    print("="*60)
    
    # ⭐ V6 프롬프트: Few-shot 예시 기반!
    FEW_SHOT_EXAMPLES = """Paper: We developed a novel deep learning architecture combining transformers and convolutional networks for image classification.
Brief: Novel hybrid architecture combining transformers and CNNs achieves superior image classification performance.

Paper: This study examines the effects of climate change on coral reef ecosystems through five-year monitoring across Pacific regions.
Brief: Five-year study reveals significant climate change impacts on Pacific coral reef ecosystems.

"""
    
    def formatting_prompts_func(example):
        # Few-shot 예시 + 실제 데이터
        text = f"{FEW_SHOT_EXAMPLES}Paper: {example['article']}\nBrief: {example['abstract']}"
        return {"text": text}
    
    print("🔄 V6 Few-shot 프롬프트 적용 중...")
    train_dataset = train_dataset.map(formatting_prompts_func)
    val_dataset = val_dataset.map(formatting_prompts_func)
    print("✅ 프롬프트 적용 완료")
    
    # ============================================================
    # STEP 5: 토크나이즈
    # ============================================================
    
    print("\n" + "="*60)
    print("🔤 STEP 5: 토크나이즈")
    print("="*60)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("✅ 토크나이저 로드")
    
    def tokenize_function(example):
        result = tokenizer(example['text'], truncation=True, max_length=512, padding=False)
        result['labels'] = result['input_ids'].copy()
        return result
    
    print("🔄 토크나이즈 중...")
    train_dataset_tokenized = train_dataset.map(tokenize_function, remove_columns=train_dataset.column_names)
    val_dataset_tokenized = val_dataset.map(tokenize_function, remove_columns=val_dataset.column_names)
    print("✅ 토크나이즈 완료")
    
    # ============================================================
    # STEP 6: 모델 로딩
    # ============================================================
    
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
    
    # ============================================================
    # STEP 7: 학습
    # ============================================================
    
    print("\n" + "="*60)
    print("🎯 STEP 7: 모델 학습")
    print("="*60)
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=20,
        eval_strategy="steps",
        eval_steps=20,
        warmup_steps=2,
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
    print(f"  Epochs: 1")
    print(f"  Batch size: 1 × 4")
    print(f"  Learning rate: 2e-4")
    print()
    
    trainer.train()
    
    print("\n✅ 학습 완료!")
    
    # ============================================================
    # STEP 8: 저장
    # ============================================================
    
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
        "prompt": "V6 Few-shot",
        "post_process": f"{POST_PROCESS_MODE} V6 초강화",
        "train_samples": TRAIN_SAMPLES,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(final_model_path / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # 정리
    del model, trainer
    gc.collect()
    torch.cuda.empty_cache()
    
    print("\n" + "="*60)
    print("✅ STEP 1-8 완료!")
    print("="*60)
    
    # ============================================================
    # A/B 테스트 (V6) ⭐
    # ============================================================
    
    print("\n" + "="*60)
    print("🔬 A/B 테스트 (V6)")
    print("="*60)
    
    # V6 Few-shot 프롬프트
    def make_prompt_v6(article):
        return f"""{FEW_SHOT_EXAMPLES}Paper: {article}
Brief:"""
    
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
    
    print("✅ 모델 로드 완료")
    
    # 테스트
    tests = [
        {"id": 1, "article": "We present a novel deep learning approach for natural language processing tasks. Our method combines recurrent and convolutional neural networks to achieve state-of-the-art results on multiple benchmarks including GLUE and SuperGLUE.", "abstract": "Novel hybrid neural architecture achieves state-of-the-art NLP results."},
        {"id": 2, "article": "This paper investigates the impact of climate change on Arctic ecosystems through extensive five-year field studies. Our observations reveal significant habitat shifts and species migration patterns across monitored regions.", "abstract": "Five-year field study reveals climate change impacts on Arctic ecosystems."},
        {"id": 3, "article": "We introduce a new quantum computing algorithm that achieves 100x speedup for optimization problems. The proposed method leverages quantum entanglement to explore solution spaces more efficiently than classical approaches.", "abstract": "New quantum algorithm achieves 100x speedup for optimization tasks."}
    ]
    
    all_results = []
    
    print("\n🧪 테스트 실행...")
    
    for i, test in enumerate(tests):
        print(f"  Test {i+1}/3...", end=" ")
        
        prompt = make_prompt_v6(test['article'])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_base.device)
        
        # 베이스
        with torch.no_grad():
            outputs = qwen_base.generate(
                **inputs, max_new_tokens=80, min_length=30, temperature=0.5,
                do_sample=True, top_p=0.9, repetition_penalty=1.2,
                no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
            )
        base_summary = clean_output(tokenizer.decode(outputs[0], skip_special_tokens=True), test['article'])
        
        # 파인튜닝
        with torch.no_grad():
            outputs = qwen_ft.generate(
                **inputs, max_new_tokens=80, min_length=30, temperature=0.5,
                do_sample=True, top_p=0.9, repetition_penalty=1.2,
                no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
            )
        ft_summary = clean_output(tokenizer.decode(outputs[0], skip_special_tokens=True), test['article'])
        
        all_results.append({
            "test_id": test['id'],
            "article": test['article'],
            "target": test['abstract'],
            "base_summary": base_summary,
            "base_words": len(base_summary.split()) if '[' not in base_summary else 0,
            "ft_summary": ft_summary,
            "ft_words": len(ft_summary.split()) if '[' not in ft_summary else 0
        })
        
        print("✅")
    
    # 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = RESULTS_DIR / f"ab_test_v6_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({"metadata": {"version": "V6", "timestamp": datetime.now().isoformat()}, "results": all_results}, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 저장: {json_file.name}")
    
    # 분석
    print("\n" + "="*60)
    print("📊 결과 분석")
    print("="*60)
    
    base_valid = [r for r in all_results if '[' not in r['base_summary']]
    ft_valid = [r for r in all_results if '[' not in r['ft_summary']]
    
    if base_valid:
        avg_base = sum(r['base_words'] for r in base_valid) / len(base_valid)
        print(f"\n베이스: {avg_base:.1f}단어 ({len(base_valid)}/3 성공)")
    else:
        print(f"\n베이스: 0/3 성공")
    
    if ft_valid:
        avg_ft = sum(r['ft_words'] for r in ft_valid) / len(ft_valid)
        print(f"파인튜닝: {avg_ft:.1f}단어 ({len(ft_valid)}/3 성공)")
    else:
        print(f"파인튜닝: 0/3 성공")
    
    print("\n샘플:")
    for r in all_results[:2]:
        print(f"\n논문: {r['article'][:60]}...")
        print(f"베이스: {r['base_summary']}")
        print(f"파인튜닝: {r['ft_summary']}")
    
    print("\n" + "="*60)
    print("✅ A/B 완료!")
    print("="*60)


# ================================================================
# 랜덤 테스트 (V6) ⭐
# ================================================================

print("\n" + "="*60)
print("🎲 랜덤 테스트 (V6)")
print("="*60)

if MODE == 1:
    import torch, gc, json, random
    from datetime import datetime
    from pathlib import Path
    from datasets import load_dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V6-FINAL"
    final_model_path = Path(OUTPUT_DIR) / "final_model"
    
    if not final_model_path.exists():
        raise FileNotFoundError(f"모델 없음: {final_model_path}")
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
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
    
    # Few-shot 예시
    FEW_SHOT_EXAMPLES = """Paper: We developed a novel deep learning architecture combining transformers and convolutional networks for image classification.
Brief: Novel hybrid architecture combining transformers and CNNs achieves superior image classification performance.

Paper: This study examines the effects of climate change on coral reef ecosystems through five-year monitoring across Pacific regions.
Brief: Five-year study reveals significant climate change impacts on Pacific coral reef ecosystems.

"""

# 데이터
def clean_arxiv_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'@xmath\d+|@xcite|@xref|\$.*?\$|\\[a-zA-Z]+\{.*?\}', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

full_dataset = load_dataset("ccdv/arxiv-summarization", split="train[:1000]")
full_dataset = full_dataset.map(lambda x: {'article': clean_arxiv_text(x['article']), 'abstract': clean_arxiv_text(x['abstract'])})
print(f"✅ 1000개 로드")

random_indices = random.sample(range(len(full_dataset)), NUM_RANDOM_TESTS)
print(f"인덱스: {random_indices}")

# V6 Few-shot 프롬프트
def make_prompt_v6(article):
    return f"""{FEW_SHOT_EXAMPLES}Paper: {article}
Brief:"""

print("\n" + "="*60)
print("🔮 추론 시작")
print("="*60)

for i, idx in enumerate(random_indices):
    paper = full_dataset[idx]
    
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📄 테스트 {i+1}/{NUM_RANDOM_TESTS} (인덱스: {idx})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    print(f"\n📖 논문 원본 (처음 500자):")
    print("-"*60)
    print(paper['article'][:500] + "...")
    print("-"*60)
    
    print(f"\n📌 원본 초록:")
    print("-"*60)
    print(paper['abstract'])
    print("-"*60)
    
    print(f"\n🔮 추론 중 (V6: {POST_PROCESS_MODE})...")
    
    prompt = make_prompt_v6(paper['article'])
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_ft.device)
    
    with torch.no_grad():
        outputs = qwen_ft.generate(
            **inputs, max_new_tokens=80, min_length=30, temperature=0.5,
            do_sample=True, top_p=0.9, repetition_penalty=1.2,
            no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
        )
    
    clean = clean_output(tokenizer.decode(outputs[0], skip_special_tokens=True), paper['article'])
    
    print(f"\n📰 Research News Brief:")
    print("="*60)
    print(clean)
    print("="*60)
    
    is_failed = '[' in clean
    word_count = 0 if is_failed else len(clean.split())
    sentence_count = 0 if is_failed else len([s for s in re.split(r'[.!?]+', clean) if s.strip()])
    
    print(f"\n📊 통계:")
    print(f"  생성 성공: {'❌ 실패' if is_failed else '✅ 성공'}")
    if not is_failed:
        print(f"  단어 수: {word_count}")
        print(f"  문장 수: {sentence_count}")
        print(f"  45단어: {'✅' if word_count <= 45 else '❌'}")
        print(f"  2문장: {'✅' if sentence_count == 2 else '⚠️ ' + str(sentence_count)}")

print("\n" + "="*60)
print("✅ 완료!")
print("="*60)

if MODE == 0:
    print("\n✨ V6 개선:")
    print("  ✅ Few-shot 프롬프트 (예시 기반)")
    print("  ✅ 초강화 후처리 (패턴 3배)")
    print("  ✅ Brief: 기준 추출")
    print("  ✅ 논문 첫 부분 스킵")
    print(f"\n📁 출력: {OUTPUT_DIR}")

print("\n🚀 V6 완성!")
print("="*60)