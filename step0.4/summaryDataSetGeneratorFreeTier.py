"""
=================================================================
📰 STEP 0.4: V3 - 고품질 학습 데이터 생성 (Multi-LLM 버전) 
v3 업데이트: 실패된 요청은 데이터셋에 포함하지 않음
=================================================================

🎯 목적:
다양한 LLM으로 ArXiv 초록을 2문장 45단어로 재요약
→ 고품질 학습 데이터 생성

📊 지원 모델:
0. OpenAI GPT-4o-mini (기본)
1. Google Gemini (추천!)
2. Anthropic Claude

💾 저장 형식:
CSV: article, original_abstract, llm_summary, word_count, sentence_count

🔄 FREE TIER 제약:
- OpenAI: 3 RPM, 200 RPD
- Gemini: 15 RPM, 1500 RPD (Free tier) ⭐ 추천
- Claude: API 사용 (별도 크레딧 필요)
→ 1회 실행: 최대 150개 (안전하게)

⏱️ 예상 시간:
- 150개: Gemini ~15분, OpenAI ~50분
- 1000개 만들려면: Gemini 7번 실행

=================================================================
"""

import subprocess
import sys
import os

print("\n" + "="*60)
print("🚀 STEP 0.4 V1: 고품질 학습 데이터 생성 (Multi-LLM)")
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
# ⚙️ 설정 - 여기만 수정하세요!
# ================================================================

print("\n" + "="*60)
print("⚙️ 설정 (Multi-LLM)")
print("="*60)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLM 선택 (플러그인 모드)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LLM_MODE = 1  # 🔧 여기를 변경하세요!
# 0: OpenAI GPT-4o-mini (기본, FREE TIER)
# 1: Google Gemini (FREE TIER, 더 높은 RPM) ⭐ 추천!
# 2: Anthropic Claude (API 크레딧 필요)

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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 선택된 LLM 패키지만 설치
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# 선택된 LLM 클라이언트만 Import
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW_SAMPLES = 300  # 1회 생성 샘플 수
START_INDEX = 0    # 시작 인덱스 (자동 설정됨)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API 키 설정 (선택된 LLM만)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# 선택된 LLM의 API 키만 로드
SECRET_NAME = LLM_SECRET_NAMES[LLM_MODE]
API_KEY = get_api_key(SECRET_NAME)

# 직접 입력 옵션 (Secrets 실패시)
# 아래 주석을 해제하고 실제 키를 입력하세요
# API_KEY = "your-api-key-here"

# API 키 상태 확인
if API_KEY:
    print(f"✅ {LLM_NAMES[LLM_MODE]} API 키: 설정됨 ({API_KEY[:10]}...)")
else:
    print(f"❌ {LLM_NAMES[LLM_MODE]} API 키: 없음")
    print(f"\n📝 설정 방법:")
    print(f"방법 1) Colab Secrets 사용 (권장):")
    print(f"  1. Colab 좌측 패널 🔑 Secrets 클릭")
    print(f"  2. Name: {SECRET_NAME}")
    print(f"  3. Value: (실제 API 키)")
    print(f"  4. 발급: {LLM_URLS[LLM_MODE]}")
    if LLM_MODE == 1:
        print(f"     → 'Create API key in new project' 선택!")
    print(f"  5. 'Notebook access' 토글 ON")
    print(f"  6. 런타임 재시작 후 코드 다시 실행")
    print(f"\n방법 2) 코드에 직접 입력:")
    print(f"  위 '# 직접 입력 옵션' 부분의 주석 해제 후 키 입력")
    raise ValueError(f"{LLM_NAMES[LLM_MODE]} API 키를 설정해주세요!")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 모델별 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODEL_CONFIGS = {
    0: {  # OpenAI
        "model": "gpt-4o-mini",
        "rpm": 3,      # FREE TIER
        "rpd": 200,
        "sleep": 21,   # 60/3 + 1
    },
    1: {  # Gemini - 기본 모델 변경
        "model": "models/gemini-pro-latest",  # ✅ 기본값
        "rpm": 15,     # FREE TIER
        "rpd": 1500,
        "sleep": 5,    # 60/15 + 1
    },
    2: {  # Claude
        "model": "claude-3-5-haiku-20241022",
        "rpm": 50,     # API 플랜에 따라 다름
        "rpd": 5000,
        "sleep": 2,    # 60/50 + 1
    }
}

