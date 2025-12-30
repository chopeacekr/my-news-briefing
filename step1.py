# ============================================================
# STEP 1: 본격 실험 (Mistral-7B, 1000개, GPU T4)
#
# 목적: STEP 0 (50개) vs STEP 1 (1000개) 성능 비교
#
# 개선사항:
#   1. 프롬프트 단순화: "1-2 sentences (under 50 words)"
#   2. 생성 파라미터: temperature=0.3, repetition_penalty=1.2
#   3. 데이터 전처리: LaTeX 기호 제거
#
# 비교:
#   STEP 0: 50개 샘플 (빠른 검증)
#   STEP 1: 1000개 샘플 (본격 실험)
#
# 예상 시간: 25분
# ============================================================

import sys
import subprocess
from pathlib import Path

INSTALL_FLAG = Path("/tmp/step1_installed.flag")

if not INSTALL_FLAG.exists():
    print("="*60)
    print("패키지 설치 중...")
    print("="*60)
    
    packages = ["transformers", "datasets", "accelerate", "peft", "bitsandbytes"]
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-U", package])
    
    INSTALL_FLAG.touch()
    
    print("\n" + "="*60)
    print("✅ 패키지 설치 완료!")
    print("🔴 Runtime 재시작 필요!")
    print("="*60)
    print("\n재시작 후 이 셀을 다시 실행하세요!")
    
