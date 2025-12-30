# ============================================================
# STEP 0.1: Phi-2 A/B 테스트 (GPU T4, 50개)
#
# 목적: Mistral-7B vs Phi-2 성능 비교
#
# 모델: microsoft/phi-2 (2.7B 파라미터)
# 데이터: STEP 0 GPU와 동일 (50개, seed=42)
# 비교: Mistral-7B 결과와 비교
#
# 장점:
#   - 더 작은 모델 (2.7B vs 7B)
#   - 더 빠른 추론
#   - 메모리 효율적
#
# 시간: 2-3분 (Mistral보다 빠름)
# ============================================================

import sys
import subprocess
from pathlib import Path

INSTALL_FLAG = Path("/tmp/step0_1_phi2_installed.flag")

if not INSTALL_FLAG.exists():
    print("="*60)
    print("패키지 설치 중...")
    print("="*60)
    
    packages = ["transformers", "datasets", "accelerate", "peft", "bitsandbytes", "einops"]
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
    print("STEP 0.1: Phi-2 A/B 테스트 (GPU)")
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
    
    BASE_MODEL = "microsoft/phi-2"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.1-Phi2-GPU-Test"
    RESULTS_DIR = Path(OUTPUT_DIR) / "ab_test_results"
    
    TRAIN_SAMPLES = 40
    VAL_SAMPLES = 10
    NUM_SAMPLES = 50
    
    # Drive 마운트
    if not Path("/content/drive").exists():
        drive.mount('/content/drive')
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ 모델: Phi-2 (2.7B)")
    print(f"✅ 출력: {OUTPUT_DIR}")
    
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
    
    # STEP 0 GPU와 동일한 split (seed=42)
    dataset = dataset.train_test_split(test_size=VAL_SAMPLES, seed=42)
    train_dataset = dataset['train']
    val_dataset = dataset['test']
    
    print(f"\n✅ Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    print("💡 STEP 0 GPU와 동일한 데이터 (seed=42)")
    
    # ================================================================
    # 개선 2: 프롬프트 단순화 (Phi-2 형식)
    # ================================================================
    
    print("\n" + "="*60)
    print("개선 2: 프롬프트 단순화 (Phi-2 형식)")
    print("="*60)
    
    def formatting_prompts_func(example):
        # Phi-2는 Instruct: 형식 사용
        text = f"Instruct: Summarize this academic paper in 1-2 sentences (under 50 words):\n\n{example['article']}\n\nOutput: {example['abstract']}"
        return {"text": text}
    
    print("✅ Phi-2 프롬프트: 'Instruct: ... Output:' 형식")
    
    train_dataset = train_dataset.map(formatting_prompts_func)
    val_dataset = val_dataset.map(formatting_prompts_func)
    print("✅ 프롬프트 적용 완료")
    
    # ================================================================
    # 모델 로딩 (GPU, 4-bit)
    # ================================================================
    
    print("\n" + "="*60)
    print("모델 로딩 (Phi-2, 4-bit 양자화)")
    print("="*60)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    
    # Phi-2는 pad_token 설정 필요
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
    
    print("\n모델 로딩 중... (Phi-2, 4-bit, ~2GB)")
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
    print("✅ 모델 로딩 완료 (4-bit, ~2GB, Mistral보다 작음!)")
    
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "dense"],  # Phi-2용
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
    print("학습 시작 (GPU, Phi-2)")
    print("="*60)
    
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
    
    print("\n학습 중... (약 2-3분 소요, Phi-2는 더 빠름!)")
    trainer.train()
    
    final_model_path = Path(OUTPUT_DIR) / "checkpoints" / "final_model"
    trainer.model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"\n✅ 모델 저장: {final_model_path}")
    
    del model, trainer
    gc.collect()
    torch.cuda.empty_cache()
    
    # ================================================================
    # A/B 테스트
    # ================================================================
    
    print("\n" + "="*60)
    print("A/B 테스트 시작")
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
    
    print("파인튜닝 모델 로딩...")
    finetuned_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    finetuned_model = PeftModel.from_pretrained(finetuned_model, final_model_path)
    
    base_model.eval()
    finetuned_model.eval()
    
    # STEP 0 GPU와 동일한 테스트 데이터
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
            "model": "microsoft/phi-2",
            "model_size": "2.7B",
            "step": "STEP 0.1",
            "training_samples": TRAIN_SAMPLES,
            "device": "GPU (4-bit)",
            "comparison": "vs Mistral-7B (STEP 0 GPU)",
            "timestamp": datetime.now().isoformat()
        },
        "tests": []
    }
    
    print("\n개선 3: 생성 파라미터 조정 (STEP 0 GPU와 동일)")
    print("  temperature: 0.3")
    print("  repetition_penalty: 1.2")
    print("  no_repeat_ngram_size: 3")
    
    for i, test in enumerate(tests):
        print(f"\n테스트 {i+1}/3...")
        prompt = f"Instruct: Summarize this academic paper in 1-2 sentences (under 50 words):\n\n{test['article']}\n\nOutput:"
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
        
        summary_base = tokenizer.decode(outputs_base[0], skip_special_tokens=True).split("Output:")[-1].strip()
        result_base = evaluate_summary_detailed(test['abstract'], summary_base)
        
        # 파인튜닝 모델
        with torch.no_grad():
            outputs_ft = finetuned_model.generate(
                **inputs,
                max_new_tokens=60,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.pad_token_id
            )
        
        summary_ft = tokenizer.decode(outputs_ft[0], skip_special_tokens=True).split("Output:")[-1].strip()
        result_ft = evaluate_summary_detailed(test['abstract'], summary_ft)
        
        print(f"  베이스: 유용성 {result_base['utility']:.1f}%, 스타일 {result_base['style']:.1f}%")
        print(f"  파인튜닝: 유용성 {result_ft['utility']:.1f}%, 스타일 {result_ft['style']:.1f}%")
        
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
            "finetuned_model": {
                "summary": summary_ft,
                "utility": result_ft['utility'],
                "style": result_ft['style'],
                "word_count": result_ft['word_count'],
                "rules": result_ft['rules']
            },
            "improvement": {
                "utility": result_ft['utility'] - result_base['utility'],
                "style": result_ft['style'] - result_base['style']
            }
        })
    
    # 평균 계산
    avg_base_u = sum(t['base_model']['utility'] for t in all_results['tests']) / 3
    avg_ft_u = sum(t['finetuned_model']['utility'] for t in all_results['tests']) / 3
    avg_base_s = sum(t['base_model']['style'] for t in all_results['tests']) / 3
    avg_ft_s = sum(t['finetuned_model']['style'] for t in all_results['tests']) / 3
    
    all_results["summary"] = {
        "average_utility": {"base": avg_base_u, "finetuned": avg_ft_u, "improvement": avg_ft_u - avg_base_u},
        "average_style": {"base": avg_base_s, "finetuned": avg_ft_s, "improvement": avg_ft_s - avg_base_s}
    }
    
    print(f"\n{'='*60}")
    print(f"평균 유용성: {avg_base_u:.1f}% → {avg_ft_u:.1f}% ({avg_ft_u-avg_base_u:+.1f}%p)")
    print(f"평균 스타일: {avg_base_s:.1f}% → {avg_ft_s:.1f}% ({avg_ft_s-avg_base_s:+.1f}%p)")
    print(f"{'='*60}")
    
    # 결과 저장 (JSON, CSV, MD)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_file = RESULTS_DIR / f"ab_test_results_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON 저장: {json_file}")
    
    # CSV
    csv_file = RESULTS_DIR / f"ab_test_results_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Test ID', 'Base Utility', 'Base Style', 'FT Utility', 'FT Style', 'Utility Imp', 'Style Imp'])
        for t in all_results['tests']:
            writer.writerow([
                t['test_id'],
                f"{t['base_model']['utility']:.1f}",
                f"{t['base_model']['style']:.1f}",
                f"{t['finetuned_model']['utility']:.1f}",
                f"{t['finetuned_model']['style']:.1f}",
                f"{t['improvement']['utility']:+.1f}",
                f"{t['improvement']['style']:+.1f}"
            ])
        writer.writerow(['Average', f"{avg_base_u:.1f}", f"{avg_base_s:.1f}", f"{avg_ft_u:.1f}", f"{avg_ft_s:.1f}", f"{avg_ft_u-avg_base_u:+.1f}", f"{avg_ft_s-avg_base_s:+.1f}"])
    print(f"✅ CSV 저장: {csv_file}")
    
    # Markdown
    md_file = RESULTS_DIR / f"ab_test_results_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# STEP 0.1 A/B 테스트 결과 (Phi-2 vs Mistral)\n\n")
        f.write(f"**모델:** microsoft/phi-2 (2.7B)\n")
        f.write(f"**비교 대상:** Mistral-7B (STEP 0 GPU)\n")
        f.write(f"**실행 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 요약\n\n")
        f.write(f"| 지표 | 베이스 | 파인튜닝 | 개선도 |\n")
        f.write(f"|------|--------|---------|--------|\n")
        f.write(f"| 유용성 | {avg_base_u:.1f}% | {avg_ft_u:.1f}% | {avg_ft_u-avg_base_u:+.1f}%p |\n")
        f.write(f"| 스타일 | {avg_base_s:.1f}% | {avg_ft_s:.1f}% | {avg_ft_s-avg_base_s:+.1f}%p |\n\n")
        f.write(f"## 상세 결과\n\n")
        for t in all_results['tests']:
            f.write(f"### Test {t['test_id']}\n\n")
            f.write(f"**베이스:** 유용성 {t['base_model']['utility']:.1f}%, 스타일 {t['base_model']['style']:.1f}%\n\n")
            f.write(f"**파인튜닝:** 유용성 {t['finetuned_model']['utility']:.1f}%, 스타일 {t['finetuned_model']['style']:.1f}%\n\n")
    print(f"✅ MD 저장: {md_file}")
    
    del base_model, finetuned_model
    gc.collect()
    torch.cuda.empty_cache()
    
    INSTALL_FLAG.unlink()
    
    print("\n" + "="*60)
    print("✅ STEP 0.1 완료! (Phi-2)")
    print("="*60)
    print(f"\nPhi-2 (2.7B) 결과:")
    print(f"  유용성: {avg_base_u:.1f}% → {avg_ft_u:.1f}% ({avg_ft_u-avg_base_u:+.1f}%p)")
    print(f"  스타일: {avg_base_s:.1f}% → {avg_ft_s:.1f}% ({avg_ft_s-avg_base_s:+.1f}%p)")
    print(f"\n💡 STEP 0 GPU (Mistral-7B) 결과와 비교하세요!")
    print(f"\n다음 단계:")
    print(f"  1. STEP 0 GPU vs STEP 0.1 결과 비교")
    print(f"  2. 더 나은 모델 선택")
    print(f"  3. STEP 2 진행")