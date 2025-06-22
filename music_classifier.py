# 감성 음악 분류기 - 향상된 알고리즘 + 통계 저장 기능 포함

import streamlit as st
import pandas as pd
import os

# -------------------- 향상된 분류 알고리즘 -------------------- #
def classify_song(title, artist):
    title_lower = title.lower()
    artist_lower = artist.lower()

    # 아티스트 기반 분류 데이터셋
    easy_artists = ["norah jones", "sade", "air", "lauv", "lisa ono", "jack johnson"]
    hard_artists = ["korn", "noisia", "metallica", "slipknot", "rage against the machine"]

    # 제목 키워드 기반
    easy_keywords = ["love", "silence", "rain", "dream", "breathe", "acoustic", "smooth"]
    hard_keywords = ["rage", "control", "dark", "blood", "scream", "burn"]

    score = 0

    if any(a in artist_lower for a in easy_artists):
        score -= 2
    if any(a in artist_lower for a in hard_artists):
        score += 2

    if any(k in title_lower for k in easy_keywords):
        score -= 1
    if any(k in title_lower for k in hard_keywords):
        score += 1

    if score >= 2:
        category = "🔊 하드 리스닝 (Hard Listening)"
        reason = "강렬한 아티스트 또는 분위기의 키워드가 포함되어 있어요."
    elif score <= -1:
        category = "🌿 이지 리스닝 (Easy Listening)"
        reason = "잔잔하고 감성적인 요소들이 많아요."
    else:
        category = "🤔 판단 보류"
        reason = "정보가 부족하거나 혼합적인 요소가 있어요."

    return category, reason

# -------------------- 분류 기록 저장 -------------------- #
def load_history():
    if os.path.exists("history.csv"):
        return pd.read_csv("history.csv")
    else:
        return pd.DataFrame(columns=["Date", "Title", "Artist", "Category"])

def save_history(title, artist, category):
    df = load_history()
    new_entry = {
        "Date": pd.Timestamp.now(),
        "Title": title,
        "Artist": artist,
        "Category": category
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv("history.csv", index=False)
    return df

# -------------------- Streamlit UI -------------------- #
st.set_page_config(page_title="감성 음악 분류기", layout="centered")
st.title("🎵 감성 음악 분류기")
st.write("곡 제목과 아티스트명을 입력하면, 이지 리스닝 / 하드 리스닝으로 분류하고 기록해드려요.")

title = st.text_input("곡 제목", "")
artist = st.text_input("아티스트명", "")

if st.button("분류하기"):
    if title.strip() and artist.strip():
        category, reason = classify_song(title, artist)
        st.subheader(f"결과: {category}")
        st.write(reason)
        save_history(title, artist, category)
    else:
        st.warning("곡 제목과 아티스트명을 모두 입력해 주세요.")

# 최근 분류 기록 보기
with st.expander("📊 최근 분류 기록 보기"):
    history_df = load_history()
    if not history_df.empty:
        st.dataframe(history_df.tail(10))
    else:
        st.write("아직 기록된 데이터가 없어요.")
