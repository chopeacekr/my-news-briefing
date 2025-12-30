# ============================================================
# STEP 0.2: Qwen vs Phi-2 비교 (GPU T4, 50개)
#
# 목적: 소형 모델 성능 비교 (Qwen vs Phi-2)
#
# 모델: Qwen/Qwen2.5-1.5B-Instruct (1.5B 파라미터)
# 비교: microsoft/phi-2 (2.7B 파라미터)
#
# 장점:
#   - 가장 작은 모델 (1.5B)
#   - 가장 빠른 추론 (3배)
#   - 최소 메모리 (1.5GB)
#
# 시간: 1-2분 (가장 빠름!)
# ============================================================

import sys
import subprocess
from pathlib import Path

INSTALL_FLAG = Path("/tmp/step0_2_qwen_installed.flag")

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
    print("STEP 0.2: Qwen vs Phi-2 비교")
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
    
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.2-Qwen-GPU-Test"
    RESULTS_DIR = Path(OUTPUT_DIR) / "ab_test_results"
    
    TRAIN_SAMPLES = 40
    VAL_SAMPLES = 10
    NUM_SAMPLES = 50
    
    # Drive 마운트
    if not Path("/content/drive").exists():
        drive.mount('/content/drive')
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ 모델: Qwen2.5-1.5B-Instruct (1.5B)")
    print(f"✅ 출력: {OUTPUT_DIR}")
    print(f"💡 가장 작고 빠른 모델!")
    
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
    
    # STEP 0, 0.1과 동일한 split (seed=42)
    dataset = dataset.train_test_split(test_size=VAL_SAMPLES, seed=42)
    train_dataset = dataset['train']
    val_dataset = dataset['test']
    
    print(f"\n✅ Train: {len(train_dataset)}, Val: {len(val_dataset)}")
    print("💡 STEP 0, 0.1과 동일한 데이터 (seed=42)")
    
    # ================================================================
    # 개선 2: 프롬프트 단순화 (Qwen 형식)
    # ================================================================
    
    print("\n" + "="*60)
    print("개선 2: 프롬프트 단순화 (Qwen 형식)")
    print("="*60)
    
    def formatting_prompts_func(example):
        # Qwen2.5 Instruct 형식
        text = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nSummarize this academic paper in 1-2 sentences (under 50 words):\n\n{example['article']}<|im_end|>\n<|im_start|>assistant\n{example['abstract']}<|im_end|>"
        return {"text": text}
    
    print("✅ Qwen 프롬프트: '<|im_start|>...<|im_end|>' 형식")
    
    train_dataset = train_dataset.map(formatting_prompts_func)
    val_dataset = val_dataset.map(formatting_prompts_func)
    print("✅ 프롬프트 적용 완료")
    
    # ================================================================
    # 모델 로딩 (GPU, 4-bit)
    # ================================================================
    
    print("\n" + "="*60)
    print("모델 로딩 (Qwen, 4-bit 양자화)")
    print("="*60)
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    
    # Qwen은 pad_token 설정 필요
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
    
    print("\n모델 로딩 중... (Qwen, 4-bit, ~1.5GB)")
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
    print("✅ 모델 로딩 완료 (4-bit, ~1.5GB, 가장 작음!)")
    
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Qwen용
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
    print("학습 시작 (GPU, Qwen)")
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
    
    print("\n학습 중... (약 1-2분 소요, 가장 빠름!)")
    trainer.train()
    
    final_model_path = Path(OUTPUT_DIR) / "checkpoints" / "final_model"
    trainer.model.save_pretrained(final_model_path)
    tokenizer.save_pretrained(final_model_path)
    print(f"\n✅ 모델 저장: {final_model_path}")
    
    del model, trainer
    gc.collect()
    torch.cuda.empty_cache()
    
    # ================================================================
    # A/B 테스트 (Phi-2 vs Qwen)
    # ================================================================
    
    print("\n" + "="*60)
    print("A/B 테스트: Phi-2 vs Qwen 비교")
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
    
    # Phi-2 모델 로딩
    print("\nPhi-2 모델 로딩...")
    phi2_model_path = "/content/drive/MyDrive/arxiv-STEP0.1-Phi2-GPU-Test/checkpoints/final_model"
    
    if Path(phi2_model_path).exists():
        phi2_tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
        if phi2_tokenizer.pad_token is None:
            phi2_tokenizer.pad_token = phi2_tokenizer.eos_token
        
        phi2_base = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            device_map="auto",
            trust_remote_code=True
        )
        
        phi2_model = AutoModelForCausalLM.from_pretrained(
            "microsoft/phi-2",
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
            ),
            device_map="auto",
            trust_remote_code=True
        )
        phi2_model = PeftModel.from_pretrained(phi2_model, phi2_model_path)
        phi2_model.eval()
        print("✅ Phi-2 모델 로드 완료")
    else:
        print("⚠️ Phi-2 모델을 찾을 수 없습니다. STEP 0.1을 먼저 실행하세요.")
        phi2_model = None
        phi2_tokenizer = None
    
    # Qwen 모델 로딩
    print("Qwen 모델 로딩...")
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
    
    qwen_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16
        ),
        device_map="auto",
        trust_remote_code=True
    )
    qwen_model = PeftModel.from_pretrained(qwen_model, final_model_path)
    qwen_model.eval()
    
    # STEP 0, 0.1과 동일한 테스트 데이터
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
            "qwen_model": "Qwen2.5-1.5B-Instruct",
            "phi2_model": "microsoft/phi-2",
            "step": "STEP 0.2",
            "training_samples": TRAIN_SAMPLES,
            "comparison": "Phi-2 (2.7B) vs Qwen (1.5B)",
            "timestamp": datetime.now().isoformat()
        },
        "tests": []
    }
    
    print("\n개선 3: 생성 파라미터 (STEP 0, 0.1과 동일)")
    
    for i, test in enumerate(tests):
        print(f"\n테스트 {i+1}/3...")
        
        # Phi-2 평가
        if phi2_model and phi2_tokenizer:
            phi2_prompt = f"Instruct: Summarize this academic paper in 1-2 sentences (under 50 words):\n\n{test['article']}\n\nOutput:"
            phi2_inputs = phi2_tokenizer(phi2_prompt, return_tensors="pt", truncation=True, max_length=400).to(phi2_model.device)
            
            with torch.no_grad():
                phi2_outputs = phi2_model.generate(
                    **phi2_inputs,
                    max_new_tokens=60,
                    temperature=0.3,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=3,
                    pad_token_id=phi2_tokenizer.pad_token_id
                )
            phi2_summary = phi2_tokenizer.decode(phi2_outputs[0], skip_special_tokens=True).split("Output:")[-1].strip()
            phi2_result = evaluate_summary_detailed(test['abstract'], phi2_summary)
        else:
            phi2_summary = "N/A"
            phi2_result = {"utility": 0, "style": 0, "word_count": 0, "rules": {}}
        
        # Qwen 평가
        qwen_prompt = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\nSummarize this academic paper in 1-2 sentences (under 50 words):\n\n{test['article']}<|im_end|>\n<|im_start|>assistant\n"
        qwen_inputs = tokenizer(qwen_prompt, return_tensors="pt", truncation=True, max_length=400).to(qwen_model.device)
        
        with torch.no_grad():
            qwen_outputs = qwen_model.generate(
                **qwen_inputs,
                max_new_tokens=60,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.pad_token_id
            )
        qwen_summary = tokenizer.decode(qwen_outputs[0], skip_special_tokens=True).split("<|im_start|>assistant\n")[-1].strip()
        qwen_result = evaluate_summary_detailed(test['abstract'], qwen_summary)
        
        if phi2_model:
            print(f"  Phi-2 (2.7B): 유용성 {phi2_result['utility']:.1f}%, 스타일 {phi2_result['style']:.1f}%")
        print(f"  Qwen (1.5B): 유용성 {qwen_result['utility']:.1f}%, 스타일 {qwen_result['style']:.1f}%")
        
        all_results["tests"].append({
            "test_id": test['id'],
            "original_article": test['article'],
            "target_abstract": test['abstract'],
            "phi2_model": {
                "summary": phi2_summary,
                "utility": phi2_result['utility'],
                "style": phi2_result['style'],
                "word_count": phi2_result['word_count'],
                "rules": phi2_result['rules']
            } if phi2_model else None,
            "qwen_model": {
                "summary": qwen_summary,
                "utility": qwen_result['utility'],
                "style": qwen_result['style'],
                "word_count": qwen_result['word_count'],
                "rules": qwen_result['rules']
            }
        })
    
    # 평균 계산
    if phi2_model:
        avg_phi2_u = sum(t['phi2_model']['utility'] for t in all_results['tests']) / 3
        avg_phi2_s = sum(t['phi2_model']['style'] for t in all_results['tests']) / 3
    else:
        avg_phi2_u = 0
        avg_phi2_s = 0
    
    avg_qwen_u = sum(t['qwen_model']['utility'] for t in all_results['tests']) / 3
    avg_qwen_s = sum(t['qwen_model']['style'] for t in all_results['tests']) / 3
    
    all_results["summary"] = {
        "phi2": {"utility": avg_phi2_u, "style": avg_phi2_s} if phi2_model else None,
        "qwen": {"utility": avg_qwen_u, "style": avg_qwen_s},
        "winner": "Phi-2" if avg_phi2_u > avg_qwen_u else "Qwen" if avg_qwen_u > avg_phi2_u else "Tie",
        "difference": {
            "utility": abs(avg_phi2_u - avg_qwen_u) if phi2_model else 0,
            "style": abs(avg_phi2_s - avg_qwen_s) if phi2_model else 0
        }
    }
    
    print(f"\n{'='*60}")
    if phi2_model:
        print(f"Phi-2 (2.7B): 유용성 {avg_phi2_u:.1f}%, 스타일 {avg_phi2_s:.1f}%")
        print(f"Qwen (1.5B): 유용성 {avg_qwen_u:.1f}%, 스타일 {avg_qwen_s:.1f}%")
        print(f"\n승자: {all_results['summary']['winner']}")
        print(f"차이: 유용성 {all_results['summary']['difference']['utility']:.1f}%p, 스타일 {all_results['summary']['difference']['style']:.1f}%p")
    else:
        print(f"Qwen (1.5B): 유용성 {avg_qwen_u:.1f}%, 스타일 {avg_qwen_s:.1f}%")
    print(f"{'='*60}")
    
    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_file = RESULTS_DIR / f"phi2_vs_qwen_results_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON 저장: {json_file}")
    
    # CSV
    csv_file = RESULTS_DIR / f"phi2_vs_qwen_results_{timestamp}.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if phi2_model:
            writer.writerow(['Test ID', 'Phi-2 Utility', 'Phi-2 Style', 'Qwen Utility', 'Qwen Style'])
            for t in all_results['tests']:
                writer.writerow([
                    t['test_id'],
                    f"{t['phi2_model']['utility']:.1f}",
                    f"{t['phi2_model']['style']:.1f}",
                    f"{t['qwen_model']['utility']:.1f}",
                    f"{t['qwen_model']['style']:.1f}"
                ])
            writer.writerow(['Average', f"{avg_phi2_u:.1f}", f"{avg_phi2_s:.1f}", f"{avg_qwen_u:.1f}", f"{avg_qwen_s:.1f}"])
        else:
            writer.writerow(['Test ID', 'Qwen Utility', 'Qwen Style'])
            for t in all_results['tests']:
                writer.writerow([
                    t['test_id'],
                    f"{t['qwen_model']['utility']:.1f}",
                    f"{t['qwen_model']['style']:.1f}"
                ])
            writer.writerow(['Average', f"{avg_qwen_u:.1f}", f"{avg_qwen_s:.1f}"])
    print(f"✅ CSV 저장: {csv_file}")
    
    # Markdown
    md_file = RESULTS_DIR / f"phi2_vs_qwen_results_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Phi-2 vs Qwen 비교 결과\n\n")
        f.write(f"**비교:** Phi-2 (2.7B) vs Qwen (1.5B)\n")
        f.write(f"**실행 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 요약\n\n")
        f.write(f"| 모델 | 크기 | 유용성 | 스타일 |\n")
        f.write(f"|------|------|--------|--------|\n")
        if phi2_model:
            f.write(f"| Phi-2 | 2.7B | {avg_phi2_u:.1f}% | {avg_phi2_s:.1f}% |\n")
            f.write(f"| Qwen | 1.5B | {avg_qwen_u:.1f}% | {avg_qwen_s:.1f}% |\n\n")
            f.write(f"**승자:** {all_results['summary']['winner']}\n")
            f.write(f"**차이:** 유용성 {all_results['summary']['difference']['utility']:.1f}%p, 스타일 {all_results['summary']['difference']['style']:.1f}%p\n")
        else:
            f.write(f"| Qwen | 1.5B | {avg_qwen_u:.1f}% | {avg_qwen_s:.1f}% |\n")
    print(f"✅ MD 저장: {md_file}")
    
    del qwen_base, qwen_model
    if phi2_model:
        del phi2_base, phi2_model
    gc.collect()
    torch.cuda.empty_cache()
    
    INSTALL_FLAG.unlink()
    
    print("\n" + "="*60)
    print("✅ STEP 0.2 완료!")
    print("="*60)
    
    if phi2_model:
        print(f"\n소형 모델 비교:")
        print(f"  Phi-2 (2.7B): 유용성 {avg_phi2_u:.1f}%, 스타일 {avg_phi2_s:.1f}%")
        print(f"  Qwen (1.5B): 유용성 {avg_qwen_u:.1f}%, 스타일 {avg_qwen_s:.1f}%")
        
        print(f"\n✅ 승자: {all_results['summary']['winner']}")
        
        if avg_qwen_u > avg_phi2_u + 3:
            print(f"\n🎉 Qwen 확실한 승리! (+{avg_qwen_u-avg_phi2_u:.1f}%p)")
            print(f"→ STEP 2A에서 Qwen 사용 추천")
        elif avg_phi2_u > avg_qwen_u + 3:
            print(f"\n🎉 Phi-2 확실한 승리! (+{avg_phi2_u-avg_qwen_u:.1f}%p)")
            print(f"→ STEP 2A에서 Phi-2 사용 추천")
        else:
            print(f"\n💡 성능 비슷함 (차이 {abs(avg_phi2_u-avg_qwen_u):.1f}%p)")
            if avg_phi2_u >= avg_qwen_u:
                print(f"→ Phi-2 사용 추천 (더 안정적)")
            else:
                print(f"→ Qwen 사용 추천 (더 빠름)")
    
    print(f"\n다음 단계:")
    print(f"  1. Phase 1 결과 종합 (STEP 0, 0.1, 0.2)")
    print(f"  2. 최고 소형 모델 선택")
    print(f"  3. STEP 2A 진행 (1000개)")