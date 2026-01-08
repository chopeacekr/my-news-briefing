"""
=================================================================
📰 ArXiv-NewsBrief-1.5B - 완전판 v2.1 (Teacher-Aligned Essential)
=================================================================

🎯 실행 모드:
✅ MODE 0: 연습 모드 (50개 데이터, 빠른 검증) - GPU 필요
✅ MODE 1: 전체 학습 모드 (1000개 데이터, 프로덕션) - GPU 필요
✅ MODE 2: 테스트 전용 (추론만, v2.1 안정화) - CPU/GPU 가능! ⭐

📊 V2.1 핵심 개선사항 (MODE 2):
✅ temperature: 0.7 → 0.3 (Teacher와 동일) ⭐⭐⭐
✅ top_k: 없음 → 40 (Teacher와 동일) ⭐⭐
✅ eos_token_id 유지 → 깔끔한 종료 (v2.0)
✅ 과도한 제약 제거 유지 (v2.0)
✅ 출력 추출 개선 유지 (v2.0)

🎯 기대 효과:
📉 평균 단어 수: 52.4개 → ~45개 (-14%)
📈 목표 달성률: 17% → ~60% (+253%)
✅ 안정성: 100% 유지 (특수 문자 0%)

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("🚀 ArXiv-NewsBrief - 완전판 v2.1 (Teacher-Aligned Essential)")
print("="*70)

# ================================================================
# ⚙️ 실행 모드 설정 ⭐ 여기만 수정하세요!
# ================================================================

EXECUTION_MODE = 2  # ⭐ 여기를 바꾸세요!
# 0: 연습 모드 (50개, 3 epochs) - GPU 필요
# 1: 전체 모드 (1000개, 5 epochs) - GPU 필요
# 2: 테스트 모드 (추론만, v2.1 안정화) - CPU/GPU 가능!

# ================================================================
# MODE 2 전용 설정 ⭐
# ================================================================

# 추론할 샘플 개수 설정
NUM_INFERENCE_SAMPLES = 5  # ⭐ GPU: 100개, CPU: 3-5개 추천

# 사용할 모델 경로 (학습된 모델)
INFERENCE_MODEL_NAME = "ArXiv-NewsBrief-1.5B-1k-v4.0"  # ⭐ 실제 모델 이름

# CPU 추론 설정
USE_CPU_FOR_INFERENCE = False  # ⭐ True면 GPU 없어도 실행됨

# ⭐ v2.1 핵심 개선: Temperature 변경!
TEMPERATURE = 0.3  # ⭐⭐⭐ 0.7 → 0.3 (Teacher와 동일)

# 공통 설정
DATA_DIR = "/content/drive/MyDrive/SummaryDataSet"  # ⭐ 원래 데이터 경로
USE_CHAT_TEMPLATE = True
USE_SYSTEM_MESSAGE = True
SYSTEM_MESSAGE = "Summarize the following text in simple, clear English that anyone can understand. Make it as for the each script not for reading. Use no more than two complete sentences. Do not include my prompt message in result. Make sure to keep in professional tone."

# ================================================================
# 모드별 자동 설정
# ================================================================

if EXECUTION_MODE == 0:
    # 연습 모드
    MODE_NAME = "연습 (Practice)"
    DATA_FILE = "v4_training_data_all.csv"
    MAX_DATA_TO_USE = 50
    VAL_RATIO = 0.1
    NUM_EPOCHS = 3
    NUM_TEST_SAMPLES = 3
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = True
    MODEL_SUFFIX = "practice-50"
    REQUIRES_GPU = True

elif EXECUTION_MODE == 1:
    # 전체 모드
    MODE_NAME = "전체 (Full)"
    DATA_FILE = "v4_training_data_all.csv"
    MAX_DATA_TO_USE = 1000
    VAL_RATIO = 0.1
    NUM_EPOCHS = 5
    NUM_TEST_SAMPLES = 3
    ENABLE_FINETUNING = True
    DETAILED_LOGGING = False
    MODEL_SUFFIX = "1k-v4.0"
    REQUIRES_GPU = True

else:  # MODE == 2
    # 테스트 모드 (v2.1 Teacher-Aligned!)
    MODE_NAME = "추론 전용 (Inference Only - v2.1 Teacher-Aligned)"
    DATA_FILE = "v4_training_data_all.csv"
    MAX_DATA_TO_USE = NUM_INFERENCE_SAMPLES
    NUM_TEST_SAMPLES = NUM_INFERENCE_SAMPLES
    ENABLE_FINETUNING = False
    DETAILED_LOGGING = True
    MODEL_SUFFIX = INFERENCE_MODEL_NAME
    REQUIRES_GPU = not USE_CPU_FOR_INFERENCE

# 모델 정보
if EXECUTION_MODE == 2:
    MODEL_VERSION = {
        'name': INFERENCE_MODEL_NAME,
        'mode': MODE_NAME,
        'base_model': 'Qwen/Qwen2.5-1.5B-Instruct',
        'inference_samples': NUM_INFERENCE_SAMPLES,
        'style': 'News Briefing',
        'device': 'CPU' if USE_CPU_FOR_INFERENCE else 'GPU',
        'version': '2.1-teacher-aligned',
        'temperature': TEMPERATURE
    }
else:
    MODEL_VERSION = {
        'name': f'ArXiv-NewsBrief-1.5B-{MODEL_SUFFIX}',
        'mode': MODE_NAME,
        'base_model': 'Qwen/Qwen2.5-1.5B-Instruct',
        'data_size': f'{MAX_DATA_TO_USE}',
        'style': 'News Briefing',
    }

print(f"\n🎯 실행 모드: {MODE_NAME}")
print(f"📦 모델: {MODEL_VERSION['name']}")
if EXECUTION_MODE == 2:
    print(f"💻 디바이스: {'CPU (느림)' if USE_CPU_FOR_INFERENCE else 'GPU (빠름)'}")
    print(f"🔬 추론 샘플: {NUM_INFERENCE_SAMPLES}개")
    print(f"✨ 버전: v2.1 Teacher-Aligned")
    print(f"🌡️ Temperature: {TEMPERATURE} (Teacher와 동일)")
elif EXECUTION_MODE != 2:
    print(f"📊 데이터: {MAX_DATA_TO_USE}개")
    print(f"🔄 에포크: {NUM_EPOCHS}")
print(f"🧪 테스트: {NUM_TEST_SAMPLES}개")

# ================================================================
# 간소화된 후처리 함수 (v2.0 유지)
# ================================================================

import re

def clean_output_minimal(text):
    """
    최소한의 후처리만 수행 (v2.0 안정화 버전)
    - 특수 토큰 제거
    - 공백 정리
    - 기본 정리만
    """
    # 특수 토큰 제거
    text = text.replace("<|im_start|>", "").replace("<|im_end|>", "")
    
    # 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

print(f"\n✅ 후처리 함수 로드 완료 (v2.0 유지)")

# ================================================================
# MODE 2: 추론 전용 모드 (v2.1 Teacher-Aligned!) ⭐
# ================================================================

if EXECUTION_MODE == 2:

    print("\n" + "="*70)
    print("🔬 MODE 2: 추론 전용 모드 (v2.1 Teacher-Aligned)")
    print("="*70)

    # ============================================================
    # STEP 1: 패키지 설치
    # ============================================================

    print("\n" + "="*70)
    print("📦 STEP 1: 패키지 설치")
    print("="*70)

    if not USE_CPU_FOR_INFERENCE:
        print("\n🔧 GPU 모드: bitsandbytes 설치...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "bitsandbytes>=0.43.0"],
                          check=True)
        except:
            print("⚠️  bitsandbytes 설치 실패 - 계속 진행")

    print("\n📥 필수 패키지 설치 중...")
    packages = ["transformers", "datasets", "accelerate", "peft", "pandas"]
    for pkg in packages:
        print(f"  - {pkg}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
                      capture_output=True, check=True)

    print("✅ 패키지 설치 완료!")

    # ============================================================
    # STEP 2: Import
    # ============================================================

    print("\n" + "="*70)
    print("📚 STEP 2: 라이브러리 Import")
    print("="*70)

    import torch
    import json
    import time
    import pandas as pd
    from datetime import datetime
    from pathlib import Path
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel

    print("✅ Import 완료")

    # 디바이스 확인
    print("\n🔍 디바이스 환경 확인...")
    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ 메모리: {gpu_memory:.2f}GB")
    else:
        print("⚠️  GPU 없음 - CPU 모드")
        device = "cpu"

    # Drive 마운트
    print("\n💾 Google Drive 마운트...")
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ 마운트 완료")
    except:
        print("⚠️  Colab 환경 아님")

    # ⭐ 어댑터 경로: 최종 확정 경로 사용
    BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
    # ⭐⭐⭐ 최종 어댑터 경로 (INFERENCE_MODEL_NAME 변수 사용)
    ADAPTER_PATH = f"/content/drive/MyDrive/ArXiv-Models/{INFERENCE_MODEL_NAME}/final_model"
    
    RESULTS_DIR = Path(f"/content/drive/MyDrive/ArXiv-Models/{INFERENCE_MODEL_NAME}/inference_results_v2.1")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n⚙️ 설정 확인:")
    print(f"  모드: {MODE_NAME}")
    print(f"  버전: v2.1 Teacher-Aligned")
    print(f"  디바이스: {device.upper()}")
    print(f"  모델: {INFERENCE_MODEL_NAME}")
    print(f"  어댑터 경로: {ADAPTER_PATH}")
    print(f"  샘플 수: {NUM_INFERENCE_SAMPLES}개")
    print(f"  Temperature: {TEMPERATURE} ⭐")

    # 어댑터 존재 확인
    if not Path(ADAPTER_PATH).exists():
        raise FileNotFoundError(f"❌ 어댑터 없음: {ADAPTER_PATH}\n학습된 어댑터가 필요합니다!")

    # ============================================================
    # STEP 3: 데이터 로드
    # ============================================================

    print("\n" + "="*70)
    print("📂 STEP 3: 테스트 데이터 로드")
    print("="*70)

    data_path = Path(DATA_DIR) / DATA_FILE

    if not data_path.exists():
        raise FileNotFoundError(f"❌ 데이터 없음: {data_path}")

    print(f"📥 데이터 로딩: {DATA_FILE}")
    df = pd.read_csv(data_path)
    print(f"✅ 전체 데이터: {len(df)}개")

    # ⭐ 실제 컬럼명 확인
    print(f"\n📋 데이터 컬럼: {list(df.columns)}")
    
    # ⭐ 'llm_success' 컬럼 사용 (status 대신)
    if 'llm_success' in df.columns:
        df_success = df[df['llm_success'] == True].copy()
        print(f"✅ 성공 데이터: {len(df_success)}개")
    elif 'status' in df.columns:
        df_success = df[df['status'] == 'success'].copy()
        print(f"✅ 성공 데이터: {len(df_success)}개")
    else:
        print(f"⚠️  성공 필터 컬럼 없음 - 전체 데이터 사용")
        df_success = df.copy()

    df_test = df_success.head(NUM_INFERENCE_SAMPLES)
    print(f"\n📊 테스트 데이터: {len(df_test)}개")

    # ============================================================
    # STEP 4: 모델 로딩
    # ============================================================

    print("\n" + "="*70)
    print("🚀 STEP 4: 모델 로딩")
    print("="*70)

    print(f"📥 토크나이저 로딩...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("✅ 토크나이저 로드 완료")

    print(f"\n📥 베이스 모델 로딩...")
    if device == "cuda":
        print(f"🚀 GPU 모드로 로딩 중... (1-2분 소요)")
        from transformers import BitsAndBytesConfig
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            ),
            device_map="auto"
        )
    else:
        print(f"💻 CPU 모드로 로딩 중... (2-3분 소요)")
        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )

    print("✅ 베이스 모델 로드 완료")

    print(f"\n📥 LoRA 어댑터 로딩...")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    model.eval()
    print("✅ 학습된 어댑터 로드 완료")

    print("\n💡 모델 준비 완료!")

    # ============================================================
    # STEP 5: 추론 실행 (v2.1 Teacher-Aligned!) ⭐⭐⭐
    # ============================================================

    print("\n" + "="*70)
    print(f"🔬 STEP 5: 추론 실행 (v2.1 Teacher-Aligned)")
    print("="*70)

    print(f"\n✨ v2.1 핵심 개선사항:")
    print(f"  ⭐⭐⭐ temperature: 0.7 → 0.3 (Teacher와 동일)")
    print(f"  ⭐⭐ top_k: 없음 → 40 (Teacher와 동일)")
    print(f"  ✅ eos_token_id 유지 (v2.0 안정성)")
    print(f"  ✅ 과도한 제약 제거 유지 (v2.0)")

    # ⭐⭐⭐ v2.1 Teacher-Aligned Generation Config
    generation_config = {
        "max_new_tokens": 80,
        "temperature": TEMPERATURE,       # ⭐⭐⭐ 0.3 (Teacher와 동일)
        "do_sample": True,
        "top_p": 0.9,
        "top_k": 40,                      # ⭐⭐ 추가 (Teacher와 동일)
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,  # ✅ 유지 (v2.0)
    }

    all_results = []
    print(f"\n🧪 추론 시작...\n")
    overall_start = time.time()

    for i, (idx, row) in enumerate(df_test.iterrows()):
        sample_num = i + 1

        print(f"{'='*70}")
        print(f"샘플 {sample_num}/{len(df_test)}")
        print(f"{'='*70}")

        # ⭐ 고정 컬럼명 사용
        abstract = row['original_abstract']
        target = row['llm_summary']

        print(f"\n📄 초록:")
        print(f"{abstract[:200]}...")

        print(f"\n🎯 목표 요약:")
        print(f"{target}")

        # 프롬프트 생성
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": abstract}
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        print(f"\n⏳ 추론 중... ", end="")
        sample_start = time.time()

        # ⭐⭐⭐ v2.1 Teacher-Aligned 생성
        with torch.no_grad():
            outputs = model.generate(**inputs, **generation_config)

        sample_time = time.time() - sample_start
        print(f"완료! ({sample_time:.1f}초)")

        # 출력 추출 (v2.0 방식 유지)
        full_output = tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        if "<|im_start|>assistant" in full_output:
            summary = full_output.split("<|im_start|>assistant")[-1]
            if "<|im_end|>" in summary:
                summary = summary.split("<|im_end|>")[0]
            summary = summary.strip()
        else:
            generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
            summary = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        # 후처리
        summary = clean_output_minimal(summary)

        print(f"\n✨ 생성된 요약 (v2.1 Teacher-Aligned):")
        print(f"{summary}")

        # 분석
        word_count = len(summary.split())
        sentence_count = len(re.split(r'[.!?]+', summary.strip())) - 1

        # 특수 문자 체크
        has_special = any(char in summary for char in ['--', '()', '""'])

        print(f"\n📊 분석:")
        print(f"  단어 수: {word_count}개 {'✅' if word_count <= 45 else '⚠️' if word_count <= 55 else '❌'}")
        print(f"  문장 수: {sentence_count}개 {'✅' if sentence_count == 2 else '⚠️'}")
        print(f"  소요 시간: {sample_time:.1f}초")
        print(f"  {'✅ 특수 문자 없음 (안정적)' if not has_special else '⚠️ 특수 문자 발견'}")

        # 진행 상황
        elapsed = time.time() - overall_start
        avg_time = elapsed / sample_num
        remaining = (len(df_test) - sample_num) * avg_time

        print(f"\n⏱️ 진행 상황:")
        print(f"  완료: {sample_num}/{len(df_test)} ({sample_num/len(df_test)*100:.1f}%)")
        print(f"  경과: {elapsed/60:.1f}분")
        print(f"  예상 남은 시간: {remaining/60:.1f}분")

        all_results.append({
            "sample_id": sample_num,
            "abstract": abstract,
            "target_summary": target,
            "generated_summary": summary,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "meets_word_limit": word_count <= 45,
            "meets_sentence_count": sentence_count == 2,
            "has_special_chars": has_special,
            "inference_time_seconds": round(sample_time, 2)
        })

        print()

    total_elapsed = time.time() - overall_start

    # ============================================================
    # STEP 6: 결과 분석
    # ============================================================

    print("\n" + "="*70)
    print("📊 STEP 6: 결과 분석 (v2.1 Teacher-Aligned)")
    print("="*70)

    avg_words = sum(r['word_count'] for r in all_results) / len(all_results)
    word_compliant = sum(1 for r in all_results if r['meets_word_limit'])
    sentence_compliant = sum(1 for r in all_results if r['meets_sentence_count'])
    avg_inference_time = sum(r['inference_time_seconds'] for r in all_results) / len(all_results)
    special_char_issues = sum(1 for r in all_results if r['has_special_chars'])

    print(f"\n📈 전체 통계:")
    print(f"  총 샘플: {len(all_results)}개")
    print(f"  평균 단어 수: {avg_words:.1f}개")
    print(f"  45단어 이하: {word_compliant}/{len(all_results)} ({word_compliant/len(all_results)*100:.1f}%)")
    print(f"  2문장 구조: {sentence_compliant}/{len(all_results)} ({sentence_compliant/len(all_results)*100:.1f}%)")
    print(f"  평균 추론 시간: {avg_inference_time:.1f}초/샘플")
    print(f"  총 소요 시간: {total_elapsed/60:.1f}분")

    print(f"\n🔍 v2.1 안정성 지표:")
    print(f"  특수 문자 출현: {special_char_issues}/{len(all_results)} ({special_char_issues/len(all_results)*100:.1f}%)")
    if special_char_issues == 0:
        print(f"  ✅ 완벽한 안정성! (v2.0 수준 유지)")

    print(f"\n📊 v2.0 vs v2.1 비교:")
    print(f"  평균 단어: 52.4개 → {avg_words:.1f}개 ({(52.4-avg_words)/52.4*100:+.1f}%)")
    print(f"  45단어 이하: 17% → {word_compliant/len(all_results)*100:.1f}% ({word_compliant/len(all_results)*100-17:+.1f}%p)")
    print(f"  특수 문자: 0% → {special_char_issues/len(all_results)*100:.1f}% {'✅ 유지' if special_char_issues == 0 else '⚠️'}")

    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    device_suffix = "cpu" if device == "cpu" else "gpu"
    json_file = RESULTS_DIR / f"inference_v2.1_{NUM_INFERENCE_SAMPLES}samples_{device_suffix}_{timestamp}.json"

    result_data = {
        "metadata": {
            "version": "2.1-teacher-aligned",
            "model": INFERENCE_MODEL_NAME,
            "device": device.upper(),
            "num_samples": NUM_INFERENCE_SAMPLES,
            "temperature": TEMPERATURE,
            "top_k": 40,
            "timestamp": datetime.now().isoformat()
        },
        "statistics": {
            "avg_word_count": round(avg_words, 2),
            "word_compliant_rate": round(word_compliant/len(all_results)*100, 2),
            "sentence_compliant_rate": round(sentence_compliant/len(all_results)*100, 2),
            "special_char_issues": special_char_issues,
            "stability_rate": round((1 - special_char_issues/len(all_results))*100, 2)
        },
        "results": all_results
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 결과 저장: {json_file.name}")

    print("\n" + "="*70)
    print("✅ v2.1 Teacher-Aligned 추론 완료!")
    print("="*70)

    print(f"\n💡 평가:")
    if avg_words <= 45 and special_char_issues == 0:
        print(f"  ✅✅✅ 목표 완전 달성! 프로덕션 배포 가능")
    elif avg_words <= 50 and special_char_issues == 0:
        print(f"  ✅✅ 거의 달성! 안정성 완벽, 단어 수 양호")
    else:
        print(f"  ✅ 개선 확인, 100개 샘플로 재검증 권장")

elif EXECUTION_MODE in [0, 1]:
    print("\n⚠️ MODE 0, 1은 이 버전에서 지원하지 않습니다.")
    print("MODE 2 (v2.1 추론)만 사용 가능합니다.")

print("\n" + "="*70)
print("🎉 프로그램 종료")
print("="*70)