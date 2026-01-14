"""
ArXiv-NewsBrief v4.4.3 Summarization Chatbot (GGUF) - CATEGORY SELECTOR
- Model: Qwen2.5-1.5B-Instruct fine-tuned -> GGUF (Q4_K_M)
- Inference: llama-cpp-python
- TTS: Google gTTS
- STT: Google Speech Recognition (Real-time recording)
- Translation (Korean UI): Google Gemini 2.5 Flash

✅ v4.4.3 Updates (2026-01-14):
- 📚 Category Dropdown: User-friendly research field selection
- 🔍 12 Major ArXiv Categories (AI, Physics, Math, Biology, etc.)
- 🎯 Automatic query generation based on selection

✅ v4.4.2 Features:
- 🎭 Dual Summary Styles: General Public (v4.4) vs Researcher (v4.2)
- 🎯 Auto Temperature/Prompt switching based on audience
- 📊 Style selector in sidebar

✅ ArXiv Categories:
┌─────────────────────┬──────────────────────────────────────┐
│ Category            │ ArXiv Query                          │
├─────────────────────┼──────────────────────────────────────┤
│ 🤖 AI & ML          │ cs.AI OR cs.LG OR cs.CL OR stat.ML   │
│ 💻 Computer Science │ cs.*                                 │
│ 🔬 Physics          │ physics.*                            │
│ 🧮 Mathematics      │ math.*                               │
│ 🧬 Biology          │ q-bio.*                              │
│ 🧪 Chemistry        │ physics.chem-ph                      │
│ 🌌 Astrophysics     │ astro-ph.*                           │
│ ⚛️ Quantum Physics   │ quant-ph                             │
│ 💰 Economics        │ econ.* OR q-fin.*                    │
│ 📊 Statistics       │ stat.*                               │
│ 🏥 Medicine         │ q-bio.* OR physics.med-ph            │
│ 🔧 Engineering      │ cs.RO OR cs.SY OR physics.app-ph     │
└─────────────────────┴──────────────────────────────────────┘
"""

import base64
import io
import os
import pprint
from datetime import datetime

import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from langchain_google_genai import ChatGoogleGenerativeAI
from llama_cpp import Llama
from streamlit_mic_recorder import mic_recorder


# ================================
# 설정
# ================================

# ⭐ GGUF 경로
GGUF_MODEL_PATH = "./ArXiv-NewsBrief-1.5B-2k-v4.2/ArXiv-NewsBrief-Q4.2_K_M.gguf"

SUPPORTED_LANGUAGES = {
    "English": {"code": "en", "gtts": "en", "gsr": "en-US", "gemini_target": "English"},
    "Korean":  {"code": "ko", "gtts": "ko", "gsr": "ko-KR", "gemini_target": "Korean"},
}

# ================================
# ✅ v4.4.3: ArXiv Category Configurations
# ================================

ARXIV_CATEGORIES = {
    "🤖 AI & Machine Learning": {
        "query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:stat.ML",
        "description": "Artificial Intelligence, Machine Learning, Natural Language Processing, Statistics ML",
        "subcategories": "cs.AI (AI), cs.LG (Learning), cs.CL (Computation & Language), stat.ML (ML Statistics)"
    },
    "💻 Computer Science (All)": {
        "query": "cat:cs.*",
        "description": "All Computer Science fields including algorithms, software, systems, theory",
        "subcategories": "cs.* (all CS categories)"
    },
    "🔬 Physics (All)": {
        "query": "cat:physics.*",
        "description": "All Physics fields including condensed matter, high energy, atomic, etc.",
        "subcategories": "physics.* (all physics categories)"
    },
    "🧮 Mathematics": {
        "query": "cat:math.*",
        "description": "All Mathematics fields including algebra, analysis, geometry, number theory",
        "subcategories": "math.* (all math categories)"
    },
    "🧬 Biology & Life Sciences": {
        "query": "cat:q-bio.*",
        "description": "Quantitative Biology including genomics, neuroscience, population biology",
        "subcategories": "q-bio.* (biomolecules, populations, neurons, etc.)"
    },
    "🧪 Chemistry": {
        "query": "cat:physics.chem-ph",
        "description": "Chemical Physics including molecular dynamics, quantum chemistry",
        "subcategories": "physics.chem-ph"
    },
    "🌌 Astrophysics & Cosmology": {
        "query": "cat:astro-ph.*",
        "description": "Astrophysics including cosmology, galaxies, stellar physics, exoplanets",
        "subcategories": "astro-ph.* (CO, GA, HE, IM, SR)"
    },
    "⚛️ Quantum Physics": {
        "query": "cat:quant-ph",
        "description": "Quantum Physics including quantum computing, quantum information, foundations",
        "subcategories": "quant-ph"
    },
    "💰 Economics & Finance": {
        "query": "cat:econ.* OR cat:q-fin.*",
        "description": "Economics and Quantitative Finance including econometrics, trading, risk",
        "subcategories": "econ.* (Econometrics), q-fin.* (Trading, Risk, Pricing)"
    },
    "📊 Statistics": {
        "query": "cat:stat.*",
        "description": "Statistics including methodology, theory, applications, machine learning",
        "subcategories": "stat.* (AP, CO, ME, ML, TH)"
    },
    "🏥 Medicine & Health": {
        "query": "cat:q-bio.* OR cat:physics.med-ph",
        "description": "Medical Physics and Quantitative Biology relevant to health sciences",
        "subcategories": "q-bio.*, physics.med-ph"
    },
    "🔧 Engineering & Robotics": {
        "query": "cat:cs.RO OR cat:cs.SY OR cat:physics.app-ph",
        "description": "Robotics, Systems & Control, Applied Physics",
        "subcategories": "cs.RO (Robotics), cs.SY (Systems), physics.app-ph (Applied)"
    }
}

