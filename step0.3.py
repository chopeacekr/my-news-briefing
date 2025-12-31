"""
=================================================================
📰 STEP 0.3: V9.1 수정 버전 (Chat Template 최적화)
=================================================================

🆕 V9.1 개선 사항:
✅ System message 간결화 ⭐⭐⭐ NEW!
✅ User 프롬프트 제거 (논문만!) ⭐⭐⭐ NEW!
✅ 중복 지시사항 제거 ⭐⭐⭐ NEW!
✅ apply_chat_template 사용 (Qwen 공식)
✅ 생성 부분만 추출 (프롬프트 제외)
✅ 복사 감지 로직 (경고만)
✅ 학습 데이터 200개 × 3 에포크

🔧 V9 → V9.1 핵심 변경:
✅ System: "2문장 45단어" → 간결한 역할 정의
✅ User: "Summarize... + 논문" → 논문만!
✅ 중복 제거 → 명확한 역할 분리

=================================================================
📊 현재 설정 (V9.1 권장값)
=================================================================

학습 데이터: Train 200개 + Val 10개 = 총 210개
학습 에포크: 3 에포크
Temperature: 0.7
Chat Template: ✅ 사용 (Qwen 공식)
System Message: ✅ 간결화 (20단어)

예상 시간: ~60분
예상 품질: 8-9/10 (V9 0-1/10에서 대폭 개선!)
예상 성능: 90%

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
# 학습 데이터 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRAIN_SAMPLES = 200  # 학습 샘플 수
VAL_SAMPLES = 10     # 검증 샘플 수
NUM_EPOCHS = 3       # 학습 에포크 수

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 챗 템플릿 설정 ⭐ V9.1 핵심 수정!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USE_CHAT_TEMPLATE = True  # apply_chat_template 사용 (강력 권장!)
USE_SYSTEM_MESSAGE = True # System message 사용 (권장)

# ⭐ V9.1: System message 간결화!
# Before: "You are a research paper summarization expert. Summarize papers concisely and accurately in exactly 2 sentences, maximum 45 words. Focus on the main contribution and key results."
# After: 간결하게!
SYSTEM_MESSAGE = "You are a research paper summarization expert. Always respond with exactly 2 sentences, maximum 45 words."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 생성 파라미터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEMPERATURE = 0.7

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 후처리 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POST_PROCESS_MODE = "smart"  # "smart": 안전, "aggressive": 적극적

ENABLE_COPY_DETECTION = True  # 복사 감지
COPY_DETECTION_THRESHOLD = 0.5  # 50% 이상 겹침 = 복사

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NUM_RANDOM_TESTS = 3  # 랜덤 테스트 개수

# ================================================================
# 📊 현재 설정 요약
# ================================================================
print("\n" + "="*60)
print("⚙️  V9.1 현재 설정")
print("="*60)
print(f"실행 모드: {'전체 실행' if MODE == 0 else '랜덤 테스트만'}")
print(f"파인튜닝: {'사용' if ENABLE_FINETUNING else '사용 안 함'}")
print(f"Chat Template: {'사용 ✅ (Qwen 공식)' if USE_CHAT_TEMPLATE else '미사용'}")
print(f"System Message: {'사용 ✅ (간결화)' if USE_SYSTEM_MESSAGE else '미사용'}")
if USE_SYSTEM_MESSAGE:
    print(f'  → "{SYSTEM_MESSAGE}"')
if ENABLE_FINETUNING:
    print(f"학습 데이터: Train {TRAIN_SAMPLES}개 + Val {VAL_SAMPLES}개")
    print(f"학습 에포크: {NUM_EPOCHS}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"예상 시간: ~{TRAIN_SAMPLES * NUM_EPOCHS // 2}분")
print(f"후처리: {POST_PROCESS_MODE}")
print(f"복사 감지: {'사용 ✅' if ENABLE_COPY_DETECTION else '미사용'}")
print(f"랜덤 테스트: {NUM_RANDOM_TESTS}개")
print("="*60)

# ================================================================

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*60)
print("🚀 STEP 0.3 V9.1 - Chat Template 최적화")
print("="*60)


# ================================================================
# 🔧 V9.1 후처리 함수 (V9에서 개선)
# ================================================================

import re

def detect_copy(text, original_article, ngram_size=5):
    """복사 감지 로직 (5-gram 겹침 체크)"""
    
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


def clean_output_v91(raw_text, original_article=""):
    """V9.1 후처리 (V9 개선)"""
    
    # STEP 0: 불필요한 단어들 완전 제거
    text = raw_text
    
    # System/User/Assistant 제거
    text = re.sub(r'\bsystem\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\buser\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bassistant\b', '', text, flags=re.IGNORECASE)
    
    # "You are" 패턴 제거
    text = re.sub(r'\byou\s+are\s+a\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou\s+are\s+an\b', '', text, flags=re.IGNORECASE)
    
    # System message 관련 패턴
    text = re.sub(r'research\s+paper\s+summarization\s+expert', '', text, flags=re.IGNORECASE)
    text = re.sub(r'always\s+respond\s+with', '', text, flags=re.IGNORECASE)
    text = re.sub(r'exactly\s+2\s+sentences', '', text, flags=re.IGNORECASE)
    text = re.sub(r'maximum\s+45\s+words', '', text, flags=re.IGNORECASE)
    
    # 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    
    # STEP 1: 시작 지점 찾기
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
    
    # STEP 2: 특수 구분자 제거
    text = re.sub(r'#{1,}', '', text)
    text = re.sub(r'={3,}', '', text)
    text = re.sub(r'-{3,}', '', text)
    
    # STEP 3: 프롬프트 패턴 제거
    prompt_patterns = [
        r'(?i)paper\s*:',
        r'(?i)brief\s*:',
        r'(?i)summary\s*:',
        r'(?i)summarize',
        r'(?i)this\s+paper',
        r'<\|im_start\|>',
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
    # 복사 여부는 플래그로만 표시
    
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


def clean_output_aggressive_v91(raw_text, original_article=""):
    """V9.1 Aggressive: 2문장 강제"""
    
    # STEP 0: 불필요한 단어 제거
    text = raw_text
    text = re.sub(r'\b(system|user|assistant)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\byou\s+are\s+(a|an)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'research\s+paper|always\s+respond|maximum\s+45', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # STEP 1-5
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
    ]
    for pattern in prompt_patterns:
        text = re.sub(pattern, '', text)
    
    text = re.sub(r'```', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if not text or len(text) < 20:
        return "[요약 생성 실패]"
    
    # 복사 감지: 경고만
    
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
    """선택된 모드로 후처리"""
    if POST_PROCESS_MODE == "aggressive":
        return clean_output_aggressive_v91(raw_text, original_article)
    else:
        return clean_output_v91(raw_text, original_article)


print(f"\n✅ 후처리 함수 V9.1 로드 완료 ({POST_PROCESS_MODE} 모드)")
print(f"   복사 감지: {'사용 ✅' if ENABLE_COPY_DETECTION else '미사용'}")


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
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V9.1-FINAL"
    RESULTS_DIR = Path(OUTPUT_DIR) / "results"
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n⚙️ 설정:")
    print(f"  모델: Qwen2.5-1.5B-Instruct")
    print(f"  Chat Template: {'사용 ✅' if USE_CHAT_TEMPLATE else '미사용'}")
    print(f"  System Message: {'사용 ✅ (간결)' if USE_SYSTEM_MESSAGE else '미사용'}")
    print(f"  파인튜닝: {'사용' if ENABLE_FINETUNING else '사용 안 함'}")
    print(f"  샘플: Train {TRAIN_SAMPLES}, Val {VAL_SAMPLES}")
    print(f"  에포크: {NUM_EPOCHS}")
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
    # STEP 4: V9.1 프롬프트 적용 (개선!) ⭐⭐⭐
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 STEP 4: V9.1 프롬프트 적용 (개선!)")
    print("="*60)
    
    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("✅ 토크나이저 로드")
    
    def formatting_prompts_func_v91(example):
        """V9.1: System 간결화 + User 프롬프트 제거!"""
        
        messages = []
        
        # System message (간결하게!)
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        # ⭐ V9.1 핵심: User는 논문만! 프롬프트 제거!
        messages.append({
            "role": "user",
            "content": example['article']  # 논문만!
        })
        
        # Assistant
        messages.append({
            "role": "assistant",
            "content": example['abstract']
        })
        
        # apply_chat_template
        if USE_CHAT_TEMPLATE:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False  # 학습 시 False
            )
        else:
            # Fallback
            text = f"Summarize this paper in 2 sentences (max 45 words):\n\n{example['article']}\n\nSummary: {example['abstract']}"
        
        return {"text": text}
    
    print("🔄 V9.1 프롬프트 적용 중...")
    print(f"  System: {USE_SYSTEM_MESSAGE}")
    if USE_SYSTEM_MESSAGE:
        print(f'    → "{SYSTEM_MESSAGE}"')
    print(f"  User: 논문만! (프롬프트 제거)")
    
    train_dataset = train_dataset.map(formatting_prompts_func_v91)
    val_dataset = val_dataset.map(formatting_prompts_func_v91)
    
    # 프롬프트 예시
    print("\n📋 프롬프트 예시:")
    print("-"*60)
    sample_text = train_dataset[0]['text']
    # 처음 500자만 (논문은 길어서)
    print(sample_text[:500] + "...")
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
        print(f"  V9.1 개선: System 간결 + User 프롬프트 제거")
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
            "version": "V9.1",
            "chat_template": USE_CHAT_TEMPLATE,
            "system_message": USE_SYSTEM_MESSAGE,
            "system_message_content": SYSTEM_MESSAGE if USE_SYSTEM_MESSAGE else None,
            "user_prompt": "논문만 (프롬프트 제거)",
            "improvements": "System 간결화 + User 프롬프트 제거 + 중복 제거",
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
        print("⏭️  파인튜닝 건너뛰기")
        print("="*60)
    
    # ============================================================
    # A/B 테스트 (V9.1)
    # ============================================================
    
    print("\n" + "="*60)
    print("🔬 A/B 테스트 (V9.1)")
    print("="*60)
    
    # V9.1 프롬프트 생성
    def make_prompt_v91(article):
        """V9.1: System 간결 + User 논문만"""
        
        messages = []
        
        if USE_SYSTEM_MESSAGE:
            messages.append({
                "role": "system",
                "content": SYSTEM_MESSAGE
            })
        
        # ⭐ V9.1: 논문만!
        messages.append({
            "role": "user",
            "content": article  # 논문만!
        })
        
        if USE_CHAT_TEMPLATE:
            prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True  # 추론 시 True
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
        print("  ✅ 파인튜닝 모델 (V9.1)")
    else:
        qwen_ft = None
        print("  ⏭️  파인튜닝 모델 없음")
    
    # 테스트 데이터
    print("\n📥 테스트용 논문 로딩...")
    
    if 'val_dataset' not in locals():
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
    
    print(f"  ✅ {len(tests)}개 논문 로드")
    
    all_results = []
    
    print("\n🧪 테스트 실행...")
    
    for i, test in enumerate(tests):
        print(f"  Test {i+1}/3...", end=" ")
        
        prompt = make_prompt_v91(test['article'])
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(qwen_base.device)
        
        # 베이스
        with torch.no_grad():
            outputs = qwen_base.generate(
                **inputs, max_new_tokens=80, min_length=30, 
                temperature=TEMPERATURE,
                do_sample=True, top_p=0.9, repetition_penalty=1.2,
                no_repeat_ngram_size=3, pad_token_id=tokenizer.pad_token_id
            )
        
        # 생성된 부분만 추출
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
            "target": test['abstract'],
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
    json_file = RESULTS_DIR / f"ab_test_v91_{timestamp}.json"
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": {
                "version": "V9.1",
                "improvements": "System 간결화 + User 프롬프트 제거",
                "chat_template": USE_CHAT_TEMPLATE,
                "system_message": USE_SYSTEM_MESSAGE,
                "system_content": SYSTEM_MESSAGE if USE_SYSTEM_MESSAGE else None,
                "finetuning": ENABLE_FINETUNING,
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
            print(f"V9.1 FT: {avg_ft:.1f}단어 ({len(ft_valid)}/3 성공)")
            print(f"  복사 감지: {ft_copy}건")
        else:
            print(f"V9.1 FT: 0/3 성공")
    
    print("\n샘플:")
    for r in all_results[:2]:
        print(f"\n논문 (길이: {r['article_length']}자):")
        print("-"*60)
        print(r['article'][:300] + "...")
        print("-"*60)
        copy_flag_base = " ⚠️ 복사 감지" if r['base_copy_detected'] else ""
        print(f"베이스: {r['base_summary']}{copy_flag_base}")
        if ENABLE_FINETUNING:
            copy_flag_ft = " ⚠️ 복사 감지" if r['ft_copy_detected'] else ""
            print(f"V9.1 FT: {r['ft_summary']}{copy_flag_ft}")
    
    print("\n" + "="*60)
    print("✅ A/B 완료!")
    print("="*60)
    
    # ============================================================
    # LLM 분석용 프롬프트 생성
    # ============================================================
    
    print("\n" + "="*60)
    print("📝 LLM 분석용 프롬프트 생성")
    print("="*60)
    
    analysis_prompt = f"""다음은 ArXiv 논문 요약 모델(V9.1)의 A/B 테스트 결과입니다.

