import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="Premix Plant 재고현황", layout="wide")

# CSS: 공정 흐름을 강조한 산업용 다크 테마
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .section-title { 
        padding: 10px; background-color: #1a1c24; border-left: 5px solid #00d4ff; 
        margin: 20px 0; font-weight: bold; font-size: 18px;
    }
    .silo-container { display: flex; flex-wrap: wrap; gap: 15px; justify-content: flex-start; padding: 20px; }
    
    /* 사일로 기본 디자인 (실제 사일로 형상 모방) */
    .silo {
        width: 100px; height: 140px; background-color: #000;
        border: 2px solid #4a5568; border-radius: 5px 5px 20px 20px;
        position: relative; overflow: hidden; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
    }
    .silo-fill {
        position: absolute; bottom: 0; left: 0; width: 100%;
        background-color: rgba(0, 212, 255, 0.3); z-index: 1; transition: height 0.5s;
    }
    .silo-label { z-index: 2; font-size: 11px; font-weight: bold; }
    .prod-label { z-index: 2; font-size: 9px; color: #a0aec0; }
    .qty-label { z-index: 2; font-size: 12px; font-weight: bold; color: #ffeb3b; }
    
    /* 물류 연결 강조 스타일 */
    .connected { border-color: #00d4ff !important; box-shadow: 0 0 10px rgba(0, 212, 255, 0.4); }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Premix Plant 실시간 재고 관리 시스템")

# 2. 데이터 입력 (Copy & Paste)
st.sidebar.header("📥 데이터 입력")
raw_input = st.sidebar.text_area("쿼리 결과 붙여넣기 ([탱크][제품][재고])", height=300)

data_dict = {}
if raw_input.strip():
    try:
        # 첫 행(헤더)을 제외하고 읽기
        df = pd.read_csv(io.StringIO(raw_input), sep=r'\s+', skiprows=1, names=['tank', 'prod', 'qty'])
        for _, row in df.iterrows():
            q_val = float(str(row['qty']).replace(',', ''))
            data_dict[row['tank']] = {"p": row['prod'], "q": q_val}
        st.sidebar.success(f"데이터 로드 완료: {len(data_dict)}건")
    except Exception as e:
        st.sidebar.error("형식 오류: 헤더 포함 3열 데이터인지 확인해주세요.")

# 3. 사일로 렌더링 함수
def draw_silo(name, max_cap, connected=False):
    info = data_dict.get(name)
    conn_cls = "connected" if connected else ""
    if info:
        pct = min(100, (info['q'] / max_cap) * 100)
        fill_html = f'<div class="silo-fill" style="height:{pct}%;"></div>'
        return f"""
        <div class="silo {conn_cls}">
            {fill_html}
            <span class="silo-label">{name}</span>
            <span class="prod-label">{info['p']}</span>
            <span class="qty-label">{info['q']:,.1f}</span>
            <span style="font-size:8px; color:#555;">{max_cap}T</span>
        </div>
        """
    return f'<div class="silo {conn_cls}" style="opacity:0.4;"><span class="silo-label">{name}</span><span style="font-size:8px;">OFFLINE</span></div>'

# 4. 공정별 레이아웃 배치
# --- Group 1 (상단 공정: 공급원) ---
st.markdown('<div class="section-title">Step 1. 버퍼 사일로 (Buffer Silos - Supply)</div>', unsafe_allow_html=True)
g1_html = '<div class="silo-container">'
for i in range(101, 105):
    g1_html += draw_silo(f"B{i}", 80, connected=True)
g1_html += '</div>'
st.markdown(g1_html, unsafe_allow_html=True)

# --- Group 2, 4 (중간 공정: #1 Rule 연결) ---
st.markdown('<div class="section-title">Step 2. 메인 생산 사일로 (Connected via #1 Rule)</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.write("🔹 신설 사일로 (Group 2 / 40T)")
    g2_html = '<div class="silo-container">'
    for i in range(101, 107):
        g2_html += draw_silo(f"S{i}", 40, connected=True)
    g2_html += '</div>'
    st.markdown(g2_html, unsafe_allow_html=True)

with col2:
    st.write("🔹 구설 사일로 (Group 4 / 18T)")
    g4_html = '<div class="silo-container">'
    for i in range(109, 114):
        g4_html += draw_silo(f"S{i}", 18, connected=True)
    g4_html += '</div>'
    st.markdown(g4_html, unsafe_allow_html=True)

# --- Group 3, 5 (기타/부원료) ---
st.markdown('<div class="section-title">Step 3. 전용 및 마이너 사일로 (Dedicated & Minor)</div>', unsafe_allow_html=True)
col3, col4 = st.columns([1, 2])
with col3:
    st.write("🔹 설탕 사일로 (Group 3 / 40T)")
    g3_html = '<div class="silo-container">'
    for i in [107, 108]:
        g3_html += draw_silo(f"S{i}", 40)
    g3_html += '</div>'
    st.markdown(g3_html, unsafe_allow_html=True)

with col4:
    st.write("🔹 마이너 사일로 (Group 5 / 5T)")
    g5_html = '<div class="silo-container">'
    for i in range(14, 22):
        g5_html += draw_silo(f"S{i}", 5)
    g5_html += '</div>'
    st.markdown(g5_html, unsafe_allow_html=True)