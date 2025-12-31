"""
=================================================================
📰 STEP 0.3: V10 Step 1 - 고품질 학습 데이터 생성 (개선 버전)
=================================================================

🎯 특징:
✅ 시작: 200개로 빠른 검증
✅ 확장: 1000개, 2000개, 3000개로 자동 확장
✅ 중복 방지: 이미 생성된 인덱스 스킵
✅ 폴더 구조: /SummaryDataSet/ 사용
✅ 자동 재시작: 중단 시 이어서 실행

📊 사용 시나리오:
1차: NEW_SAMPLES = 200  → 200개 생성 (빠른 검증)
2차: NEW_SAMPLES = 1000 → 200~1000 자동 추가 (800개)
3차: NEW_SAMPLES = 2000 → 1000~2000 자동 추가 (1000개)

💾 저장 위치:
/content/drive/MyDrive/SummaryDataSet/
├── v10_training_data.csv       # 메인 데이터
├── v10_progress.json           # 진행 상황
└── logs/                       # 로그 (선택)

=================================================================
"""

import subprocess
import sys
import os

print("\n" + "="*60)
print("🚀 V10 Step 1: 고품질 학습 데이터 생성")
print("="*60)

# ================================================================
# STEP 1: 패키지 설치
# ================================================================

print("\n" + "="*60)
print("📦 STEP 1: 패키지 설치")
print("="*60)

print("📥 필수 패키지 설치 중...")
packages = ["datasets", "pandas", "openai"]
for pkg in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", pkg],
                  capture_output=True, check=True)

print("✅ 패키지 설치 완료!")

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
from openai import OpenAI
from google.colab import drive, userdata

print("✅ Import 완료")

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
# ⚙️ 설정 - 여기만 수정하세요!
# ================================================================

print("\n" + "="*60)
print("⚙️ 설정")
print("="*60)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 설정 ⭐ 여기만 수정!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TARGET_TOTAL = 200  # 목표 총 개수
# 1차 실행: 200  → 0~200 생성
# 2차 실행: 1000 → 200~1000 자동 추가
# 3차 실행: 2000 → 1000~2000 자동 추가

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
    print("✅ API 키 로드 완료 (Colab Secrets)")
except:
    print("⚠️ API 키 없음! 아래 코드로 직접 입력하세요:")
    print('OPENAI_API_KEY = "sk-..."')
    OPENAI_API_KEY = None

# 또는 직접 입력 가능 
OPENAI_API_KEY = "sk-proj-....." #  

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 모델 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODEL = "gpt-4o-mini"  # 권장: 저렴하고 빠름
# MODEL = "gpt-4o"     # 최고 품질
# MODEL = "gpt-4-turbo"  # 균형

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프롬프트 설정
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
# 속도 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUESTS_PER_MINUTE = 50  # Tier 1 기준
SLEEP_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE + 0.2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 파일 이름
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_FILE = "v10_training_data.csv"
PROGRESS_FILE = "v10_progress.json"

# ================================================================
# 기존 데이터 확인 및 계획 수립
# ================================================================

print("\n" + "="*60)
print("📂 STEP 3: 기존 데이터 확인")
print("="*60)

data_path = Path(OUTPUT_DIR) / DATA_FILE
progress_path = Path(OUTPUT_DIR) / PROGRESS_FILE

existing_data = []
existing_indices = set()

if data_path.exists():
    print(f"✅ 기존 데이터 발견: {data_path}")
    existing_df = pd.read_csv(data_path)
    existing_data = existing_df.to_dict('records')
    existing_indices = set(existing_df['index'].tolist())
    current_count = len(existing_data)
    print(f"  현재 데이터: {current_count}개")
    print(f"  인덱스 범위: {min(existing_indices)}~{max(existing_indices)}")
else:
    print("ℹ️ 기존 데이터 없음 - 새로 시작")
    current_count = 0

