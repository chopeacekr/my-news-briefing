"""
=================================================================
📰 STEP 0.3: V10 Step 1 - 고품질 학습 데이터 생성 (ChatGPT FREE TIER 버전)
=================================================================

🎯 목적:
ChatGPT (OpenAI GPT-4) Free Tier로 ArXiv 초록을 2문장 45단어로 재요약
→ 고품질 학습 데이터 생성

📊 데이터 흐름:
Input: ArXiv 논문 초록 (100-150단어, 4-6문장)
Output: GPT-4 요약 (45단어, 2문장)

💾 저장 형식:
CSV: article, original_abstract, gpt4_summary, word_count, sentence_count

🔄 FREE TIER 제약:
- RPM: 3 requests/minute
- TPM: 40,000 tokens/minute
- RPD: 200 requests/day
→ 1회 실행: 최대 150개 (안전하게)
→ 여러 번 나눠서 실행 필요 (자동으로 이어서 생성)

⏱️ 예상 시간:
- 150개: ~50분 (3 RPM 제한)
- 1000개 만들려면: 7번 실행 필요

=================================================================
"""

import subprocess
import sys
import os

print("\n" + "="*60)
print("🚀 V10 Step 1: 고품질 학습 데이터 생성 (FREE TIER)")
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
OUTPUT_DIR = "/content/drive/MyDrive/arxiv-STEP0.3-V10-DATA"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
print(f"✅ 출력 디렉토리: {OUTPUT_DIR}")

# ================================================================
# ⚙️ 설정 - 여기만 수정하세요!
# ================================================================

print("\n" + "="*60)
print("⚙️ 설정 (FREE TIER)")
print("="*60)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 설정 (FREE TIER 제약)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW_SAMPLES = 50  # FREE TIER: 최대 150개/일 (안전하게)
                   # 1000개 목표 → 7번 실행 필요
START_INDEX = 0    # 시작 인덱스 (추가 모드에서 자동 설정됨)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Colab Secrets에서 API 키 가져오기
# 설정: 좌측 패널 🔑 Secrets → OPENAI_API_KEY 추가
try:
    OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
    print("✅ API 키 로드 완료 (Colab Secrets)")
except:
    print("⚠️ API 키 없음! 아래 코드로 직접 입력하세요:")
    print('OPENAI_API_KEY = "sk-..."')
    OPENAI_API_KEY = None

# 또는 직접 입력 (보안상 권장하지 않음)
# OPENAI_API_KEY = "sk-..."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GPT-4 모델 설정 (FREE TIER)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODEL = "gpt-4o-mini"  # FREE TIER에서 사용 가능
# gpt-4o-mini: 저렴하고 빠름, Free Tier 지원

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GPT-4 프롬프트 설정
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
# 속도 제한 설정 (FREE TIER)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FREE TIER: 3 RPM, 40000 TPM, 200 RPD
REQUESTS_PER_MINUTE = 3    # FREE TIER 제한
REQUESTS_PER_DAY = 200     # FREE TIER 일일 제한
SLEEP_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE + 1  # ~21초 (안전하게)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 파일 이름
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA_FILE = "v10_training_data.csv"  # 최종 데이터 파일
PROGRESS_FILE = "v10_progress.json"  # 진행 상황 저장

# ================================================================
# 설정 요약
# ================================================================

print(f"\n{'='*60}")
print("📊 현재 설정 (FREE TIER)")
print(f"{'='*60}")
print(f"⚠️ FREE TIER 제약:")
print(f"   - RPM: {REQUESTS_PER_MINUTE} requests/minute")
print(f"   - RPD: {REQUESTS_PER_DAY} requests/day")
print(f"   - 1회 최대: {NEW_SAMPLES}개 (안전하게)")
print()
print(f"생성할 샘플: {NEW_SAMPLES}개")
print(f"모델: {MODEL}")
print(f"API 키: {'✅ 설정됨' if OPENAI_API_KEY else '❌ 없음'}")
print(f"요청 간격: {SLEEP_BETWEEN_REQUESTS:.1f}초")
print(f"예상 시간: ~{NEW_SAMPLES * SLEEP_BETWEEN_REQUESTS / 60:.0f}분")
print(f"출력 파일: {DATA_FILE}")
print()
print(f"💡 1000개 만들려면: 약 7번 실행 필요")
print(f"   (자동으로 이어서 생성됨)")
print(f"{'='*60}")

