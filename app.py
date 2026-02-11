import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="Premix Plant Flow Dashboard", layout="wide")

# CSS: 사일로 배치 및 배관(Line) 스타일
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #333333; }
    .main-container { position: relative; width: 100%; height: 850px; padding: 20px; }
    
    /* 사일로 공통 스타일 */
    .silo-box {
        position: absolute; width: 80px; height: 110px; background-color: #f1f3f5;
        border: 2px solid #dee2e6; border-radius: 5px 5px 15px 15px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 10; text-align: center; overflow: hidden;
    }
    .silo-fill { position: absolute; bottom: 0; left: 0; width: 100%; background-color: rgba(0, 123, 255, 0.4); z-index: 1; }
    .silo-label { z-index: 2; font-size: 10px; font-weight: bold; }
    .qty-label { z-index: 2; font-size: 10px; color: #d9480f; font-weight: bold; }

    /* SVG 배관 스타일 */
    .pipe-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
    .pipe-base { fill: none; stroke: #f1f3f5; stroke-width: 2; }
    .pipe-active { fill: none; stroke: #007bff; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; filter: drop-shadow(0 0 3px rgba(0, 123, 255, 0.5)); }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Premix Plant 실시간 공정 흐름도")

# 2. 데이터 처리
st.sidebar.header("📥 Data Input")
raw_input = st.sidebar.text_area("Copy & Paste Data", height=250)
data = {}
if raw_input.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_input), sep=r'\s+', skiprows=1, names=['t', 'p', 'q'])
        for _, r in df.iterrows():
            data[r['t']] = {"p": r['p'], "q": float(str(r['q']).replace(',', ''))}
    except: st.sidebar.error("Check Data Format")

# 3. 좌표 및 렌더링 정의
def get_silo(name, x, y, cap):
    info = data.get(name)
    pct = min(100, (info['q']/cap)*100) if info else 0
    prod = info['p'] if info else ""
    qty = f"{info['q']:,.1f}" if info else "OFF"
    return f"""<div class="silo-box" style="left:{x}px; top:{y}px;">
        <div class="silo-fill" style="height:{pct}%;"></div>
        <div class="silo-label">{name}</div>
        <div style="font-size:8px; z-index:2;">{prod}</div>
        <div class="qty-label">{qty}</div>
    </div>"""

# 4. 레이아웃 렌더링
html = '<div class="main-container">'
svg = '<svg class="pipe-svg" viewBox="0 0 1200 800">'

# 좌표 정의 (B: 상단, S_New: 중단, S_Old: 하단)
b_coords = {f"B{i}": (150 + (i-101)*250, 100) for i in range(101, 105)}
sn_coords = {f"S{i}": (100 + (i-101)*150, 400) for i in range(101, 105)}
so_coords = {f"S{i}": (750 + (i-109)*110, 650) for i in range(109, 114)}

# 배관 연결선 생성 (B -> SN, B -> SO)
for b_name, b_pos in b_coords.items():
    b_info = data.get(b_name)
    # To New Silos
    for sn_name, sn_pos in sn_coords.items():
        sn_info = data.get(sn_name)
        active = "pipe-active" if (b_info and sn_info and b_info['p'] == sn_info['p']) else "pipe-base"
        svg += f'<path class="{active}" d="M {b_pos[0]+40} {b_pos[1]+110} L {b_pos[0]+40} 250 L {sn_pos[0]+40} 300 L {sn_pos[0]+40} 400" />'
    
    # To Old Silos
    for so_name, so_pos in so_coords.items():
        so_info = data.get(so_name)
        active = "pipe-active" if (b_info and so_info and b_info['p'] == so_info['p']) else "pipe-base"
        svg += f'<path class="{active}" d="M {b_pos[0]+40} {b_pos[1]+110} L {b_pos[0]+40} 250 L {so_pos[0]+40} 550 L {so_pos[0]+40} 650" />'

svg += '</svg>'
html += svg

# 사일로 그리기
for name, pos in b_coords.items(): html += get_silo(name, pos[0], pos[1], 80)
for name, pos in sn_coords.items(): html += get_silo(name, pos[0], pos[1], 40)
for name, pos in so_coords.items(): html += get_silo(name, pos[0], pos[1], 18)

# 기타 사일로 (선 없이 배치)
s_other = {f"S{i}": (800 + (i-107)*100, 400) for i in [107, 108]} # 설탕
for name, pos in s_other.items(): html += get_silo(name, pos[0], pos[1], 40)

html += '</div>'
st.markdown(html, unsafe_allow_html=True)