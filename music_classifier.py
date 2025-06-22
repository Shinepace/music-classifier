# 감성 음악 분류기 - Spotify 검색 향상 + 고급 분류 알고리즘 통합 버전 (Streamlit Cloud 대응)

import streamlit as st
import pandas as pd
import os
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

# -------------------- Spotify API 인증 -------------------- #
SPOTIFY_CLIENT_ID = st.secrets.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = st.secrets.get("SPOTIFY_CLIENT_SECRET")

if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    # 캐시 파일 없이 timeout/retries 옵션 추가 (Streamlit Cloud 대응)
    sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=10, retries=3)
else:
    st.error("Spotify API 인증 정보가 없습니다. secrets.toml에 설정하세요.")
    st.stop()

# -------------------- Spotify에서 트랙 정보 가져오기 -------------------- #
def clean_text(text):
    return re.sub(r"[\(\)\[\]\-–_:]|feat\..*|remaster.*", "", text.lower()).strip()

def get_best_matching_track(title, artist):
    query = f"{title} {artist}"
    results = sp.search(q=query, type="track", limit=5)
    if not results['tracks']['items']:
        results = sp.search(q=title, type="track", limit=5)

    best_score = -1
    best_track = None
    tc = clean_text(title)
    ac = clean_text(artist)

    for item in results['tracks']['items']:
        tn = clean_text(item['name'])
        an = clean_text(item['artists'][0]['name'])
        score = (tc in tn) + (ac in an)
        if score > best_score:
            best_score = score
            best_track = item

    if best_track:
        fid = best_track['id']
        feat = sp.audio_features([fid])[0]
        return feat, best_track['name'], best_track['artists'][0]['name']
    return None, None, None

# -------------------- 고급 분류 알고리즘 -------------------- #
def classify_by_features(feat):
    energy = feat['energy']
    valence = feat['valence']
    acousticness = feat['acousticness']
    tempo = feat['tempo']
    duration = feat['duration_ms'] // 1000
    reasons = []

    if tempo < 90:
        reasons.append("템포가 매우 느려서 마음이 차분해져요.")
    elif tempo < 110:
        reasons.append("편안한 리듬감으로 흐르듯이 이어져요.")
    elif tempo > 140:
        reasons.append("빠른 템포가 곡의 에너지를 극대화시켜요.")

    if duration < 150:
        reasons.append("짧은 곡 길이로 강렬하게 휘몰아치는 느낌이에요.")
    elif duration > 300:
        reasons.append("긴 러닝타임 덕분에 서서히 몰입하게 돼요.")

    if valence < 0.3 and acousticness > 0.6:
        category = "🌿 이지 리스닝 (Easy Listening)"
        reasons.append("감정 표현이 절제되어 있고, 사운드가 부드러워요.")
    elif energy > 0.7 and tempo > 130:
        category = "🔊 하드 리스닝 (Hard Listening)"
        reasons.append("에너지가 높고 전개가 강렬해서 집중하게 만들어요.")
    else:
        category = "🤔 판단 보류"
        reasons.append("특징이 섞여 있어 명확히 분류하기 어려운 곡이에요.")

    return category, "- " + "\n- ".join(reasons)

# -------------------- 분류 기록 저장 -------------------- #
def load_history():
    if os.path.exists("history.csv"):
        return pd.read_csv("history.csv")
    return pd.DataFrame(columns=["Date","Title","Artist","Category","Reason"])

def save_history(t, a, c, r):
    df = load_history()
    df = pd.concat([df, pd.DataFrame([{"Date":pd.Timestamp.now(), "Title":t,"Artist":a,"Category":c,"Reason":r}])], ignore_index=True)
    df.to_csv("history.csv", index=False)

# -------------------- Streamlit UI -------------------- #
st.set_page_config(page_title="감성 음악 분류기", layout="centered")
st.title("🎵 감성 음악 분류기 (Spotify 연동)")

title = st.text_input("곡 제목")
artist = st.text_input("아티스트명")

if st.button("자동 분석"):
    if not (title and artist):
        st.warning("곡 제목과 아티스트명을 모두 입력하세요.")
    else:
        feat, mtitle, martist = get_best_matching_track(title, artist)
        if feat:
            cat, reason = classify_by_features(feat)
            st.subheader(f"🔎 매칭된 트랙: {mtitle} - {martist}")
            st.write(f"✅ 결과: {cat}")
            st.write("📝 상세 해설:\n" + reason)
            save_history(mtitle, martist, cat, reason)
        else:
            st.error("Spotify에서 곡 정보를 찾을 수 없어요. 입력을 확인해 주세요.")

with st.expander("📊 최근 분류 기록"):
    df = load_history()
    st.dataframe(df.tail(10))
