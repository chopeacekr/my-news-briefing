"""
=================================================================
📰 V4.1 - AI 논문 특화 뉴스 브리핑 요약 (환각 방지 강화)
=================================================================

🎯 V4.1 핵심 개선:
✅ AI 논문 특화: 1000개 이상 모드 시 AI 관련 논문만 학습
✅ 타겟: 일반인도 이해 가능한 뉴스 브리핑 스타일
✅ 환각 방지: 초록에 없는 정보 생성 금지
✅ 규격: 1-2문장(최대 45단어)
✅ 자동 데이터 확장: 필요한 만큼 AI 논문 필터링

📊 V4.0 대비 개선:
- AI 논문 자동 필터링 (참조수 + 최신순)
- 유연한 샘플 수 설정 (1000개, 4000개 등)
- 자동 그룹 분할 및 병렬 처리

=================================================================
"""

import subprocess
import sys
import os

print("\n" + "="*60)
print("🚀 V4.1 - AI 논문 특화 뉴스 브리핑 요약")
print("="*60)

# ================================================================
# ⭐⭐⭐ 설정 - 여기만 수정하세요! ⭐⭐⭐
# ================================================================

# 테스트 모드 설정
TEST_MODE = False  # 🔧 True: 테스트, False: 프로덕션

# 테스트 샘플 수 (TEST_MODE = True일 때만 적용)
TEST_SAMPLES = 3  # 🔧 테스트할 샘플 수

# 프로덕션 샘플 수
NUM_OF_NEW_SAMPLE = 1200  # 🔧 생성할 총 샘플 수 (1000, 2000, 4000 등)

# 그룹 설정
GROUP_NUM = 1  # 🔧 총 그룹 수 (디폴트: 4)
GROUP_ID = 1   # 🔧 현재 그룹 ID (1 ~ GROUP_NUM)

# ================================================================
# 입력 검증
# ================================================================

if GROUP_ID < 1 or GROUP_ID > GROUP_NUM:
    raise ValueError(f"❌ GROUP_ID는 1 ~ {GROUP_NUM} 사이여야 합니다! (현재: {GROUP_ID})")

if TEST_SAMPLES < 1:
    raise ValueError(f"❌ TEST_SAMPLES는 1 이상이어야 합니다! (현재: {TEST_SAMPLES})")

if NUM_OF_NEW_SAMPLE < GROUP_NUM:
    raise ValueError(f"❌ NUM_OF_NEW_SAMPLE({NUM_OF_NEW_SAMPLE})은 GROUP_NUM({GROUP_NUM}) 이상이어야 합니다!")

# ================================================================
# 그룹별 설정 자동 계산
# ================================================================

if TEST_MODE:
    print(f"\n⚠️ 테스트 모드: {TEST_SAMPLES}개만 생성합니다.")
    print("   프로덕션: TEST_MODE = False로 변경하세요.\n")
    SAMPLES_PER_GROUP = TEST_SAMPLES
    TOTAL_SAMPLES = TEST_SAMPLES
else:
    SAMPLES_PER_GROUP = NUM_OF_NEW_SAMPLE // GROUP_NUM
    TOTAL_SAMPLES = NUM_OF_NEW_SAMPLE

# AI 논문 필터링 모드 (1000개 이상일 때)
AI_FILTER_MODE = (NUM_OF_NEW_SAMPLE >= 1000 and not TEST_MODE)

# AI 필터링 시 필요한 논문 수 (여유있게 1.5배)
REQUIRED_AI_PAPERS = int(NUM_OF_NEW_SAMPLE * 1.5) if AI_FILTER_MODE else 0

# 그룹별 인덱스 범위 계산
GROUP_CONFIGS = {}
for gid in range(1, GROUP_NUM + 1):
    start_idx = (gid - 1) * SAMPLES_PER_GROUP
    end_idx = start_idx + SAMPLES_PER_GROUP - 1

    GROUP_CONFIGS[gid] = {
        "START_INDEX": start_idx,
        "SAMPLES": SAMPLES_PER_GROUP,
        "END_INDEX": end_idx,
        "OUTPUT_FILE": f"v4.1_training_data_group{gid}_{'test' if TEST_MODE else 'prod'}.csv",
        "PROGRESS_FILE": f"v4.1_progress_group{gid}_{'test' if TEST_MODE else 'prod'}.json"
    }

