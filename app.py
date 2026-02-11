import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="Premix Plant Orthogonal Dashboard", layout="wide")

# CSS: 직교 배관 스타일 및 레이아웃
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #333333; }
    .main-container { position: relative; width: 100%; height: 900px; padding: 20px; overflow: hidden; }
    
    .silo-box {
        position: absolute; width: 75px; height: 100px; background-color: #f8f9fa;
        border: 2px solid #adb5bd; border-radius: 5px 5px 12px 12px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 10; text-align: center;
    }
    .silo-fill { position: absolute; bottom: 0; left: 0; width: 100%; background-color: rgba(0, 123, 255, 0.4); z-index: 1; transition: height 0.5s; }
    .silo-label { z-index: 2; font-size: 10px; font-weight: bold; margin-bottom: 2px; }
    .qty-label { z-index: 2; font-size: 10px; color: #d9480f; font-weight: bold; }

    .pipe-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
    .pipe-base { fill: none; stroke: #e9ecef; stroke-width: 2; }
    .pipe-active { fill: none; stroke: #007bff; stroke-width: 4; stroke-linecap: square; filter: drop-shadow(0 0 2px rgba(0, 123, 255, 0.4)); }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Premix Plant 직교 배관 공정 모니터링")

# 2. 데이터 처리
st.sidebar.header("📥 Data Input")
raw_input = st.sidebar.text_area("데이터 붙여넣기", height=200)
data = {}
if raw_input.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_input), sep=r'\s+', skiprows=1, names=['t', 'p', 'q'])
        for _, r in df.iterrows():
            data[r['t']] = {"p": r['p'], "q": float(str(r['q']).replace(',', ''))}
    except: st.sidebar.error("데이터 형식을 확인해주세요.")

# 3. 좌표 정의
# 버퍼(B): 상단
b_coords = {f"B{i}": (180 + (i-101)*240, 80) for i in range(101, 105)}
# 신설(SN): 중단 (S101~S104)
sn_coords = {f"S{i}": (100 + (i-101)*120, 450) for i in range(101, 105)}
# 구설(SO): 하단 (S109~S113)
so_coords = {f"S{i}": (650 + (i-109)*110, 700) for i in range(109, 114)}

# 4. 배관 렌더링 함수 (수직/수평만 사용)
def draw_orthogonal_pipes():
    paths = ""
    for b_name, b_pos in b_coords.items():
        b_info = data.get(b_name)
        bx, by = b_pos[0] + 37, b_pos[1] + 100
        
        # 1. 신설 사일로 그룹으로 향하는 메인 라인 (수직 후 수평 분기)
        for sn_name, sn_pos in sn_coords.items():
            sn_info = data.get(sn_name)
            is_active = "pipe-active" if (b_info and sn_info and b_info['p'] == sn_info['p']) else "pipe-base"
            snx, sny = sn_pos[0] + 37, sn_pos[1]
            # 경로: 하강(200) -> 수평이동(snx) -> 하강(sny)
            paths += f'<path class="{is_active}" d="M {bx} {by} V 250 H {snx} V {sny}" />'

        # 2. 구설 사일로 그룹으로 향하는 메인 라인
        for so_name, so_pos in so_coords.items():
            so_info = data.get(so_name)
            is_active = "pipe-active" if (b_info and so_info and b_info['p'] == so_info['p']) else "pipe-base"
            sox, soy = so_pos[0] + 37, so_pos[1]
            # 경로: 하강(220) -> 수평이동(sox) -> 하강(soy)
            paths += f'<path class="{is_active}" d="M {bx} {by} V 280 H {sox} V {soy}" />'
    return paths

# 5. HTML 조립
def get_silo_html(name, x, y, cap):
    info = data.get(name)
    pct = min(100, (info['q']/cap)*100) if info else 0
    prod = info['p'] if info else "Empty"
    qty = f"{info['q']:,.1f}" if info else "-"
    return f"""<div class="silo-box" style="left:{x}px; top:{y}px;">
        <div class="silo-fill" style="height:{pct}%;"></div>
        <div class="silo-label">{name}</div>
        <div style="font-size:8px; z-index:2; color:#666;">{prod}</div>
        <div class="qty-label">{qty}</div>
    </div>"""

main_html = '<div class="main-container">'
main_html += f'<svg class="pipe-svg" viewBox="0 0 1300 900">{draw_orthogonal_pipes()}</svg>'

# 사일로 배치
for name, pos in b_coords.items(): main_html += get_silo_html(name, pos[0], pos[1], 80)
for name, pos in sn_coords.items(): main_html += get_silo_html(name, pos[0], pos[1], 40)
for name, pos in so_coords.items(): main_html += get_silo_html(name, pos[0], pos[1], 18)

# 기타 사일로 (S105, S106 등 선 제외 배치 가능)
extra_silos = {"S105