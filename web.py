"""
ArXiv-NewsBrief v0.2 Summarization Chatbot (GGUF)
- Model: Qwen2.5-1.5B-Instruct fine-tuned -> GGUF (Q4_K_M)
- Inference: llama-cpp-python
- TTS: Google gTTS
- STT: Google Speech Recognition
- Translation (Korean UI): Google Gemini 2.5 Flash

✅ Update:
- 📰 Make News Brief 버튼은 언어/상태와 무관하게 항상 클릭 가능
- 버튼 클릭 시:
  - 최신 논문이 없으면 자동 Fetch
  - 3개 논문 abstract를 summarize_with_gguf로 3번 요약
  - 오프닝/클로징 포함 템플릿 스크립트 생성
  - ✅ 선택 언어가 Korean일 때만 영→한 번역(Gemini)
  - chat에 스크립트 추가 + (옵션) TTS autoplay
"""

import base64
import io
import os
import pprint  # ✅ (추가) 터미널 출력용

import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from langchain_google_genai import ChatGoogleGenerativeAI
from llama_cpp import Llama


# ================================
# 설정
# ================================

# ⭐ GGUF 경로 (프로젝트 경로에 맞게 수정)
GGUF_MODEL_PATH = "./ArXiv-NewsBrief-1.5B-2k-v4.2/ArXiv-NewsBrief-Q4.2_K_M.gguf"

SUPPORTED_LANGUAGES = {
    "English": {"code": "en", "gtts": "en", "gsr": "en-US", "gemini_target": "English"},
    "Korean":  {"code": "ko", "gtts": "ko", "gsr": "ko-KR", "gemini_target": "Korean"},
}

# GGUF 추론 설정 (CPU)
DEFAULT_N_CTX = 2048
DEFAULT_N_THREADS = max(1, os.cpu_count() // 2)
DEFAULT_N_BATCH = 256
DEFAULT_TEMPERATURE = 0.4
DEFAULT_TOP_P = 0.9

# Teacher 학습 시 사용한 시스템 메시지 (추론에서도 동일하게 사용)
SYSTEM_MESSAGE = (
    "Summarize the following text in simple, clear English that anyone can understand. "
    "Make it as for the each script not for reading. "
    "Use no more than two complete sentences. "
    "Do not include my prompt message in result. "
    "Make sure to keep in professional tone."
)

# ================================
# Debug  ✅ (변경) 터미널 출력 방식
# ================================
IS_DEBUG = False  # ✅ True면 디버그 로그 터미널 출력

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
SEMANTIC_SCHOLAR_BATCH = "https://api.semanticscholar.org/graph/v1/paper/batch"


def _days_ago(days: int) -> dt.datetime:
    return dt.datetime.utcnow() - dt.timedelta(days=days)


def _clean_whitespace(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s


def _parse_arxiv_id(entry_id: str) -> str:
    # entry.id 예: "http://arxiv.org/abs/2401.12345v2"
    if not entry_id:
        return ""
    return entry_id.rsplit("/", 1)[-1].strip()


def fetch_recent_arxiv_candidates(
    days: int = 7,
    max_candidates: int = 50,
    query: str = "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:stat.ML",
    timeout_sec: int = 20,
) -> List[Dict]:
    """
    arXiv에서 최근 논문 후보들을 가져옵니다.
    - sortBy=submittedDate&sortOrder=descending 로 최신순
    - 최근 {days}일 필터는 클라이언트에서 published 날짜로 필터링
    """
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_candidates,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    r = requests.get(ARXIV_API, params=params, timeout=timeout_sec)
    r.raise_for_status()

    feed = feedparser.parse(r.text)
    cutoff = _days_ago(days)

    out = []
    for e in feed.entries:
        # published는 UTC ISO 형태
        published = getattr(e, "published", None)
        published_dt = None
        if published:
            try:
                published_dt = dt.datetime(*e.published_parsed[:6])
            except Exception:
                published_dt = None

        if published_dt and published_dt < cutoff:
            continue

        arxiv_id = _parse_arxiv_id(getattr(e, "id", ""))
        title = _clean_whitespace(getattr(e, "title", ""))
        abstract = _clean_whitespace(getattr(e, "summary", ""))

        out.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "published": published_dt.isoformat() if published_dt else None,
            "link": getattr(e, "link", None),
        })

    return out