# GGUF 추론 설정
DEFAULT_N_CTX = 2048
DEFAULT_N_THREADS = max(1, os.cpu_count() // 2)
DEFAULT_N_BATCH = 256
DEFAULT_TOP_P = 0.9

# ================================
# ✅ v4.4.2: Summary Style Configurations
# ================================

SUMMARY_STYLES = {
    "🎯 General Public (v4.4)": {
        "temperature": 0.6,
        "description": "NPR/BBC news style - Zero jargon, real-world examples",
        "target_audience": "일반인",
        "version": "v4.4",
        "key": "general"
    },
    "🔬 Researcher (v4.2)": {
        "temperature": 0.4,
        "description": "Professional tone - Technical accuracy, formal style",
        "target_audience": "연구자/전문가",
        "version": "v4.2",
        "key": "researcher"
    }
}

# ================================
# System Messages per Style
# ================================

# v4.4 System Message: General Public Style (일반인용)
SYSTEM_MESSAGE_GENERAL = (
    "You are writing a 20-second radio news brief for listeners with NO science background.\n"
    "\n"
    "CRITICAL RULES (MUST FOLLOW):\n"
    "\n"
    "1. EXACTLY TWO SENTENCES - NO MORE, NO LESS:\n"
    "   - Sentence 1: What did they do? (15-25 words)\n"
    "   - Sentence 2: Why does it matter? (15-25 words)\n"
    "   \n"
    "   ❌ FORBIDDEN:\n"
    "   - Three sentences (even if you want to add results)\n"
    "   - One sentence (too short)\n"
    "   - Adding 'Our results show...' as a third sentence\n"
    "   \n"
    "   ✅ CORRECT APPROACH:\n"
    "   - Merge results into sentence 2\n"
    "   - Example: '...ultimately achieving 6.88% improvement.'\n"
    "   - Count your sentences BEFORE outputting!\n"
    "\n"
    "2. ZERO JARGON - EXPLAIN LIKE TO A FRIEND:\n"
    "   ❌ NEVER USE:\n"
    "   - 'neural network' → use 'AI system' or 'computer program'\n"
    "   - 'language model' → use 'AI tool' or 'text generator'\n"
    "   - 'manifold' → use 'pattern' or 'shape'\n"
    "   - 'algorithm' → use 'method' or 'approach'\n"
    "   - 'parameter' → use 'setting'\n"
    "   - 'ensemble' → use 'combination'\n"
    "   - 'convolutional' → use 'pattern-finding'\n"
    "   \n"
    "   ✅ ALWAYS USE:\n"
    "   - Simple everyday words\n"
    "   - Real-world analogies\n"
    "   - Concrete examples\n"
    "\n"
    "3. SOUND LIKE NPR/BBC NEWS:\n"
    "   - Natural, conversational tone\n"
    "   - Smooth rhythm for reading aloud\n"
    "   - No academic language\n"
    "   - Confident and clear\n"
    "\n"
    "4. MAKE IT ACCESSIBLE:\n"
    "   - Use analogies: 'like organizing files on a computer'\n"
    "   - Focus on real-world impact: 'improve social media recommendations'\n"
    "   - Include concrete examples: 'traffic predictions', 'friend suggestions'\n"
    "   - Sound relatable and practical\n"
    "\n"
    "5. COUNT YOUR WORDS:\n"
    "   - Each sentence: 15-25 words MAX\n"
    "   - If over 25, split or simplify\n"
    "   - Keep it tight and focused\n"
    "\n"
    "PERFECT EXAMPLE (32 words, 2 sentences):\n"
    "\"Scientists developed a faster way to teach AI systems to recognize patterns in social network data. "
    "This breakthrough could improve friend suggestions on social media and detect fake accounts more effectively.\"\n"
    "\n"
    "✅ Why this works:\n"
    "- Exactly 2 sentences\n"
    "- Sentence 1: 16 words (what they did)\n"
    "- Sentence 2: 16 words (why it matters + real examples)\n"
    "- No jargon ('AI systems' not 'neural networks')\n"
    "- Real-world examples (social media, fake accounts)\n"
    "- Natural rhythm for TTS\n"
    "\n"
    "BAD EXAMPLE (Don't do this):\n"
    "\"This research examines how training shallow graph convolutional neural networks on manifold data "
    "aligns with underlying topological structures. The study establishes theoretical foundations. "
    "Results show 15% improvement.\"\n"
    "\n"
    "❌ Why this fails:\n"
    "- Three sentences (not two!)\n"
    "- Technical jargon ('convolutional', 'manifold', 'topological')\n"
    "- No real-world examples\n"
    "- Too academic\n"
    "\n"
    "Remember: You're explaining to someone listening while driving. Keep it simple, natural, and useful!"
)

# v4.2 System Message: Researcher Style (전문가용)
SYSTEM_MESSAGE_RESEARCHER = (
    "Summarize the following text in simple, clear English that anyone can understand. "
    "Make it as for the each script not for reading. Use no more than two complete sentences. "
    "Do not include my prompt message in result. Make sure to keep in professional tone.\n"
    "\n"
    "RULES:\n"
    "1. EXACTLY TWO SENTENCES:\n"
    "   - Sentence 1: Core contribution and method\n"
    "   - Sentence 2: Results and implications\n"
    "\n"
    "2. PROFESSIONAL TONE:\n"
    "   - Use technical terms when necessary\n"
    "   - Keep formal, academic style\n"
    "   - Focus on accuracy over accessibility\n"
    "\n"
    "3. MINIMIZE (NOT ELIMINATE) JARGON:\n"
    "   - Technical terms allowed if standard in field\n"
    "   - Brief explanations optional\n"
    "   - Maintain scientific precision\n"
    "\n"
    "4. WORD COUNT:\n"
    "   - Target: 40-55 words total\n"
    "   - Each sentence: 20-27 words\n"
    "\n"
    "EXAMPLE:\n"
    "\"This research introduces a novel graph convolutional approach for learning on manifold-structured data, "
    "demonstrating improved feature extraction compared to shallow architectures. "
    "Experiments show 15% accuracy gains on benchmark datasets, with applications in molecular property prediction.\"\n"
)


def get_system_message(style_key: str) -> str:
    """스타일에 따른 System Message 반환"""
    if style_key == "general":
        return SYSTEM_MESSAGE_GENERAL
    elif style_key == "researcher":
        return SYSTEM_MESSAGE_RESEARCHER
    else:
        return SYSTEM_MESSAGE_GENERAL  # default


# ================================
# Debug
# ================================
IS_DEBUG = False

def debug_log(title: str, data):
    """IS_DEBUG일 때만 터미널(stdout)에 로그 출력"""
    if not IS_DEBUG:
        return
    print("\n" + "=" * 80)
    print(f"[DEBUG] {title}")
    print("-" * 80)
    if isinstance(data, (dict, list)):
        pprint.pprint(data, width=140, sort_dicts=False)
    else:
        print(str(data))
    print("=" * 80)



import datetime as dt
import re
import time
from typing import List, Dict, Tuple, Optional

import requests
import feedparser


ARXIV_API = "http://export.arxiv.org/api/query"


def _days_ago(days: int) -> dt.datetime:
    return dt.datetime.utcnow() - dt.timedelta(days=days)


def _clean_whitespace(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s


def _parse_arxiv_id(entry_id: str) -> str:
    if not entry_id:
        return ""
    return entry_id.rsplit("/", 1)[-1].strip()


def fetch_recent_arxiv_candidates(
    days: int = 7,
    max_candidates: int = 50,
    query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:stat.ML",
    timeout_sec: int = 20,
    max_retries: int = 3,
    retry_delay: float = 3.0,
) -> List[Dict]:
    """
    arXiv에서 최근 논문 후보들을 가져옵니다.
    Rate limit 대응: 429 에러 시 재시도
    """
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_candidates,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    for attempt in range(max_retries):
        try:
            r = requests.get(ARXIV_API, params=params, timeout=timeout_sec)
            
            # ✅ Rate limit 체크
            if r.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)  # 3초, 6초, 9초
                    print(f"⚠️ ArXiv rate limit hit. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    raise requests.exceptions.HTTPError(
                        f"ArXiv API rate limit exceeded after {max_retries} retries. "
                        f"Please wait a few minutes before trying again."
                    )
            
            r.raise_for_status()
            break  # 성공하면 루프 탈출
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"⚠️ Request timeout. Retrying... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            else:
                raise
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1 and "429" in str(e):
                wait_time = retry_delay * (attempt + 1)
                print(f"⚠️ Request failed. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                raise

    feed = feedparser.parse(r.text)
    cutoff = _days_ago(days)

    out = []
    for e in feed.entries:
        published_dt = None
        published = getattr(e, "published", None)
        if published:
            try:
                published_dt = dt.datetime(*e.published_parsed[:6])
            except Exception:
                published_dt = None

        if published_dt and published_dt < cutoff:
            continue

        updated_dt = None
        updated = getattr(e, "updated", None)
        if updated and getattr(e, "updated_parsed", None):
            try:
                updated_dt = dt.datetime(*e.updated_parsed[:6])
            except Exception:
                updated_dt = None

        arxiv_id = _parse_arxiv_id(getattr(e, "id", ""))
        title = _clean_whitespace(getattr(e, "title", ""))
        abstract = _clean_whitespace(getattr(e, "summary", ""))

        out.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "published": published_dt.isoformat() if published_dt else None,
            "published_dt": published_dt,
            "updated": updated_dt.isoformat() if updated_dt else None,
            "updated_dt": updated_dt,
            "link": getattr(e, "link", None),
        })

    return out


