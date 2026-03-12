streamlit
pandas
st-gsheets-connection

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="CBL 배송 관리", layout="centered")

# 구글 시트와 연결하는 마법의 도구
conn = st.connection("gsheets", type=GSheetsConnection)

# 시트에서 데이터 가져오기 (ttl=0은 실시간 반영을 뜻함)
def load_data():
    try:
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=['시약명', '상태'])

df = load_data()

st.title("🧪 CBL 배송 관리")
st.caption("배송후, 꼭 기록하기.")

# 1. 입력 폼 (st.form 사용으로 입력 오류 방지)
with st.form("add_item", clear_on_submit=True):
    new_item = st.text_input("새 물품 이름")
    if st.form_submit_button("등록") and new_item.strip():
        new_row = pd.DataFrame([{"시약명": new_item.strip(), "상태": "미도착"}])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=updated_df) # 구글 시트에 즉시 기록
        st.success(f"'{new_item}' 등록 성공!")
        st.rerun()

st.divider()

# 2. 리스트 관리
if df.empty:
    st.info("현재 등록된 물품이 없습니다.")
else:
    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([0.15, 0.65, 0.2])
        
        # 상태 체크
        is_done = (row['상태'] == '도착')
        checked = col1.checkbox("도착", value=is_done, key=f"c_{idx}")
        
        if checked != is_done:
            df.at[idx, '상태'] = '도착' if checked else '미도착'
            conn.update(data=df)
            st.rerun()
            
        # 이름 표시
        display_text = f"~~{row['시약명']}~~" if is_done else f"**{row['시약명']}**"
        col2.write(display_text)
            
        # 개별 삭제
        if col3.button("🗑️", key=f"d_{idx}"):
            df = df.drop(idx)
            conn.update(data=df)
            st.rerun()
