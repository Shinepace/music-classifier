# 감성 음악 분류기 - Spotify 검색 향상 + 고급 분류 알고리즘 통합 버전

import streamlit as st
import pandas as pd
import os
import random
import spotify
from spotify.oauth2 import SpotifyClientCredentials
import re

# -------------------- Spotify API 인증 -------------------- #
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotify.Spotify(auth_manager=auth_manager)
else:
    st.error("Spotify API 인증 정보가 없습니다. SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET 환경변수를 설정해주세요.")
    sp = None

# -------------------- Spotify에서 트랙 정보 가져오기 -------------------- #
def clean_text(text):
    return re.sub(r"[\(\)\[\]\-–_:]|feat\..*|remaster.*", "", text.lower()).strip()

def get_best_matching_track(title, artist):
    if not sp:
        return None, None, None

    query = f"{title} {artist}"
    results = sp.search(q=query, type="track", limit=5)

    if not results['tracks']['items']:
        results = sp.search(q=title, type="track", limit=5)

    best_score = -1
    best_track = None
    title_clean = clean_text(title)
    artist_clean = clean_text(artist)

    for item in results['tracks']['items']:
        track_name = clean_text(item['name'])
        artist_name = clean_text(item['artists'][0]['name'])

        score = 0
        if title_clean in track_name:
            score += 1
        if artist_clean in artist_name:
            score += 1
        if score > best_score:
            best_score = score
            best_track = item

    if best_track:
        track_id = best_track['id']
        features = sp.audio_features([track_id])[0]
        return features, best_track['name'], best_track['artists'][0]['name']

    return None, None, None

# -------------------- 고급 분류 알고리즘 -------------------- #
def classify_by_features(features):
    energy = features['energy']
    valence = features['valence']
    acousticness = features['acousticness']
    tempo = features['tempo']
    duration = features['duration_ms'] // 1000

    reasons = []

    # 템포 기반
    if tempo < 90:
        reasons.append("템포가 매우 느려서 마음이 차분해져요.")
    elif tempo < 110:
        reasons.append("편안한 리듬감으로 흐르듯이 이어져요.")
    elif tempo > 140:
        reasons.append("빠른 템포가 곡의 에너지를 극대화시켜요.")

    # 길이 기반
    if duration < 150:
        reasons.append("짧은 곡 길이로 강렬하게 휘몰아치는 느낌이에요.")
    elif duration > 300:
        reasons.append("긴 러닝타임 덕분에 서서히 몰입하게 돼요.")

    # 분위기 기반
    if valence < 0.3 and acousticness > 0.6:
        category = "🌿 이지 리스닝 (Easy Listening)"
        reasons.append("감정 표현이 절제되어 있고, 사운드가 부드러워요.")
    elif energy > 0.7 and tempo > 130:
        category = "🔊 하드 리스닝 (Hard Listening)"
        reasons.append("에너지가 높고 전개가 강렬해서 집중하게 만들어요.")
    else:
        category = "🤔 판단 보류"
        reasons.append("특징이 섞여 있어 명확히 분류하기 어려운 곡이에요.")

    reason = "\n- " + "\n- ".join(reasons)
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
st.write("곡 제목과 아티스트명을 입력하면 Spotify에서 곡 정보를 검색하여 자동 분류해드려요.")

title = st.text_input("곡 제목", "")
artist = st.text_input("아티스트명", "")

if st.button("Spotify에서 자동 분석하기"):
    if title.strip() and artist.strip():
        features, matched_title, matched_artist = get_best_matching_track(title, artist)
        if features:
            category, reason = classify_by_features(features)
            st.subheader(f"결과: {category}")
            st.write(f"🔎 매칭된 트랙: {matched_title} - {matched_artist}")
            st.write(f"📝 상세한 해설:\n{reason}")
            save_history(matched_title, matched_artist, category, reason)
        else:
            st.error("Spotify에서 곡 정보를 찾을 수 없습니다. 제목이나 아티스트를 다시 확인해보세요.")
    else:
        st.warning("곡 제목과 아티스트명을 모두 입력해 주세요.")

# 최근 분류 기록 보기
with st.expander("📊 최근 분류 기록 보기"):
    history_df = load_history()
    if not history_df.empty:
        st.dataframe(history_df.tail(10))
    else:
        st.write("아직 기록된 데이터가 없어요.")
