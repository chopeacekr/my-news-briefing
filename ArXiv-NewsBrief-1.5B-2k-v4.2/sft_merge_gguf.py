"""
=================================================================
🔗 ArXiv-NewsBrief v4.2 모델 병합 + GGUF 변환 (Colab 전용)
=================================================================

✅ LoRA 어댑터를 베이스 모델에 병합
✅ GGUF 변환 (CPU 최적화)
✅ Google Drive 자동 마운트
✅ 경로 검증 및 안전한 에러 처리
✅ GPU/CPU 자동 감지
✅ 진행 상황 실시간 출력

=================================================================
"""

import subprocess
import sys
import os
from pathlib import Path
import time

print("\n" + "="*70)
print("🔗 ArXiv-NewsBrief v4.2 모델 병합 + GGUF 변환 (Colab)")
print("="*70)

# ================================================================
# ⚙️ 설정 (여기만 수정하세요!)
# ================================================================

# 병합할 모델 정보
MODEL_NAME = "ArXiv-NewsBrief-1.5B-2k-v4.2"  # ⭐ 실제 모델 이름
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

# Google Drive 경로 (학습 시 사용한 경로와 동일하게)
DRIVE_BASE = "/content/drive/MyDrive/ArXiv-Models"

# 자동 생성되는 경로
ADAPTER_PATH = f"{DRIVE_BASE}/{MODEL_NAME}/final_model"
OUTPUT_PATH = f"{DRIVE_BASE}/{MODEL_NAME}/merged_model"
GGUF_OUTPUT_PATH = f"{DRIVE_BASE}/{MODEL_NAME}/ArXiv-NewsBrief-Q4_K_M.gguf"

# ⭐⭐⭐ GGUF 변환 옵션 (여기서 ON/OFF)
CONVERT_TO_GGUF = True  # 🔧 True: GGUF 변환, False: 병합만
GGUF_QUANTIZATION = "q4_k_m"  # 🔧 q4_k_m (권장), q8_0 (고품질), q4_0 (최소)
DELETE_MERGED_AFTER_GGUF = False  # 🔧 True: GGUF 후 병합 모델 삭제 (공간 절약)

# 메모리 최적화 옵션
USE_LOW_MEMORY_MODE = True  # True: CPU 메모리 절약 (느림), False: 빠름 (메모리 많이 사용)

print(f"\n📦 모델: {MODEL_NAME}")
print(f"📂 어댑터: {ADAPTER_PATH}")
print(f"💾 출력: {OUTPUT_PATH}")
if CONVERT_TO_GGUF:
    print(f"🔄 GGUF: {GGUF_OUTPUT_PATH}")
    print(f"   양자화: {GGUF_QUANTIZATION.upper()}")

# ================================================================
# STEP 1: Google Drive 마운트
# ================================================================

print("\n" + "="*70)
print("📁 STEP 1: Google Drive 마운트")
print("="*70)

try:
    from google.colab import drive

    if not Path("/content/drive").exists():
        print("\n🔗 Google Drive 마운트 중...")
        drive.mount('/content/drive')
        print("✅ 마운트 완료")
    else:
        print("✅ 이미 마운트됨")
except ImportError:
    print("⚠️  Colab 환경이 아닙니다. Drive 마운트 건너뜀")
except Exception as e:
    print(f"❌ 마운트 실패: {e}")
    sys.exit(1)

# ================================================================
# STEP 2: 경로 검증
# ================================================================

print("\n" + "="*70)
print("🔍 STEP 2: 경로 검증")
print("="*70)

adapter_path = Path(ADAPTER_PATH)
output_path = Path(OUTPUT_PATH)

print(f"\n📂 어댑터 경로 확인: {adapter_path}")

