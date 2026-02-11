import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정 (Page Configuration)
st.set_page_config(page_title="Premix Plant Orthogonal Layout", layout="wide")

# CSS: 직교 배관 및 화이트 테마 UI
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
    .silo-label { z-index: 2; font-size: 10px; font-weight: bold; }
    .qty-label { z-index: 2; font-size: 10px; color: #d9480f; font-weight: bold; }

    .pipe-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
    .pipe-base { fill: none; stroke: #e9ecef; stroke-width: 2; }
    .pipe-active { fill: none; stroke: #007bff; stroke-width: 4; stroke-linecap: square; filter: drop-shadow(0 0 2px rgba(0, 123, 255, 0.4)); }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Premix Plant 직교 배관 및 재고 관리")

# 2. 데이터 처리 (Data Processing)
st.sidebar.header("📥 Data Input")
raw_input = st.sidebar.text_area("데이터 붙여넣기 ([탱크][제품][재고])", height=250)
data = {}
if raw_input.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_input), sep=r'\s+', skiprows=1, names=['t', 'p', 'q'])
        for _, r in df.iterrows():
            data[r['t']] = {"p": r['p'], "q": float(str(r['q']).replace(',', ''))}
    except: st.sidebar.error("Data Format Error")

# 3. 좌표 및 설정 (Coordinates & Settings)
b_coords = {f"B{i}": (180 + (i-101)*240, 80) for i in range(101, 105)}
sn_targets = [f"S{i}" for i in range(101, 105)]
so_targets = [f"S{i}" for i in range(109, 114)]

sn_coords = {f"S{i}": (100 + (i-101)*120, 450) for i in range(101, 105)}
so_coords = {f"S{i}": (650 + (i-109)*110, 700) for i in range(109, 114)}

# 4. 배관 렌더링 (Manifold 구조 - 입체 교차 적용)
def draw_manifold_pipes():
    paths = ""
    # 수평 배관이 지나가는 기준 높이
    h_level_new = 240
    h_level_old = 280
    
    for b_name, b_pos in b_coords.items():
        b_info = data.get(b_name)
        bx, by = b_pos[0] + 37, b_pos[1] + 100
        
        # 신설 그룹행 (Horizontal level 240)
        for sn_name in sn_targets:
            sn_pos = sn_coords.get(sn_name)
            sn_info = data.get(sn_name)
            active = "pipe-active" if (b_info and sn_info and b_info['p'] == sn_info['p']) else "pipe-base"
            snx, sny = sn_pos[0] + 37, sn_pos[1]
            
            # 수직으로 내려와서(V) 수평으로 가는데(H), 시작점의 수직선(bx)을 피하기 위해 아크(a) 삽입
            path_d = f"M {bx} {by} V {h_level_new} H {bx-10} a 10 10 0 0 1 20 0 H {snx} V {sny}"
            paths += f'<path class="{active}" d="{path_d}" />'

        # 구설 그룹행 (Horizontal level 280)
        for so_name in so_targets:
            so_pos = so_coords.get(so_name)
            so_info = data.get(so_name)
            active = "pipe-active" if (b_info and so_info and b_info['p'] == so_info['p']) else "pipe-base"
            sox, soy = so_pos[0] + 37, so_pos[1]
            
            # 동일하게 시작 수직선 위치에서 점프
            path_d = f"M {bx} {by} V {h_level_old} H {bx-10} a 10 10 0 0 1 20 0 H {sox} V {soy}"
            paths += f'<path class="{active}" d="{path_d}" />'
            
    return paths

# 5. 사일로 HTML 생성 (Silo Generation)
def get_silo(name, x, y, cap):
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

# 6. 레이아웃 조립 (Layout Assembly)
main_html = f'<div class="main-container">'
main_html += f'<svg class="pipe-svg" viewBox="0 0 1300 900">{draw_manifold_pipes()}</svg>'

# 그룹 사일로 그리기
for name, pos in b_coords.items(): main_html += get_silo(name, pos[0], pos[1], 80)
for name, pos in sn_coords.items(): main_html += get_silo(name, pos[0], pos[1], 40)
for name, pos in so_coords.items(): main_html += get_silo(name, pos[0], pos[1], 18)

# 기타 사일로
others = {
    "S105": (100 + 4*120, 450), 
    "S106": (100 + 5*120, 450), 
    "S107": (100, 700), 
    "S108": (210, 700)
}
for name, pos in others.items(): main_html += get_silo(name, pos[0], pos[1], 40)

main_html += '</div>'
st.markdown(main_html, unsafe_allow_html=True)