config = GROUP_CONFIGS[GROUP_ID]

print(f"\n{'='*60}")
print(f"📊 V4.1 설정 정보")
print(f"{'='*60}")
print(f"🎮 모드: {'테스트' if TEST_MODE else '프로덕션'}")
if TEST_MODE:
    print(f"   테스트 샘플: {TEST_SAMPLES}개")
else:
    print(f"   전체 샘플: {NUM_OF_NEW_SAMPLE}개")
    if AI_FILTER_MODE:
        print(f"   🤖 AI 논문 필터링: 활성화")
        print(f"   필요 AI 논문: {REQUIRED_AI_PAPERS}개")
print(f"👥 그룹: {GROUP_ID}/{GROUP_NUM}")
print(f"   그룹당 샘플: {SAMPLES_PER_GROUP}개")
print(f"   인덱스 범위: {config['START_INDEX']} ~ {config['END_INDEX']}")
print(f"📁 출력 파일: {config['OUTPUT_FILE']}")
print(f"{'='*60}")

# ================================================================
# STEP 1: 패키지 설치 (안정화 버전 - 수정 금지)
# ================================================================

print("\n" + "="*60)
print("📦 STEP 1: 패키지 설치")
print("="*60)

print("📥 필수 패키지 설치 중...")
packages = ["datasets", "pandas"]

for pkg in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
                  capture_output=True, check=True)

print("✅ 기본 패키지 설치 완료!")

# ================================================================
# ⚙️ LLM 설정
# ================================================================

print("\n" + "="*60)
print("⚙️ LLM 설정")
print("="*60)

# LLM 선택
LLM_MODE = 1  # 0: OpenAI, 1: Gemini, 2: Claude

LLM_NAMES = {
    0: "OpenAI GPT-4o-mini",
    1: "Google Gemini",
    2: "Anthropic Claude"
}

LLM_SECRET_NAMES = {
    0: "OPENAI_API_KEY",
    1: "GEMINI_API_KEY",
    2: "ANTHROPIC_API_KEY"
}

print(f"🤖 선택된 LLM: {LLM_NAMES[LLM_MODE]}")

# LLM 패키지 설치
llm_packages = {
    0: ["openai"],
    1: ["google-generativeai"],
    2: ["anthropic"]
}

print(f"📥 {LLM_NAMES[LLM_MODE]} 패키지 설치 중...")
for pkg in llm_packages[LLM_MODE]:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
                  capture_output=True, check=True)
print("✅ LLM 패키지 설치 완료!")

# ================================================================
# STEP 2: Import 및 설정
# ================================================================

print("\n" + "="*60)
print("📚 STEP 2: Import 및 초기 설정")
print("="*60)

import pandas as pd
import json
import re
import time
from pathlib import Path
from datetime import datetime
from datasets import load_dataset
from google.colab import drive, userdata

# LLM 클라이언트 Import
if LLM_MODE == 0:
    from openai import OpenAI
    print("✅ OpenAI Import 완료")
elif LLM_MODE == 1:
    import google.generativeai as genai
    print("✅ Gemini Import 완료")
elif LLM_MODE == 2:
    from anthropic import Anthropic
    print("✅ Claude Import 완료")

# Drive 마운트
print("\n💾 Drive 마운트...")
if not Path("/content/drive").exists():
    drive.mount('/content/drive')
print("✅ 마운트 완료")

# 출력 디렉토리 설정
OUTPUT_DIR = "/content/drive/MyDrive/SummaryDataSet"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
print(f"✅ 출력 디렉토리: {OUTPUT_DIR}")

# AI 필터링 데이터 경로 (샘플 수에 따라 다른 파일)
AI_FILTERED_DATA_PATH = Path(OUTPUT_DIR) / f"AI_DATA_V4.1_{REQUIRED_AI_PAPERS}.csv"

# ================================================================
# API 키 설정
# ================================================================

print("\n" + "="*60)
print("🔑 API 키 설정")
print("="*60)

def get_api_key(key_name):
    """Colab Secrets에서 API 키 가져오기"""
    try:
        key = userdata.get(key_name)
        if key and len(key.strip()) > 0:
            return key.strip()
        return None
    except Exception as e:
        return None