## 모델 설정

**버전:** V9.1 (Chat Template 최적화)
**개선 사항:**
- System message 간결화: 50단어 → 20단어
- User 프롬프트 제거: "Summarize..." + 논문 → 논문만
- 중복 지시사항 제거

**Chat Template:** 사용 ✅
**System Message:** "{SYSTEM_MESSAGE}"
**학습:** {TRAIN_SAMPLES}개 × {NUM_EPOCHS} 에포크
**Temperature:** {TEMPERATURE}

## 테스트 결과

"""
    
    for i, r in enumerate(all_results, 1):
        analysis_prompt += f"""
### Test {i}

**논문 원문 (전체):**
```
{r['article']}
```

**원본 초록:**
```
{r['target']}
```

**베이스:**
```
{r['base_summary']}
```
- 단어: {r['base_words']}
- 복사: {'⚠️ 예' if r['base_copy_detected'] else '아니오'}

"""
        
        if ENABLE_FINETUNING and r['ft_summary'] != "N/A (파인튜닝 미사용)":
            analysis_prompt += f"""**V9.1 파인튜닝:**
```
{r['ft_summary']}
```
- 단어: {r['ft_words']}
- 복사: {'⚠️ 예' if r['ft_copy_detected'] else '아니오'}

"""
    
    analysis_prompt += """