if not OPENAI_API_KEY:
    raise ValueError("❌ API 키를 설정해주세요!")

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
# STEP 5: OpenAI API 설정
# ================================================================

print("\n" + "="*60)
print("🤖 STEP 5: OpenAI API 초기화")
print("="*60)

client = OpenAI(api_key=OPENAI_API_KEY)

print("✅ OpenAI API 초기화 완료")
print(f"   모델: {MODEL}")
print(f"   속도 제한: {REQUESTS_PER_MINUTE} RPM (FREE TIER)")
print(f"   요청 간격: {SLEEP_BETWEEN_REQUESTS:.1f}초")

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
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": USER_PROMPT_TEMPLATE.format(abstract=abstract)
                    }
                ],
                max_tokens=150,
                temperature=0.3,  # 일관성을 위해 낮게
            )

            summary = response.choices[0].message.content.strip()

            # 품질 검증
            word_count = count_words(summary)
            sentence_count = count_sentences(summary)

            # 기본 검증
            if word_count > 60:  # 너무 길면 재시도
                print(f"    ⚠️ 너무 김 ({word_count}단어), 재시도...")
                continue

            if sentence_count > 3:  # 너무 많은 문장
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
            
            # Rate limit 에러 처리
            if "rate_limit" in error_msg.lower():
                wait_time = 60  # 1분 대기
                print(f"    ⚠️ Rate limit! {wait_time}초 대기...")
                time.sleep(wait_time)
                continue
            
            print(f"    ❌ 오류 (시도 {attempt+1}/{retry_count}): {error_msg}")
            if attempt < retry_count - 1:
                time.sleep(5)
            else:
                return {
                    'summary': None,
                    'word_count': 0,
                    'sentence_count': 0,
                    'success': False,
                    'error': error_msg
                }

    return {
        'summary': None,
        'word_count': 0,
        'sentence_count': 0,
        'success': False,
        'error': 'Max retries reached'
    }

# ================================================================
# STEP 7: 배치 처리
# ================================================================

print("\n" + "="*60)
print("🔄 STEP 7: 요약 생성 시작 (FREE TIER)")
print("="*60)

print(f"\n⚠️ FREE TIER 알림:")
print(f"   - 요청 간격: {SLEEP_BETWEEN_REQUESTS:.1f}초")
print(f"   - 예상 시간: ~{NEW_SAMPLES * SLEEP_BETWEEN_REQUESTS / 60:.0f}분")
print(f"   - 중간 저장: 10개마다 자동 저장")
print(f"   - 안전 종료: Ctrl+C로 중단 가능 (진행 상황 저장됨)")
print()
print(f"시작: {START_INDEX}")
print(f"종료: {START_INDEX + NEW_SAMPLES}")
print(f"생성할 개수: {NEW_SAMPLES}개")
print()

# 진행 상황 저장 함수
def save_progress(data, completed, total):
    """진행 상황 저장"""
    # CSV 저장
    df = pd.DataFrame(data)
    df.to_csv(data_path, index=False, encoding='utf-8')

    # 진행 상황 JSON 저장
    progress = {
        'completed': completed,
        'total': total,
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
        print(f"  초록 길이: {count_words(paper['abstract'])}단어, {count_sentences(paper['abstract'])}문장")

        # OpenAI GPT-4로 요약 생성
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
            save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)

            elapsed = time.time() - start_time
            rate = stats['completed'] / elapsed * 60  # per minute
            remaining = (NEW_SAMPLES - stats['completed']) / rate if rate > 0 else 0

            print(f"\n  📊 중간 통계:")
            print(f"     성공률: {stats['success']}/{stats['completed']} ({stats['success']/stats['completed']*100:.1f}%)")
            if stats['success'] > 0:
                print(f"     평균 단어: {stats['avg_words']/stats['success']:.1f}")
                print(f"     평균 문장: {stats['avg_sentences']/stats['success']:.1f}")
            print(f"     처리 속도: {rate:.2f}/분")
            print(f"     남은 시간: ~{remaining:.0f}분")
            print(f"  💾 중간 저장 완료")

        # 속도 제한 (FREE TIER)
        if current < NEW_SAMPLES:  # 마지막이 아니면
            print(f"  ⏳ {SLEEP_BETWEEN_REQUESTS:.1f}초 대기 중...")
            time.sleep(SLEEP_BETWEEN_REQUESTS)