def fetch_citations_semantic_scholar(
    arxiv_ids: List[str],
    timeout_sec: int = 20,
    sleep_sec: float = 0.0,
) -> Dict[str, int]:
    """Semantic Scholar batch API로 citationCount를 조회합니다."""
    if not arxiv_ids:
        return {}

    out = {}
    for aid in arxiv_ids:
        if not aid:
            continue
        url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{aid}"
        try:
            rr = requests.get(url, params={"fields": "citationCount"}, timeout=timeout_sec)
            if rr.status_code == 200:
                jj = rr.json()
                out[aid] = int(jj.get("citationCount") or 0)
            else:
                out[aid] = 0
        except Exception:
            out[aid] = 0

        if sleep_sec > 0:
            time.sleep(sleep_sec)

    return out


def get_top_recent_papers_pipe_string(
    days: int = 7,
    top_k: int = 3,
    query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:stat.ML",
    max_candidates: int = 50,
    prefer_citations: bool = True,
    delimiter: str = " | ",
) -> Tuple[str, List[Dict]]:
    """최근 논문 가져오기"""
    candidates = fetch_recent_arxiv_candidates(
        days=days,
        max_candidates=max_candidates,
        query=query,
    )

    if not candidates:
        return ("", [])

    citations = {}
    if prefer_citations:
        arxiv_ids = [c["arxiv_id"] for c in candidates if c.get("arxiv_id")]
        arxiv_ids = arxiv_ids[: min(len(arxiv_ids), 30)]
        citations = fetch_citations_semantic_scholar(arxiv_ids, sleep_sec=0.2)

    for c in candidates:
        aid = c.get("arxiv_id")
        c["citationCount"] = int(citations.get(aid, 0)) if citations else 0

    def _sort_key(x):
        pub = x.get("published") or ""
        return (x.get("citationCount", 0), pub)

    if prefer_citations and citations:
        ranked = sorted(candidates, key=_sort_key, reverse=True)
    else:
        ranked = sorted(candidates, key=lambda x: x.get("published") or "", reverse=True)

    selected = ranked[:top_k]

    blocks = []
    for i, p in enumerate(selected, 1):
        title = p.get("title", "").strip()
        abstract = p.get("abstract", "").strip()
        aid = p.get("arxiv_id", "").strip()
        ccount = p.get("citationCount", 0)

        header = f"[{i}] {title} (arXiv:{aid})"
        if prefer_citations:
            header += f" — citations: {ccount}"

        block = f"{header}\n{abstract}"
        blocks.append(block)

    pipe_joined = delimiter.join(blocks)
    return pipe_joined, selected



# ================================
# 세션 상태 초기화
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm" not in st.session_state:
    st.session_state.llm = None

if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

if "autoplay_audio_html" not in st.session_state:
    st.session_state.autoplay_audio_html = None

if "latest_papers_blob" not in st.session_state:
    st.session_state.latest_papers_blob = ""
if "latest_papers_items" not in st.session_state:
    st.session_state.latest_papers_items = []

if "recorded_audio" not in st.session_state:
    st.session_state.recorded_audio = None

if "last_selected_category" not in st.session_state:
    st.session_state.last_selected_category = None