## 분석 요청

1. **형식**: 2문장, 45단어 이하?
2. **내용**: 핵심 요약?
3. **V9.1 개선 효과**: System 간결화 + User 프롬프트 제거가 효과있었나?
4. **점수**: 각 출력에 10점 만점 점수

---

**상세 분석 부탁드립니다!**
"""
    
    prompt_file = RESULTS_DIR / f"analysis_prompt_v91_{timestamp}.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(analysis_prompt)
    
    print(f"✅ 분석 프롬프트 저장: {prompt_file.name}")
    
    print("\n" + "="*60)
    print("✅ 완료!")
    print("="*60)


# ================================================================
# 랜덤 테스트 (V9.1)
# ================================================================

print("\n" + "="*60)
print("🎲 랜덤 테스트 (V9.1)")
print("="*60)

if MODE == 1:
    import torch, gc, json, random
    from datetime import datetime
    from pathlib import Path
    from datasets import load_dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    from peft import PeftModel
    
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V9.1-FINAL"
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
        print("✅ V9.1 모델 로드")
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

# V9.1 프롬프트
def make_prompt_v91(article):
    """V9.1: System 간결 + User 논문만"""
    
    messages = []
    
    if USE_SYSTEM_MESSAGE:
        messages.append({
            "role": "system",
            "content": SYSTEM_MESSAGE
        })
    
    messages.append({
        "role": "user",
        "content": article  # 논문만!
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

print("\n🔮 추론 시작...")

for i, idx in enumerate(random_indices):
    paper = full_dataset[idx]
    
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📄 테스트 {i+1}/{NUM_RANDOM_TESTS} (인덱스: {idx})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    print(f"\n📖 논문 (처음 500자):")
    print("-"*60)
    print(paper['article'][:500] + "...")
    print("-"*60)
    
    print(f"\n📌 원본 초록:")
    print("-"*60)
    print(paper['abstract'])
    print("-"*60)
    
    print(f"\n🔮 V9.1 추론 중...")
    
    prompt = make_prompt_v91(paper['article'])
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
    
    print(f"\n📰 V9.1 요약:")
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
print("✅ 완료!")
print("="*60)

print("\n✨ V9.1 개선:")
print("  ✅ System message 간결화 (50단어 → 20단어)")
print("  ✅ User 프롬프트 제거 (논문만!)")
print("  ✅ 중복 지시사항 제거")
print(f"\n📁 출력: {OUTPUT_DIR}")

print("\n🚀 V9.1 완성!")
print("  V9 → V9.1: Chat Template 최적화")
print("  예상 품질: 8-9/10 (V9 0-1/10)")
print("="*60)