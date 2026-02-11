import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="Premix Plant Orthogonal Layout", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #333333; }
    .main-container { position: relative; width: 100%; height: 900px; padding: 20px; overflow: hidden; }
    
    .silo-box {
        position: absolute; width: 75px; height: 100px; background-color: #f8f9fa;
        border: 2px solid #adb5bd; border-radius: 5px 5px 12px 12px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 10; text-align: center; transform: translateX(-50%); /* 중심 정렬을 위해 추가 */
    }
    .silo-fill { position: absolute; bottom: 0; left: 0; width: 100%; background-color: rgba(0, 123, 255, 0.4); z-index: 1; transition: height 0.5s; }
    .silo-label { z-index: 2; font-size: 10px; font-weight: bold; }
    .qty-label { z-index: 2; font-size: 10px; color: #d9480f; font-weight: bold; }

    .pipe-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
    .pipe-base { fill: none; stroke: #e9ecef; stroke-width: 2; }
    .pipe-active { fill: none; stroke: #007bff; stroke-width: 4; stroke-linecap: square; filter: drop-shadow(0 0 2px rgba(0, 123, 255, 0.4)); }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Premix Plant 정밀 정렬 배관 시스템")

# 2. 데이터 처리
st.sidebar.header("📥 Data Input")
raw_input = st.sidebar.text_area("데이터 붙여넣기", height=200)
data = {}
if raw_input.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_input), sep=r'\s+', skiprows=1, names=['t', 'p', 'q'])
        for _, r in df.iterrows():
            data[r['t']] = {"p": r['p'], "q": float(str(r['q']).replace(',', ''))}
    except: st.sidebar.error("Data Format Error")

# 3. 좌표 설정 (중심점 기준)
# 각 사일로의 '중앙 X좌표'를 기준으로 설정합니다.
b_coords = {f"B{i}": (200 + (i-101)*240, 80) for i in range(101, 105)}
sn_coords = {f"S{i}": (150 + (i-101)*150, 450) for i in range(101, 105)}
so_coords = {f"S{i}": (700 + (i-109)*120, 700) for i in range(109, 114)}

sn_targets = [f"S{i}" for i in range(101, 105)]
so_targets = [f"S{i}" for i in range(109, 114)]

# 4. 배관 렌더링 (정밀 정렬 및 입체 교차)
def draw_manifold_pipes():
    paths = ""
    h_level_new = 240
    h_level_old = 300 # 교차 가시성을 위해 간격 조정
    
    for b_name, bx_center in b_coords.items():
        b_info = data.get(b_name)
        bx, by_bottom = bx_center[0], bx_center[1] + 100 # 사일로 바닥 중앙
        
        # 신설 그룹 (S101-104)
        for sn_name in sn_targets:
            sn_pos = sn_coords.get(sn_name)
            sn_info = data.get(sn_name)
            active = "pipe-active" if (b_info and sn_info and b_info['p'] == sn_info['p']) else "pipe-base"
            snx, sny_top = sn_pos[0], sn_pos[1] # 타겟 사일로 상단 중앙
            
            # 경로: 수직 하강 -> 시작점 수직선 우회(Jump) -> 수평 이동 -> 수직 하강
            path_d = f"M {bx} {by_bottom} V {h_level_new} H {bx-10} a 10 10 0 0 1 20 0 H {snx} V {sny_top}"
            paths += f'<path class="{active}" d="{path_d}" />'

        # 구설 그룹 (S109-113)
        for so_name in so_targets:
            so_pos = so_coords.get(so_name)
            so_info = data.get(so_name)
            active = "pipe-active" if (b_info and so_info and b_info['p'] == so_info['p']) else "pipe-base"
            sox, soy_top = so_pos[0], so_pos[1]
            
            path_d = f"M {bx} {by_bottom} V {h_level_old} H {bx-10} a 10 10 0 0 1 20 0 H {sox} V {soy_top}"
            paths += f'<path class="{active}" d="{path_d}" />'
            
    return paths

# 5. 사일로 생성 함수
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

# 6. 레이아웃 조립
main_html = f'<div class="main-container">'
main_html += f'<svg class="pipe-svg" viewBox="0 0 1300 900">{draw_manifold_pipes()}</svg>'

# 사일로 배치 (정의된 중심 좌표 사용)
for name, pos in b_coords.items(): main_html += get_silo(name, pos[0], pos[1], 80)
for name, pos in sn_coords.items(): main_html += get_silo(name, pos[0], pos[1], 40)
for name, pos in so_coords.items(): main_html += get_silo(name, pos[0], pos[1], 18)

main_html += '</div>'
st.markdown(main_html, unsafe_allow_html=True)