except KeyboardInterrupt:
    print("\n\n⚠️ 사용자가 중단했습니다!")
    print("📊 현재까지 진행 상황 저장 중...")
    
    # 중단 시에도 저장
    if new_data:
        all_data = existing_data + new_data
        save_progress(all_data, len(all_data), START_INDEX + NEW_SAMPLES)
        print("✅ 진행 상황 저장 완료!")
        print(f"   저장된 샘플: {len(new_data)}개")
        print(f"   다음 실행 시 {START_INDEX + len(new_data)}번째부터 시작됩니다.")
    
    sys.exit(0)

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

print(f"\n✅ 완료!")
print(f"\n📊 최종 통계:")
print(f"{'='*60}")
print(f"총 생성: {stats['completed']}개")
print(f"성공: {stats['success']}개 ({stats['success']/stats['completed']*100:.1f}%)")
print(f"실패: {stats['failed']}개 ({stats['failed']/stats['completed']*100:.1f}%)")
if stats['success'] > 0:
    print(f"평균 단어: {stats['avg_words']/stats['success']:.1f}")
    print(f"평균 문장: {stats['avg_sentences']/stats['success']:.1f}")
print(f"소요 시간: {elapsed/60:.1f}분")
print(f"처리 속도: {stats['completed']/(elapsed/60):.1f}개/분")
print(f"{'='*60}")

print(f"\n📁 저장 위치:")
print(f"  데이터: {data_path}")
print(f"  진행: {progress_path}")

print(f"\n📊 데이터 샘플:")
if new_data:
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

success_data = [d for d in new_data if d['gpt4_success']]

if success_data:
    words = [d['gpt4_words'] for d in success_data]
    sentences = [d['gpt4_sentences'] for d in success_data]

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
print("🎉 V10 Step 1 완료! (FREE TIER 버전)")
print("="*60)

total_created = len(all_data)
remaining_to_1000 = max(0, 1000 - total_created)
runs_needed = (remaining_to_1000 + NEW_SAMPLES - 1) // NEW_SAMPLES  # 올림

print(f"\n다음 단계:")
print(f"1. 데이터 확인: {data_path}")
print(f"2. 현재 총 데이터: {total_created}개")
if remaining_to_1000 > 0:
    print(f"3. 1000개까지 {remaining_to_1000}개 남음 → 약 {runs_needed}번 더 실행 필요")
    print(f"   (자동으로 이어서 생성됨)")
else:
    print(f"3. ✅ 1000개 달성! V10 Step 2로 이동 가능")

print(f"\n현재 상태:")
print(f"  총 데이터: {total_created}개")
print(f"  다음 실행 시: {total_created}번째부터 시작")
print(f"  목표 (1000개)까지: {remaining_to_1000}개 남음")

print("\n" + "="*60)
print("💡 FREE TIER 가이드:")
print("="*60)
print(f"RPM: 3 requests/minute")
print(f"RPD: 200 requests/day")
print(f"1회 실행: 최대 {NEW_SAMPLES}개 (안전)")
print(f"1000개 목표: 약 7번 실행")
print(f"예상 시간/회: ~{NEW_SAMPLES * SLEEP_BETWEEN_REQUESTS / 60:.0f}분")
print()
print("⚠️ 팁:")
print("  - 매일 실행하면 1주일 내 완성")
print("  - 중단해도 자동 저장됨 (Ctrl+C)")
print("  - 다시 실행하면 이어서 생성")
print("="*60)