# ================================
# GGUF 모델 로드 함수
# ================================
@st.cache_resource
def load_gguf_model(model_path: str, n_ctx: int, n_threads: int, n_batch: int):
    with st.spinner("🔄 Loading GGUF model..."):
        abs_path = os.path.abspath(model_path)
        st.info(f"Loading GGUF from: {abs_path}")

        if not os.path.exists(abs_path):
            st.error(f"❌ GGUF not found: {abs_path}")
            return None

        try:
            llm = Llama(
                model_path=abs_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_batch=n_batch,
                verbose=False,
            )
            st.success("✅ GGUF model loaded successfully!")
            return llm
        except Exception as e:
            st.error(f"❌ GGUF loading failed: {e}")
            return None


# ================================
# ChatML 프롬프트 빌더
# ================================
def build_chatml_prompt(messages: list[dict]) -> str:
    out = []
    for m in messages:
        role = (m.get("role") or "").strip()
        content = (m.get("content") or "").strip()
        out.append(f"<|im_start|>{role}\n{content}\n<|im_end|>\n")
    out.append("<|im_start|>assistant\n")
    return "".join(out)


# ================================
# ✅ v4.4.2: 스타일 기반 요약 함수
# ================================
def summarize_with_gguf(
    text: str,
    llm: Llama,
    system_message: str,
    max_new_tokens: int = 120,
    temperature: float = 0.6,
    top_p: float = 0.9,
) -> str:
    if llm is None:
        return "⚠️ Model not loaded"

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": text},
    ]
    prompt = build_chatml_prompt(messages)

    debug_log("GGUF prompt (preview)", {
        "len_chars": len(prompt),
        "head": prompt[:800],
        "tail": prompt[-200:] if len(prompt) > 200 else prompt,
    })

    try:
        out = llm(
            prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=["<|im_end|>", "</s>", "<|endoftext|>"],
        )
        generated = out["choices"][0]["text"].strip()
        generated = generated.replace("<|im_end|>", "").strip()
        return generated
    except Exception as e:
        return f"⚠️ Summarization failed: {e}"


# ================================
# 번역 함수 (Gemini)
# ================================
def translate_with_gemini(
    text: str,
    api_key: str,
    target_lang: str = "Korean",
    style_key: str = "general",  # ✅ v4.4.3: 스타일 파라미터 추가
    max_tokens: int = 3072,
    max_retries: int = 2,
) -> str:
    """Gemini로 번역 (스타일별 프롬프트)"""
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,
            max_tokens=max_tokens,
            google_api_key=api_key,
        )

        # ✅ v4.4.3: 스타일에 따른 프롬프트 선택
        if style_key == "general":
            # General Public 스타일: 괄호 안 영문 용어 제거
            base_prompt = f"""Translate the following text into {target_lang}.

CRITICAL RULES:
1. Keep it natural and clear for general audiences
2. Preserve numbers, proper nouns, and dates exactly as they appear
3. Do NOT add English terms in parentheses (e.g., avoid "제한된 역학(constrained dynamics)")
4. Do NOT add abbreviations in parentheses (e.g., avoid "TDDFT", "AI")
5. Translate technical terms to simple {target_lang} equivalents without showing the original English
6. Do not add new information - only translate what is provided
7. Output only the translated text with no explanations or notes

Examples of what NOT to do:
❌ "시간 의존 밀도 범함수 이론(Time-Dependent Density-Functional Theory, TDDFT)"
✅ "시간 의존 밀도 범함수 이론"

❌ "제한된 역학(constrained dynamics)"
✅ "제한된 역학"

❌ "인공지능(AI)"
✅ "인공지능"

Text to translate:
{text}
"""
        else:
            # Researcher 스타일: 괄호 안 영문 용어 허용 (전문가용)
            base_prompt = f"""Translate the following text into {target_lang}.

Rules:
1. Keep professional and academic tone
2. Preserve numbers, proper nouns, and dates exactly as they appear
3. For technical terms, you MAY add English terms in parentheses if it helps clarity
   - Example: "시간 의존 밀도 범함수 이론(Time-Dependent Density-Functional Theory)"
4. Preserve technical accuracy over simplification
5. Do not add new information - only translate what is provided
6. Output only the translated text

Text to translate:
{text}
"""

        response = llm.invoke(base_prompt)
        translated = (response.content or "").strip()

        def looks_truncated(s: str) -> bool:
            if not s:
                return True
            ending_chars = '.!?。？！"\'""）)】]…'
            if s[-1] not in ending_chars:
                return True
            if s.endswith("이 연구는") or s.endswith("본 연구는"):
                return True
            return False

        tries = 0
        while tries < max_retries and looks_truncated(translated):
            tries += 1

            if style_key == "general":
                continuation_prompt = f"""The translation output seems truncated.
Continue the translation in {target_lang} from where it left off.

CRITICAL RULES:
- Do NOT repeat the already translated part
- Do NOT add English terms in parentheses
- Do NOT add abbreviations in parentheses
- Do NOT add any new information
- Output only the continuation text

Already translated:
{translated}

Original text:
{text}
"""
            else:
                continuation_prompt = f"""The translation output seems truncated.
Continue the translation in {target_lang} from where it left off.

Rules:
- Do NOT repeat the already translated part
- Do NOT add any new information
- Output only the continuation text

Already translated:
{translated}

Original text:
{text}
"""
            
            cont_resp = llm.invoke(continuation_prompt)
            cont = (cont_resp.content or "").strip()

            if not cont or cont in translated:
                break

            translated = (translated.rstrip() + " " + cont.lstrip()).strip()

        return translated

    except Exception as e:
        return f"⚠️ Gemini translation failed: {e}"


def summarize_then_translate_if_needed(
    user_text: str,
    llm_local: Llama,
    system_message: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    ui_lang_display: str,
    gemini_api_key: str | None,
    enable_translation: bool,
    style_key: str = "general",  # ✅ v4.4.3: 스타일 파라미터 추가
) -> str:
    summary = summarize_with_gguf(
        user_text,
        llm_local,
        system_message,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
    )

    debug_log("GGUF summary output", {
        "len_chars": len(summary),
        "head": summary[:600],
        "tail": summary[-200:] if len(summary) > 200 else summary
    })

    if summary.startswith("⚠️"):
        return summary

    if ui_lang_display == "Korean" and enable_translation:
        if not gemini_api_key:
            return "⚠️ Korean output requires Gemini API Key for translation."

        translated = translate_with_gemini(
            summary, 
            gemini_api_key, 
            target_lang="Korean",
            style_key=style_key  # ✅ v4.4.3: 스타일 전달
        )
        if translated.startswith("⚠️"):
            return f"{translated}\n\n---\n(Original summary)\n{summary}"
        return translated

    return summary