SECRET_NAME = LLM_SECRET_NAMES[LLM_MODE]
API_KEY = get_api_key(SECRET_NAME)

if API_KEY:
    print(f"✅ {LLM_NAMES[LLM_MODE]} API 키: 설정됨 ({API_KEY[:10]}...)")
else:
    print(f"❌ {LLM_NAMES[LLM_MODE]} API 키: 없음")
    print(f"\n📝 Colab Secrets에 {SECRET_NAME} 추가 필요")
    raise ValueError(f"{LLM_NAMES[LLM_MODE]} API 키를 설정해주세요!")

# ================================================================
# 모델 설정
# ================================================================

MODEL_CONFIGS = {
    0: {
        "model": "gpt-4o-mini",
        "rpm": 3,
        "rpd": 200,
        "sleep": 21,
    },
    1: {
        "model": "models/gemma-3-27b-it",
        "rpm": 15,
        "rpd": 1500,
        "sleep": 5,
    },
    2: {
        "model": "claude-3-5-haiku-20241022",
        "rpm": 50,
        "rpd": 5000,
        "sleep": 2,
    }
}

current_config = MODEL_CONFIGS[LLM_MODE]

# ================================================================
# 🔥 V4.1 프롬프트 설정
# ================================================================

USER_PROMPT_V4_1 = """Summarize the following text in simple, clear English that anyone can understand. Use no more than two complete sentences.

{abstract}"""

# ================================================================
# 설정 요약
# ================================================================

print(f"\n{'='*60}")
print("📊 V4.1 설정 요약")
print(f"{'='*60}")
print(f"🎮 모드: {'테스트 (' + str(TEST_SAMPLES) + '개)' if TEST_MODE else '프로덕션 (' + str(NUM_OF_NEW_SAMPLE) + '개)'}")
print(f"👥 그룹: {GROUP_ID}/{GROUP_NUM}")
print(f"   샘플: {SAMPLES_PER_GROUP}개")
if AI_FILTER_MODE:
    print(f"🤖 AI 논문 필터링: 활성화")
    print(f"   필요 논문: {REQUIRED_AI_PAPERS}개")
print(f"🤖 LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   모델: {current_config['model']}")
print(f"   요청 간격: {current_config['sleep']}초")
print(f"   예상 시간: ~{SAMPLES_PER_GROUP * current_config['sleep'] / 60:.1f}분")
print(f"{'='*60}")

# ================================================================
# STEP 3: AI 논문 필터링 (1000개 이상 모드일 때만)
# ================================================================