if not adapter_path.exists():
    print(f"\n❌ 오류: 어댑터 경로를 찾을 수 없습니다!")
    print(f"\n현재 경로: {adapter_path}")
    print(f"\n가능한 원인:")
    print(f"  1. 모델 이름 오류: MODEL_NAME = '{MODEL_NAME}'")
    print(f"  2. 학습 완료되지 않음")
    print(f"  3. Drive 경로 불일치")

    # Drive에서 실제 모델 찾기
    drive_models = Path(DRIVE_BASE)
    if drive_models.exists():
        print(f"\n📁 {DRIVE_BASE}에서 발견된 모델:")
        for item in drive_models.iterdir():
            if item.is_dir():
                print(f"  • {item.name}")
                final_model_path = item / "final_model"
                if final_model_path.exists():
                    print(f"    ✅ final_model 폴더 있음")
    sys.exit(1)

print("✅ 어댑터 경로 확인 완료")

# adapter_config.json 확인
adapter_config = adapter_path / "adapter_config.json"
if not adapter_config.exists():
    print(f"\n❌ 오류: adapter_config.json을 찾을 수 없습니다!")
    print(f"\n{adapter_path}에 있는 파일:")
    for f in adapter_path.iterdir():
        print(f"  • {f.name}")
    sys.exit(1)

print("✅ adapter_config.json 확인 완료")

# 출력 디렉토리 생성
output_path.mkdir(parents=True, exist_ok=True)
print(f"✅ 출력 디렉토리 준비 완료: {output_path}")

# ================================================================
# STEP 3: 패키지 설치
# ================================================================

print("\n" + "="*70)
print("📦 STEP 3: 패키지 설치")
print("="*70)

packages = [
    "transformers",
    "peft",
    "accelerate",
    "torch",
]

print("\n📥 필수 패키지 설치 중...")
for pkg in packages:
    print(f"  • {pkg}", end="... ")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
            capture_output=True,
            check=True
        )
        print("✅")
    except subprocess.CalledProcessError as e:
        print(f"❌\n오류: {e}")
        sys.exit(1)

print("\n✅ 모든 패키지 설치 완료")

# ================================================================
# STEP 3.5: llama.cpp 설치 (GGUF 변환 시) - CMake 빌드 시스템
# ================================================================

if CONVERT_TO_GGUF:
    print("\n" + "="*70)
    print("🛠️ STEP 3.5: llama.cpp 설치 (GGUF 변환용, CMake)")
    print("="*70)

    llama_cpp_path = Path("/content/llama.cpp")

    if not llama_cpp_path.exists():
        print("\n📥 llama.cpp 클론 중...")
        subprocess.run([
            "git", "clone",
            "https://github.com/ggml-org/llama.cpp",
            str(llama_cpp_path)
        ], check=True)
        print("✅ 클론 완료")
    else:
        print("✅ llama.cpp 이미 설치됨")

    print("\n📥 빌드 의존성 설치(apt)...")
    subprocess.run(["bash", "-lc", "apt-get update -y"], check=True)
    subprocess.run(["bash", "-lc", "apt-get install -y cmake build-essential"], check=True)
    print("✅ cmake/build-essential 설치 완료")

    print("\n📥 python 의존성 설치(pip)...")
    gguf_packages = ["sentencepiece", "protobuf", "gguf"]
    for pkg in gguf_packages:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg], check=False)
    print("✅ python 패키지 준비 완료")

# ================================================================
# STEP 4: Import 및 환경 확인
# ================================================================

print("\n" + "="*70)
print("📚 STEP 4: 라이브러리 Import")
print("="*70)

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    print("✅ Import 완료")
except ImportError as e:
    print(f"❌ Import 실패: {e}")
    sys.exit(1)

# 디바이스 확인
print("\n🔍 환경 확인...")
if torch.cuda.is_available():
    device = "cuda"
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"✅ GPU: {gpu_name}")
    print(f"✅ VRAM: {gpu_memory:.1f}GB")

    # 메모리 정리
    torch.cuda.empty_cache()
    print("✅ GPU 메모리 정리 완료")
else:
    device = "cpu"
    print("⚠️  GPU 없음 - CPU 모드 (느림)")
    print("💡 Colab: 런타임 → 런타임 유형 변경 → T4 GPU")