# ================================
# ✅ 개선된 뉴스 스크립트 템플릿
# ================================
def format_publication_dates(papers: List[Dict]) -> str:
    """날짜 포맷팅 (중복 제거)"""
    dates = []
    for p in papers:
        pub_dt = p.get("published_dt")
        if pub_dt and isinstance(pub_dt, dt.datetime):
            dates.append(pub_dt)
    
    if not dates:
        return "recent days"
    
    dates = sorted(set(dates))
    
    if len(dates) == 1:
        d = dates[0]
        return d.strftime("%B %d, %Y")
    elif len(dates) == 2:
        d1, d2 = dates
        if d1.date() == d2.date():
            return d1.strftime("%B %d, %Y")
        elif d1.year == d2.year and d1.month == d2.month:
            return f"{d1.strftime('%B')} {d1.day} and {d2.day}, {d1.year}"
        else:
            return f"{d1.strftime('%B %d')} and {d2.strftime('%B %d')}, {d1.year}"
    else:
        first = dates[0]
        last = dates[-1]
        if first.date() == last.date():
            return first.strftime("%B %d, %Y")
        return f"{first.strftime('%B %d')} to {last.strftime('%B %d')}, {first.year}"


def get_ordinal_word(n: int) -> str:
    """숫자를 서수 단어로 변환"""
    words = ["First", "Second", "Third", "Fourth", "Fifth"]
    if 1 <= n <= len(words):
        return words[n-1]
    return f"{n}th"


def build_news_script_template_en(papers: List[Dict], summaries_en: List[str], category_name: str = "AI") -> str:
    """뉴스 브리핑 템플릿"""
    lines = []
    
    n_papers = len(papers)
    date_str = format_publication_dates(papers)
    
    # ✅ v4.4.3: 카테고리명 추출 (이모지 제거)
    # "🤖 AI & Machine Learning" → "AI & Machine Learning"
    clean_category = category_name.split(" ", 1)[1] if " " in category_name else category_name
    
    if n_papers == 1:
        lines.append(f"Here's your {clean_category} research brief. Today, we're covering one paper published on {date_str}.")
    else:
        lines.append(f"Here's your {clean_category} research brief. Today, we're covering {n_papers} papers published on {date_str}.")
    
    lines.append("")
    
    for i, (p, s) in enumerate(zip(papers, summaries_en), start=1):
        ordinal = get_ordinal_word(i)
        s = _clean_whitespace(s)
        lines.append(f"{ordinal}, {s}")
        lines.append("")
    
    lines.append("That's your update—links to the full papers are available if you want more details.")
    
    return "\n".join(lines).strip()


def make_news_script_translate_only(
    selected_papers: List[Dict],
    llm_local: Llama,
    system_message: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    ui_lang_display: str,
    gemini_api_key: str | None,
    enable_translation: bool,
    category_name: str = "AI",
    style_key: str = "general",  # ✅ v4.4.3: 스타일 파라미터 추가
    progress_cb=None,
) -> str:
    """뉴스 스크립트 생성"""
    if not selected_papers:
        return "⚠️ No papers selected."
    if llm_local is None:
        return "⚠️ Model not loaded"

    n_papers = len(selected_papers)
    total_steps = n_papers + (1 if (ui_lang_display == "Korean" and enable_translation) else 0)

    summaries_en: List[str] = []
    for idx, p in enumerate(selected_papers, start=1):
        title = _clean_whitespace(p.get("title", f"Paper {idx}"))
        if callable(progress_cb):
            progress_cb(f"{idx}/{n_papers} 요약 추론중... — {title}", idx, total_steps)

        abs_text = (p.get("abstract") or "").strip()
        if not abs_text:
            summaries_en.append("⚠️ Missing abstract.")
            continue

        s = summarize_with_gguf(
            abs_text,
            llm_local,
            system_message,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        summaries_en.append(_clean_whitespace(s))

    script_en = build_news_script_template_en(selected_papers, summaries_en, category_name)

    if ui_lang_display == "Korean" and enable_translation:
        if not gemini_api_key:
            return "⚠️ Korean output requires Gemini API Key for translation."

        if callable(progress_cb):
            progress_cb("한-영 번역중...", n_papers + 1, total_steps)

        translated = translate_with_gemini(
            script_en, 
            gemini_api_key, 
            target_lang="Korean",
            style_key=style_key  # ✅ v4.4.3: 스타일 전달
        )
        if translated.startswith("⚠️"):
            return f"{translated}\n\n---\n(English script)\n{script_en}"
        return translated.strip()

    return script_en.strip()



# ================================
# TTS 함수 (gTTS)
# ================================
def text_to_speech(text: str, lang_code: str = "en") -> str:
    if not text.strip():
        return ""

    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        with io.BytesIO() as audio_buffer:
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return f'<audio controls><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
    except Exception as e:
        st.warning(f"⚠️ TTS failed: {e}")
        return ""


def enable_autoplay(audio_html: str) -> str:
    if not audio_html:
        return ""
    if "<audio controls>" in audio_html:
        return audio_html.replace("<audio controls>", "<audio controls autoplay playsinline>")
    if "<audio" in audio_html and "autoplay" not in audio_html:
        return audio_html.replace("<audio", "<audio autoplay playsinline", 1)
    return audio_html


# ================================
# STT 함수 수정 (v4.4.2 - Fixed)
# ================================

def speech_to_text_from_bytes(audio_bytes: bytes, lang_code: str = "en-US") -> str:
    """
    녹음된 오디오 바이트를 텍스트로 변환
    
    ✅ v4.4.2 Fixes:
    - Proper audio format conversion
    - 16kHz resampling for Google SR
    - Ambient noise filtering
    - Volume normalization
    - Better error messages
    """
    recognizer = sr.Recognizer()
    
    # ✅ 잡음 필터링 설정 최적화
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment = audio_segment.set_channels(1)
        
        if audio_segment.dBFS < -30:
            gain = min(-30 - audio_segment.dBFS, 20)
            audio_segment = audio_segment + gain
        
        wav_buffer = io.BytesIO()
        audio_segment.export(
            wav_buffer, 
            format="wav",
            parameters=["-ar", "16000", "-ac", "1"]
        )
        wav_buffer.seek(0)
        
        with sr.AudioFile(wav_buffer) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data, language=lang_code)
        return text.strip()

    except sr.UnknownValueError:
        return "⚠️ Could not understand audio. Please speak clearly and try again."
    except sr.RequestError as e:
        return f"⚠️ Google SR service error: {e}"
    except Exception as e:
        return f"⚠️ STT failed: {str(e)[:100]}"


