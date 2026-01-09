"""
=================================================================
📰 V4.2 - 뉴스 브리핑용 논문 요약 (환각 방지 강화)
=================================================================

🎯 V4 핵심 개선:
✅ 타겟: 일반인도 이해 가능한 뉴스 브리핑 스타일
✅ 환각 방지: 초록에 없는 정보 생성 금지
✅ 규격: 1-2문장, 최대 45단어
✅ 데이터량: 3개 (테스트) → 2000개로 변경 가능

📊 V3 대비 개선:
- 환각 방지 프롬프트 강화
- 일반인 친화적 표현
- 전처리 강화 (긴 초록 대응)
- GROUP_ID=0으로 2000개 통합 생성 가능

=================================================================
"""

import subprocess
import sys
import os

print("\n" + "="*60)
print("🚀 STEP 0.5 V4 - 뉴스 브리핑용 요약 (환각 방지)")
print("="*60)

# ================================================================
# ⭐⭐⭐ 버전 설정 - 여기만 수정하세요! ⭐⭐⭐
# ================================================================

VERSION = "v4.2"  # 🔧 버전 번호 (v4.0, v4.1, v4.2 등)

# ================================================================
# ⭐⭐⭐ 그룹 설정 - 여기만 수정하세요! ⭐⭐⭐
# ================================================================

GROUP_ID = 0  # 🔧 0: 전체 2000개, 1/2/3/4: 각 250개씩

# ================================================================
# 테스트/프로덕션 모드 설정
# ================================================================

TEST_MODE = False  # 🔧 True: 3개 테스트, False: 전체 생성

# ================================================================
# 그룹별 설정 (자동 적용)
# ================================================================

if TEST_MODE:
    print("\n⚠️ 테스트 모드: 3개만 생성합니다.")
    print("   프로덕션: TEST_MODE = False로 변경하세요.\n")

GROUP_CONFIGS = {
    0: {  # 전체 생성 모드 (2000개)
        "START_INDEX": 3100,
        "NEW_SAMPLES": 3 if TEST_MODE else 1700,
        "MAX_INDEX": 2002 if TEST_MODE else 4999,
        "OUTPUT_FILE": f"{VERSION}_training_data_test.csv" if TEST_MODE else f"{VERSION}_training_data_all.csv",
        "PROGRESS_FILE": f"{VERSION}_progress_test.json" if TEST_MODE else f"{VERSION}_progress_all.json"
    },
    1: {  # 그룹 1 (500개)
        "START_INDEX": 2000,
        "NEW_SAMPLES": 3 if TEST_MODE else 500,
        "MAX_INDEX": 2002 if TEST_MODE else 2499,
        "OUTPUT_FILE": f"{VERSION}_training_data_group1_test.csv" if TEST_MODE else f"{VERSION}_training_data_group1.csv",
        "PROGRESS_FILE": f"{VERSION}_progress_group1_test.json" if TEST_MODE else f"{VERSION}_progress_group1.json"
    },
    2: {  # 그룹 2 (500개)
        "START_INDEX": 2500,
        "NEW_SAMPLES": 3 if TEST_MODE else 500,
        "MAX_INDEX": 2502 if TEST_MODE else 2999,
        "OUTPUT_FILE": f"{VERSION}_training_data_group2_test.csv" if TEST_MODE else f"{VERSION}_training_data_group2.csv",
        "PROGRESS_FILE": f"{VERSION}_progress_group2_test.json" if TEST_MODE else f"{VERSION}_progress_group2.json"
    },
    3: {  # 그룹 3 (500개)
        "START_INDEX": 3000,
        "NEW_SAMPLES": 3 if TEST_MODE else 500,
        "MAX_INDEX": 3002 if TEST_MODE else 3499,
        "OUTPUT_FILE": f"{VERSION}_training_data_group3_test.csv" if TEST_MODE else f"{VERSION}_training_data_group3.csv",
        "PROGRESS_FILE": f"{VERSION}_progress_group3_test.json" if TEST_MODE else f"{VERSION}_progress_group3.json"
    },
    4: {  # 그룹 4 (500개)
        "START_INDEX": 3500,
        "NEW_SAMPLES": 3 if TEST_MODE else 500,
        "MAX_INDEX": 3502 if TEST_MODE else 3999,
        "OUTPUT_FILE": f"{VERSION}_training_data_group4_test.csv" if TEST_MODE else f"{VERSION}_training_data_group4.csv",
        "PROGRESS_FILE": f"{VERSION}_progress_group4_test.json" if TEST_MODE else f"{VERSION}_progress_group4.json"
    }
}

