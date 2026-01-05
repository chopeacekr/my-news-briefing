"""
=================================================================
📰 STEP 0.4 V4 - 4그룹 병렬 실행 버전 (시작 인덱스: 1000)
=================================================================

🎯 목적:
4명이 동시에 다른 인덱스 범위에서 150개씩 생성
→ 중복 없이 총 600개 생성

📊 그룹 분할 (1000부터 시작):
그룹 1: 인덱스 1000~1149  (150개)
그룹 2: 인덱스 1150~1299  (150개)
그룹 3: 인덱스 1300~1449  (150개)
그룹 4: 인덱스 1450~1599  (150개)

=================================================================
"""

import subprocess
import sys
import os

print("\n" + "="*60)
print("🚀 STEP 0.4 V1: 4그룹 병렬 실행 버전 (1000부터)")
print("="*60)

# ================================================================
# ⭐⭐⭐ 그룹 설정 - 여기만 수정하세요! ⭐⭐⭐
# ================================================================

GROUP_ID = 1  # 🔧 1, 2, 3, 4 중 선택!

# ================================================================
# 그룹별 설정 (자동 적용) - 1000부터 시작, 각 150개씩
# ================================================================

GROUP_CONFIGS = {
    1: {
        "START_INDEX": 1000,
        "NEW_SAMPLES": 150,
        "MAX_INDEX": 1149,
        "OUTPUT_FILE": "v1_training_data_group1.csv",
        "PROGRESS_FILE": "v1_progress_group1.json"
    },
    2: {
        "START_INDEX": 1150,
        "NEW_SAMPLES": 150,
        "MAX_INDEX": 1299,
        "OUTPUT_FILE": "v1_training_data_group2.csv",
        "PROGRESS_FILE": "v1_progress_group2.json"
    },
    3: {
        "START_INDEX": 1300,
        "NEW_SAMPLES": 150,
        "MAX_INDEX": 1449,
        "OUTPUT_FILE": "v1_training_data_group3.csv",
        "PROGRESS_FILE": "v1_progress_group3.json"
    },
    4: {
        "START_INDEX": 1450,
        "NEW_SAMPLES": 150,
        "MAX_INDEX": 1599,
        "OUTPUT_FILE": "v1_training_data_group4.csv",
        "PROGRESS_FILE": "v1_progress_group4.json"
    }
}

# 그룹 설정 적용
if GROUP_ID not in GROUP_CONFIGS:
    raise ValueError(f"❌ 잘못된 GROUP_ID: {GROUP_ID}. 1, 2, 3, 4 중 선택하세요!")

config = GROUP_CONFIGS[GROUP_ID]
FIXED_START_INDEX = config['START_INDEX']
NEW_SAMPLES = config['NEW_SAMPLES']
MAX_INDEX = config['MAX_INDEX']
DATA_FILE = config['OUTPUT_FILE']
PROGRESS_FILE = config['PROGRESS_FILE']

print(f"\n🎯 그룹 {GROUP_ID} 설정:")
print(f"   인덱스 범위: {FIXED_START_INDEX} ~ {MAX_INDEX}")
print(f"   할당: {MAX_INDEX - FIXED_START_INDEX + 1}개")
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