if AI_FILTER_MODE:
    print("\n" + "="*60)
    print("🤖 STEP 3: AI 논문 필터링")
    print("="*60)

    if AI_FILTERED_DATA_PATH.exists():
        print(f"✅ 기존 AI 필터링 데이터 발견: {AI_FILTERED_DATA_PATH}")
        ai_papers_df = pd.read_csv(AI_FILTERED_DATA_PATH)
        print(f"   로드 완료: {len(ai_papers_df)}개")

        # 필요한 만큼 있는지 확인
        if len(ai_papers_df) < NUM_OF_NEW_SAMPLE:
            print(f"\n⚠️ 데이터 부족: {len(ai_papers_df)}개 < {NUM_OF_NEW_SAMPLE}개 필요")
            print(f"   추가 필터링을 진행합니다...")
            ai_papers_df = None  # 재생성
        else:
            print(f"✅ 충분한 데이터 확보: {len(ai_papers_df)}개 >= {NUM_OF_NEW_SAMPLE}개")
    else:
        ai_papers_df = None

    if ai_papers_df is None:
        print("\n📥 ArXiv 전체 데이터셋 로딩 중...")
        print("   (시간이 걸릴 수 있습니다...)")

        # 전체 데이터셋 로드
        full_dataset = load_dataset("ccdv/arxiv-summarization", split="train")
        print(f"✅ 전체 {len(full_dataset)}개 로드 완료")

        print(f"\n🔍 AI 관련 논문 필터링 중 (목표: {REQUIRED_AI_PAPERS}개)...")

        # AI 관련 키워드
        ai_keywords = [
            'machine learning', 'deep learning', 'neural network',
            'artificial intelligence', 'natural language processing',
            'computer vision', 'reinforcement learning', 'transformer',
            'attention mechanism', 'generative model', 'llm', 'gpt',
            'bert', 'diffusion model', 'gan', 'vae', 'autoencoder',
            'classification', 'regression', 'supervised learning',
            'unsupervised learning', 'semi-supervised', 'transfer learning',
            'fine-tuning', 'prompt engineering', 'embedding', 'convolution',
            'recurrent', 'lstm', 'gru', 'optimization', 'gradient descent',
            'backpropagation', 'activation function', 'dropout', 'batch norm'
        ]

        ai_papers = []

        for idx, item in enumerate(full_dataset):
            if idx % 10000 == 0:
                print(f"   진행: {idx}/{len(full_dataset)} ({idx/len(full_dataset)*100:.1f}%) - 발견: {len(ai_papers)}개")

            abstract_lower = item['abstract'].lower()

            # AI 관련 키워드 체크
            is_ai = any(keyword in abstract_lower for keyword in ai_keywords)

            if is_ai:
                # 참조수 추출
                cite_count = item['article'].count('@xcite')

                ai_papers.append({
                    'index': idx,
                    'article': item['article'],
                    'abstract': item['abstract'],
                    'cite_count': cite_count
                })

                # 충분히 모았으면 조기 종료 (효율성)
                if len(ai_papers) >= REQUIRED_AI_PAPERS * 2:
                    print(f"\n✅ 충분한 AI 논문 발견: {len(ai_papers)}개")
                    break

        print(f"\n✅ AI 논문 필터링 완료: {len(ai_papers)}개")

        if len(ai_papers) < REQUIRED_AI_PAPERS:
            print(f"\n⚠️ 경고: 발견된 AI 논문({len(ai_papers)}개)이 목표({REQUIRED_AI_PAPERS}개)보다 적습니다.")
            print(f"   가능한 범위 내에서 진행합니다.")
            REQUIRED_AI_PAPERS = len(ai_papers)

        # 참조수 기반 정렬 (최신순 + 인기순)
        print("📊 참조수 기반 정렬 중...")

        # 정렬: 인덱스 높을수록 최신(30%), 참조수 많을수록 인기(70%)
        ai_papers_sorted = sorted(
            ai_papers,
            key=lambda x: (x['index'] * 0.3 + x['cite_count'] * 0.7),
            reverse=True
        )

        print(f"✅ 정렬 완료")

        # 상위 N개 선택
        top_ai_papers = ai_papers_sorted[:REQUIRED_AI_PAPERS]

        # 데이터프레임으로 저장
        ai_papers_df = pd.DataFrame(top_ai_papers)
        ai_papers_df.to_csv(AI_FILTERED_DATA_PATH, index=False, encoding='utf-8')

        print(f"\n💾 AI 논문 데이터 저장 완료")
        print(f"   파일: {AI_FILTERED_DATA_PATH}")
        print(f"   개수: {len(ai_papers_df)}개")
        print(f"\n📊 참조수 통계:")
        print(f"   평균: {ai_papers_df['cite_count'].mean():.1f}")
        print(f"   최대: {ai_papers_df['cite_count'].max()}")
        print(f"   최소: {ai_papers_df['cite_count'].min()}")
        print(f"   중앙값: {ai_papers_df['cite_count'].median():.1f}")

# ================================================================
# STEP 4: 기존 데이터 확인
# ================================================================

print("\n" + "="*60)
print("📂 STEP 4: 기존 데이터 확인")
print("="*60)

data_path = Path(OUTPUT_DIR) / config['OUTPUT_FILE']
progress_path = Path(OUTPUT_DIR) / config['PROGRESS_FILE']

existing_data = []
current_progress = 0

if data_path.exists():
    print(f"✅ 기존 데이터 발견: {data_path}")
    existing_df = pd.read_csv(data_path)
    existing_data = existing_df.to_dict('records')
    current_progress = len(existing_data)

    print(f"   기존 샘플 수: {current_progress}개")

    if current_progress >= SAMPLES_PER_GROUP:
        print(f"\n✅ 이미 할당된 범위를 모두 완료했습니다!")
        print(f"   완료: {current_progress}/{SAMPLES_PER_GROUP}")
        sys.exit(0)