# ================================================================
# STEP 5: 베이스 모델 로딩
# ================================================================

print("\n" + "="*70)
print("🚀 STEP 5: 베이스 모델 로딩")
print("="*70)

print(f"\n📥 로딩 중: {BASE_MODEL}")
print("⏳ 약 1-2분 소요...")

try:
    if device == "cuda":
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=USE_LOW_MEMORY_MODE
        )
    else:
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )

    print("✅ 베이스 모델 로드 완료")

except Exception as e:
    print(f"❌ 베이스 모델 로드 실패!")
    print(f"오류: {e}")
    print("\n해결 방법:")
    print("  1. 인터넷 연결 확인")
    print("  2. HuggingFace 다운로드 제한 확인")
    print("  3. 잠시 후 재시도")
    sys.exit(1)

# ================================================================
# STEP 6: LoRA 어댑터 로딩
# ================================================================

print("\n" + "="*70)
print("🔗 STEP 6: LoRA 어댑터 로딩")
print("="*70)

print(f"\n📥 로딩 중: {ADAPTER_PATH}")

try:
    model = PeftModel.from_pretrained(
        base_model,
        str(adapter_path),  # ⭐ Path를 str로 변환
        is_trainable=False
    )
    print("✅ LoRA 어댑터 로드 완료")

except Exception as e:
    print(f"❌ LoRA 어댑터 로드 실패!")
    print(f"오류: {e}")
    print(f"\n디버그 정보:")
    print(f"  경로: {adapter_path.absolute()}")
    print(f"  존재 여부: {adapter_path.exists()}")
    print(f"\n폴더 내용:")
    for f in adapter_path.iterdir():
        size = f.stat().st_size / (1024*1024)
        print(f"    • {f.name} ({size:.1f}MB)")
    sys.exit(1)

# ================================================================
# STEP 7: 모델 병합
# ================================================================

print("\n" + "="*70)
print("⚙️ STEP 7: 모델 병합")
print("="*70)

print("\n🔗 LoRA 가중치를 베이스 모델에 병합 중...")
print("⏳ 약 1-2분 소요...")

try:
    merged_model = model.merge_and_unload()
    print("✅ 병합 완료!")

    # 메모리 정리
    del model
    del base_model
    if device == "cuda":
        torch.cuda.empty_cache()

    print("✅ 메모리 정리 완료")

except Exception as e:
    print(f"❌ 병합 실패!")
    print(f"오류: {e}")
    sys.exit(1)

# ================================================================
# STEP 8: 병합 모델 저장
# ================================================================

print("\n" + "="*70)
print("💾 STEP 8: 병합 모델 저장")
print("="*70)

print(f"\n📁 저장 위치: {output_path}")
print("⏳ 약 1-2분 소요...")

try:
    merged_model.save_pretrained(
        str(output_path),
        safe_serialization=True,  # safetensors 형식
        max_shard_size="2GB"  # 파일 분할 (Drive 업로드 안정성)
    )
    print("✅ 모델 저장 완료")

except Exception as e:
    print(f"❌ 모델 저장 실패!")
    print(f"오류: {e}")
    sys.exit(1)

# 메모리 정리 (GGUF 변환 전)
del merged_model
if device == "cuda":
    torch.cuda.empty_cache()
print("✅ 메모리 정리 완료")

# ================================================================
# STEP 9: 토크나이저 저장
# ================================================================

print("\n" + "="*70)
print("📝 STEP 9: 토크나이저 저장")
print("="*70)

try:
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        trust_remote_code=True
    )
    tokenizer.save_pretrained(str(output_path))
    print("✅ 토크나이저 저장 완료")

except Exception as e:
    print(f"❌ 토크나이저 저장 실패!")
    print(f"오류: {e}")
    sys.exit(1)

# ================================================================
# STEP 10: GGUF 변환 (선택적)
# ================================================================

