"""
병합 모델 빠른 추론 테스트 (Colab)
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
from pathlib import Path
import sys

print("="*70)
print("🧪 병합 모델 빠른 추론 테스트")
print("="*70)

# ================================================================
# STEP 1: Drive 마운트
# ================================================================
print("\n📁 Google Drive 확인...")

try:
    from google.colab import drive

    if not Path("/content/drive").exists():
        print("🔗 Google Drive 마운트 중...")
        drive.mount('/content/drive')
        print("✅ 마운트 완료")
    else:
        print("✅ 이미 마운트됨")
except ImportError:
    print("⚠️  Colab 환경이 아닙니다")
except Exception as e:
    print(f"❌ 마운트 실패: {e}")
    sys.exit(1)

# ================================================================
# STEP 2: 경로 설정 및 검증
# ================================================================
print("\n🔍 모델 경로 확인...")

# 기본 경로
MODEL_NAME = "ArXiv-NewsBrief-1.5B-1k-v4.0"
MODEL_PATH = f"/content/drive/MyDrive/ArXiv-Models/{MODEL_NAME}/merged_model"

model_path = Path(MODEL_PATH)

# 경로 존재 확인
if not model_path.exists():
    print(f"\n❌ 오류: 모델을 찾을 수 없습니다!")
    print(f"경로: {MODEL_PATH}")

    # 상위 폴더 확인
    parent = model_path.parent
    if parent.exists():
        print(f"\n📂 {parent}에 있는 폴더:")
        for item in parent.iterdir():
            if item.is_dir():
                print(f"  • {item.name}")
    else:
        # ArXiv-Models 폴더 확인
        models_dir = Path("/content/drive/MyDrive/ArXiv-Models")
        if models_dir.exists():
            print(f"\n📂 사용 가능한 모델:")
            for item in models_dir.iterdir():
                if item.is_dir():
                    print(f"  • {item.name}")
                    merged = item / "merged_model"
                    if merged.exists():
                        print(f"    → merged_model ✅")
        else:
            print(f"\n❌ ArXiv-Models 폴더가 없습니다!")

    print("\n💡 해결 방법:")
    print("  1. 위에 표시된 실제 경로로 MODEL_PATH 수정")
    print("  2. 또는 병합 스크립트 먼저 실행")
    sys.exit(1)

print(f"✅ 모델 경로 확인: {MODEL_PATH}")

# 필수 파일 확인
config_file = model_path / "config.json"
if not config_file.exists():
    print(f"\n⚠️  경고: config.json이 없습니다!")
    print(f"폴더 내용:")
    for f in model_path.iterdir():
        print(f"  • {f.name}")
    print("\n이 폴더가 올바른 모델 폴더인지 확인하세요.")
    sys.exit(1)

# ================================================================
# STEP 3: 테스트 설정
# ================================================================

# 테스트 초록
TEST_ABSTRACT = """
Recent advances in large language models have demonstrated remarkable
capabilities in natural language understanding and generation. This paper
introduces a novel parameter-efficient fine-tuning approach that achieves
state-of-the-art performance while using significantly less computational
resources. Our method enables high-quality text generation on consumer hardware.
"""

print(f"\n📦 모델: {MODEL_NAME}")
print(f"📂 경로: {MODEL_PATH}")
print(f"💻 디바이스: {'GPU' if torch.cuda.is_available() else 'CPU'}")

if not torch.cuda.is_available():
    print("⚠️  GPU 없음 - CPU 모드 (느림)")
    print("💡 Colab: 런타임 → 런타임 유형 변경 → T4 GPU")

# ================================================================
# STEP 4: 모델 로딩
# ================================================================

print("\n⏳ 모델 로딩 중... (1-2분)")
start_load = time.time()

try:
    tokenizer = AutoTokenizer.from_pretrained(
        str(model_path),  # ⭐ Path를 str로 변환
        trust_remote_code=True,
        local_files_only=True  # ⭐ 로컬 파일만 사용
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("✅ 토크나이저 로드 완료")

except Exception as e:
    print(f"❌ 토크나이저 로드 실패: {e}")
    sys.exit(1)

try:
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),  # ⭐ Path를 str로 변환
        device_map="auto" if torch.cuda.is_available() else "cpu",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        trust_remote_code=True,
        local_files_only=True  # ⭐ 로컬 파일만 사용
    )
    model.eval()

    print("✅ 모델 로드 완료")

except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    print("\n가능한 원인:")
    print("  1. 병합이 완전히 완료되지 않음")
    print("  2. 필요한 파일 누락")
    print("  3. 메모리 부족")
    sys.exit(1)

load_time = time.time() - start_load
print(f"\n✅ 로딩 완료! ({load_time:.1f}초)")

# ================================================================
# STEP 5: 추론
# ================================================================

print("\n📄 테스트 초록:")
print(TEST_ABSTRACT.strip())

system_msg = "Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences."

messages = [
    {"role": "system", "content": system_msg},
    {"role": "user", "content": TEST_ABSTRACT.strip()}
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

print("\n⏳ 추론 중...", end=" ")
start_infer = time.time()

inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
inputs = {k: v.to(model.device) for k, v in inputs.items()}

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        min_length=30,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        repetition_penalty=1.2,
        no_repeat_ngram_size=3,
        pad_token_id=tokenizer.pad_token_id
    )

infer_time = time.time() - start_infer
print(f"완료! ({infer_time:.1f}초)")

# 결과
generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
summary = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

print("\n✨ 생성된 요약:")
print(summary)

# ================================================================
# STEP 6: 분석
# ================================================================

import re
words = len(summary.split())
sentences = len(re.split(r'[.!?]+', summary.strip())) - 1

print("\n📊 분석:")
print(f"  단어 수: {words}개 {'✅' if words <= 45 else '⚠️'}")
print(f"  문장 수: {sentences}개 {'✅' if sentences == 2 else '⚠️'}")
print(f"  로딩 시간: {load_time:.1f}초")
print(f"  추론 시간: {infer_time:.1f}초")
print(f"  디바이스: {model.device}")

print("\n" + "="*70)
print("🎉 테스트 완료!")
print("="*70)

print("\n💡 성능 요약:")
print(f"  - 병합 모델 크기: ~3GB")
print(f"  - 추론 속도: {infer_time:.1f}초/샘플")
print(f"  - 품질: {'✅ 양호' if words <= 50 and sentences <= 3 else '⚠️ 조정 필요'}")

print("\n🚀 다음 단계:")
print("  1. Streamlit 챗봇으로 대화형 테스트")
print("  2. MODE 2로 100개 샘플 평가")
print("  3. 프로덕션 배포")

print("\n" + "="*70)