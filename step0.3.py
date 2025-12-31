"""
=================================================================
📰 STEP 0.3: V9 최종 버전 (apply_chat_template + 최적화)
=================================================================

🆕 V9 개선 사항:
✅ apply_chat_template 사용 (Qwen 공식 형식) ⭐⭐⭐ NEW!
✅ System message 추가 (역할 명확화) ⭐⭐ NEW!
✅ 복사 감지 로직 (5-gram 체크) ⭐⭐⭐
✅ 프롬프트 명시적 개선 ("Summarize") ⭐⭐⭐
✅ 학습 데이터 200개 (5배 증가!) ⭐⭐⭐
✅ 에포크 3개 (3배 증가)
✅ Temperature 0.7 (창의성 증가)
✅ LLM 분석 프롬프트 자동 생성 ⭐
✅ 전체 논문 저장 (정확한 분석) ⭐

🚀 V8 → V9 핵심 변경:
✅ Qwen 공식 챗 형식 사용 (+15% 성능 예상)
✅ Special tokens 자동 처리
✅ 안정성 대폭 향상

=================================================================
📊 현재 설정 (V9 권장값)
=================================================================

학습 데이터: Train 200개 + Val 10개 = 총 210개
학습 에포크: 3 에포크
Temperature: 0.7
Chat Template: ✅ 사용 (Qwen 공식)
System Message: ✅ 사용 (역할 명확화)

예상 시간: ~60분 (V8과 동일)
예상 품질: 7-8/10 (V8 6-7/10에서 개선)
예상 성능: 85% (V8 70%에서 +15%)

=================================================================
⚙️ 설정 방법
=================================================================

아래 "⚙️ 설정 - 여기만 수정하세요!" 섹션에서:

1. TRAIN_SAMPLES = 200  ← 학습 샘플 수
2. NUM_EPOCHS = 3       ← 에포크 수
3. TEMPERATURE = 0.7    ← Temperature
4. USE_SYSTEM_MESSAGE = True  ← System message 사용

💡 빠른 테스트:
  TRAIN_SAMPLES = 40
  NUM_EPOCHS = 1
  → 시간: ~10분 (품질 낮음)

=================================================================
"""

# ================================================================
# ⚙️ 설정 - 여기만 수정하세요!
# ================================================================

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 실행 모드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE = 0  # 0: 전체 실행 (학습+테스트), 1: 랜덤 테스트만
ENABLE_FINETUNING = True  # True: 파인튜닝 실행, False: 베이스 모델만

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 학습 데이터 설정 ⭐ V9 권장값!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRAIN_SAMPLES = 200  # 학습 샘플 수 (V9 권장: 200)
VAL_SAMPLES = 10     # 검증 샘플 수 (보통 10-20)
NUM_EPOCHS = 3       # 학습 에포크 수 (V9 권장: 3)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 챗 템플릿 설정 ⭐ V9 신규!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_CHAT_TEMPLATE = True  # apply_chat_template 사용 (강력 권장!)
USE_SYSTEM_MESSAGE = True # System message 추가 (권장)

SYSTEM_MESSAGE = "You are a research paper summarization expert. Summarize papers concisely and accurately in exactly 2 sentences, maximum 45 words. Focus on the main contribution and key results."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 생성 파라미터 ⭐ V9 최적화!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEMPERATURE = 0.7    # Temperature (V9: 0.7)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 후처리 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST_PROCESS_MODE = "smart"  # "smart": 안전, "aggressive": 적극적

ENABLE_COPY_DETECTION = True  # 복사 감지 (V8+)
COPY_DETECTION_THRESHOLD = 0.5  # 50% 이상 겹침 = 복사

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUM_RANDOM_TESTS = 3  # 랜덤 테스트 개수 (1-10)