else:
    print("ℹ️ 기존 데이터 없음 - 새로 시작")

remaining_samples = SAMPLES_PER_GROUP - current_progress
print(f"\n  목표: {SAMPLES_PER_GROUP}개")
print(f"  완료: {current_progress}개")
print(f"  남은: {remaining_samples}개")

# ================================================================
# STEP 5: ArXiv 데이터 로드
# ================================================================

print("\n" + "="*60)
print("📥 STEP 5: ArXiv 데이터 로드")
print("="*60)

def clean_arxiv_text_v4(text):
    """V4.1 강화 전처리"""

    if not isinstance(text, str):
        return ""

    if len(text) > 1500:
        text = text[:1500]

    text = re.sub(r'#\s*\d+\s*#\s*\d+', '', text)
    text = re.sub(r'_\s*mem\s*\.\s*soc\s*\.', '', text)
    text = re.sub(r'\*\s*#\s*\d+\s*\*', '', text)
    text = re.sub(r'_\s*\w+\s*\.\s*\w+\s*\.', '', text)

    text = re.sub(r'@xmath\d+', '', text)
    text = re.sub(r'@xcite', '', text)
    text = re.sub(r'@xref', '', text)
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)

    text = re.sub(r'[#_*]{2,}', '', text)
    text = re.sub(r'[\.\s]{3,}', '. ', text)

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r'--+', '-', text)

    return text.strip()

def validate_abstract_v4(text):
    """V4.1 초록 검증"""

    metadata_patterns = [
        r'#\s*\d+\s*#',
        r'_\s*mem\s*\.\s*soc',
        r'astron\s*\.\s*it\s*\.',
        r'\*\s*#\s*\d+',
        r'publ\s*\.\s*astron'
    ]

    for pattern in metadata_patterns:
        if re.search(pattern, text):
            return False, "Metadata detected"

    words = text.split()
    if len(words) < 30:
        return False, f"Too short: {len(words)} words"
    if len(words) > 500:
        return False, f"Too long: {len(words)} words"

    if text.count('.') < 2:
        return False, "Not enough sentences"

    return True, "Valid"

# 데이터 로드
if AI_FILTER_MODE:
    print(f"🤖 AI 필터링 데이터에서 로드")
    print(f"   그룹 {GROUP_ID} 범위: {config['START_INDEX']} ~ {config['END_INDEX']}")

    # AI 필터링 데이터에서 해당 그룹 범위 추출
    group_data = ai_papers_df.iloc[config['START_INDEX']:config['END_INDEX']+1]

    # 이미 완료된 만큼 건너뛰기
    if current_progress > 0:
        group_data = group_data.iloc[current_progress:]

    print(f"✅ {len(group_data)}개 로드 완료")

    print("🔄 전처리 중...")
    processed_dataset = []
    skipped = 0

    for _, row in group_data.iterrows():
        cleaned_abstract = clean_arxiv_text_v4(row['abstract'])
        is_valid, msg = validate_abstract_v4(cleaned_abstract)

        if is_valid:
            processed_dataset.append({
                'article': clean_arxiv_text_v4(row['article']),
                'abstract': cleaned_abstract,
                'original_index': row['index'],
                'cite_count': row['cite_count']
            })
        else:
            skipped += 1

    print(f"✅ 전처리 완료")
    print(f"   유효: {len(processed_dataset)}개")
    if skipped > 0:
        print(f"   건너뜀: {skipped}개")

else:
    print(f"📥 일반 ArXiv 데이터에서 로드")

    # 그룹 시작 인덱스 계산
    base_start = 2000
    group_start = base_start + config['START_INDEX'] + current_progress
    group_end = group_start + remaining_samples

    print(f"   범위: {group_start} ~ {group_end-1}")

    dataset = load_dataset(
        "ccdv/arxiv-summarization",
        split=f"train[{group_start}:{group_end}]"
    )

    print(f"✅ {len(dataset)}개 로드 완료")

    print("🔄 전처리 중...")
    processed_dataset = []
    skipped = 0

    for item in dataset:
        cleaned_abstract = clean_arxiv_text_v4(item['abstract'])
        is_valid, msg = validate_abstract_v4(cleaned_abstract)

        if is_valid:
            processed_dataset.append({
                'article': clean_arxiv_text_v4(item['article']),
                'abstract': cleaned_abstract
            })
        else:
            skipped += 1

    print(f"✅ 전처리 완료")
    print(f"   유효: {len(processed_dataset)}개")
    if skipped > 0:
        print(f"   건너뜀: {skipped}개")