# 생성 계획
if current_count >= TARGET_TOTAL:
    print(f"\n✅ 목표 달성!")
    print(f"  현재: {current_count}개")
    print(f"  목표: {TARGET_TOTAL}개")
    print(f"\n더 많은 데이터를 원하시면 TARGET_TOTAL을 증가시키세요!")
    sys.exit(0)

NEW_SAMPLES = TARGET_TOTAL - current_count

print(f"\n📊 생성 계획:")
print(f"  현재 데이터: {current_count}개")
print(f"  목표 총량: {TARGET_TOTAL}개")
print(f"  생성할 개수: {NEW_SAMPLES}개")
print(f"  시작 인덱스: {current_count}")
print(f"  종료 인덱스: {TARGET_TOTAL-1}")

# 설정 요약
print(f"\n{'='*60}")
print("📊 실행 설정")
print(f"{'='*60}")
print(f"모델: {MODEL}")
print(f"API 키: {'✅ 설정됨' if OPENAI_API_KEY else '❌ 없음'}")
print(f"속도 제한: {REQUESTS_PER_MINUTE} RPM")
print(f"예상 시간: ~{NEW_SAMPLES * SLEEP_BETWEEN_REQUESTS / 60:.0f}분")
print(f"{'='*60}")

if not OPENAI_API_KEY:
    raise ValueError("❌ API 키를 설정해주세요!")

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

print(f"📥 ArXiv 데이터 로딩... (총 {TARGET_TOTAL}개 필요)")

dataset = load_dataset(
    "ccdv/arxiv-summarization",
    split=f"train[:{TARGET_TOTAL}]"
)

print(f"✅ {len(dataset)}개 로드 완료")

print("🔄 전처리 중...")
dataset = dataset.map(lambda x: {
    'article': clean_arxiv_text(x['article']),
    'abstract': clean_arxiv_text(x['abstract'])
})

print("✅ 전처리 완료")

# ================================================================
# STEP 5: OpenAI API 설정
# ================================================================

print("\n" + "="*60)
print("🤖 STEP 5: OpenAI API 초기화")
print("="*60)

client = OpenAI(api_key=OPENAI_API_KEY)

print("✅ OpenAI API 초기화 완료")
print(f"   모델: {MODEL}")

# API 연결 테스트
print("\n🔍 API 연결 테스트 중...")
try:
    test_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Hello"}
        ],
        max_tokens=10,
        timeout=30.0
    )
    print("✅ API 연결 성공!")
    print(f"   응답: {test_response.choices[0].message.content[:50]}...")