# ================================================================
# 📊 현재 설정 요약
# ================================================================
print("\n" + "="*60)
print("⚙️  V9 현재 설정")
print("="*60)
print(f"실행 모드: {'전체 실행' if MODE == 0 else '랜덤 테스트만'}")
print(f"파인튜닝: {'사용' if ENABLE_FINETUNING else '사용 안 함'}")
print(f"Chat Template: {'사용 ✅ (Qwen 공식)' if USE_CHAT_TEMPLATE else '미사용'}")
print(f"System Message: {'사용 ✅' if USE_SYSTEM_MESSAGE else '미사용'}")
if ENABLE_FINETUNING:
    print(f"학습 데이터: Train {TRAIN_SAMPLES}개 + Val {VAL_SAMPLES}개 = 총 {TRAIN_SAMPLES + VAL_SAMPLES}개")
    print(f"학습 에포크: {NUM_EPOCHS}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"예상 시간: ~{TRAIN_SAMPLES * NUM_EPOCHS // 2}분")
print(f"후처리 모드: {POST_PROCESS_MODE}")
print(f"복사 감지: {'사용 ✅' if ENABLE_COPY_DETECTION else '미사용'} (임계값: {COPY_DETECTION_THRESHOLD})")
print(f"랜덤 테스트: {NUM_RANDOM_TESTS}개")
print("="*60)

# ================================================================

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*60)
print("🚀 STEP 0.3 V9 - apply_chat_template + 최적화")
print("="*60)


# ================================================================
# 🔧 V9 후처리 함수 (V8과 동일)
# ================================================================

import re

def detect_copy(text, original_article, ngram_size=5):
    """V8/V9 복사 감지 로직 (5-gram 겹침 체크)"""
    
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


def clean_output_v9(raw_text, original_article=""):
    """V9 후처리 (V8과 동일 + 개선)"""
    
    # STEP 1: "Summary:" 또는 "Brief:" 이후만 추출
    if "Summary:" in raw_text:
        text = raw_text.split("Summary:")[-1].strip()
    elif "Brief:" in raw_text:
        text = raw_text.split("Brief:")[-1].strip()
    elif "<|im_end|>" in raw_text:  # V9: chat template 처리
        text = raw_text.split("<|im_end|>")[-1].strip()
    else:
        text = raw_text.strip()
    
    # STEP 2: 모든 ### 및 특수 구분자 제거
    text = re.sub(r'#{1,}', '', text)
    text = re.sub(r'={3,}', '', text)
    text = re.sub(r'-{3,}', '', text)
    
    # STEP 3: 프롬프트 패턴 제거
    prompt_patterns = [
        r'(?i)paper\s*:',
        r'(?i)brief\s*:',
        r'(?i)summary\s*:',
        r'(?i)summarize',
        r'(?i)max\s+\d+\s+words?',
        r'(?i)\d+-sentence',
        r'(?i)2-sentence',
        r'(?i)45\s+words?',
        r'(?i)write\s+a',
        r'(?i)task\s*:',
        r'<\|im_start\|>',  # V9: special tokens
        r'<\|im_end\|>',
    ]
    
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text)
    
    # STEP 4: LaTeX 제거
    latex_patterns = [r'\$+', r'\\[a-zA-Z]+', r'@xmath\d+', r'@xcite']
    for pattern in latex_patterns:
        text = re.sub(pattern, '', text)
    
    # STEP 5: 특수 문자 정리
    text = re.sub(r'```', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    text = text.strip()
    
    # STEP 6: 빈 텍스트 체크
    if not text or len(text) < 20:
        return "[요약 생성 실패 - 출력 없음]"
    
    # STEP 7: 복사 감지 (경고만, 차단 안 함)
    # Note: 복사 여부는 플래그로만 표시하고 출력은 그대로 반환
    # 이유: 품질 평가를 위해 결과를 봐야 함
    
    # STEP 8: 문장 분리 및 선택
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 5]
    
    if not sentences:
        return "[요약 생성 실패 - 유효 문장 없음]"
    
    cleaned_sentences = []
    for s in sentences:
        if not s[-1] in '.!?':
            s += '.'
        cleaned_sentences.append(s)
    
    # STEP 9: Smart 선택
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