# ================================================================
# STEP 6: LLM 클라이언트 초기화
# ================================================================

print("\n" + "="*60)
print("🤖 STEP 6: LLM 클라이언트 초기화")
print("="*60)

try:
    if LLM_MODE == 0:
        client = OpenAI(api_key=API_KEY)
        test_response = client.models.list()
        print(f"✅ OpenAI 클라이언트 초기화 완료")

    elif LLM_MODE == 1:
        genai.configure(api_key=API_KEY)

        models_to_try = [
            'models/gemma-3-27b-it',
            'models/gemini-2.5-flash',
            'models/gemini-2.0-flash',
            'models/gemini-2.5-pro'
        ]

        client = None
        for model_attempt in models_to_try:
            try:
                print(f"  시도: {model_attempt}")
                test_client = genai.GenerativeModel(model_attempt)
                test_response = test_client.generate_content(
                    "Say OK",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1,
                    )
                )
                client = test_client
                current_config['model'] = model_attempt
                print(f"✅ Gemini 클라이언트 초기화 완료: {model_attempt}")
                break
            except Exception as e:
                print(f"   ❌ 실패: {str(e)[:100]}")
                continue

        if client is None:
            raise Exception("사용 가능한 Gemini 모델을 찾을 수 없습니다.")

    elif LLM_MODE == 2:
        client = Anthropic(api_key=API_KEY)
        print(f"✅ Claude 클라이언트 초기화 완료")

    print(f"   속도 제한: {current_config['rpm']} RPM")
    print(f"   요청 간격: {current_config['sleep']}초")

except Exception as e:
    print(f"\n❌ 클라이언트 초기화 실패: {str(e)}")
    raise

# ================================================================
# STEP 7: 요약 생성 함수
# ================================================================

def count_sentences(text):
    """문장 수 카운트"""
    sentences = re.split(r'[.!?]+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)

def count_words(text):
    """단어 수 카운트"""
    return len(text.split())

def detect_hallucination_v4(summary, abstract):
    """V4.1 환각 감지"""

    summary_numbers = re.findall(r'\d+\.?\d*%?', summary)
    abstract_numbers = re.findall(r'\d+\.?\d*%?', abstract)

    for num in summary_numbers:
        if num not in abstract_numbers:
            return True, f"Unverified number: {num}"

    hallucination_keywords = [
        'approximately', 'around', '~',
        'roughly', 'nearly', 'almost'
    ]

    for keyword in hallucination_keywords:
        if keyword in summary.lower():
            if keyword not in abstract.lower():
                return True, f"Hallucination keyword: {keyword}"

    return False, "OK"

def generate_summary_gemini_v4(abstract, client, retry_count=3):
    """Gemini V4.1 요약 생성"""

    for attempt in range(retry_count):
        try:
            prompt = USER_PROMPT_V4_1.format(abstract=abstract)

            response = client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=100,
                    top_p=0.9,
                    top_k=40,
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )

            if not response.text:
                print(f"    ⚠️ 빈 응답, 재시도...")
                time.sleep(2)
                continue

            summary = response.text.strip()
            word_count = count_words(summary)
            sentence_count = count_sentences(summary)

            if word_count > 60 or sentence_count > 3:
                print(f"    ⚠️ 재시도 (단어:{word_count}, 문장:{sentence_count})")
                continue

            is_hallucination, hall_msg = detect_hallucination_v4(summary, abstract)
            if is_hallucination:
                print(f"    ⚠️ 환각 감지: {hall_msg}, 재시도...")
                continue

            return {
                'summary': summary,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'success': True
            }

        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ 오류 (시도 {attempt+1}/{retry_count}): {error_msg[:200]}")

            if "quota" in error_msg.lower() or "429" in error_msg:
                print(f"    ⏳ Quota 제한! 60초 대기...")
                time.sleep(60)
                continue

            if "api key" in error_msg.lower() or "401" in error_msg:
                return {'summary': None, 'word_count': 0, 'sentence_count': 0,
                       'success': False, 'error': 'API key error'}

            if attempt < retry_count - 1:
                time.sleep(5)

    return {'summary': None, 'word_count': 0, 'sentence_count': 0,
            'success': False, 'error': 'Max retries reached'}

