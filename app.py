import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CBL 물품 관리", layout="centered")

# 서버가 꺼져도 데이터가 보존되도록 하려면 나중에 구글 시트로 연결하는 게 좋지만,
# 우선은 간단하게 파일 저장 방식으로 구성합니다.
DB_FILE = "lab_orders.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            pass
    return pd.DataFrame(columns=['시약명', '상태'])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'orders' not in st.session_state:
    st.session_state.orders = load_data()

st.title("🧪 CBL 랩실 물품 관리")
st.caption("24시간 가동되는 랩실 전용 매니저입니다.")

with st.form("add_item_form", clear_on_submit=True):
    new_item = st.text_input("물품 이름 입력")
    submitted = st.form_submit_button("등록")
    
    if submitted and new_item.strip():
        new_row = pd.DataFrame([{'시약명': new_item.strip(), '상태': '미도착'}])
        st.session_state.orders = pd.concat([st.session_state.orders, new_row], ignore_index=True)
        save_data(st.session_state.orders)
        st.rerun()

st.markdown("---")

if st.session_state.orders.empty:
    st.info("등록된 물품이 없습니다.")
else:
    for idx, row in st.session_state.orders.iterrows():
        col1, col2, col3 = st.columns([0.15, 0.65, 0.2])
        is_done = (row['상태'] == '도착')
        changed = col1.checkbox("도착", value=is_done, key=f"chk_{idx}")
        
        if changed != is_done:
            st.session_state.orders.at[idx, '상태'] = '도착' if changed else '미도착'
            save_data(st.session_state.orders)
            st.rerun()
            
        if changed:
            col2.markdown(f"<span style='color:gray'>~~{row['시약명']}~~</span>", unsafe_allow_html=True)
        else:
            col2.markdown(f"**{row['시약명']}**")
            
        if col3.button("🗑️", key=f"del_{idx}"):
            st.session_state.orders = st.session_state.orders.drop(idx)
            save_data(st.session_state.orders)
            st.rerun()