# 그룹 설정 적용
if GROUP_ID not in GROUP_CONFIGS:
    raise ValueError(f"❌ 잘못된 GROUP_ID: {GROUP_ID}. 0, 1, 2, 3, 4 중 선택하세요!")

config = GROUP_CONFIGS[GROUP_ID]
FIXED_START_INDEX = config['START_INDEX']
NEW_SAMPLES = config['NEW_SAMPLES']
MAX_INDEX = config['MAX_INDEX']
DATA_FILE = config['OUTPUT_FILE']
PROGRESS_FILE = config['PROGRESS_FILE']

if GROUP_ID == 0:
    print(f"\n🎯 통합 생성 모드 (GROUP_ID = 0)")
    print(f"   한 사람이 전체를 생성합니다.")
else:
    print(f"\n🎯 그룹 {GROUP_ID} 병렬 모드")

print(f"   인덱스 범위: {FIXED_START_INDEX} ~ {MAX_INDEX}")
print(f"   생성 목표: {NEW_SAMPLES}개")
print(f"   출력 파일: {DATA_FILE}")
print("="*60)

# ================================================================
# STEP 1: 패키지 설치
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
# 🔥 V4 프롬프트 설정 (단순하고 명확하게)
# ================================================================

# V4 User Prompt: 매우 단순하고 직접적
USER_PROMPT_V4 = """Summarize the following text in simple, clear English that anyone can understand. Make it as for the each script not for reading. Use no more than two complete sentences. Do not include my prompt message in result. Make sure to keep in professional tone.

{abstract}"""

# ================================================================
# 설정 요약
# ================================================================

print(f"\n{'='*60}")
print("📊 V4 설정")
print(f"{'='*60}")
print(f"🎮 모드: {'테스트 (3개)' if TEST_MODE else '프로덕션 (2000개)'}")
if GROUP_ID == 0:
    print(f"👥 그룹: 통합 모드 (한 사람이 전체 생성)")
else:
    print(f"👥 그룹: {GROUP_ID} (병렬 처리)")
print(f"🤖 LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   모델: {current_config['model']}")
print(f"   RPM: {current_config['rpm']}")
print(f"   요청 간격: {current_config['sleep']}초")
print()
print(f"📊 데이터:")
print(f"   인덱스 범위: {FIXED_START_INDEX} ~ {MAX_INDEX}")
print(f"   생성 목표: {NEW_SAMPLES}개")
print(f"   예상 시간: ~{NEW_SAMPLES * current_config['sleep'] / 60:.1f}분")
print()
print(f"✨ V4 특징:")
print(f"   - 매우 단순하고 명확한 프롬프트")
print(f"   - 일반인도 이해 가능한 언어")
print(f"   - 최대 2문장 (45단어 이하)")
print(f"   - 환각 방지 강화")
print(f"{'='*60}")

# ================================================================
# STEP 3: 기존 데이터 확인
# ================================================================

print("\n" + "="*60)
print("📂 STEP 3: 기존 데이터 확인")
print("="*60)

data_path = Path(OUTPUT_DIR) / DATA_FILE
progress_path = Path(OUTPUT_DIR) / PROGRESS_FILE

existing_data = []
START_INDEX = FIXED_START_INDEX

if data_path.exists():
    print(f"✅ 기존 데이터 발견: {data_path}")
    existing_df = pd.read_csv(data_path)
    existing_data = existing_df.to_dict('records')
    
    if 'index' in existing_df.columns and len(existing_df) > 0:
        last_index = existing_df['index'].max()
        START_INDEX = last_index + 1
        print(f"  기존 샘플 수: {len(existing_data)}개")
        print(f"  마지막 인덱스: {last_index}")
        print(f"  다음 시작 인덱스: {START_INDEX}")
        
        if START_INDEX > MAX_INDEX:
            print(f"\n✅ 이미 할당된 범위를 모두 완료했습니다!")
            print(f"   현재 인덱스: {START_INDEX}")
            print(f"   최대 인덱스: {MAX_INDEX}")
            sys.exit(0)
    else:
        START_INDEX = FIXED_START_INDEX
else:
    print("ℹ️ 기존 데이터 없음 - 새로 시작")
    START_INDEX = FIXED_START_INDEX
    print(f"  시작 인덱스: {START_INDEX}")

available_count = MAX_INDEX - START_INDEX + 1
actual_samples = min(NEW_SAMPLES, available_count)

if actual_samples < NEW_SAMPLES:
    print(f"\n⚠️ 범위 조정:")
    print(f"   요청: {NEW_SAMPLES}개")
    print(f"   가능: {available_count}개")
    print(f"   실제 생성: {actual_samples}개")
    NEW_SAMPLES = actual_samples

