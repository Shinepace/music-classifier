import streamlit as st

# 간단한 음악 분류 함수
def classify_song(title, artist):
    title_lower = title.lower()
    artist_lower = artist.lower()
    
    # 단순 키워드 기반 예시 (후에 데이터 기반 확장 가능)
    hard_keywords = ['korn', 'noisia', 'metal', 'rage', 'distortion', 'hard']
    easy_keywords = ['norah jones', 'sade', 'acoustic', 'jazz', 'smooth', 'bossa']

    if any(word in title_lower or word in artist_lower for word in hard_keywords):
        category = "🔊 하드 리스닝 (Hard Listening)"
        reason = "사운드가 강렬하고 몰입감을 요구하는 곡이에요."
    elif any(word in title_lower or word in artist_lower for word in easy_keywords):
        category = "🌿 이지 리스닝 (Easy Listening)"
        reason = "잔잔하고 편안한 분위기의 곡이에요."
    else:
        category = "🤔 판단 보류"
        reason = "추가 정보가 필요해요. 수동 확인이 필요합니다."

    return category, reason

# Streamlit UI
st.title("🎵 감성 음악 분류기")
st.write("곡 제목과 아티스트명을 입력하면, 이지 리스닝 / 하드 리스닝으로 분류해드려요.")

title = st.text_input("곡 제목")
artist = st.text_input("아티스트명")

if st.button("분류하기"):
    if title and artist:
        category, reason = classify_song(title, artist)
        st.subheader(f"결과: {category}")
        st.write(reason)
    else:
        st.warning("곡 제목과 아티스트명을 모두 입력해주세요.")