current_config = MODEL_CONFIGS[LLM_MODE]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프롬프트 설정 (모든 모델 공통)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 파일 이름
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_FILE = "v1_training_data.csv"
PROGRESS_FILE = "v1_progress.json"

# ================================================================
# 설정 요약
# ================================================================

print(f"\n{'='*60}")
print("📊 현재 설정")
print(f"{'='*60}")
print(f"🤖 LLM: {LLM_NAMES[LLM_MODE]}")
print(f"   모델: {current_config['model']}")
print(f"   RPM: {current_config['rpm']}")
print(f"   RPD: {current_config['rpd']}")
print(f"   요청 간격: {current_config['sleep']}초")
print()
print(f"📊 데이터:")
print(f"   생성할 샘플: {NEW_SAMPLES}개")
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
if data_path.exists():
    print(f"✅ 기존 데이터 발견: {data_path}")
    existing_df = pd.read_csv(data_path)
    existing_data = existing_df.to_dict('records')
    START_INDEX = len(existing_data)
    print(f"  기존 샘플 수: {len(existing_data)}개")
    print(f"  시작 인덱스: {START_INDEX}")
    print(f"  목표 샘플 수: {START_INDEX + NEW_SAMPLES}개")
    print(f"  1000개까지: {max(0, 1000 - (START_INDEX + NEW_SAMPLES))}개 남음")
else:
    print("ℹ️ 기존 데이터 없음 - 새로 시작")
    START_INDEX = 0
    print(f"  시작 인덱스: 0")
    print(f"  목표 샘플 수: {NEW_SAMPLES}개")
    print(f"  1000개까지: {1000 - NEW_SAMPLES}개 남음")

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

# 필요한 만큼만 로드
total_needed = START_INDEX + NEW_SAMPLES
print(f"📥 ArXiv 데이터 로딩... (총 {total_needed}개 필요)")

dataset = load_dataset(
    "ccdv/arxiv-summarization",
    split=f"train[:{total_needed}]"
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

# 선택된 LLM에 따라 클라이언트 초기화
try:
    if LLM_MODE == 0:  # OpenAI
        client = OpenAI(api_key=API_KEY)
        # 연결 테스트
        test_response = client.models.list()
        print(f"✅ OpenAI 클라이언트 초기화 완료")
        print(f"   연결 테스트: 성공")
        
    elif LLM_MODE == 1:  # Gemini
        genai.configure(api_key=API_KEY)
        
        # 사용 가능한 모델 확인
        print("📋 사용 가능한 Gemini 모델 확인 중...")
        available_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
                    print(f"   ✓ {m.name}")
        except Exception as e:
            print(f"   ⚠️ 모델 목록 조회 실패: {e}")
        
        # 시도할 모델 목록 (우선순위 순) 
        models_to_try = [
            'models/gemini-2.5-flash',  # 기본값
            'models/gemini-2.0-flash',
            'models/gemini-2.5-pro', 
            'models/gemma-3-27b-it'
        ]
        
        client = None
        for model_attempt in models_to_try:
            try:
                print(f"\n시도: {model_attempt}")
                test_client = genai.GenerativeModel(model_attempt)
                
                # 간단한 테스트
                test_response = test_client.generate_content(
                    "Say OK",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1,
                    )
                )
                
                # 성공하면 이 모델 사용
                client = test_client
                current_config['model'] = model_attempt
                print(f"✅ Gemini 클라이언트 초기화 완료")
                print(f"   모델: {model_attempt}")
                print(f"   연결 테스트: 성공 ({test_response.text.strip()})")
                break
                
            except Exception as e:
                print(f"   ❌ {model_attempt} 실패: {str(e)[:100]}")
                continue
        
        if client is None:
            raise Exception("사용 가능한 Gemini 모델을 찾을 수 없습니다.")
        
    elif LLM_MODE == 2:  # Claude
        client = Anthropic(api_key=API_KEY)
        print(f"✅ Claude 클라이언트 초기화 완료")

    print(f"   속도 제한: {current_config['rpm']} RPM")
    print(f"   요청 간격: {current_config['sleep']}초")
    