except Exception as e:
    print(f"❌ API 연결 실패!")
    print(f"   오류: {str(e)}")
    print(f"\n해결 방법:")
    print(f"1. API 키 확인: OPENAI_API_KEY가 올바른지 확인")
    print(f"2. 인터넷 연결 확인")
    print(f"3. OpenAI 서비스 상태 확인: https://status.openai.com")
    print(f"4. 방화벽/프록시 설정 확인")
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
    """OpenAI GPT-4로 2문장 45단어 요약 생성"""
    
    for attempt in range(retry_count):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT_TEMPLATE.format(abstract=abstract)}
                ],
                max_tokens=150,
                temperature=0.3,
                timeout=60.0  # 60초 타임아웃
            )
            
            summary = response.choices[0].message.content.strip()
            
            word_count = count_words(summary)
            sentence_count = count_sentences(summary)
            
            # 검증
            if word_count > 60:
                print(f"    ⚠️ 너무 김 ({word_count}단어), 재시도...")
                continue
            
            if sentence_count > 3:
                print(f"    ⚠️ 문장 너무 많음 ({sentence_count}), 재시도...")
                continue
            
            return {
                'summary': summary,
                'word_count': word_count,
                'sentence_count': sentence_count,
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # 상세 오류 메시지
            if "Connection" in error_msg or "connection" in error_msg:
                print(f"    ❌ 연결 오류 (시도 {attempt+1}/{retry_count}): 네트워크 문제")
            elif "timeout" in error_msg.lower():
                print(f"    ❌ 타임아웃 (시도 {attempt+1}/{retry_count}): 응답 대기 시간 초과")
            elif "API key" in error_msg or "api_key" in error_msg:
                print(f"    ❌ API 키 오류: {error_msg}")
                return {
                    'summary': None,
                    'word_count': 0,
                    'sentence_count': 0,
                    'success': False,
                    'error': f'API Key Error: {error_msg}'
                }
            elif "rate_limit" in error_msg.lower() or "rate limit" in error_msg.lower():
                print(f"    ❌ 속도 제한 (시도 {attempt+1}/{retry_count}): 잠시 대기 중...")
                wait_time = 60  # 1분 대기
                print(f"    ⏰ {wait_time}초 대기...")
                time.sleep(wait_time)
                continue
            else:
                print(f"    ❌ 오류 (시도 {attempt+1}/{retry_count}): {error_type} - {error_msg[:100]}")
            
            # 재시도 전 대기
            if attempt < retry_count - 1:
                wait_time = (attempt + 1) * 10  # 10초, 20초, 30초...
                print(f"    ⏰ {wait_time}초 후 재시도...")
                time.sleep(wait_time)
            else:
                return {
                    'summary': None,
                    'word_count': 0,
                    'sentence_count': 0,
                    'success': False,
                    'error': f'{error_type}: {error_msg}'
                }
    
    return {
        'summary': None,
        'word_count': 0,
        'sentence_count': 0,
        'success': False,
        'error': 'Max retries reached'
    }

# ================================================================
# STEP 7: 배치 처리 (중복 방지)
# ================================================================

print("\n" + "="*60)
print("🔄 STEP 7: 요약 생성 시작 (중복 방지)")
print("="*60)

print(f"\n시작 인덱스: {current_count}")
print(f"종료 인덱스: {TARGET_TOTAL-1}")
print(f"생성할 개수: {NEW_SAMPLES}개")
print(f"예상 시간: ~{NEW_SAMPLES * SLEEP_BETWEEN_REQUESTS / 60:.0f}분")
print()

def save_progress(data, completed, total):
    """진행 상황 저장"""
    # 인덱스로 정렬
    data_sorted = sorted(data, key=lambda x: x['index'])
    
    # CSV 저장
    df = pd.DataFrame(data_sorted)
    df.to_csv(data_path, index=False, encoding='utf-8')
    
    # 진행 상황 JSON 저장
    progress = {
        'completed': completed,
        'total': total,
        'target_total': TARGET_TOTAL,
        'last_update': datetime.now().isoformat(),
        'success_rate': sum(1 for d in data if d.get('gpt4_success', False)) / len(data) if data else 0
    }
    with open(progress_path, 'w') as f:
        json.dump(progress, f, indent=2)

# 통계
stats = {
    'total': NEW_SAMPLES,
    'completed': 0,
    'success': 0,
    'failed': 0,
    'skipped': 0,
    'avg_words': 0,
    'avg_sentences': 0
}

new_data = []
start_time = time.time()

print("="*60)
print("🚀 생성 시작!")
print("="*60)

for i in range(current_count, TARGET_TOTAL):
    current = i - current_count + 1
    progress_pct = (current / NEW_SAMPLES) * 100
    
    # 중복 체크 ⭐ 핵심!
    if i in existing_indices:
        print(f"\n[{current}/{NEW_SAMPLES}] ({progress_pct:.1f}%) 인덱스 {i}")
        print(f"  ⏭️ 이미 존재 - 건너뛰기")
        stats['skipped'] += 1
        stats['completed'] += 1
        continue
    
    paper = dataset[i]
    
    print(f"\n[{current}/{NEW_SAMPLES}] ({progress_pct:.1f}%) 인덱스 {i}")
    print(f"  초록 길이: {count_words(paper['abstract'])}단어, {count_sentences(paper['abstract'])}문장")
    
    # GPT-4로 요약 생성
    result = generate_summary_openai(paper['abstract'])
    
    if result['success']:
        stats['success'] += 1
        print(f"  ✅ 성공: {result['word_count']}단어, {result['sentence_count']}문장")
        print(f"     \"{result['summary'][:80]}...\"")
        
        new_data.append({
            'index': i,
            'article': paper['article'],
            'original_abstract': paper['abstract'],
            'original_words': count_words(paper['abstract']),
            'original_sentences': count_sentences(paper['abstract']),
            'gpt4_summary': result['summary'],
            'gpt4_words': result['word_count'],
            'gpt4_sentences': result['sentence_count'],
            'gpt4_success': True,
            'created_at': datetime.now().isoformat()
        })
        
        stats['avg_words'] += result['word_count']
        stats['avg_sentences'] += result['sentence_count']
    else:
        stats['failed'] += 1
        print(f"  ❌ 실패: {result.get('error', 'Unknown error')}")
        
        new_data.append({
            'index': i,
            'article': paper['article'],
            'original_abstract': paper['abstract'],
            'original_words': count_words(paper['abstract']),
            'original_sentences': count_sentences(paper['abstract']),
            'gpt4_summary': None,
            'gpt4_words': 0,
            'gpt4_sentences': 0,
            'gpt4_success': False,
            'error': result.get('error', 'Unknown'),
            'created_at': datetime.now().isoformat()
        })
    
    stats['completed'] += 1
    
    # 중간 저장 (10개마다)
    if stats['completed'] % 10 == 0:
        all_data = existing_data + new_data
        save_progress(all_data, len(all_data), TARGET_TOTAL)
        
        elapsed = time.time() - start_time
        actual_generated = stats['success'] + stats['failed']
        rate = actual_generated / elapsed * 60 if actual_generated > 0 else 0
        remaining = (NEW_SAMPLES - stats['completed']) / rate if rate > 0 else 0
        
        print(f"\n  📊 중간 통계:")
        print(f"     진행: {stats['completed']}/{NEW_SAMPLES}")
        print(f"     성공: {stats['success']}")
        print(f"     실패: {stats['failed']}")
        print(f"     건너뜀: {stats['skipped']}")
        if stats['success'] > 0:
            print(f"     평균 단어: {stats['avg_words']/stats['success']:.1f}")
            print(f"     평균 문장: {stats['avg_sentences']/stats['success']:.1f}")
        print(f"     처리 속도: {rate:.2f}/분")
        print(f"     남은 시간: ~{remaining:.0f}분")
        print(f"  💾 중간 저장 완료")
    
    # 속도 제한 (실제 생성한 경우만)
    if current < NEW_SAMPLES and not (i in existing_indices):
        time.sleep(SLEEP_BETWEEN_REQUESTS)

# ================================================================
# STEP 8: 최종 저장 및 통계
# ================================================================

print("\n" + "="*60)
print("💾 STEP 8: 최종 저장")
print("="*60)

# 최종 저장
all_data = existing_data + new_data
save_progress(all_data, len(all_data), len(all_data))

elapsed = time.time() - start_time
actual_generated = stats['success'] + stats['failed']

print(f"\n✅ 완료!")
print(f"\n📊 최종 통계:")
print(f"{'='*60}")
print(f"총 처리: {stats['completed']}개")
print(f"  새로 생성: {actual_generated}개")
print(f"  건너뜀: {stats['skipped']}개")
print(f"\n생성 결과:")
print(f"  성공: {stats['success']}개 ({stats['success']/actual_generated*100:.1f}%)") if actual_generated > 0 else print(f"  성공: 0개")
print(f"  실패: {stats['failed']}개 ({stats['failed']/actual_generated*100:.1f}%)") if actual_generated > 0 else print(f"  실패: 0개")
if stats['success'] > 0:
    print(f"\n품질:")
    print(f"  평균 단어: {stats['avg_words']/stats['success']:.1f}")
    print(f"  평균 문장: {stats['avg_sentences']/stats['success']:.1f}")
print(f"\n시간:")
print(f"  소요 시간: {elapsed/60:.1f}분")
if actual_generated > 0:
    print(f"  처리 속도: {actual_generated/(elapsed/60):.1f}개/분")
print(f"\n현재 총 데이터: {len(all_data)}개")
print(f"{'='*60}")

print(f"\n📁 저장 위치:")
print(f"  데이터: {data_path}")
print(f"  진행: {progress_path}")

# 샘플 표시
if new_data:
    print(f"\n📊 생성된 데이터 샘플:")
    sample = new_data[0]
    print(f"{'='*60}")
    print(f"원본 초록 ({sample['original_words']}단어, {sample['original_sentences']}문장):")
    print(f"  {sample['original_abstract'][:200]}...")
    print()
    print(f"GPT-4 요약 ({sample['gpt4_words']}단어, {sample['gpt4_sentences']}문장):")
    print(f"  {sample['gpt4_summary']}")
    print(f"{'='*60}")

# ================================================================
# 품질 검증
# ================================================================

print("\n" + "="*60)
print("✅ STEP 9: 품질 검증")
print("="*60)

# 전체 데이터 통계
all_success = [d for d in all_data if d['gpt4_success']]

if all_success:
    words = [d['gpt4_words'] for d in all_success]
    sentences = [d['gpt4_sentences'] for d in all_success]
    
    print(f"\n전체 데이터 ({len(all_success)}개 성공):")
    print(f"\n단어 수 분포:")
    print(f"  최소: {min(words)}")
    print(f"  최대: {max(words)}")
    print(f"  평균: {sum(words)/len(words):.1f}")
    print(f"  45단어 이하: {sum(1 for w in words if w <= 45)}/{len(words)} ({sum(1 for w in words if w <= 45)/len(words)*100:.1f}%)")
    
    print(f"\n문장 수 분포:")
    print(f"  최소: {min(sentences)}")
    print(f"  최대: {max(sentences)}")
    print(f"  평균: {sum(sentences)/len(sentences):.1f}")
    print(f"  2문장: {sum(1 for s in sentences if s == 2)}/{len(sentences)} ({sum(1 for s in sentences if s == 2)/len(sentences)*100:.1f}%)")
    print(f"  1-3문장: {sum(1 for s in sentences if 1 <= s <= 3)}/{len(sentences)} ({sum(1 for s in sentences if 1 <= s <= 3)/len(sentences)*100:.1f}%)")

print("\n" + "="*60)
print("🎉 V10 Step 1 완료!")
print("="*60)

print(f"\n📊 현재 상태:")
print(f"  총 데이터: {len(all_data)}개")
print(f"  목표: {TARGET_TOTAL}개")
print(f"  달성률: {len(all_data)/TARGET_TOTAL*100:.1f}%")

if len(all_data) < TARGET_TOTAL:
    print(f"\n⚠️ 목표 미달!")
    print(f"  부족: {TARGET_TOTAL - len(all_data)}개")
    print(f"  다음 실행 시 자동으로 이어서 생성됩니다.")
else:
    print(f"\n✅ 목표 달성!")
    print(f"  더 많은 데이터를 원하시면:")
    print(f"  TARGET_TOTAL을 증가시키고 재실행하세요!")

print(f"\n다음 단계:")
print(f"1. 데이터 확인: {data_path}")
print(f"2. 더 많은 데이터 필요 시: TARGET_TOTAL 증가 후 재실행")
print(f"3. V10 Step 2로 이동: 이 데이터로 모델 학습")

print("\n" + "="*60)