print(f"\n  목표: {START_INDEX} ~ {START_INDEX + NEW_SAMPLES - 1} ({NEW_SAMPLES}개)")

# ================================================================
# STEP 4: ArXiv 데이터 로드 (강화된 전처리)
# ================================================================

print("\n" + "="*60)
print("📥 STEP 4: ArXiv 데이터 로드 (V4 전처리)")
print("="*60)

def clean_arxiv_text_v4(text):
    """V4 강화 전처리 - Test 3 실패 방지"""
    
    if not isinstance(text, str):
        return ""
    
    # 1. 길이 제한 (처음 1500자만 사용)
    if len(text) > 1500:
        text = text[:1500]
    
    # 2. 참고문헌 패턴 제거
    text = re.sub(r'#\s*\d+\s*#\s*\d+', '', text)
    text = re.sub(r'_\s*mem\s*\.\s*soc\s*\.', '', text)
    text = re.sub(r'\*\s*#\s*\d+\s*\*', '', text)
    text = re.sub(r'_\s*\w+\s*\.\s*\w+\s*\.', '', text)
    
    # 3. LaTeX 수식 제거
    text = re.sub(r'@xmath\d+', '', text)
    text = re.sub(r'@xcite', '', text)
    text = re.sub(r'@xref', '', text)
    text = re.sub(r'\$.*?\$', '', text)
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)
    
    # 4. 연속 특수문자 제거
    text = re.sub(r'[#_*]{2,}', '', text)
    text = re.sub(r'[\.\s]{3,}', '. ', text)
    
    # 5. 공백 정규화
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\.+', '.', text)
    text = re.sub(r'--+', '-', text)
    
    return text.strip()

def validate_abstract_v4(text):
    """V4 초록 검증"""
    
    # 메타데이터 패턴 감지
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

end_index = START_INDEX + NEW_SAMPLES
print(f"📥 ArXiv 데이터 로딩...")
print(f"   범위: {START_INDEX} ~ {end_index-1}")
print(f"   개수: {NEW_SAMPLES}개")

dataset = load_dataset(
    "ccdv/arxiv-summarization",
    split=f"train[{START_INDEX}:{end_index}]"
)

print(f"✅ {len(dataset)}개 로드 완료")

print("🔄 V4 전처리 중...")
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
        print(f"  ⚠️ 건너뜀: {msg}")

print(f"✅ 전처리 완료")
print(f"   유효: {len(processed_dataset)}개")
print(f"   건너뜀: {skipped}개")

# ================================================================
# STEP 5: LLM 클라이언트 초기화
# ================================================================

print("\n" + "="*60)
print("🤖 STEP 5: LLM 클라이언트 초기화")
print("="*60)

try:
    if LLM_MODE == 0:  # OpenAI
        client = OpenAI(api_key=API_KEY)
        test_response = client.models.list()
        print(f"✅ OpenAI 클라이언트 초기화 완료")
        
    elif LLM_MODE == 1:  # Gemini
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
        
    elif LLM_MODE == 2:  # Claude
        client = Anthropic(api_key=API_KEY)
        print(f"✅ Claude 클라이언트 초기화 완료")

    print(f"   속도 제한: {current_config['rpm']} RPM")
    print(f"   요청 간격: {current_config['sleep']}초")
    
except Exception as e:
    print(f"\n❌ 클라이언트 초기화 실패: {str(e)}")
    raise

# ================================================================
# STEP 6: V4 요약 생성 함수
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
    """V4 환각 감지"""
    
    # 1. 숫자 검증
    summary_numbers = re.findall(r'\d+\.?\d*%?', summary)
    abstract_numbers = re.findall(r'\d+\.?\d*%?', abstract)
    
    for num in summary_numbers:
        if num not in abstract_numbers:
            return True, f"Unverified number: {num}"
    
    # 2. 환각 키워드
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
    """Gemini V4 요약 생성"""
    
    for attempt in range(retry_count):
        try:
            # V4 단순 프롬프트
            prompt = USER_PROMPT_V4.format(abstract=abstract)
            
            response = client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # 낮춤
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
            
            # 품질 체크
            if word_count > 60 or sentence_count > 3:
                print(f"    ⚠️ 재시도 (단어:{word_count}, 문장:{sentence_count})")
                continue
            
            # 환각 감지
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
# STEP 7: 배치 처리
# ================================================================

print("\n" + "="*60)
print(f"🔄 STEP 7: V4 요약 생성 시작")
print("="*60)