LLM_URLS = {
    0: "https://platform.openai.com/api-keys",
    1: "https://aistudio.google.com/app/apikey",
    2: "https://console.anthropic.com"
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
        "model": "models/gemini-pro-latest",
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
# 프롬프트 설정
# ================================================================

SYSTEM_PROMPT = """You are a research paper summarization expert. Your task is to create high-quality, concise summaries of academic paper abstracts.

Requirements:
- EXACTLY 2 sentences
- MAXIMUM 45 words total
- Focus on: main contribution + key results
- Use clear, technical language
- No bullet points, no lists
- Complete sentences only

Quality criteria:
- Capture the core innovation
- Include quantitative results if available
- Maintain technical accuracy
- Be concise but informative"""

USER_PROMPT_TEMPLATE = """Summarize this research paper abstract in EXACTLY 2 sentences with a MAXIMUM of 45 words.

Focus on:
1. Main contribution/method
2. Key results/findings

Abstract:
{abstract}

Requirements:
- EXACTLY 2 sentences
- MAXIMUM 45 words
- No introduction phrases (e.g., "This paper...", "The authors...")
- Start directly with the content

Summary:"""

# ================================================================
# 설정 요약
# ================================================================

print(f"\n{'='*60}")
print("📊 현재 설정")
print(f"{'='*60}")
print(f"👥 그룹: {GROUP_ID}")
print(f"🤖 LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   모델: {current_config['model']}")
print(f"   RPM: {current_config['rpm']}")
print(f"   요청 간격: {current_config['sleep']}초")
print()
print(f"📊 데이터:")
print(f"   인덱스 범위: {FIXED_START_INDEX} ~ {MAX_INDEX}")
print(f"   할당 개수: {MAX_INDEX - FIXED_START_INDEX + 1}개")
print(f"   생성 목표: {NEW_SAMPLES}개")
print(f"   예상 시간: ~{NEW_SAMPLES * current_config['sleep'] / 60:.0f}분")
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
START_INDEX = FIXED_START_INDEX  # 그룹별 고정 시작 인덱스

if data_path.exists():
    print(f"✅ 기존 데이터 발견: {data_path}")
    existing_df = pd.read_csv(data_path)
    existing_data = existing_df.to_dict('records')
    
    # 기존 데이터의 마지막 인덱스 확인
    if 'index' in existing_df.columns and len(existing_df) > 0:
        last_index = existing_df['index'].max()
        START_INDEX = last_index + 1
        print(f"  기존 샘플 수: {len(existing_data)}개")
        print(f"  마지막 인덱스: {last_index}")
        print(f"  다음 시작 인덱스: {START_INDEX}")
        
        # 범위 초과 체크
        if START_INDEX > MAX_INDEX:
            print(f"\n✅ 이미 할당된 범위를 모두 완료했습니다!")
            print(f"   현재 인덱스: {START_INDEX}")
            print(f"   최대 인덱스: {MAX_INDEX}")
            print(f"   → 더 이상 생성할 수 없습니다.")
            sys.exit(0)
    else:
        START_INDEX = FIXED_START_INDEX
else:
    print("ℹ️ 기존 데이터 없음 - 새로 시작")
    START_INDEX = FIXED_START_INDEX
    print(f"  시작 인덱스: {START_INDEX}")

# 생성 가능한 최대 개수 계산
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
# STEP 4: ArXiv 데이터 로드
# ================================================================

print("\n" + "="*60)
print("📥 STEP 4: ArXiv 데이터 로드")
print("="*60)

def clean_arxiv_text(text):
    """ArXiv 텍스트 전처리"""
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

# 필요한 범위만 로드
end_index = START_INDEX + NEW_SAMPLES
print(f"📥 ArXiv 데이터 로딩...")
print(f"   범위: {START_INDEX} ~ {end_index-1}")
print(f"   개수: {NEW_SAMPLES}개")

dataset = load_dataset(
    "ccdv/arxiv-summarization",
    split=f"train[{START_INDEX}:{end_index}]"
)

print(f"✅ {len(dataset)}개 로드 완료")

# 전처리
print("🔄 전처리 중...")
dataset = dataset.map(lambda x: {
    'article': clean_arxiv_text(x['article']),
    'abstract': clean_arxiv_text(x['abstract'])
})

print("✅ 전처리 완료")

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
                print(f"시도: {model_attempt}")
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
# STEP 6: 요약 생성 함수
# ================================================================

def count_sentences(text):
    """문장 수 카운트"""
    sentences = re.split(r'[.!?]+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)

def count_words(text):
    """단어 수 카운트"""
    return len(text.split())

def generate_summary_openai(abstract, retry_count=3):
    """OpenAI로 요약 생성"""
    for attempt in range(retry_count):
        try:
            response = client.chat.completions.create(
                model=current_config['model'],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(abstract=abstract)}
                ],
                max_tokens=150,
                temperature=0.3,
            )
            
            summary = response.choices[0].message.content.strip()
            word_count = count_words(summary)
            sentence_count = count_sentences(summary)
            
            if word_count > 60 or sentence_count > 3:
                print(f"    ⚠️ 재시도 (단어:{word_count}, 문장:{sentence_count})")
                continue
            
            return {
                'summary': summary,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ 오류 (시도 {attempt+1}/{retry_count}): {error_msg[:100]}")
            
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                wait_time = 60
                print(f"    ⏳ Rate limit! {wait_time}초 대기...")
                time.sleep(wait_time)
                continue
            elif "authentication" in error_msg.lower() or "401" in error_msg:
                return {'summary': None, 'word_count': 0, 'sentence_count': 0, 
                       'success': False, 'error': 'Authentication failed'}
            elif "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                return {'summary': None, 'word_count': 0, 'sentence_count': 0,
                       'success': False, 'error': 'Quota exceeded'}
            
            if attempt < retry_count - 1:
                time.sleep(5)
    
    return {'summary': None, 'word_count': 0, 'sentence_count': 0, 
            'success': False, 'error': 'Max retries reached'}