generate_summary = generate_summary_gemini_v4

# ================================================================
# STEP 8: 배치 처리
# ================================================================

print("\n" + "="*60)
print(f"🔄 STEP 8: V4.1 요약 생성 시작")
print("="*60)

print(f"\n⚠️ V4.1 설정:")
print(f"   - 그룹: {GROUP_ID}/{GROUP_NUM}")
if AI_FILTER_MODE:
    print(f"   - 데이터: AI 논문 특화")
else:
    print(f"   - 데이터: 일반 ArXiv")
print(f"   - LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   - 요청 간격: {current_config['sleep']}초")
print(f"   - 예상 시간: ~{len(processed_dataset) * current_config['sleep'] / 60:.1f}분")
print(f"\n생성: {len(processed_dataset)}개")
print()

def save_progress(data, completed, total):
    """진행 상황 저장"""
    df = pd.DataFrame(data)
    df.to_csv(data_path, index=False, encoding='utf-8')

    progress = {
        'group_id': GROUP_ID,
        'group_num': GROUP_NUM,
        'version': 'V4.1',
        'test_mode': TEST_MODE,
        'ai_filter_mode': AI_FILTER_MODE,
        'total_samples': NUM_OF_NEW_SAMPLE,
        'completed': completed,
        'total': total,
        'llm_mode': LLM_MODE,
        'llm_name': LLM_NAMES[LLM_MODE],
        'model': current_config['model'],
        'last_update': datetime.now().isoformat(),
        'success_rate': sum(1 for d in data if d.get('llm_success', False)) / len(data) if data else 0
    }
    with open(progress_path, 'w') as f:
        json.dump(progress, f, indent=2)

stats = {
    'total': len(processed_dataset),
    'completed': 0,
    'success': 0,
    'failed': 0,
    'avg_words': 0,
    'avg_sentences': 0
}

new_data = []
start_time = time.time()

print("="*60)
print("🚀 V4.1 생성 시작!")
print("="*60)

try:
    for idx, paper in enumerate(processed_dataset):
        current = idx + 1
        progress_pct = (current / len(processed_dataset)) * 100

        paper_idx = paper.get('original_index', config['START_INDEX'] + current_progress + idx)
        cite_count = paper.get('cite_count', 0)

        print(f"\n[{current}/{len(processed_dataset)}] ({progress_pct:.1f}%) 논문 인덱스 {paper_idx}")
        if AI_FILTER_MODE:
            print(f"  참조수: {cite_count}")
        print(f"  초록: {count_words(paper['abstract'])}단어")

        result = generate_summary(paper['abstract'], client)

        if result['success']:
            stats['success'] += 1
            print(f"  ✅ 성공: {result['word_count']}단어, {result['sentence_count']}문장")
            print(f"     \"{result['summary']}...\"")

            new_data.append({
                'index': paper_idx,
                'article': paper['article'],
                'original_abstract': paper['abstract'],
                'original_words': count_words(paper['abstract']),
                'original_sentences': count_sentences(paper['abstract']),
                'llm_summary': result['summary'],
                'llm_words': result['word_count'],
                'llm_sentences': result['sentence_count'],
                'llm_mode': LLM_MODE,
                'llm_name': LLM_NAMES[LLM_MODE],
                'llm_model': current_config['model'],
                'llm_success': True,
                'llm_version': 'V4.1',
                'group_id': GROUP_ID,
                'group_num': GROUP_NUM,
                'test_mode': TEST_MODE,
                'ai_filter_mode': AI_FILTER_MODE,
                'cite_count': cite_count if AI_FILTER_MODE else 0,
                'created_at': datetime.now().isoformat()
            })

            stats['avg_words'] += result['word_count']
            stats['avg_sentences'] += result['sentence_count']
        else:
            stats['failed'] += 1
            error_msg = result.get('error', 'Unknown')
            print(f"  ❌ 실패: {error_msg}")

            if error_msg in ['API key error', 'Quota exceeded']:
                print(f"\n⛔ 치명적 오류! 중단합니다.")
                break

        stats['completed'] += 1

        if not TEST_MODE and stats['success'] > 0 and stats['success'] % 10 == 0:
            all_data = existing_data + new_data
            save_progress(all_data, len(all_data), SAMPLES_PER_GROUP)

            elapsed = time.time() - start_time
            rate = stats['completed'] / elapsed * 60
            remaining = (len(processed_dataset) - stats['completed']) / rate if rate > 0 else 0

            print(f"\n  📊 중간 통계:")
            print(f"     처리: {stats['completed']}/{len(processed_dataset)}")
            print(f"     성공: {stats['success']}개")
            if stats['success'] > 0:
                print(f"     평균: {stats['avg_words']/stats['success']:.1f}단어")
            print(f"     남은 시간: ~{remaining:.0f}분")
            print(f"  💾 중간 저장 완료")

        if current < len(processed_dataset):
            time.sleep(current_config['sleep'])