def fetch_citations_semantic_scholar(
    arxiv_ids: List[str],
    timeout_sec: int = 20,
    sleep_sec: float = 0.0,
) -> Dict[str, int]:
    """
    Semantic Scholar batch API로 citationCount를 조회합니다.
    - 무키로도 동작하지만, 호출 제한이 있을 수 있어 실패 시 빈 dict 반환 가능
    """
    if not arxiv_ids:
        return {}

    # ⚠️ 단건 조회 방식(느리지만 확실)
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
    """
    최근 {days}일 arXiv 후보 → (가능하면) citationCount로 정렬 → top_k 반환.
    - return: (pipe_joined_string, selected_items)
    """
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

# ✅ autoplay 1회 실행을 위한 상태
if "autoplay_audio_html" not in st.session_state:
    st.session_state.autoplay_audio_html = None

# ✅ 최신 논문 상태
if "latest_papers_blob" not in st.session_state:
    st.session_state.latest_papers_blob = ""
if "latest_papers_items" not in st.session_state:
    st.session_state.latest_papers_items = []


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
# ChatML 프롬프트 빌더 (Teacher messages 구조 재현)
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
# 요약 함수 (GGUF)
# ================================
def summarize_with_gguf(
    text: str,
    llm: Llama,
    max_new_tokens: int = 120,
    temperature: float = 0.4,
    top_p: float = 0.9,
) -> str:
    if llm is None:
        return "⚠️ Model not loaded"

    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
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
    max_tokens: int = 3072,
    max_retries: int = 2,
) -> str:
    """
    Gemini로 번역 (짤림 방지: 끊김 감지 + 이어쓰기)
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.4,
            max_tokens=max_tokens,
            google_api_key=api_key,
        )

        base_prompt = f"""Translate the following text into {target_lang}.
Rules:
- Keep it natural and clear for general audiences.
- Preserve numbers, proper nouns, and technical terms as appropriate.
- Do not add new information. Only translate.
- Output only the translated text.

Text:
{text}
"""

        response = llm.invoke(base_prompt)
        translated = (response.content or "").strip()

        def looks_truncated(s: str) -> bool:
            if not s:
                return True
            if s[-1] not in ".!?。？！\"”’）)】]…":
                return True
            if s.endswith("이 연구는") or s.endswith("본 연구는"):
                return True
            return False

        tries = 0
        while tries < max_retries and looks_truncated(translated):
            tries += 1

            continuation_prompt = f"""The translation output seems truncated.
Continue the translation in {target_lang} from where it left off.