print(f"\n⚠️ V4 설정:")
if GROUP_ID == 0:
    print(f"   - 모드: 통합 (한 사람이 전체)")
else:
    print(f"   - 그룹: {GROUP_ID}")
print(f"   - LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   - 프롬프트: 매우 단순하고 명확")
print(f"   - 요청 간격: {current_config['sleep']}초")
print(f"   - 예상 시간: ~{NEW_SAMPLES * current_config['sleep'] / 60:.1f}분")
print()
print(f"범위: {START_INDEX} ~ {START_INDEX + NEW_SAMPLES - 1}")
print(f"생성: {NEW_SAMPLES}개")
print()

def save_progress(data, completed, total):
    """진행 상황 저장"""
    df = pd.DataFrame(data)
    df.to_csv(data_path, index=False, encoding='utf-8')
    
    progress = {
        'group_id': GROUP_ID,
        'version': 'V4',
        'test_mode': TEST_MODE,
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
    'total': NEW_SAMPLES,
    'completed': 0,
    'success': 0,
    'failed': 0,
    'avg_words': 0,
    'avg_sentences': 0
}

new_data = []
start_time = time.time()

print("="*60)
print("🚀 V4 생성 시작!")
print("="*60)

try:
    for idx, paper in enumerate(processed_dataset):
        arxiv_index = START_INDEX + idx
        current = idx + 1
        progress_pct = (current / NEW_SAMPLES) * 100

        print(f"\n[{current}/{NEW_SAMPLES}] ({progress_pct:.1f}%) ArXiv 인덱스 {arxiv_index}")
        print(f"  초록: {count_words(paper['abstract'])}단어")

        result = generate_summary(paper['abstract'], client)

        if result['success']:
            stats['success'] += 1
            print(f"  ✅ 성공: {result['word_count']}단어, {result['sentence_count']}문장")
            print(f"     \"{result['summary'][:100]}...\"")

            new_data.append({
                'index': arxiv_index,
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
                'llm_version': 'V4',
                'group_id': GROUP_ID,
                'test_mode': TEST_MODE,
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

        # 테스트 모드가 아닐 때만 중간 저장
        if not TEST_MODE and stats['success'] > 0 and stats['success'] % 10 == 0:
            all_data = existing_data + new_data
            save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)

            elapsed = time.time() - start_time
            rate = stats['completed'] / elapsed * 60
            remaining = (NEW_SAMPLES - stats['completed']) / rate if rate > 0 else 0

            print(f"\n  📊 중간 통계:")
            print(f"     처리: {stats['completed']}/{NEW_SAMPLES}")
            print(f"     성공: {stats['success']}개")
            if stats['success'] > 0:
                print(f"     평균: {stats['avg_words']/stats['success']:.1f}단어")
            print(f"     남은 시간: ~{remaining:.0f}분")
            print(f"  💾 중간 저장 완료")

        if current < NEW_SAMPLES:
            time.sleep(current_config['sleep'])

except KeyboardInterrupt:
    print("\n\n⚠️ 사용자 중단!")
    if new_data:
        all_data = existing_data + new_data
        save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)
        print(f"✅ 진행 저장 완료!")
    sys.exit(0)

# ================================================================
# STEP 8: 최종 저장 및 통계
# ================================================================

print("\n" + "="*60)
print("💾 STEP 8: 최종 저장")
print("="*60)

all_data = existing_data + new_data
save_progress(all_data, len(all_data), len(all_data))

elapsed = time.time() - start_time

print(f"\n✅ 완료!")
print(f"\n📊 최종 통계:")
print(f"{'='*60}")
print(f"버전: V4")
print(f"모드: {'테스트' if TEST_MODE else '프로덕션'}")
if GROUP_ID == 0:
    print(f"그룹: 통합 모드")
else:
    print(f"그룹: {GROUP_ID}")
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
    print(f"\n📊 V4 샘플:")
    print(f"{'='*60}")
    for i, sample in enumerate(new_data[:3], 1):  # 처음 3개만
        print(f"\n[샘플 {i}] ArXiv {sample['index']}")
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
    print("     로 변경 후 2000개 생성")
else:
    if GROUP_ID == 0:
        print("🎉 V4 통합 생성 완료!")
        print("="*60)
        print(f"\n💡 2000개 데이터 생성 완료!")
        print(f"  파일: {DATA_FILE}")
    else:
        print(f"🎉 그룹 {GROUP_ID} V4 완료!")
        print("="*60)
        print(f"\n💡 다음 단계:")
        print(f"  다른 그룹도 완료 후 병합하세요")
print("="*60)