def clean_output_aggressive_v9(raw_text, original_article=""):
    """V9 Aggressive: 2문장 강제"""
    
    # STEP 1-5: Smart와 동일
    if "Summary:" in raw_text:
        text = raw_text.split("Summary:")[-1].strip()
    elif "Brief:" in raw_text:
        text = raw_text.split("Brief:")[-1].strip()
    elif "<|im_end|>" in raw_text:
        text = raw_text.split("<|im_end|>")[-1].strip()
    else:
        text = raw_text.strip()
    
    text = re.sub(r'#{1,}|={3,}|-{3,}|<\|im_start\|>|<\|im_end\|>', '', text)
    
    prompt_patterns = [
        r'(?i)paper\s*:', r'(?i)summary\s*:', r'(?i)summarize',
        r'(?i)max\s+\d+\s+words?', r'(?i)2-sentence',
    ]
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text)
    
    text = re.sub(r'```', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text or len(text) < 20:
        return "[요약 생성 실패]"
    
    # 복사 감지: 경고만, 차단 안 함
    # (플래그는 별도로 반환됨)
    
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
    
    sentence1 = cleaned_sentences[0]
    sentence2 = cleaned_sentences[1]
    
    words1 = sentence1.split()
    words2 = sentence2.split()
    total = len(words1) + len(words2)
    
    if total <= 45:
        return f"{sentence1} {sentence2}"
    
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
        return clean_output_aggressive_v9(raw_text, original_article)
    else:
        return clean_output_v9(raw_text, original_article)


print(f"\n✅ 후처리 함수 V9 로드 완료 ({POST_PROCESS_MODE} 모드)")
print(f"   복사 감지: {'사용 ✅' if ENABLE_COPY_DETECTION else '미사용'} (임계값: {COPY_DETECTION_THRESHOLD})")


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
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V9-FINAL"
    RESULTS_DIR = Path(OUTPUT_DIR) / "results"
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n⚙️ 설정:")
    print(f"  모델: Qwen2.5-1.5B-Instruct")
    print(f"  Chat Template: {'사용 ✅' if USE_CHAT_TEMPLATE else '미사용'}")
    print(f"  System Message: {'사용 ✅' if USE_SYSTEM_MESSAGE else '미사용'}")
    print(f"  파인튜닝: {'사용' if ENABLE_FINETUNING else '사용 안 함'}")
    print(f"  후처리: {POST_PROCESS_MODE} V9 + 복사 감지")
    print(f"  샘플: Train {TRAIN_SAMPLES}, Val {VAL_SAMPLES}")
    print(f"  에포크: {NUM_EPOCHS}")
    print(f"  Temperature: {TEMPERATURE}")
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
    dataset = load_dataset("ccdv/arxiv-summarization", split=f"train[:{TRAIN_SAMPLES + VAL_SAMPLES}]")
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
    # STEP 4: V9 프롬프트 적용 (apply_chat_template!) ⭐⭐⭐
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 STEP 4: V9 프롬프트 적용 (apply_chat_template)")
    print("="*60)
    
    # 토크나이저 먼저 로드 (chat template 사용 위해)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("✅ 토크나이저 로드")
    
    def formatting_prompts_func_v9(example):
        """V9: apply_chat_template 사용!"""
        
        messages = []
        
        # System message 추가 (선택적)
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        # User message
        messages.append({
            "role": "user",
            "content": f"Summarize this paper in 2 sentences (max 45 words):\n\n{example['article']}"
        })
        
        # Assistant message
        messages.append({
            "role": "assistant",
            "content": example['abstract']
        })
        
        # ⭐ 핵심: apply_chat_template 사용!
        if USE_CHAT_TEMPLATE:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False  # 학습 시 False
            )
        else:
            # Fallback: V8 방식
            text = f"Summarize this paper in 2 sentences (max 45 words):\n\n{example['article']}\n\nSummary: {example['abstract']}"
        
        return {"text": text}
    
    print("🔄 V9 프롬프트 적용 중...")
    if USE_CHAT_TEMPLATE:
        print("  형식: Qwen 공식 챗 템플릿 ✅")
        print(f"  System: {SYSTEM_MESSAGE[:50]}..." if USE_SYSTEM_MESSAGE else "  System: 미사용")
    else:
        print("  형식: V8 호환 (직접 포매팅)")
    
    train_dataset = train_dataset.map(formatting_prompts_func_v9)
    val_dataset = val_dataset.map(formatting_prompts_func_v9)
    
    # 프롬프트 예시 출력
    print("\n📋 프롬프트 예시:")
    print("-"*60)
    print(train_dataset[0]['text'][:500] + "...")
    print("-"*60)
    
    print("✅ 프롬프트 적용 완료")
    
    # ============================================================
    # STEP 5-8: 학습 (ENABLE_FINETUNING=True일 때만)
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
        
        # ========================================================
        # STEP 6: 모델 로딩
        # ========================================================
        
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
        
        # ========================================================
        # STEP 7: 학습
        # ========================================================
        
        print("\n" + "="*60)
        print("🎯 STEP 7: 모델 학습")
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
            warmup_steps=5,
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
        print(f"  Epochs: {NUM_EPOCHS}")
        print(f"  Batch size: 1 × 4 = 4")
        print(f"  Learning rate: 2e-4")
        print(f"  Chat Template: {'사용 ✅' if USE_CHAT_TEMPLATE else '미사용'}")
        print(f"  총 학습 스텝: ~{len(train_dataset_tokenized) // 4 * NUM_EPOCHS}")
        print(f"  예상 시간: ~{TRAIN_SAMPLES * NUM_EPOCHS // 2}분")
        print()
        
        trainer.train()
        
        print("\n✅ 학습 완료!")
        
        # ========================================================
        # STEP 8: 저장
        # ========================================================
        
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
            "version": "V9",
            "chat_template": USE_CHAT_TEMPLATE,
            "system_message": USE_SYSTEM_MESSAGE,
            "system_message_content": SYSTEM_MESSAGE if USE_SYSTEM_MESSAGE else None,
            "prompt": "Summarize this paper in 2 sentences (max 45 words)",
            "post_process": f"{POST_PROCESS_MODE} V9 + 복사 감지",
            "copy_detection": ENABLE_COPY_DETECTION,
            "copy_threshold": COPY_DETECTION_THRESHOLD,
            "train_samples": TRAIN_SAMPLES,
            "val_samples": VAL_SAMPLES,
            "num_epochs": NUM_EPOCHS,
            "temperature": TEMPERATURE,
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
    
    else:
        print("\n" + "="*60)
        print("⏭️  파인튜닝 건너뛰기 (베이스 모델만 사용)")
        print("="*60)
    
    # ============================================================
    # A/B 테스트 (V9) ⭐
    # ============================================================
    
    print("\n" + "="*60)
    print("🔬 A/B 테스트 (V9)")
    print("="*60)
    
    # V9 프롬프트 생성 함수
    def make_prompt_v9(article):
        """V9: apply_chat_template 사용 (추론용)"""
        
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        messages.append({
            "role": "user",
            "content": f"Summarize this paper in 2 sentences (max 45 words):\n\n{article}"
        })
        
        if USE_CHAT_TEMPLATE:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True  # 추론 시 True!
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
    
    if ENABLE_FINETUNING:
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
        print("  ✅ 파인튜닝 모델")
    else:
        qwen_ft = None
        print("  ⏭️  파인튜닝 모델 없음")
    
    # 테스트: 실제 ArXiv 논문 전체 사용
    print("\n📥 테스트용 논문 로딩...")
    
    if 'val_dataset' not in locals():
        print("  Val 데이터셋 다시 로딩...")
        from datasets import load_dataset
        
        dataset_temp = load_dataset("ccdv/arxiv-summarization", split=f"train[:{TRAIN_SAMPLES + VAL_SAMPLES}]")
        dataset_temp = dataset_temp.map(lambda x: {
            'article': clean_arxiv_text(x['article']),
            'abstract': clean_arxiv_text(x['abstract'])
        })
        dataset_temp = dataset_temp.train_test_split(test_size=VAL_SAMPLES, seed=42)
        val_dataset_raw = dataset_temp['test']
    else:
        val_dataset_raw = val_dataset
    
    tests = []
    for i in range(min(3, len(val_dataset_raw))):
        paper = val_dataset_raw[i]
        tests.append({
            "id": i + 1,
            "article": paper['article'],
            "abstract": paper['abstract']
        })
    
    print(f"  ✅ {len(tests)}개 논문 로드 완료")
    
    all_results = []
    
    print("\n🧪 테스트 실행...")
    
    for i, test in enumerate(tests):
        print(f"  Test {i+1}/3...", end=" ")
        
        prompt = make_prompt_v9(test['article'])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_base.device)
        
        # 베이스
        with torch.no_grad():
            outputs = qwen_base.generate(
                **inputs, max_new_tokens=80, min_length=30, 
                temperature=TEMPERATURE,
                do_sample=True, top_p=0.9, repetition_penalty=1.2,
                no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
            )
        base_summary = clean_output(tokenizer.decode(outputs[0], skip_special_tokens=True), test['article'])
        
        # 복사 감지 체크 (출력과 별도)
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
            ft_summary = clean_output(tokenizer.decode(outputs[0], skip_special_tokens=True), test['article'])
            
            # 복사 감지 체크 (출력과 별도)
            ft_is_copy = detect_copy(ft_summary, test['article']) if ft_summary and '[' not in ft_summary else False
        else:
            ft_summary = "N/A (파인튜닝 미사용)"
            ft_is_copy = False
        
        all_results.append({
            "test_id": test['id'],
            "article": test['article'],
            "article_length": len(test['article']),
            "target": test['abstract'],
            "base_summary": base_summary,
            "base_words": len(base_summary.split()) if '[' not in base_summary else 0,
            "base_copy_detected": base_is_copy,  # 복사 감지 플래그
            "ft_summary": ft_summary,
            "ft_words": len(ft_summary.split()) if '[' not in ft_summary and ft_summary != "N/A (파인튜닝 미사용)" else 0,
            "ft_copy_detected": ft_is_copy  # 복사 감지 플래그
        })
        
        print("✅")
    
    # 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = RESULTS_DIR / f"ab_test_v9_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "version": "V9",
                "chat_template": USE_CHAT_TEMPLATE,
                "system_message": USE_SYSTEM_MESSAGE,
                "finetuning": ENABLE_FINETUNING,
                "copy_detection": ENABLE_COPY_DETECTION,
                "copy_threshold": COPY_DETECTION_THRESHOLD,
                "train_samples": TRAIN_SAMPLES,
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
            print(f"파인튜닝: {avg_ft:.1f}단어 ({len(ft_valid)}/3 성공)")
            print(f"  복사 감지: {ft_copy}건")
        else:
            print(f"파인튜닝: 0/3 성공")
    
    print("\n샘플:")
    for r in all_results[:2]:
        print(f"\n논문 (길이: {r['article_length']}자):")
        print("-"*60)
        print(r['article'][:300] + "...")
        print("-"*60)
        copy_flag_base = " ⚠️ 복사 감지됨" if r['base_copy_detected'] else ""
        print(f"베이스: {r['base_summary']}{copy_flag_base}")
        if ENABLE_FINETUNING:
            copy_flag_ft = " ⚠️ 복사 감지됨" if r['ft_copy_detected'] else ""
            print(f"파인튜닝: {r['ft_summary']}{copy_flag_ft}")
    
    print("\n" + "="*60)
    print("✅ A/B 완료!")
    print("="*60)
    
    # ============================================================
    # LLM 분석용 프롬프트 생성 ⭐
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 LLM 분석용 프롬프트 생성")
    print("="*60)
    
    analysis_prompt = f"""다음은 ArXiv 논문 요약 모델(V9)의 A/B 테스트 결과입니다. 결과를 분석해주세요.

## 모델 설정

**버전:** V9 (apply_chat_template + 최적화)
**Chat Template:** {'사용 ✅ (Qwen 공식 형식)' if USE_CHAT_TEMPLATE else '미사용'}
**System Message:** {'사용 ✅' if USE_SYSTEM_MESSAGE else '미사용'}
{f'- Content: "{SYSTEM_MESSAGE}"' if USE_SYSTEM_MESSAGE else ''}
**학습 데이터:** {TRAIN_SAMPLES}개 (Train) + {VAL_SAMPLES}개 (Val)
**에포크:** {NUM_EPOCHS}
**Temperature:** {TEMPERATURE}
**복사 감지:** {'사용' if ENABLE_COPY_DETECTION else '미사용'} (임계값: {COPY_DETECTION_THRESHOLD})
**프롬프트:** "Summarize this paper in 2 sentences (max 45 words)"

## 요구사항

- **형식:** 2문장, 45단어 이하
- **내용:** 논문의 핵심 내용 요약
- **금지:** 논문 원문 복사

## 테스트 결과

"""
    
    for i, r in enumerate(all_results, 1):
        analysis_prompt += f"""
### Test {i}

**논문 원문 (전체):**
```
{r['article']}
```

**원본 초록 (정답):**
```
{r['target']}
```

**베이스 모델 출력:**
```
{r['base_summary']}
```
- 단어 수: {r['base_words']}
- 복사 감지: {'⚠️ 예 (경고)' if r['base_copy_detected'] else '아니오'}
{f"  → 주의: 5-gram 분석 결과 논문과 {COPY_DETECTION_THRESHOLD*100:.0f}% 이상 겹침 감지됨" if r['base_copy_detected'] else ""}

"""
        
        if ENABLE_FINETUNING and r['ft_summary'] != "N/A (파인튜닝 미사용)":
            analysis_prompt += f"""**파인튜닝 모델 출력:**
```
{r['ft_summary']}
```
- 단어 수: {r['ft_words']}
- 복사 감지: {'⚠️ 예 (경고)' if r['ft_copy_detected'] else '아니오'}
{f"  → 주의: 5-gram 분석 결과 논문과 {COPY_DETECTION_THRESHOLD*100:.0f}% 이상 겹침 감지됨" if r['ft_copy_detected'] else ""}

"""
    
    analysis_prompt += """
## 분석 요청

다음 항목들을 분석해주세요:

### 1. 형식 준수
- 각 출력이 2문장인가?
- 각 출력이 45단어 이하인가?
- 문장이 완결되었는가?

### 2. 내용 품질
- 논문의 핵심 내용을 담고 있는가?
- 원본 초록과 비교했을 때 정확한가?
- 요약이 명확하고 이해하기 쉬운가?

### 3. 복사 여부
- 논문 원문을 그대로 복사했는가?
- 자신의 언어로 재작성했는가?
- 복사 감지 기능이 제대로 작동했는가?

### 4. 모델 비교 (파인튜닝이 있는 경우)
- 베이스 모델 vs 파인튜닝 모델 중 어느 것이 더 나은가?
- 각각의 강점과 약점은?
- 파인튜닝의 효과가 있는가?

### 5. V9 개선 효과
- V8 대비 apply_chat_template의 효과는?
- System message의 효과는?
- 전반적 품질 개선이 있는가?

### 6. 개선 방향
- 어떤 문제점이 있는가?
- 어떻게 개선할 수 있는가?
- V10에서 무엇을 바꿔야 하는가?

### 7. 점수 (10점 만점)
각 테스트의 베이스/파인튜닝 모델에 점수를 매기고, 평균을 계산해주세요.

---

**상세하고 구체적으로 분석해주세요!**
"""
    
    prompt_file = RESULTS_DIR / f"analysis_prompt_v9_{timestamp}.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(analysis_prompt)
    
    print(f"✅ 분석용 프롬프트 저장: {prompt_file.name}")
    
    print("\n💡 사용 방법:")
    print(f"  1. {prompt_file.name} 파일을 다운로드")
    print("  2. Claude.ai 또는 ChatGPT에 프롬프트 입력")
    print("  3. 상세한 분석 결과 받기")
    
    print("\n" + "="*60)
    print("✅ LLM 분석용 프롬프트 생성 완료!")
    print("="*60)


