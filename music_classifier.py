# 감성 음악 분류기 - Spotify API 연동 포함

import streamlit as st
import pandas as pd
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# -------------------- Spotify API 인증 -------------------- #
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
else:
    st.error("Spotify API 인증 정보가 없습니다. SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET 환경변수를 설정해주세요.")
    sp = None

# -------------------- Spotify에서 트랙 정보 가져오기 -------------------- #
def get_track_info_from_spotify(title, artist):
    if not sp:
        return None, None
    
    query = f"track:{title} artist:{artist}"
    results = sp.search(q=query, type="track", limit=1)
    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        track_id = track["id"]
        features = sp.audio_features([track_id])[0]
        bpm = features["tempo"]
        duration = features["duration_ms"] // 1000
        return bpm, duration
    return None, None

# -------------------- 향상된 분류 알고리즘 -------------------- #
def classify_song(title, artist, bpm=None, duration=None):
    title_lower = title.lower()
    artist_lower = artist.lower()

    easy_artists = ["norah jones", "sade", "air", "lauv", "lisa ono", "jack johnson"]
    hard_artists = ["korn", "noisia", "metallica", "slipknot", "rage against the machine"]

    easy_keywords = ["love", "silence", "rain", "dream", "breathe", "acoustic", "smooth", "soft", "light"]
    hard_keywords = ["rage", "control", "dark", "blood", "scream", "burn", "power", "storm"]

    easy_detail_phrases = [
        "템포가 느리거나 일정하고, 반복되는 리듬이 안정감을 줘요.",
        "감정 표현이 절제되어 있고, 듣는 이를 조용히 감싸요.",
        "복잡하지 않은 구성 덕분에 흐름을 따라가기 쉬워요.",
        "백그라운드로 흘려듣기 좋아요, 집중 없이도 편안함을 느낄 수 있거든요."
    ]

    hard_detail_phrases = [
        "고조되는 전개와 갑작스러운 전환이 긴장을 유도해요.",
        "사운드가 풍부하고, 다층적인 구조로 깊은 몰입을 요구해요.",
        "감정을 강하게 분출하며 듣는 사람의 에너지를 자극해요.",
        "복잡하고 예측 불가능한 흐름이라 쉽게 듣기는 어렵지만 그만큼 강렬해요."
    ]

    bpm_phrases = []
    if bpm:
        if bpm < 90:
            bpm_phrases.append("템포가 매우 느려서 마음이 차분해져요.")
        elif bpm < 110:
            bpm_phrases.append("편안한 리듬감으로 흐르듯이 이어져요.")
        elif bpm > 140:
            bpm_phrases.append("빠른 템포가 곡의 에너지를 극대화시켜요.")

    if duration:
        if duration < 150:
            bpm_phrases.append("짧은 곡 길이로 강렬하게 휘몰아치는 느낌이에요.")
        elif duration > 300:
            bpm_phrases.append("긴 러닝타임 덕분에 서서히 몰입하게 돼요.")

    score = 0
    reasons = []

    if any(a in artist_lower for a in easy_artists):
        score -= 2
        reasons.append(random.choice(easy_detail_phrases))
    if any(a in artist_lower for a in hard_artists):
        score += 2
        reasons.append(random.choice(hard_detail_phrases))

    if any(k in title_lower for k in easy_keywords):
        score -= 1
        reasons.append(random.choice(easy_detail_phrases))
    if any(k in title_lower for k in hard_keywords):
        score += 1
        reasons.append(random.choice(hard_detail_phrases))

    reasons.extend(bpm_phrases)

    if score >= 2:
        category = "🔊 하드 리스닝 (Hard Listening)"
    elif score <= -1:
        category = "🌿 이지 리스닝 (Easy Listening)"
    else:
        category = "🤔 판단 보류"

    if reasons:
        reason = "\n- " + "\n- ".join(reasons)
    else:
        reason = "정보가 부족해 추가 확인이 필요해요."

    return category, reason

# -------------------- 분류 기록 저장 -------------------- #
def load_history():
    if os.path.exists("history.csv"):
        return pd.read_csv("history.csv")
    else:
        return pd.DataFrame(columns=["Date", "Title", "Artist", "Category", "Reason"])

def save_history(title, artist, category, reason):
    df = load_history()
    new_entry = {
        "Date": pd.Timestamp.now(),
        "Title": title,
        "Artist": artist,
        "Category": category,
        "Reason": reason
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv("history.csv", index=False)
    return df

# -------------------- Streamlit UI -------------------- #
st.set_page_config(page_title="감성 음악 분류기", layout="centered")
st.title("🎵 감성 음악 분류기")
st.write("곡 제목과 아티스트명을 입력하면, 이지 리스닝 / 하드 리스닝으로 분류하고 Spotify에서 곡 정보를 자동으로 가져와요.")

title = st.text_input("곡 제목", "")
artist = st.text_input("아티스트명", "")

if st.button("Spotify에서 자동 분석하기"):
    if title.strip() and artist.strip():
        bpm, duration = get_track_info_from_spotify(title, artist)
        if bpm and duration:
            category, reason = classify_song(title, artist, bpm, duration)
            st.subheader(f"결과: {category}")
            st.write(f"📝 상세한 해설:\n{reason}")
            save_history(title, artist, category, reason)
        else:
            st.error("Spotify에서 곡 정보를 찾을 수 없습니다.")
    else:
        st.warning("곡 제목과 아티스트명을 모두 입력해 주세요.")

# 최근 분류 기록 보기
with st.expander("📊 최근 분류 기록 보기"):
    history_df = load_history()
    if not history_df.empty:
        st.dataframe(history_df.tail(10))
    else:
        st.write("아직 기록된 데이터가 없어요.")
