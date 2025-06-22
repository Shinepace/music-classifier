# 감성 음악 분류기 - Spotify 없이 동작하는 로컬 버전

import streamlit as st
import pandas as pd
import os
import random
import re

# -------------------- 고급 분류 알고리즘 -------------------- #
def classify_by_manual_input(title, artist):
    # 단순한 키워드 기반 가상 분류 로직 (예시)
    title_lower = title.lower()
    artist_lower = artist.lower()

    reasons = []
    category = "🤔 판단 보류"

    if any(x in title_lower for x in ["love", "quiet", "dream", "breeze"]):
        category = "🌿 이지 리스닝 (Easy Listening)"
        reasons.append("제목이나 아티스트에서 감성적인 분위기가 느껴져요.")
    elif any(x in title_lower for x in ["rage", "hard", "fire", "storm"]):
        category = "🔊 하드 리스닝 (Hard Listening)"
        reasons.append("강렬한 느낌의 단어가 포함되어 있어요.")
    elif any(x in artist_lower for x in ["korn", "metal", "noisia"]):
        category = "🔊 하드 리스닝 (Hard Listening)"
        reasons.append("하드한 장르를 주로 하는 아티스트예요.")
    elif any(x in artist_lower for x in ["mango", "roald velden", "lumidelic"]):
        category = "🌿 이지 리스닝 (Easy Listening)"
        reasons.append("잔잔하고 감성적인 사운드를 만드는 아티스트예요.")

    if not reasons:
        reasons.append("명확한 판단 기준에 부합하지 않아 중립적으로 분류했어요.")

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
st.title("🎵 감성 음악 분류기 (로컬 분류 버전)")

st.write("Spotify API 없이 곡 제목과 아티스트명을 기준으로 이지/하드 리스닝을 간단하게 분류해드립니다.")

title = st.text_input("곡 제목")
artist = st.text_input("아티스트명")

if st.button("간단 분석"):
    if not (title and artist):
        st.warning("곡 제목과 아티스트명을 모두 입력하세요.")
    else:
        cat, reason = classify_by_manual_input(title, artist)
        st.subheader(f"🎧 결과: {cat}")
        st.write("📝 상세 해설:\n" + reason)
        save_history(title, artist, cat, reason)

with st.expander("📊 최근 분류 기록"):
    df = load_history()
    st.dataframe(df.tail(10))