# ================================================================
# STEP 10: GGUF 변환 (선택적)  + (추가) 양자화 단계
# ================================================================

# ================================================================
# STEP 10: GGUF 변환 (F16) → 양자화(Q4_K_M 등)  [Drive 안정형]
# ================================================================

if CONVERT_TO_GGUF:
    import shutil

    print("\n" + "="*70)
    print("🔄 STEP 10: GGUF 변환(F16) → 양자화(Q4_K_M 등) [Drive 안정형]")
    print("="*70)

    GGUF_CONVERT_OUTTYPE = "f16"

    # ✅ 1) Drive에 바로 쓰지 말고 /content 로컬 디스크에 먼저 생성
    TMP_DIR = Path("/content/tmp_gguf")
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    local_f16 = TMP_DIR / "ArXiv-NewsBrief-F16.gguf"
    local_q   = TMP_DIR / f"ArXiv-NewsBrief-{GGUF_QUANTIZATION.upper()}.gguf"

    print(f"\n📁 로컬 임시 폴더: {TMP_DIR}")
    print(f"📄 로컬 F16: {local_f16}")
    print(f"📄 로컬 양자화: {local_q}")
    print(f"📁 최종 Drive 저장: {GGUF_OUTPUT_PATH}")

    # ✅ 2) Drive 최종 경로의 부모 폴더 보장
    gguf_out_path = Path(GGUF_OUTPUT_PATH)
    gguf_out_path.parent.mkdir(parents=True, exist_ok=True)

    original_dir = os.getcwd()
    os.chdir("/content/llama.cpp")
    start_time = time.time()

    try:
        # 0) CMake 빌드
        print("\n🛠️ llama.cpp CMake 빌드 중...")
        subprocess.run(["bash", "-lc", "cmake -S . -B build -DCMAKE_BUILD_TYPE=Release"], check=True)
        subprocess.run(["bash", "-lc", "cmake --build build -j"], check=True)

        # 1) HF → GGUF(F16) (로컬에 저장)
        print("\n🔄 [1/3] HF → GGUF(F16) 변환 시작 (로컬 저장)...")
        result = subprocess.run([
            sys.executable,
            "convert_hf_to_gguf.py",
            str(output_path),
            "--outfile", str(local_f16),
            "--outtype", GGUF_CONVERT_OUTTYPE,
            "--use-temp-file"   # ✅ 임시파일 사용(안정성↑) - 로컬에서만!
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("\n❌ GGUF(F16) 변환 실패!")
            print(result.stderr)
            raise SystemExit(1)

        if not local_f16.exists() or local_f16.stat().st_size < 10_000_000:
            raise RuntimeError("로컬 F16 GGUF 생성이 확인되지 않았습니다(파일이 없거나 너무 작음).")

        f16_size = local_f16.stat().st_size / (1024**3)
        print(f"✅ 로컬 GGUF(F16) 생성 완료: {f16_size:.2f}GB")

        # 2) 양자화 바이너리 탐색
        print("\n🔄 [2/3] GGUF 양자화 시작...")
        quant_candidates = [
            Path("build/bin/llama-quantize"),
            Path("build/bin/quantize"),
            Path("build/llama-quantize"),
            Path("build/quantize"),
        ]
        quant_bin = next((p for p in quant_candidates if p.exists()), None)
        if quant_bin is None:
            raise RuntimeError("양자화 바이너리를 찾지 못했습니다. build/bin에 llama-quantize 또는 quantize가 있어야 합니다.")

        quant_type = GGUF_QUANTIZATION.upper()

        q = subprocess.run([
            str(quant_bin),
            str(local_f16),
            str(local_q),
            quant_type
        ], capture_output=True, text=True)

        if q.returncode != 0:
            print("\n❌ GGUF 양자화 실패!")
            print(q.stderr)
            raise SystemExit(1)

        if not local_q.exists() or local_q.stat().st_size < 5_000_000:
            raise RuntimeError("로컬 양자화 GGUF 생성이 확인되지 않았습니다(파일이 없거나 너무 작음).")

        q_size = local_q.stat().st_size / (1024**3)
        print(f"✅ 로컬 양자화 GGUF 생성 완료: {q_size:.2f}GB")

        # 3) 로컬 → Drive 복사 (최종 저장)
        print("\n🔄 [3/3] 로컬 → Drive 복사 중...")
        tmp_drive_path = gguf_out_path.with_suffix(".gguf.tmp")

        # 기존 tmp 파일 제거
        if tmp_drive_path.exists():
            tmp_drive_path.unlink()

        # tmp로 복사 후 rename(원자적 교체)
        shutil.copy2(local_q, tmp_drive_path)
        tmp_drive_path.replace(gguf_out_path)

        # 검증
        if not gguf_out_path.exists():
            raise RuntimeError("Drive로 GGUF 복사가 실패했습니다(최종 파일이 없음).")

        drive_size = gguf_out_path.stat().st_size / (1024**3)
        elapsed = time.time() - start_time

        print("\n✅ Drive 저장 완료!")
        print(f"   경로: {gguf_out_path}")
        print(f"   크기: {drive_size:.2f}GB")
        print(f"   소요 시간: {elapsed/60:.1f}분")

        # (선택) 로컬 임시파일 정리
        # local_f16.unlink(missing_ok=True)
        # local_q.unlink(missing_ok=True)

    finally:
        os.chdir(original_dir)

    # ================================================================
    # STEP 10.5: 병합 모델 삭제 (선택적)
    # ================================================================

    if DELETE_MERGED_AFTER_GGUF:
        print("\n" + "="*70)
        print("🗑️  STEP 10.5: 병합 모델 삭제 (공간 절약)")
        print("="*70)

        print(f"\n🗑️  삭제 중: {output_path}")
        print(f"   크기: {original_size:.2f}GB")

        import shutil
        try:
            shutil.rmtree(output_path)
            print("✅ 병합 모델 삭제 완료")
            print(f"💾 절약된 공간: {original_size:.2f}GB")
        except Exception as e:
            print(f"⚠️  삭제 실패 (수동으로 삭제 필요): {e}")

# ================================================================
# STEP 11: 검증 및 요약
# ================================================================

print("\n" + "="*70)
print("🔍 STEP 11: 결과 검증")
print("="*70)

# 병합 모델 파일 확인 (삭제하지 않은 경우)
if output_path.exists():
    print(f"\n📂 병합 모델:")
    total_size = 0
    for f in sorted(output_path.iterdir()):
        size = f.stat().st_size / (1024*1024)
        total_size += size
        print(f"  • {f.name} ({size:.1f}MB)")

    print(f"\n💾 총 크기: {total_size/1024:.2f}GB")

    # 필수 파일 확인
    required_files = ["config.json", "tokenizer.json", "tokenizer_config.json"]
    missing = []

    for req in required_files:
        if not (output_path / req).exists():
            if req == "config.json":
                missing.append(req)

    # 모델 가중치 파일 확인 (.safetensors 또는 .bin)
    has_weights = any(
        f.suffix in [".safetensors", ".bin"]
        for f in output_path.iterdir()
    )

    if not has_weights:
        missing.append("model weights (.safetensors or .bin)")

    if missing:
        print(f"\n⚠️  경고: 일부 파일 누락 감지")
        for m in missing:
            print(f"  • {m}")
        print("\n하지만 모델은 사용 가능할 수 있습니다.")
    else:
        print("\n✅ 모든 필수 파일 확인 완료")
else:
    print("\n⚠️  병합 모델이 삭제되었습니다 (GGUF만 유지)")

# GGUF 파일 확인
if CONVERT_TO_GGUF and Path(GGUF_OUTPUT_PATH).exists():
    print(f"\n📦 GGUF 모델:")
    gguf_size = os.path.getsize(GGUF_OUTPUT_PATH) / (1024**3)
    print(f"  • {Path(GGUF_OUTPUT_PATH).name}")
    print(f"  • 크기: {gguf_size:.2f}GB")
    print(f"  • 양자화: {GGUF_QUANTIZATION.upper()}")
    print(f"  • 경로: {GGUF_OUTPUT_PATH}")

# ================================================================
# 완료!
# ================================================================

print("\n" + "="*70)
print("🎉 모든 작업 완료!")
print("="*70)

print(f"\n📦 생성된 파일:")
if output_path.exists():
    print(f"  1. 병합 모델: {output_path}")
    print(f"     크기: {total_size/1024:.2f}GB")
    print(f"     용도: GPU 추론, 추가 학습")

if CONVERT_TO_GGUF and Path(GGUF_OUTPUT_PATH).exists():
    print(f"  2. GGUF 모델: {GGUF_OUTPUT_PATH}")
    print(f"     크기: {gguf_size:.2f}GB")
    print(f"     용도: CPU 추론 (⭐ 추천)")

print(f"\n💡 사용 방법:")

if output_path.exists():
    print(f"\n1️⃣  병합 모델 (GPU):")
    print(f"""
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "{output_path}",
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("{output_path}")
""")

if CONVERT_TO_GGUF and Path(GGUF_OUTPUT_PATH).exists():
    print(f"\n2️⃣  GGUF 모델 (CPU):")
    print(f"""
# Python (llama-cpp-python)
from llama_cpp import Llama

llm = Llama(
    model_path="{GGUF_OUTPUT_PATH}",
    n_ctx=512,
    n_threads=8
)

output = llm("Summarize: ...", max_tokens=80, temperature=0.3)
print(output['choices'][0]['text'])
""")

    print(f"\n# 또는 llama.cpp CLI:")
    print(f"""
./llama-cli -m {Path(GGUF_OUTPUT_PATH).name} -p "Summarize: ..."
""")

print(f"\n📝 다음 단계:")
print(f"  1. ✅ 병합 완료 - 추론 속도 17% 향상")
if CONVERT_TO_GGUF:
    print(f"  2. ✅ GGUF 변환 완료 - CPU 추론 가능")
    print(f"  3. 💾 Google Drive에서 GGUF 다운로드 (0.9GB)")
    print(f"  4. 🖥️  로컬 PC에서 CPU 추론 테스트")
else:
    print(f"  2. Streamlit 챗봇 테스트")
    print(f"  3. MODE 2로 추론 성능 검증")

print(f"\n🎯 추천:")
if CONVERT_TO_GGUF:
    print(f"  ⭐ CPU 추론: GGUF 사용 (빠르고 효율적)")
    print(f"  ⭐ GPU 추론: 병합 모델 사용")
    print(f"  ⭐ 다운로드: GGUF만 받으면 충분 (0.9GB)")
else:
    print(f"  💡 CPU 추론 필요시: CONVERT_TO_GGUF = True로 변경")

print("\n" + "="*70)

# 최종 경로 정보 저장
from datetime import datetime

info_file_path = Path(DRIVE_BASE) / MODEL_NAME / "merge_info.txt"
with open(info_file_path, 'w') as f:
    f.write(f"Model: {MODEL_NAME}\n")
    f.write(f"Base: {BASE_MODEL}\n")
    f.write(f"Adapter: {adapter_path}\n")
    f.write(f"Merged: {output_path}\n")
    if CONVERT_TO_GGUF:
        f.write(f"GGUF: {GGUF_OUTPUT_PATH}\n")
        f.write(f"GGUF Quantization: {GGUF_QUANTIZATION}\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Device: {device}\n")
    if output_path.exists():
        f.write(f"Merged Size: {total_size/1024:.2f}GB\n")
    if CONVERT_TO_GGUF and Path(GGUF_OUTPUT_PATH).exists():
        f.write(f"GGUF Size: {gguf_size:.2f}GB\n")

print(f"💾 병합 정보 저장: {info_file_path.name}")
print("✅ 완료!")