else:
    import torch
    import gc
    import json
    import csv
    import re
    from datetime import datetime
    from datasets import load_dataset
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, PeftModel, prepare_model_for_kbit_training
    from google.colab import drive
    
    print("="*60)
    print("STEP 1: 본격 실험 (1000개)")
    print("="*60)
    
    # GPU 확인
    if not torch.cuda.is_available():
        raise RuntimeError("❌ GPU 없음! Runtime → T4 GPU 선택")
    
    print(f"\n✅ GPU: {torch.cuda.get_device_name(0)}")
    
    # GPU 메모리 정리
    print("\nGPU 메모리 정리 중...")
    torch.cuda.empty_cache()
    gc.collect()
    
    total_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
    allocated_mem = torch.cuda.memory_allocated(0) / 1024**3
    print(f"✅ GPU 메모리: {total_mem:.2f} GB (사용: {allocated_mem:.2f} GB)")
    
    # ================================================================
    # 설정
    # ================================================================
    
    BASE_MODEL = "mistralai/Mistral-7B-v0.1"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP1-Mistral-7B-1000"
    RESULTS_DIR = Path(OUTPUT_DIR) / "ab_test_results"
    
    TRAIN_SAMPLES = 800
    VAL_SAMPLES = 200
    NUM_SAMPLES = 1000
    
    # Drive 마운트
    if not Path("/content/drive").exists():
        drive.mount('/content/drive')
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ 출력: {OUTPUT_DIR}")
    print(f"✅ 샘플: {NUM_SAMPLES}개 (Train {TRAIN_SAMPLES}, Val {VAL_SAMPLES})")
    
    # ================================================================
    # 개선 1: 데이터 전처리
    # ================================================================
    
    print("\n" + "="*60)
    print("개선 1: 데이터 전처리 (LaTeX 기호 제거)")
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
    
    print("데이터 로딩...")
    dataset = load_dataset("ccdv/arxiv-summarization", split=f"train[:{NUM_SAMPLES}]")
    print(f"✅ {len(dataset)}개 로드")
    
    print("전처리 적용...")
    dataset = dataset.map(lambda x: {
        'article': clean_arxiv_text(x['article']),
        'abstract': clean_arxiv_text(x['abstract'])
    })
    print("✅ 전처리 완료")
    
    dataset = dataset.train_test_split(test_size=VAL_SAMPLES, seed=42)
    train_dataset = dataset['train']
    val_dataset = dataset['test']
    
    print(f"\n✅ Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    
    # ================================================================
    # 개선 2: 프롬프트 단순화
    # ================================================================
    
    print("\n" + "="*60)
    print("개선 2: 프롬프트 단순화")
    print("="*60)
    
    def formatting_prompts_func(example):
        text = f"<s>[INST] Summarize this academic paper in 1-2 sentences (under 50 words):\n\n{example['article']}\n\n[/INST]{example['abstract']}</s>"
        return {"text": text}
    
    print("✅ 간소화된 프롬프트: '1-2 sentences (under 50 words)'")
    
    train_dataset = train_dataset.map(formatting_prompts_func)
    val_dataset = val_dataset.map(formatting_prompts_func)
    print("✅ 프롬프트 적용 완료")
    
    # ================================================================
    # 모델 로딩 (GPU, 4-bit)
    # ================================================================
    
    print("\n" + "="*60)
    print("모델 로딩 (GPU, 4-bit 양자화)")
    print("="*60)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
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
    
    print("\n데이터 토크나이즈 중...")
    train_dataset = train_dataset.map(
        tokenize_function,
        remove_columns=train_dataset.column_names
    )
    val_dataset = val_dataset.map(
        tokenize_function,
        remove_columns=val_dataset.column_names
    )
    print("✅ 토크나이즈 완료")
    
    print("\n모델 로딩 중... (4-bit, 메모리 절약)")
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
    print("✅ 모델 로딩 완료 (4-bit, ~3.5GB)")
    
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    print("✅ LoRA 적용 완료")
    model.print_trainable_parameters()
    
    # ================================================================
    # 학습
    # ================================================================
    
    print("\n" + "="*60)
    print("학습 시작 (GPU)")
    print("="*60)
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=1,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
        learning_rate=2e-4,
        logging_steps=50,
        save_steps=400,
        save_total_limit=2,
        eval_strategy="steps",
        eval_steps=400,
        warmup_steps=40,
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
    
    print("\n학습 중... (약 25분 소요)")
    print("💡 1000개 샘플: STEP 0 (50개)보다 20배 많음!")
    trainer.train()
    
    final_model_path = Path(OUTPUT_DIR) / "checkpoints" / "final_model"
    trainer.model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"\n✅ 모델 저장: {final_model_path}")
    
    del model, trainer
    gc.collect()
    torch.cuda.empty_cache()
    
    # ================================================================
    # A/B 테스트 (STEP 0 vs STEP 1)
    # ================================================================
    
    print("\n" + "="*60)
    print("A/B 테스트: STEP 0 vs STEP 1 비교")
    print("="*60)
    
    def evaluate_summary_detailed(original, generated):
        orig_words = set(original.lower().split())
        gen_words = set(generated.lower().split())
        utility = len(orig_words & gen_words) / max(len(orig_words), 1) * 100
        
        word_count = len(generated.split())
        rule1 = 100 if word_count <= 50 else max(0, 100 - (word_count - 50) * 2)
        rule2 = 100 if any(kw in generated.lower() for kw in ["novel", "new", "achieve", "improve", "propose"]) else 50
        tech_terms = [w for w in generated.split() if w[0].isupper() or len(w) > 15]
        rule3 = 100 if len(tech_terms) >= 4 else (75 if len(tech_terms) >= 2 else max(0, len(tech_terms) * 25))
        rule4 = 100 if not any(sw in generated.lower() for sw in ["amazing", "wonderful", "terrible"]) else 50
        rule5 = 100 if any(kw in generated.lower() for kw in ["application", "use", "practical"]) else 50
        style = (rule1 + rule2 + rule3 + rule4 + rule5) / 5
        
        return {"utility": utility, "style": style, "word_count": word_count,
                "rules": {"rule1": rule1, "rule2": rule2, "rule3": rule3, "rule4": rule4, "rule5": rule5}}
    
    print("\n베이스 모델 로딩...")
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    
    # STEP 0 모델 초기화 (중요!)
    step0_model = None
    
    print("STEP 0 파인튜닝 모델 로딩...")
    step0_model_path = "/content/drive/MyDrive/arxiv-STEP0-Mistral-7B-GPU-Test/checkpoints/final_model"
    
    if Path(step0_model_path).exists():
        step0_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            device_map="auto",
            trust_remote_code=True
        )
        step0_model = PeftModel.from_pretrained(step0_model, step0_model_path)
        print("✅ STEP 0 모델 로드 완료")
    else:
        print("⚠️ STEP 0 모델을 찾을 수 없습니다. STEP 0을 먼저 실행하세요.")
        step0_model = None
    
    print("STEP 1 파인튜닝 모델 로딩...")
    step1_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    step1_model = PeftModel.from_pretrained(step1_model, final_model_path)
    
    base_model.eval()
    if step0_model:
        step0_model.eval()
    step1_model.eval()
    
    # STEP 0과 동일한 테스트 데이터
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
    
    all_results = {
        "metadata": {
            "model": "Mistral-7B-v0.1",
            "step": "STEP 1",
            "training_samples": TRAIN_SAMPLES,
            "comparison": "STEP 0 (50) vs STEP 1 (1000)",
            "device": "GPU (4-bit)",
            "timestamp": datetime.now().isoformat()
        },
        "tests": []
    }
    
    print("\n개선 3: 생성 파라미터 조정")
    print("  temperature: 0.3")
    print("  repetition_penalty: 1.2")
    print("  no_repeat_ngram_size: 3")
    
    for i, test in enumerate(tests):
        print(f"\n테스트 {i+1}/3...")
        prompt = f"<s>[INST] Summarize this academic paper in 1-2 sentences (under 50 words):\n\n{test['article']}\n\n[/INST]"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=400).to(base_model.device)
        
        # 베이스 모델
        with torch.no_grad():
            outputs_base = base_model.generate(
                **inputs,
                max_new_tokens=60,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.pad_token_id
            )
        summary_base = tokenizer.decode(outputs_base[0], skip_special_tokens=True).split("[/INST]")[-1].strip()
        result_base = evaluate_summary_detailed(test['abstract'], summary_base)
        
        # STEP 0 모델
        if step0_model:
            with torch.no_grad():
                outputs_step0 = step0_model.generate(
                    **inputs,
                    max_new_tokens=60,
                    temperature=0.3,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=3,
                    pad_token_id=tokenizer.pad_token_id
                )
            summary_step0 = tokenizer.decode(outputs_step0[0], skip_special_tokens=True).split("[/INST]")[-1].strip()
            result_step0 = evaluate_summary_detailed(test['abstract'], summary_step0)
        else:
            summary_step0 = "N/A"
            result_step0 = {"utility": 0, "style": 0, "word_count": 0, "rules": {}}
        
        # STEP 1 모델
        with torch.no_grad():
            outputs_step1 = step1_model.generate(
                **inputs,
                max_new_tokens=60,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.pad_token_id
            )
        summary_step1 = tokenizer.decode(outputs_step1[0], skip_special_tokens=True).split("[/INST]")[-1].strip()
        result_step1 = evaluate_summary_detailed(test['abstract'], summary_step1)
        
        print(f"  베이스: 유용성 {result_base['utility']:.1f}%, 스타일 {result_base['style']:.1f}%")
        if step0_model:
            print(f"  STEP 0 (50개): 유용성 {result_step0['utility']:.1f}%, 스타일 {result_step0['style']:.1f}%")
        print(f"  STEP 1 (1000개): 유용성 {result_step1['utility']:.1f}%, 스타일 {result_step1['style']:.1f}%")
        
        all_results["tests"].append({
            "test_id": test['id'],
            "original_article": test['article'],
            "target_abstract": test['abstract'],
            "base_model": {
                "summary": summary_base,
                "utility": result_base['utility'],
                "style": result_base['style'],
                "word_count": result_base['word_count'],
                "rules": result_base['rules']
            },
            "step0_model": {
                "summary": summary_step0,
                "utility": result_step0['utility'],
                "style": result_step0['style'],
                "word_count": result_step0['word_count'],
                "rules": result_step0['rules']
            } if step0_model else None,
            "step1_model": {
                "summary": summary_step1,
                "utility": result_step1['utility'],
                "style": result_step1['style'],
                "word_count": result_step1['word_count'],
                "rules": result_step1['rules']
            }
        })
    
    # 평균 계산
    avg_base_u = sum(t['base_model']['utility'] for t in all_results['tests']) / 3
    avg_base_s = sum(t['base_model']['style'] for t in all_results['tests']) / 3
    
    if step0_model:
        avg_step0_u = sum(t['step0_model']['utility'] for t in all_results['tests']) / 3
        avg_step0_s = sum(t['step0_model']['style'] for t in all_results['tests']) / 3
    else:
        avg_step0_u = 0
        avg_step0_s = 0
    
    avg_step1_u = sum(t['step1_model']['utility'] for t in all_results['tests']) / 3
    avg_step1_s = sum(t['step1_model']['style'] for t in all_results['tests']) / 3
    
    all_results["summary"] = {
        "base": {"utility": avg_base_u, "style": avg_base_s},
        "step0": {"utility": avg_step0_u, "style": avg_step0_s} if step0_model else None,
        "step1": {"utility": avg_step1_u, "style": avg_step1_s},
        "improvement_step0_to_step1": {
            "utility": avg_step1_u - avg_step0_u if step0_model else 0,
            "style": avg_step1_s - avg_step0_s if step0_model else 0
        }
    }
    
    print(f"\n{'='*60}")
    print(f"베이스: 유용성 {avg_base_u:.1f}%, 스타일 {avg_base_s:.1f}%")
    if step0_model:
        print(f"STEP 0 (50개): 유용성 {avg_step0_u:.1f}%, 스타일 {avg_step0_s:.1f}%")
        print(f"STEP 1 (1000개): 유용성 {avg_step1_u:.1f}%, 스타일 {avg_step1_s:.1f}%")
        print(f"\nSTEP 0 → STEP 1 개선:")
        print(f"  유용성: {avg_step1_u-avg_step0_u:+.1f}%p")
        print(f"  스타일: {avg_step1_s-avg_step0_s:+.1f}%p")
    else:
        print(f"STEP 1 (1000개): 유용성 {avg_step1_u:.1f}%, 스타일 {avg_step1_s:.1f}%")
    print(f"{'='*60}")
    
    # 결과 저장 (JSON, CSV, MD)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_file = RESULTS_DIR / f"step0_vs_step1_results_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON 저장: {json_file}")
    
    # CSV
    csv_file = RESULTS_DIR / f"step0_vs_step1_results_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if step0_model:
            writer.writerow(['Test ID', 'Base Utility', 'Base Style', 'STEP 0 Utility', 'STEP 0 Style', 'STEP 1 Utility', 'STEP 1 Style'])
            for t in all_results['tests']:
                writer.writerow([
                    t['test_id'],
                    f"{t['base_model']['utility']:.1f}",
                    f"{t['base_model']['style']:.1f}",
                    f"{t['step0_model']['utility']:.1f}",
                    f"{t['step0_model']['style']:.1f}",
                    f"{t['step1_model']['utility']:.1f}",
                    f"{t['step1_model']['style']:.1f}"
                ])
            writer.writerow(['Average', f"{avg_base_u:.1f}", f"{avg_base_s:.1f}", f"{avg_step0_u:.1f}", f"{avg_step0_s:.1f}", f"{avg_step1_u:.1f}", f"{avg_step1_s:.1f}"])
        else:
            writer.writerow(['Test ID', 'Base Utility', 'Base Style', 'STEP 1 Utility', 'STEP 1 Style'])
            for t in all_results['tests']:
                writer.writerow([
                    t['test_id'],
                    f"{t['base_model']['utility']:.1f}",
                    f"{t['base_model']['style']:.1f}",
                    f"{t['step1_model']['utility']:.1f}",
                    f"{t['step1_model']['style']:.1f}"
                ])
            writer.writerow(['Average', f"{avg_base_u:.1f}", f"{avg_base_s:.1f}", f"{avg_step1_u:.1f}", f"{avg_step1_s:.1f}"])
    print(f"✅ CSV 저장: {csv_file}")
    
    # Markdown
    md_file = RESULTS_DIR / f"step0_vs_step1_results_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# STEP 0 vs STEP 1 비교 결과\n\n")
        f.write(f"**비교:** STEP 0 (50개) vs STEP 1 (1000개)\n")
        f.write(f"**실행 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 요약\n\n")
        f.write(f"| 모델 | 유용성 | 스타일 |\n")
        f.write(f"|------|--------|--------|\n")
        f.write(f"| 베이스 | {avg_base_u:.1f}% | {avg_base_s:.1f}% |\n")
        if step0_model:
            f.write(f"| STEP 0 (50개) | {avg_step0_u:.1f}% | {avg_step0_s:.1f}% |\n")
            f.write(f"| STEP 1 (1000개) | {avg_step1_u:.1f}% | {avg_step1_s:.1f}% |\n\n")
            f.write(f"**개선도 (STEP 0 → STEP 1):**\n")
            f.write(f"- 유용성: {avg_step1_u-avg_step0_u:+.1f}%p\n")
            f.write(f"- 스타일: {avg_step1_s-avg_step0_s:+.1f}%p\n")
        else:
            f.write(f"| STEP 1 (1000개) | {avg_step1_u:.1f}% | {avg_step1_s:.1f}% |\n")
    print(f"✅ MD 저장: {md_file}")
    
    del base_model
    if step0_model:
        del step0_model
    del step1_model
    gc.collect()
    torch.cuda.empty_cache()
    
    INSTALL_FLAG.unlink()
    
    print("\n" + "="*60)
    print("✅ STEP 1 완료!")
    print("="*60)
    print(f"\nSTEP 1 (1000개) 결과:")
    print(f"  유용성: {avg_step1_u:.1f}%")
    print(f"  스타일: {avg_step1_s:.1f}%")
    
    if step0_model:
        print(f"\nSTEP 0 (50개) vs STEP 1 (1000개):")
        print(f"  유용성 개선: {avg_step1_u-avg_step0_u:+.1f}%p")
        print(f"  스타일 개선: {avg_step1_s-avg_step0_s:+.1f}%p")
        
        if avg_step1_u > avg_step0_u + 5:
            print(f"\n✅ 1000개 샘플이 50개보다 확실히 우수!")
        elif avg_step1_u > avg_step0_u:
            print(f"\n✅ 1000개 샘플이 약간 더 우수")
        else:
            print(f"\n💡 성능 차이 작음 (더 많은 에폭 필요할 수 있음)")
    
    print(f"\n다음 단계:")
    print(f"  1. STEP 0 vs STEP 1 결과 비교")
    print(f"  2. 더 나은 설정 선택")
    print(f"  3. STEP 3 (3 Epochs) 진행")