Rules:
- Do NOT repeat the already translated part.
- Do NOT add any new information.
- Output only the continuation text.

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
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    ui_lang_display: str,
    gemini_api_key: str | None,
    enable_translation: bool,
) -> str:
    summary = summarize_with_gguf(
        user_text,
        llm_local,
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

        translated = translate_with_gemini(summary, gemini_api_key, target_lang="Korean")
        if translated.startswith("⚠️"):
            return f"{translated}\n\n---\n(Original summary)\n{summary}"
        return translated

    return summary


# ================================
# 📰 News Brief (Template + Korean-only translation)  ✅ FIXED
# ================================
def build_news_script_template_en(papers: List[Dict], summaries_en: List[str]) -> str:
    """
    고정 포맷:
    오프닝 1문장 → 논문1/2/3 한 문단씩 → 클로징 1문장
    """
    lines = []
    lines.append("Here’s your quick AI paper news brief with three highlights.")
    for i, (p, s) in enumerate(zip(papers, summaries_en), start=1):
        title = _clean_whitespace(p.get("title", f"Paper {i}"))
        s = _clean_whitespace(s)
        lines.append(f"{i}) {title}\n{s}")
    lines.append("That’s it for today—check the paper links if you want the full details.")
    return "\n\n".join(lines).strip()


def make_news_script_translate_only(
    selected_papers: List[Dict],
    llm_local: Llama,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    ui_lang_display: str,      # "English" / "Korean"
    gemini_api_key: str | None,
    enable_translation: bool,
    progress_cb=None,          # progress_cb(msg: str, step: int, total: int)
) -> str:
    """
    - 3개 논문 abstract 요약(영문) 3회
    - 오프닝/클로징 포함 템플릿 스크립트 생성(영문)
    - ✅ Korean일 때만 번역
    - 진행상태: msg + (step/total)
    """
    if not selected_papers:
        return "⚠️ No papers selected."
    if llm_local is None:
        return "⚠️ Model not loaded"

    papers = selected_papers[:3]
    total_steps = 3 + (1 if (ui_lang_display == "Korean" and enable_translation) else 0)

    summaries_en: List[str] = []
    for idx, p in enumerate(papers, start=1):
        title = _clean_whitespace(p.get("title", f"Paper {idx}"))
        if callable(progress_cb):
            progress_cb(f"{idx}/3 요약 추론중... — {title}", idx, total_steps)

        abs_text = (p.get("abstract") or "").strip()
        if not abs_text:
            summaries_en.append("⚠️ Missing abstract.")
            continue

        s = summarize_with_gguf(
            abs_text,
            llm_local,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        summaries_en.append(_clean_whitespace(s))

    script_en = build_news_script_template_en(papers, summaries_en)

    # Korean일 때만 번역
    if ui_lang_display == "Korean" and enable_translation:
        if not gemini_api_key:
            return "⚠️ Korean output requires Gemini API Key for translation."

        if callable(progress_cb):
            progress_cb("한-영 번역중...", 4, total_steps)  # 요청 문구 그대로

        translated = translate_with_gemini(script_en, gemini_api_key, target_lang="Korean")
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
# STT 함수 (Google SR)
# ================================
def speech_to_text(audio_data, lang_code: str = "en-US") -> str:
    recognizer = sr.Recognizer()

    try:
        audio_buffer = io.BytesIO()
        audio_data.export(audio_buffer, format="wav")
        audio_buffer.seek(0)

        audio_sr = sr.AudioData(audio_buffer.read(), sample_rate=16000, sample_width=2)
        text = recognizer.recognize_google(audio_sr, language=lang_code)
        return text

    except sr.UnknownValueError:
        return "⚠️ Could not understand audio"
    except sr.RequestError as e:
        return f"⚠️ Google SR error: {e}"
    except Exception as e:
        return f"⚠️ STT failed: {e}"


# ================================
# UI 유틸
# ================================
def clear_history():
    st.session_state.messages = []


# ================================
# Streamlit UI
# ================================
st.set_page_config(page_title="ArXiv-NewsBrief v4.0 (GGUF)", page_icon="📰", layout="wide")

st.title("📰 ArXiv-NewsBrief v4.2 Chatbot (GGUF)")
st.caption("GGUF(Q4_K_M) | llama.cpp 기반 CPU 추론 | (Korean UI) Gemini 번역 + TTS")

with st.sidebar:
    st.header("⚙️ Settings")

    lang_display = st.selectbox("Language", list(SUPPORTED_LANGUAGES.keys()))
    lang_info = SUPPORTED_LANGUAGES[lang_display]
    gtts_lang = lang_info["gtts"]
    gsr_lang = lang_info["gsr"]

    st.markdown("---")
    gemini_api_key = st.text_input("Gemini API Key (Optional)", type="password")

    st.markdown("---")
    st.header("🤖 Model Settings")

    use_local_model = st.checkbox("Use Local GGUF Model", value=True)
    max_new_tokens = st.slider("Max tokens", 50, 250, 120)

    temperature = st.slider("Temperature", 0.0, 1.2, DEFAULT_TEMPERATURE)
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
    enable_stt = st.checkbox("Enable STT", value=True)

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


# ✅ rerun 직후 autoplay 오디오가 있으면 먼저 재생
if enable_tts and st.session_state.autoplay_audio_html:
    st.markdown(enable_autoplay(st.session_state.autoplay_audio_html), unsafe_allow_html=True)
    st.session_state.autoplay_audio_html = None



# ================================
# 최신 AI 논문 몇개 가져오기 (Streamlit UX 개선)
# ================================
with st.sidebar:
    st.markdown("---")
    st.header("🧠 Latest Papers")
    fetch_days = st.slider("Lookback days", 1, 30, 7)
    fetch_top_k = st.slider("How many papers", 1, 10, 3)
    fetch_query = st.text_input(
        "arXiv query",
        value="cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:stat.ML"
    )
    prefer_citations = st.checkbox("Prefer citations (Semantic Scholar)", value=True)
    delimiter = st.text_input("Delimiter", value="\\n|\\n")
    st.caption("Tip: 최근 7일은 인용수가 거의 없을 수 있어요. 그래도 가능하면 citation으로 정렬 후, 실패 시 최신순 fallback됩니다.")


st.subheader("🗞️ Latest AI Papers (arXiv)")

# ✅ FIX: news_btn always enabled + auto-fetch on click
cols = st.columns([1, 1, 1, 2])

with cols[0]:
    fetch_btn = st.button("📌 Fetch papers", use_container_width=True)

with cols[1]:
    send_btn = st.button("➡️ Send to chat", use_container_width=True, disabled=(not st.session_state.latest_papers_blob))

with cols[2]:
    news_btn = st.button("📰 Make News Brief", use_container_width=True)  # ✅ always enabled

with cols[3]:
    st.caption("Fetch → top3 → summarize 3x → template script → (Korean only) translate → (optional) TTS autoplay")


# Fetch 실행
if fetch_btn:
    with st.spinner("🔎 Fetching recent papers from arXiv (and citations if enabled)..."):
        try:
            blob, items = get_top_recent_papers_pipe_string(
                days=int(fetch_days),
                top_k=int(fetch_top_k),
                query=fetch_query.strip(),
                max_candidates=50,
                prefer_citations=prefer_citations,
                delimiter=delimiter.encode("utf-8").decode("unicode_escape")
            )

            if not blob.strip():
                st.warning("⚠️ No papers found. Try increasing max days or adjusting query.")
            else:
                st.session_state.latest_papers_blob = blob
                st.session_state.latest_papers_items = items
                st.success(f"✅ Fetched {len(items)} papers.")
        except Exception as e:
            st.error(f"❌ Fetch failed: {e}")


# 결과 표시(항상)
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


# Send to chat 실행
if send_btn and st.session_state.latest_papers_blob:
    st.session_state.messages.append({
        "role": "user",
        "content": st.session_state.latest_papers_blob
    })
    st.rerun()


# ✅ Make News Brief 실행: papers 없으면 자동 fetch 후 생성
if news_btn:
    status_slot = st.empty()     # 텍스트 상태
    bar_slot = st.empty()        # progress bar
    progress_bar = bar_slot.progress(0)

    status_slot.info("Creating news brief (3 summaries + template + optional KO translation)...")

    def _progress(msg: str, step: int, total: int):
        # step: 1..total
        status_slot.info(msg)
        pct = int((step / max(total, 1)) * 100)
        progress_bar.progress(min(max(pct, 0), 100))

    try:
        # papers 없으면 자동 fetch
        if not st.session_state.latest_papers_items:
            status_slot.info("🔎 No fetched papers yet. Auto-fetching top papers...")
            blob, items = get_top_recent_papers_pipe_string(
                days=int(fetch_days),
                top_k=int(fetch_top_k),
                query=fetch_query.strip(),
                max_candidates=50,
                prefer_citations=prefer_citations,
                delimiter=delimiter.encode("utf-8").decode("unicode_escape")
            )
            st.session_state.latest_papers_blob = blob or ""
            st.session_state.latest_papers_items = items or []

        if not st.session_state.latest_papers_items:
            status_slot.empty()
            bar_slot.empty()
            st.warning("⚠️ No papers available. Try Fetch papers or adjust query/days.")
            st.stop()

        if use_local_model and st.session_state.llm:
            selected = st.session_state.latest_papers_items[:3]
            script = make_news_script_translate_only(
                selected_papers=selected,
                llm_local=st.session_state.llm,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                ui_lang_display=lang_display,
                gemini_api_key=gemini_api_key,
                enable_translation=enable_translation,
                progress_cb=_progress,
            )
        else:
            script = "⚠️ No local GGUF model available. Please load GGUF."

        # TTS 생성 + autoplay
        audio_html = ""
        if enable_tts and script and not script.startswith("⚠️"):
            status_slot.info("🔊 TTS generating...")
            progress_bar.progress(100)

            audio_html = text_to_speech(script, gtts_lang)
            st.session_state.autoplay_audio_html = audio_html

        st.session_state.messages.append({
            "role": "assistant",
            "content": script + "\n",
            "audio_html": audio_html
        })

        # ✅ 완료 → 상태/바 제거
        status_slot.empty()
        bar_slot.empty()
        st.rerun()

    except Exception as e:
        status_slot.empty()
        bar_slot.empty()
        st.error(f"❌ News brief failed: {e}")



# ================================
# 채팅 히스토리 렌더링  ✅ (유지)
# ================================
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            content = msg.get("content", "")
            audio_html = msg.get("audio_html", "")
            if content:
                st.markdown(content)
            if audio_html and enable_tts:
                st.markdown(audio_html, unsafe_allow_html=True)


# ================================
# 음성 입력 (STT)  ✅ (유지)
# ================================
if enable_stt:
    st.subheader("🎤 Voice Input")
    audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a"])

    if audio_file:
        audio_data = AudioSegment.from_file(audio_file)

        with st.spinner("🎧 Transcribing..."):
            transcribed_text = speech_to_text(audio_data, gsr_lang)

        if transcribed_text and not transcribed_text.startswith("⚠️"):
            st.success(f"✅ Transcribed: {transcribed_text}")

            st.session_state.messages.append({
                "role": "user",
                "content": f"**[Voice Input]:** {transcribed_text}"
            })

            with st.spinner("📝 Generating summary..."):
                if use_local_model and st.session_state.llm:
                    summary = summarize_then_translate_if_needed(
                        transcribed_text,
                        st.session_state.llm,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        ui_lang_display=lang_display,
                        gemini_api_key=gemini_api_key,
                        enable_translation=enable_translation,
                    )
                else:
                    summary = "⚠️ No local GGUF model available. Please load GGUF."

            audio_html = ""
            if enable_tts and summary and not summary.startswith("⚠️"):
                audio_html = text_to_speech(summary, gtts_lang)
                st.session_state.autoplay_audio_html = audio_html

            st.session_state.messages.append({
                "role": "assistant",
                "content": summary,
                "audio_html": audio_html
            })

            st.rerun()
        else:
            st.error(transcribed_text)


# ================================
# 텍스트 입력  ✅ (유지)
# ================================
st.subheader("💬 Text Input")
prompt = st.chat_input("Enter ArXiv paper text or abstract...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("📝 Generating summary..."):
        if use_local_model and st.session_state.llm:
            summary = summarize_then_translate_if_needed(
                prompt,
                st.session_state.llm,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                ui_lang_display=lang_display,
                gemini_api_key=gemini_api_key,
                enable_translation=enable_translation,
            )
        else:
            summary = "⚠️ No local GGUF model available. Please load GGUF."

    audio_html = ""
    if enable_tts and summary and not summary.startswith("⚠️"):
        audio_html = text_to_speech(summary, gtts_lang)
        st.session_state.autoplay_audio_html = audio_html

    st.session_state.messages.append({
        "role": "assistant",
        "content": summary,
        "audio_html": audio_html
    })

    st.rerun()


# ================================
# 상태 표시  ✅ (유지)
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