def generate_summary_gemini(abstract, retry_count=3):
    """Gemini로 요약 생성"""
    for attempt in range(retry_count):
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(abstract=abstract)}"
            
            response = client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=150,
                    top_p=0.95,
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
            
            return {
                'summary': summary,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ 오류 (시도 {attempt+1}/{retry_count}): {error_msg[:200]}")
            
            if "quota" in error_msg.lower() or "resource" in error_msg.lower() or "429" in error_msg:
                wait_time = 60
                print(f"    ⏳ Quota/Rate limit! {wait_time}초 대기...")
                time.sleep(wait_time)
                continue
            
            if "api key" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                print(f"    ❌ API 키 오류!")
                return {'summary': None, 'word_count': 0, 'sentence_count': 0,
                       'success': False, 'error': 'API key error'}
                
            if attempt < retry_count - 1:
                time.sleep(5)
    
    return {'summary': None, 'word_count': 0, 'sentence_count': 0, 
            'success': False, 'error': 'Max retries reached'}

def generate_summary_claude(abstract, retry_count=3):
    """Claude로 요약 생성"""
    for attempt in range(retry_count):
        try:
            message = client.messages.create(
                model=current_config['model'],
                max_tokens=150,
                temperature=0.3,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(abstract=abstract)}
                ]
            )
            
            summary = message.content[0].text.strip()
            word_count = count_words(summary)
            sentence_count = count_sentences(summary)
            
            if word_count > 60 or sentence_count > 3:
                print(f"    ⚠️ 재시도 (단어:{word_count}, 문장:{sentence_count})")
                continue
            
            return {
                'summary': summary,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"    ❌ 오류 (시도 {attempt+1}/{retry_count}): {error_msg[:100]}")
            
            if "rate_limit" in error_msg.lower():
                print(f"    ⏳ Rate limit! 60초 대기...")
                time.sleep(60)
                continue
                
            if attempt < retry_count - 1:
                time.sleep(5)
    
    return {'summary': None, 'word_count': 0, 'sentence_count': 0,
            'success': False, 'error': 'Max retries reached'}

generate_summary = {
    0: generate_summary_openai,
    1: generate_summary_gemini,
    2: generate_summary_claude
}[LLM_MODE]

# ================================================================
# STEP 7: 배치 처리
# ================================================================

print("\n" + "="*60)
print(f"🔄 STEP 7: 요약 생성 시작")
print("="*60)

print(f"\n⚠️ 설정:")
print(f"   - 그룹: {GROUP_ID}")
print(f"   - LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   - 모델: {current_config['model']}")
print(f"   - 요청 간격: {current_config['sleep']}초")
print(f"   - 예상 시간: ~{NEW_SAMPLES * current_config['sleep'] / 60:.0f}분")
print(f"   - 실패한 요청은 데이터셋에 추가되지 않음")
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
print("🚀 생성 시작!")
print("="*60)