except KeyboardInterrupt:
    print("\n\n⚠️ 사용자 중단!")
    if new_data:
        all_data = existing_data + new_data
        save_progress(all_data, len(all_data), SAMPLES_PER_GROUP)
        print(f"✅ 진행 저장 완료!")
    sys.exit(0)

# ================================================================
# STEP 9: 최종 저장 및 통계
# ================================================================

print("\n" + "="*60)
print("💾 STEP 9: 최종 저장")
print("="*60)

all_data = existing_data + new_data
save_progress(all_data, len(all_data), SAMPLES_PER_GROUP)

elapsed = time.time() - start_time

print(f"\n✅ 완료!")
print(f"\n📊 최종 통계:")
print(f"{'='*60}")
print(f"버전: V4.1")
print(f"모드: {'테스트' if TEST_MODE else '프로덕션'}")
print(f"그룹: {GROUP_ID}/{GROUP_NUM}")
if AI_FILTER_MODE:
    print(f"데이터: AI 논문 특화 ({NUM_OF_NEW_SAMPLE}개)")
print(f"LLM: {LLM_NAMES[LLM_MODE]}")
print(f"모델: {current_config['model']}")
print(f"처리: {stats['completed']}개")
print(f"성공: {stats['success']}개 ({stats['success']/stats['completed']*100:.1f}%)")
print(f"실패: {stats['failed']}개")
if stats['success'] > 0:
    print(f"평균: {stats['avg_words']/stats['success']:.1f}단어, {stats['avg_sentences']/stats['success']:.1f}문장")
print(f"소요: {elapsed/60:.1f}분")
print(f"{'='*60}")

print(f"\n📁 저장 위치:")
print(f"  파일: {data_path}")
print(f"  행 수: {len(all_data)}개")

if new_data:
    print(f"\n📊 V4.1 샘플:")
    print(f"{'='*60}")
    for i, sample in enumerate(new_data[:3], 1):
        print(f"\n[샘플 {i}] 논문 {sample['index']}")
        if AI_FILTER_MODE:
            print(f"참조수: {sample.get('cite_count', 0)}")
        print(f"원본: {sample['original_words']}단어")
        print(f"요약: {sample['llm_words']}단어, {sample['llm_sentences']}문장")
        print(f"\n\"{sample['llm_summary']}\"")
        print("-"*60)

print("\n" + "="*60)
if TEST_MODE:
    print("🎉 테스트 완료!")
    print("="*60)
    print("\n💡 다음 단계:")
    print("  1. 위 샘플들을 확인하세요")
    print("  2. 품질이 좋으면:")
    print("     TEST_MODE = False")
    print("     로 변경 후 생성")
else:
    print(f"🎉 그룹 {GROUP_ID} V4.1 완료!")
    print("="*60)
    if AI_FILTER_MODE:
        print(f"\n✨ AI 논문 특화 데이터 생성 완료! ({NUM_OF_NEW_SAMPLE}개)")
    print(f"\n💡 다음 단계:")
    if GROUP_ID < GROUP_NUM:
        print(f"  다른 그룹({GROUP_ID+1}~{GROUP_NUM})도 완료 후 병합하세요")
    else:
        print(f"  모든 그룹 완료! 데이터 병합 가능")
print("="*60)