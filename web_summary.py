"""
ArXiv-NewsBrief v0.1 Summarization Chatbot (GGUF)
- Model: Qwen2.5-1.5B-Instruct fine-tuned -> GGUF (Q4_K_M)
- Inference: llama-cpp-python
- TTS: Google gTTS
- STT: Google Speech Recognition
- Translation (Korean UI): Google Gemini 2.5 Flash
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


# ================================
# 세션 상태 초기화
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "llm" not in st.session_state:
    st.session_state.llm = None

if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False

# ✅ (추가) autoplay 1회 실행을 위한 상태
if "autoplay_audio_html" not in st.session_state:
    st.session_state.autoplay_audio_html = None


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
    """
    Teacher 학습 때의 messages=[{role,content}, ...]를
    llama.cpp/gguf에 넣을 ChatML 문자열로 변환
    """
    out = []
    for m in messages:
        role = (m.get("role") or "").strip()
        content = (m.get("content") or "").strip()
        out.append(f"<|im_start|>{role}\n{content}\n<|im_end|>\n")
    out.append("<|im_start|>assistant\n")
    return "".join(out)


# ================================
# 요약 함수 (GGUF) - Teacher 방식 messages 적용
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
# 번역 함수 (Gemini) - Korean 선택 시 사용
# ================================
def translate_with_gemini(text: str, api_key: str, target_lang: str = "Korean") -> str:
    """
    Gemini로 번역 (재시도 없음, IS_DEBUG=True일 때만 로그 출력)
    """
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
            max_tokens=1024,  # ✅ 번역 짤림 완화
            google_api_key=api_key,
        )

        prompt = f"""Translate the following text into {target_lang}.
Rules:
- Keep it natural and clear for general audiences.
- Preserve numbers, proper nouns, and technical terms as appropriate.
- Do not add new information. Only translate.
- Output only the translated text.

Text:
{text}
"""

        debug_log("Translation input (original summary)", {
            "len_chars": len(text),
            "head": text[:600],
            "tail": text[-200:] if len(text) > 200 else text
        })
        debug_log("Translation prompt (preview)", prompt[:1200])

        response = llm.invoke(prompt)
        translated = (response.content or "").strip()

        debug_log("Translation output", {
            "len_chars": len(translated),
            "head": translated[:600],
            "tail": translated[-200:] if len(translated) > 200 else translated
        })

        return translated

    except Exception as e:
        debug_log("Translation exception", str(e))
        return f"⚠️ Gemini translation failed: {e}"


def summarize_then_translate_if_needed(
    user_text: str,
    llm_local: Llama,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    ui_lang_display: str,     # "English" / "Korean"
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

    # Korean 선택 + 번역 활성화면 번역
    if ui_lang_display == "Korean" and enable_translation:
        if not gemini_api_key:
            return "⚠️ Korean output requires Gemini API Key for translation."

        translated = translate_with_gemini(summary, gemini_api_key, target_lang="Korean")
        if translated.startswith("⚠️"):
            return f"{translated}\n\n---\n(Original summary)\n{summary}"
        return translated

    return summary


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


# ✅ (추가) autoplay 변환: 준비되면 즉시 재생하도록
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

st.title("📰 ArXiv-NewsBrief v4.0 Chatbot (GGUF)")
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


# ✅ (추가) rerun 직후 autoplay 오디오가 있으면 먼저 재생 (플레이어 준비되면 바로 재생)
if enable_tts and st.session_state.autoplay_audio_html:
    st.markdown(enable_autoplay(st.session_state.autoplay_audio_html), unsafe_allow_html=True)
    st.session_state.autoplay_audio_html = None


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

            # ✅ TTS 생성해서 히스토리에 저장 + autoplay 예약
            audio_html = ""
            if enable_tts and summary and not summary.startswith("⚠️"):
                audio_html = text_to_speech(summary, gtts_lang)
                st.session_state.autoplay_audio_html = audio_html  # ✅ (추가) 다음 rerun에서 자동 재생

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

    # ✅ TTS 생성해서 히스토리에 저장 + autoplay 예약
    audio_html = ""
    if enable_tts and summary and not summary.startswith("⚠️"):
        audio_html = text_to_speech(summary, gtts_lang)
        st.session_state.autoplay_audio_html = audio_html  # ✅ (추가) 다음 rerun에서 자동 재생

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