# ================================================================
# 랜덤 테스트 (V9) ⭐
# ================================================================

print("\n" + "="*60)
print("🎲 랜덤 테스트 (V9)")
print("="*60)

if MODE == 1:
    import torch, gc, json, random
    from datetime import datetime
    from pathlib import Path
    from datasets import load_dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V9-FINAL"
    final_model_path = Path(OUTPUT_DIR) / "final_model"
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
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
        print("✅ 파인튜닝 모델 로드")
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

# V9 프롬프트
def make_prompt_v9(article):
    """V9: apply_chat_template 사용"""
    
    messages = []
    
    if USE_SYSTEM_MESSAGE:
        messages.append({
            "role": "system",
            "content": SYSTEM_MESSAGE
        })
    
    messages.append({
        "role": "user",
        "content": f"Summarize this paper in 2 sentences (max 45 words):\n\n{article}"
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
    
    print(f"\n🔮 추론 중 (V9: Chat Template {'ON' if USE_CHAT_TEMPLATE else 'OFF'}, System {'ON' if USE_SYSTEM_MESSAGE else 'OFF'})...")
    
    prompt = make_prompt_v9(paper['article'])
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_ft.device)
    
    with torch.no_grad():
        outputs = qwen_ft.generate(
            **inputs, max_new_tokens=80, min_length=30, 
            temperature=TEMPERATURE,
            do_sample=True, top_p=0.9, repetition_penalty=1.2,
            no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
        )
    
    clean = clean_output(tokenizer.decode(outputs[0], skip_special_tokens=True), paper['article'])
    
    # 복사 감지 체크 (별도)
    is_copy = detect_copy(clean, paper['article']) if clean and '[' not in clean else False
    
    print(f"\n📰 Research News Brief:")
    print("="*60)
    print(clean)
    if is_copy:
        print("\n⚠️ 복사 경고: 5-gram 분석 결과 논문과 {:.0f}% 이상 겹침 감지됨".format(COPY_DETECTION_THRESHOLD*100))
    print("="*60)
    
    is_failed = '[' in clean
    word_count = 0 if is_failed else len(clean.split())
    sentence_count = 0 if is_failed else len([s for s in re.split(r'[.!?]+', clean) if s.strip()])
    
    print(f"\n📊 통계:")
    print(f"  생성 성공: {'❌ 실패' if is_failed else '✅ 성공'}")
    if is_copy:
        print(f"  복사 경고: ⚠️ 5-gram 분석 결과 논문과 겹침 감지됨")
    if not is_failed:
        print(f"  단어 수: {word_count}")
        print(f"  문장 수: {sentence_count}")
        print(f"  45단어: {'✅' if word_count <= 45 else '❌'}")
        print(f"  2문장: {'✅' if sentence_count == 2 else '⚠️ ' + str(sentence_count)}")

print("\n" + "="*60)
print("✅ 완료!")
print("="*60)

if MODE == 0:
    print("\n✨ V9 개선:")
    print("  ✅ apply_chat_template (Qwen 공식) ⭐⭐⭐")
    print("  ✅ System message (역할 명확화) ⭐⭐")
    print("  ✅ 복사 감지 로직 (5-gram)")
    print("  ✅ 프롬프트 명시 (Summarize)")
    print(f"  ✅ 데이터 {TRAIN_SAMPLES}개")
    print(f"  ✅ 에포크 {NUM_EPOCHS}")
    print(f"  ✅ Temperature {TEMPERATURE}")
    print(f"  ✅ LLM 분석 프롬프트 자동 생성")
    print(f"\n📁 출력: {OUTPUT_DIR}")
    print(f"📝 분석 프롬프트: {OUTPUT_DIR}/results/analysis_prompt_v9_*.txt")

print("\n🚀 V9 완성!")
print("  V8 → V9: apply_chat_template 추가 (+15% 성능 예상)")
print("  예상 품질: 7-8/10 (V8 6-7/10)")
print("="*60)