except Exception as e:
    print(f"\n❌ 클라이언트 초기화 실패!")
    print(f"오류: {str(e)}")
    print(f"\n💡 해결 방법:")
    if LLM_MODE == 1:
        print(f"1. Gemini API 키 재발급:")
        print(f"   {LLM_URLS[LLM_MODE]}")
        print(f"   → 'Create API key in new project' 선택!")
        print(f"2. 새 키를 Colab Secrets에 등록")
        print(f"3. 런타임 재시작 후 다시 실행")
        print(f"\n4. 또는 OpenAI로 전환:")
        print(f"   LLM_MODE = 0")
    elif LLM_MODE == 0:
        print(f"1. OpenAI 계정 크레딧 확인")
        print(f"2. API 키 확인")
        print(f"3. LLM_MODE = 1로 변경 (Gemini 사용)")
    elif LLM_MODE == 2:
        print(f"1. Claude 계정 크레딧 확인")
        print(f"2. API 키 확인")
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
            # 프롬프트 결합
            full_prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(abstract=abstract)}"
            
            # Gemini API 호출
            response = client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=150,
                    top_p=0.95,
                    top_k=40,
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE",
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE",
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE",
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE",
                    },
                ]
            )
            
            # 응답 확인
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
            
            # Rate limit 처리
            if "quota" in error_msg.lower() or "resource" in error_msg.lower() or "429" in error_msg:
                wait_time = 60
                print(f"    ⏳ Quota/Rate limit! {wait_time}초 대기...")
                time.sleep(wait_time)
                continue
            
            # API 키 오류
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

# LLM 모드에 따라 함수 선택
generate_summary = {
    0: generate_summary_openai,
    1: generate_summary_gemini,
    2: generate_summary_claude
}[LLM_MODE]

# ================================================================
# STEP 7: 배치 처리
# ================================================================

print("\n" + "="*60)
print(f"🔄 STEP 7: 요약 생성 시작 ({LLM_NAMES[LLM_MODE]})")
print("="*60)

print(f"\n⚠️ {LLM_NAMES[LLM_MODE]} 설정:")
print(f"   - 모델: {current_config['model']}")
print(f"   - 요청 간격: {current_config['sleep']}초")
print(f"   - 예상 시간: ~{NEW_SAMPLES * current_config['sleep'] / 60:.0f}분")
print(f"   - 중간 저장: 10개마다 자동 저장")
print(f"   - 안전 종료: Ctrl+C로 중단 가능")
print(f"   - 실패한 요청은 데이터셋에 추가되지 않음")
print()
print(f"시작: {START_INDEX}")
print(f"종료: {START_INDEX + NEW_SAMPLES}")
print(f"생성할 개수: {NEW_SAMPLES}개")
print()

def save_progress(data, completed, total):
    """진행 상황 저장"""
    df = pd.DataFrame(data)
    df.to_csv(data_path, index=False, encoding='utf-8')
    
    progress = {
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
    for i in range(START_INDEX, START_INDEX + NEW_SAMPLES):
        paper = dataset[i]
        current = i - START_INDEX + 1
        progress_pct = (current / NEW_SAMPLES) * 100

        print(f"\n[{current}/{NEW_SAMPLES}] ({progress_pct:.1f}%) 인덱스 {i}")
        print(f"  초록: {count_words(paper['abstract'])}단어, {count_sentences(paper['abstract'])}문장")

        result = generate_summary(paper['abstract'])

        if result['success']:
            stats['success'] += 1
            print(f"  ✅ 성공: {result['word_count']}단어, {result['sentence_count']}문장")
            print(f"     \"{result['summary'][:80]}...\"")

            # 성공한 경우만 데이터 추가
            new_data.append({
                'index': i,
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
                'created_at': datetime.now().isoformat()
            })

            stats['avg_words'] += result['word_count']
            stats['avg_sentences'] += result['sentence_count']
        else:
            stats['failed'] += 1
            error_msg = result.get('error', 'Unknown')
            print(f"  ❌ 실패: {error_msg} (데이터셋에 추가 안 됨)")
            
            # 치명적 오류 체크
            if error_msg in ['Authentication failed', 'Quota exceeded', 'API key error']:
                print(f"\n⛔ 치명적 오류 발생! 중단합니다.")
                print(f"현재까지 진행 상황을 저장합니다...")
                break
            
            # 실패한 경우 데이터에 추가하지 않음!

        stats['completed'] += 1

        # 중간 저장 (10개마다)
        if stats['success'] > 0 and stats['success'] % 10 == 0:
            all_data = existing_data + new_data
            save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)

            elapsed = time.time() - start_time
            rate = stats['completed'] / elapsed * 60
            remaining = (NEW_SAMPLES - stats['completed']) / rate if rate > 0 else 0

            print(f"\n  📊 중간 통계:")
            print(f"     처리: {stats['completed']}/{NEW_SAMPLES} ({stats['completed']/NEW_SAMPLES*100:.1f}%)")
            print(f"     성공: {stats['success']}개 ({stats['success']/stats['completed']*100:.1f}%)")
            print(f"     실패: {stats['failed']}개 (데이터셋에 미포함)")
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
print(f"LLM: {LLM_NAMES[LLM_MODE]}")
print(f"모델: {current_config['model']}")
print(f"총 처리: {stats['completed']}개")
print(f"성공: {stats['success']}개 ({stats['success']/stats['completed']*100:.1f}%) ✅ 데이터셋에 저장")
print(f"실패: {stats['failed']}개 ({stats['failed']/stats['completed']*100:.1f}%) ❌ 데이터셋에서 제외")
if stats['success'] > 0:
    print(f"평균: {stats['avg_words']/stats['success']:.1f}단어, {stats['avg_sentences']/stats['success']:.1f}문장")