# ================================
# UI 유틸
# ================================
def clear_history():
    st.session_state.messages = []


# ================================
# Streamlit UI
# ================================
st.set_page_config(page_title="ArXiv-NewsBrief v4.4.3", page_icon="📰", layout="wide")

st.title("📰 ArXiv-NewsBrief v4.4.3 Chatbot (GGUF)")
st.caption("✨ v4.4.3: Research Category Selector | v4.4.2: Dual Summary Styles | GGUF(Q4_K_M) | llama.cpp CPU")

# v4.4.3 개선사항 안내
with st.expander("✨ v4.4.3 New Feature: Category Selector", expanded=False):
    st.markdown("""
    ### 📚 Choose Your Research Field
    
    Select from 12 major ArXiv categories:
    
    **🤖 AI & Machine Learning** - cs.AI, cs.LG, cs.CL, stat.ML
    **💻 Computer Science** - All CS fields
    **🔬 Physics** - All physics fields
    **🧮 Mathematics** - All math fields
    **🧬 Biology & Life Sciences** - Quantitative biology
    **🧪 Chemistry** - Chemical physics
    **🌌 Astrophysics** - Cosmology, galaxies, stellar
    **⚛️ Quantum Physics** - Quantum computing, information
    **💰 Economics** - Econometrics, quantitative finance
    **📊 Statistics** - Methodology, theory, ML stats
    **🏥 Medicine** - Medical physics, health sciences
    **🔧 Engineering** - Robotics, systems, applied physics
    
    No need to write complex queries - just pick your field!
    """)


with st.sidebar:
    st.header("⚙️ Settings")

    # Language 선택
    lang_display = st.selectbox("Language", list(SUPPORTED_LANGUAGES.keys()))
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    gtts_lang = lang_info["gtts"]
    gsr_lang = lang_info["gsr"]

    st.markdown("---")
    
    # ✅ v4.4.3: Research Category (Language 다음)
    st.header("📚 Research Category")
    
    # Category 드롭다운
    selected_category = st.selectbox(
        "Choose research field",
        list(ARXIV_CATEGORIES.keys()),
        index=0,
        help="Select your field of interest"
    )
    
    # 카테고리 변경 감지 및 캐시 초기화
    if st.session_state.last_selected_category != selected_category:
        st.session_state.latest_papers_blob = ""
        st.session_state.latest_papers_items = []
        st.session_state.last_selected_category = selected_category
        if st.session_state.last_selected_category is not None:
            st.sidebar.success(f"✅ Category changed to: {selected_category}")
    
    # 선택된 카테고리 정보
    category_info = ARXIV_CATEGORIES[selected_category]
    fetch_query = category_info["query"]
    
    # 카테고리 설명 표시
    with st.expander("ℹ️ Category Info"):
        st.caption(f"**Description:** {category_info['description']}")
        st.caption(f"**Subcategories:** {category_info['subcategories']}")
        st.caption(f"**Query:** `{fetch_query}`")

    st.markdown("---")
    
    # Summary Style 선택
    st.header("🎭 Summary Style")
    style_display = st.selectbox(
        "Target Audience",
        list(SUMMARY_STYLES.keys()),
        help="Choose style based on your audience"
    )
    
    style_config = SUMMARY_STYLES[style_display]
    style_key = style_config["key"]
    
    st.caption(f"📝 {style_config['description']}")
    st.caption(f"👥 Target: {style_config['target_audience']}")
    st.caption(f"🌡️ Temperature: {style_config['temperature']}")
    st.caption(f"📌 Version: {style_config['version']}")

    st.markdown("---")
    gemini_api_key = st.text_input("Gemini API Key (Optional)", type="password")

    st.markdown("---")
    st.header("🤖 Model Settings")

    use_local_model = st.checkbox("Use Local GGUF Model", value=True)
    max_new_tokens = st.slider("Max tokens", 50, 250, 120)

    temperature = style_config["temperature"]
    st.info(f"🌡️ Temperature: **{temperature}** (auto-set by style)")
    
    top_p = st.slider("Top-p", 0.1, 1.0, DEFAULT_TOP_P)

    st.markdown("---")
    st.subheader("⚙️ GGUF Runtime")
    n_ctx = st.selectbox("Context (n_ctx)", [1024, 2048, 4096], index=1)
    n_threads = st.slider("Threads (n_threads)", 1, max(1, os.cpu_count()), DEFAULT_N_THREADS)
    n_batch = st.selectbox("Batch (n_batch)", [64, 128, 256, 512], index=2)

    st.markdown("---")
    st.header("🌐 Translation")
    enable_translation = st.checkbox("Enable Gemini Translation (for Korean)", value=True)
    st.caption("Korean 선택 시: GGUF 요약 → Gemini 번역 → TTS")

    st.markdown("---")
    st.header("🔊 Audio Settings")
    enable_tts = st.checkbox("Enable TTS", value=True)

    st.markdown("---")
    st.header("🎮 Controls")
    if st.button("Clear History", use_container_width=True):
        clear_history()
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Load/Reload GGUF", use_container_width=True, type="primary"):
        st.session_state.llm = None
        st.session_state.model_loaded = False
        st.cache_resource.clear()
        st.rerun()

    st.markdown("---")
    st.header("🪵 Debug")
    IS_DEBUG = st.checkbox("Show debug logs", value=False)