try:
    for idx, paper in enumerate(dataset):
        arxiv_index = START_INDEX + idx
        current = idx + 1
        progress_pct = (current / NEW_SAMPLES) * 100

        print(f"\n[{current}/{NEW_SAMPLES}] ({progress_pct:.1f}%) ArXiv 인덱스 {arxiv_index}")
        print(f"  초록: {count_words(paper['abstract'])}단어, {count_sentences(paper['abstract'])}문장")

        result = generate_summary(paper['abstract'])

        if result['success']:
            stats['success'] += 1
            print(f"  ✅ 성공: {result['word_count']}단어, {result['sentence_count']}문장")
            print(f"     \"{result['summary'][:80]}...\"")

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
                'group_id': GROUP_ID,
                'created_at': datetime.now().isoformat()
            })

            stats['avg_words'] += result['word_count']
            stats['avg_sentences'] += result['sentence_count']
        else:
            stats['failed'] += 1
            error_msg = result.get('error', 'Unknown')
            print(f"  ❌ 실패: {error_msg} (데이터셋에 추가 안 됨)")
            
            if error_msg in ['Authentication failed', 'Quota exceeded', 'API key error']:
                print(f"\n⛔ 치명적 오류 발생! 중단합니다.")
                break

        stats['completed'] += 1

        if stats['success'] > 0 and stats['success'] % 10 == 0:
            all_data = existing_data + new_data
            save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)

            elapsed = time.time() - start_time
            rate = stats['completed'] / elapsed * 60
            remaining = (NEW_SAMPLES - stats['completed']) / rate if rate > 0 else 0

            print(f"\n  📊 중간 통계:")
            print(f"     처리: {stats['completed']}/{NEW_SAMPLES} ({stats['completed']/NEW_SAMPLES*100:.1f}%)")
            print(f"     성공: {stats['success']}개 ({stats['success']/stats['completed']*100:.1f}%)")
            print(f"     실패: {stats['failed']}개")
            if stats['success'] > 0:
                print(f"     평균: {stats['avg_words']/stats['success']:.1f}단어, {stats['avg_sentences']/stats['success']:.1f}문장")
            print(f"     속도: {rate:.2f}/분, 남은 시간: ~{remaining:.0f}분")
            print(f"  💾 중간 저장 완료 ({len(all_data)}개)")

        if current < NEW_SAMPLES:
            print(f"  ⏳ {current_config['sleep']}초 대기...")
            time.sleep(current_config['sleep'])

except KeyboardInterrupt:
    print("\n\n⚠️ 사용자 중단!")
    if new_data:
        all_data = existing_data + new_data
        save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)
        print(f"✅ 진행 저장 완료! (성공한 {len(new_data)}개만 저장)")
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
print(f"그룹: {GROUP_ID}")
print(f"LLM: {LLM_NAMES[LLM_MODE]}")
print(f"모델: {current_config['model']}")
print(f"총 처리: {stats['completed']}개")
print(f"성공: {stats['success']}개 ({stats['success']/stats['completed']*100:.1f}%)")
print(f"실패: {stats['failed']}개")
if stats['success'] > 0:
    print(f"평균: {stats['avg_words']/stats['success']:.1f}단어, {stats['avg_sentences']/stats['success']:.1f}문장")
print(f"소요: {elapsed/60:.1f}분 ({stats['completed']/(elapsed/60):.1f}개/분)")
print(f"{'='*60}")

print(f"\n📁 저장 위치:")
print(f"  파일: {data_path}")
print(f"  행 수: {len(all_data)}개")

if new_data:
    success_samples = [d for d in new_data if d['llm_success']]
    if success_samples:
        sample = success_samples[0]
        print(f"\n📊 샘플:")
        print(f"{'='*60}")
        print(f"ArXiv 인덱스: {sample['index']}")
        print(f"원본: {sample['original_words']}단어, {sample['original_sentences']}문장")
        print(f"요약: {sample['llm_words']}단어, {sample['llm_sentences']}문장")
        print(f"\n\"{sample['llm_summary']}\"")
        print(f"{'='*60}")

print("\n" + "="*60)
print(f"🎉 그룹 {GROUP_ID} 완료!")
print("="*60)

print(f"\n💡 다음 단계:")
print(f"  모든 그룹 완료 후 병합:")
print(f"  → v1_training_data_group1.csv (1000~1149)")
print(f"  → v1_training_data_group2.csv (1150~1299)")
print(f"  → v1_training_data_group3.csv (1300~1449)")
print(f"  → v1_training_data_group4.csv (1450~1599)")
print("="*60)