print(f"소요: {elapsed/60:.1f}분 ({stats['completed']/(elapsed/60):.1f}개/분)")
print(f"{'='*60}")

print(f"\n📁 저장 위치:")
print(f"  데이터: {data_path}")
print(f"  진행: {progress_path}")
print(f"  저장된 행 수: {len(all_data)}개 (성공한 것만)")

if new_data:
    success_samples = [d for d in new_data if d['llm_success']]
    if success_samples:
        sample = success_samples[0]
        print(f"\n📊 샘플:")
        print(f"{'='*60}")
        print(f"원본 ({sample['original_words']}단어, {sample['original_sentences']}문장):")
        print(f"  {sample['original_abstract'][:200]}...")
        print()
        print(f"{LLM_NAMES[LLM_MODE]} 요약 ({sample['llm_words']}단어, {sample['llm_sentences']}문장):")
        print(f"  {sample['llm_summary']}")
        print(f"{'='*60}")

# ================================================================
# 품질 검증
# ================================================================

print("\n" + "="*60)
print("✅ STEP 9: 품질 검증")
print("="*60)

success_data = [d for d in new_data if d['llm_success']]

if success_data:
    words = [d['llm_words'] for d in success_data]
    sentences = [d['llm_sentences'] for d in success_data]

    print(f"\n단어 수:")
    print(f"  범위: {min(words)}-{max(words)}, 평균: {sum(words)/len(words):.1f}")
    print(f"  45단어 이하: {sum(1 for w in words if w <= 45)}/{len(words)} ({sum(1 for w in words if w <= 45)/len(words)*100:.1f}%)")

    print(f"\n문장 수:")
    print(f"  범위: {min(sentences)}-{max(sentences)}, 평균: {sum(sentences)/len(sentences):.1f}")
    print(f"  2문장: {sum(1 for s in sentences if s == 2)}/{len(sentences)} ({sum(1 for s in sentences if s == 2)/len(sentences)*100:.1f}%)")
else:
    print("\n⚠️ 성공한 요약이 없습니다.")
    print("\n문제 해결:")
    print(f"1. {LLM_NAMES[LLM_MODE]} API 키 확인")
    print(f"2. 런타임 재시작 후 다시 실행")
    print(f"3. 다른 LLM 시도:")
    if LLM_MODE != 0:
        print(f"   LLM_MODE = 0  # OpenAI")

print("\n" + "="*60)
print("🎉 STEP 0.4 V1 완료!")
print("="*60)

total_created = len(all_data)
remaining = max(0, 1000 - total_created)

print(f"\n다음 단계:")
print(f"1. 데이터 확인: {data_path}")
print(f"2. 현재: {total_created}개 (성공한 것만)")
if remaining > 0:
    print(f"3. 1000개까지: {remaining}개 남음")
    runs_remaining = (remaining + stats['success'] - 1) // stats['success'] if stats['success'] > 0 else 0
    print(f"   → 현재 성공률 {stats['success']}/{stats['completed']}로 약 {runs_remaining}번 더 실행 필요")
else:
    print(f"3. ✅ 1000개 달성!")

print(f"\n💡 LLM 전환 방법:")
print(f"  LLM_MODE = 0  # OpenAI (3 RPM, 크레딧 필요)")
print(f"  LLM_MODE = 1  # Gemini (15 RPM, 무료!) ⭐ 현재")
print(f"  LLM_MODE = 2  # Claude (50 RPM, 크레딧 필요)")
print("="*60)