# ================================
# 모델 로드 (최초 1회)
# ================================
if use_local_model and not st.session_state.model_loaded:
    llm = load_gguf_model(GGUF_MODEL_PATH, n_ctx=n_ctx, n_threads=n_threads, n_batch=n_batch)
    if llm:
        st.session_state.llm = llm
        st.session_state.model_loaded = True


# rerun 직후 autoplay 오디오
if enable_tts and st.session_state.autoplay_audio_html:
    st.markdown(enable_autoplay(st.session_state.autoplay_audio_html), unsafe_allow_html=True)
    st.session_state.autoplay_audio_html = None


# 현재 선택된 스타일의 System Message
current_system_message = get_system_message(style_key)


# ================================
# Latest Papers 섹션
# ================================
with st.sidebar:
    st.markdown("---")
    st.header("🧠 Latest Papers")
    fetch_days = st.slider("Lookback days", 1, 30, 7)
    fetch_top_k = st.slider("How many papers", 1, 10, 3)
    prefer_citations = st.checkbox("Prefer citations (Semantic Scholar)", value=True)
    delimiter = st.text_input("Delimiter", value="\\n|\\n")
    
    st.markdown("---")
    st.header("📰 News Brief Settings")
    news_brief_count = st.selectbox(
        "Papers in News Brief", 
        [1, 2, 3, 4, 5], 
        index=1,
        help="뉴스 브리핑에 포함할 논문 개수 (기본: 2개)"
    )
    st.caption(f"✅ News Brief will summarize **{news_brief_count}** paper(s)")


st.subheader(f"🗞️ Latest Papers: {selected_category}")

cols = st.columns([1, 1, 1, 2])

with cols[0]:
    fetch_btn = st.button("📌 Fetch papers", use_container_width=True)

with cols[1]:
    send_btn = st.button("➡️ Send to chat", use_container_width=True, disabled=(not st.session_state.latest_papers_blob))

with cols[2]:
    news_btn = st.button("📰 Make News Brief", use_container_width=True)

with cols[3]:
    st.caption(f"Fetch → top {news_brief_count} → summarize ({style_config['version']}) → (Korean) translate → (opt) TTS")


# Fetch 실행
if fetch_btn:
    with st.spinner(f"🔎 Fetching {selected_category} papers from arXiv..."):
        try:
            blob, items = get_top_recent_papers_pipe_string(
                days=int(fetch_days),
                top_k=int(fetch_top_k),
                query=fetch_query,  # ✅ 드롭다운에서 선택된 쿼리 사용
                max_candidates=50,
                prefer_citations=prefer_citations,
                delimiter=delimiter.encode("utf-8").decode("unicode_escape")
            )

            if not blob.strip():
                st.warning("⚠️ No papers found. Try adjusting parameters.")
            else:
                st.session_state.latest_papers_blob = blob
                st.session_state.latest_papers_items = items
                st.success(f"✅ Fetched {len(items)} {selected_category} papers.")
        except requests.exceptions.HTTPError as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                st.error(
                    "🚫 **ArXiv API Rate Limit Exceeded**\n\n"
                    "ArXiv API has temporarily blocked requests. This is normal.\n\n"
                    "**Solutions:**\n"
                    "1. Wait 3-5 minutes before trying again\n"
                    "2. Reduce 'How many papers' setting\n"
                    "3. Use cached papers if available\n\n"
                    "💡 Tip: ArXiv allows ~1 request per 3 seconds"
                )
            else:
                st.error(f"❌ ArXiv API error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Fetch failed: {str(e)}\n\nPlease try again in a few moments.")


# 결과 표시
if st.session_state.latest_papers_blob:
    st.text_area(
        "Fetched abstracts (pipe-separated)",
        value=st.session_state.latest_papers_blob,
        height=320
    )

    with st.expander("Show metadata"):
        for p in st.session_state.latest_papers_items:
            st.write({
                "arxiv_id": p.get("arxiv_id"),
                "published": p.get("published"),
                "citationCount": p.get("citationCount"),
                "link": p.get("link"),
                "title": p.get("title"),
            })


# Send to chat
if send_btn and st.session_state.latest_papers_blob:
    st.session_state.messages.append({
        "role": "user",
        "content": st.session_state.latest_papers_blob
    })
    st.rerun()


# Make News Brief
if news_btn:
    status_slot = st.empty()
    bar_slot = st.empty()
    progress_bar = bar_slot.progress(0)

    status_slot.info(f"Creating news brief ({news_brief_count} papers, {style_config['version']} style)...")

    def _progress(msg: str, step: int, total: int):
        status_slot.info(msg)
        pct = int((step / max(total, 1)) * 100)
        progress_bar.progress(min(max(pct, 0), 100))

    try:
        if not st.session_state.latest_papers_items:
            status_slot.info(f"🔎 Auto-fetching {selected_category} papers...")
            try:
                blob, items = get_top_recent_papers_pipe_string(
                    days=int(fetch_days),
                    top_k=int(fetch_top_k),
                    query=fetch_query,  # ✅ 드롭다운에서 선택된 쿼리 사용
                    max_candidates=50,
                    prefer_citations=prefer_citations,
                    delimiter=delimiter.encode("utf-8").decode("unicode_escape")
                )
                st.session_state.latest_papers_blob = blob or ""
                st.session_state.latest_papers_items = items or []
            except requests.exceptions.HTTPError as e:
                status_slot.empty()
                bar_slot.empty()
                if "429" in str(e) or "rate limit" in str(e).lower():
                    st.error(
                        "🚫 **ArXiv API Rate Limit**\n\n"
                        "Please wait 3-5 minutes, then try:\n"
                        "1. Click 'Fetch papers' first\n"
                        "2. Then click 'Make News Brief'"
                    )
                else:
                    st.error(f"❌ ArXiv error: {str(e)}")
                st.stop()

        if not st.session_state.latest_papers_items:
            status_slot.empty()
            bar_slot.empty()
            st.warning("⚠️ No papers available.")
            st.stop()

        if use_local_model and st.session_state.llm:
            selected = st.session_state.latest_papers_items[:news_brief_count]
            
            script = make_news_script_translate_only(
                selected_papers=selected,
                llm_local=st.session_state.llm,
                system_message=current_system_message,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                ui_lang_display=lang_display,
                gemini_api_key=gemini_api_key,
                enable_translation=enable_translation,
                category_name=selected_category,
                style_key=style_key,  # ✅ v4.4.3: 스타일 전달
                progress_cb=_progress,
            )
        else:
            script = "⚠️ No local GGUF model available."

        audio_html = ""
        if enable_tts and script and not script.startswith("⚠️"):
            status_slot.info("🔊 TTS generating...")
            progress_bar.progress(100)

            audio_html = text_to_speech(script, gtts_lang)
            st.session_state.autoplay_audio_html = audio_html

        paper_links = []
        for idx, p in enumerate(selected, start=1):
            paper_links.append({
                "index": idx,
                "title": p.get("title", f"Paper {idx}"),
                "link": p.get("link", ""),
                "arxiv_id": p.get("arxiv_id", "")
            })

        st.session_state.messages.append({
            "role": "assistant",
            "content": script + "\n",
            "audio_html": audio_html,
            "paper_links": paper_links,
            "style": style_display,
            "category": selected_category  # ✅ 카테고리 정보 저장
        })

        status_slot.empty()
        bar_slot.empty()
        st.rerun()

    except Exception as e:
        status_slot.empty()
        bar_slot.empty()
        st.error(f"❌ News brief failed: {e}")



# ================================
# 채팅 히스토리 렌더링
# ================================
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            content = msg.get("content", "")
            audio_html = msg.get("audio_html", "")
            paper_links = msg.get("paper_links", [])
            msg_style = msg.get("style", "")
            msg_category = msg.get("category", "")
            
            # ✅ v4.4.3: 카테고리 + 스타일 표시
            if msg_category and msg_style:
                st.caption(f"📚 Category: {msg_category} | 🎭 Style: {msg_style}")
            elif msg_style:
                st.caption(f"🎭 Style: {msg_style}")
            
            if content:
                st.markdown(content)
            
            if audio_html and enable_tts:
                if paper_links:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**🔊 Audio Player:**")
                        st.markdown(audio_html, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**📄 Paper Links:**")
                        for paper in paper_links:
                            idx = paper["index"]
                            title = paper["title"]
                            link = paper["link"]
                            
                            short_title = title[:47] + "..." if len(title) > 50 else title
                            
                            if link:
                                st.markdown(
                                    f'<a href="{link}" target="_blank" style="text-decoration:none;">'
                                    f'📑 <strong>논문 {idx}</strong></a><br/>'
                                    f'<small style="color:gray;">{short_title}</small>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(f"📑 **논문 {idx}** (링크 없음)")
                            
                            st.markdown("---")
                else:
                    st.markdown(audio_html, unsafe_allow_html=True)


# ================================
# 텍스트 입력 + 음성 녹음
# ================================
st.subheader("💬 Text Input & 🎤 Voice Recording")

col_input, col_mic = st.columns([4, 1])

with col_input:
    prompt = st.chat_input("Enter ArXiv paper text or abstract...")

with col_mic:
    st.markdown("**🎤 Record:**")
    audio = mic_recorder(
        start_prompt="🔴 Record",
        stop_prompt="⏹️ Stop",
        just_once=False,
        use_container_width=True,
        format="wav",
        callback=None,
        args=(),
        kwargs={},
        key="mic_recorder"
    )


# 음성 녹음 처리
if audio:
    with st.spinner("🎧 Transcribing recorded audio..."):
        audio_bytes = audio["bytes"]
        transcribed_text = speech_to_text_from_bytes(audio_bytes, gsr_lang)

    if transcribed_text and not transcribed_text.startswith("⚠️"):
        st.success(f"✅ Transcribed: {transcribed_text}")

        st.session_state.messages.append({
            "role": "user",
            "content": f"**[Voice Recording]:** {transcribed_text}"
        })

        with st.spinner("📝 Generating summary..."):
            if use_local_model and st.session_state.llm:
                summary = summarize_then_translate_if_needed(
                    transcribed_text,
                    st.session_state.llm,
                    current_system_message,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    ui_lang_display=lang_display,
                    gemini_api_key=gemini_api_key,
                    enable_translation=enable_translation,
                    style_key=style_key,  # ✅ v4.4.3: 스타일 전달
                )
            else:
                summary = "⚠️ No local GGUF model available."

        audio_html = ""
        if enable_tts and summary and not summary.startswith("⚠️"):
            audio_html = text_to_speech(summary, gtts_lang)
            st.session_state.autoplay_audio_html = audio_html

        st.session_state.messages.append({
            "role": "assistant",
            "content": summary,
            "audio_html": audio_html,
            "style": style_display
        })

        st.rerun()
    else:
        st.error(transcribed_text)


# 텍스트 입력 처리
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("📝 Generating summary..."):
        if use_local_model and st.session_state.llm:
            summary = summarize_then_translate_if_needed(
                prompt,
                st.session_state.llm,
                current_system_message,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                ui_lang_display=lang_display,
                gemini_api_key=gemini_api_key,
                enable_translation=enable_translation,
                style_key=style_key,  # ✅ v4.4.3: 스타일 전달
            )
        else:
            summary = "⚠️ No local GGUF model available."

    audio_html = ""
    if enable_tts and summary and not summary.startswith("⚠️"):
        audio_html = text_to_speech(summary, gtts_lang)
        st.session_state.autoplay_audio_html = audio_html

    st.session_state.messages.append({
        "role": "assistant",
        "content": summary,
        "audio_html": audio_html,
        "style": style_display
    })

    st.rerun()


# ================================
# 상태 표시
# ================================
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Status")

if use_local_model:
    if st.session_state.model_loaded:
        st.sidebar.success("✅ GGUF Model Loaded")
    else:
        st.sidebar.warning("⚠️ GGUF Model Not Loaded")
else:
    st.sidebar.info("ℹ️ Local GGUF Disabled")

if lang_display == "Korean" and enable_translation and not gemini_api_key:
    st.sidebar.warning("⚠️ Korean translation needs Gemini API Key")
elif lang_display == "Korean" and enable_translation and gemini_api_key:
    st.sidebar.success("✅ Gemini Translation Ready")

# ✅ 현재 설정 표시
st.sidebar.markdown("---")
st.sidebar.info(f"📚 Category: **{selected_category}**\n🎭 Style: **{style_display}**\n🌡️ Temperature: **{temperature}**")