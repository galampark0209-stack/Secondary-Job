import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정
st.set_page_config(page_title="Premix Plant 물류 경로 대시보드", layout="wide")

# CSS: 선(Line) 및 하이라이트 효과 정의
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #333333; }
    .section-title { 
        padding: 10px; background-color: #f1f3f5; border-left: 5px solid #007bff; 
        margin: 10px 0; font-weight: bold; font-size: 16px;
    }
    .main-layout { position: relative; width: 100%; padding: 20px; }
    
    /* 사일로 컨테이너 */
    .row-container { display: flex; justify-content: space-around; margin-bottom: 80px; position: relative; z-index: 2; }
    .silo-group { display: flex; gap: 15px; }

    .silo {
        width: 90px; height: 120px; background-color: #f8f9fa;
        border: 2px solid #dee2e6; border-radius: 5px 5px 15px 15px;
        position: relative; overflow: hidden; display: flex; flex-direction: column;
        align-items: center; justify-content: center; text-align: center;
    }
    .silo-fill { position: absolute; bottom: 0; left: 0; width: 100%; background-color: rgba(0, 123, 255, 0.4); z-index: 1; }
    .silo-label { z-index: 2; font-size: 11px; font-weight: bold; color: #212529; }
    .prod-label { z-index: 2; font-size: 9px; color: #6c757d; }
    .qty-label { z-index: 2; font-size: 11px; font-weight: bold; color: #d9480f; }

    /* SVG 연결선 스타일 */
    .svg-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
    .base-path { fill: none; stroke: #e9ecef; stroke-width: 2; transition: all 0.3s; }
    .active-path { stroke: #007bff; stroke-width: 5; stroke-linecap: round; filter: drop-shadow(0 0 5px rgba(0, 123, 255, 0.5)); }
</style>
""", unsafe_allow_html=True)

st.title("🏭 Premix Plant 물류 이동 및 재고 현황")

# 2. 데이터 입력
st.sidebar.header("📥 데이터 입력")
raw_input = st.sidebar.text_area("쿼리 결과 붙여넣기", height=300)
data_dict = {}

if raw_input.strip():
    try:
        df = pd.read_csv(io.StringIO(raw_input), sep=r'\s+', skiprows=1, names=['tank', 'prod', 'qty'])
        for _, row in df.iterrows():
            q_val = float(str(row['qty']).replace(',', ''))
            data_dict[row['tank']] = {"p": row['prod'], "q": q_val}
    except:
        st.sidebar.error("데이터 형식을 확인해주세요.")

# 3. 렌더링 함수
def draw_silo_html(name, max_cap):
    info = data_dict.get(name)
    if info:
        pct = min(100, (info['q'] / max_cap) * 100)
        return f"""
        <div class="silo">
            <div class="silo-fill" style="height:{pct}%;"></div>
            <span class="silo-label">{name}</span>
            <span class="prod-label">{info['p']}</span>
            <span class="qty-label">{info['q']:,.1f}</span>
        </div>"""
    return f'<div class="silo" style="opacity:0.3;"><span class="silo-label">{name}</span></div>'

# 4. 화면 구성
st.markdown('<div class="section-title">Upper: Buffer Silos (Supply)</div>', unsafe_allow_html=True)

# 상단 버퍼 사일로 렌더링
b_tanks = [f"B{i}" for i in range(101, 105)]
s_new_tanks = [f"S{i}" for i in range(101, 105)] # 신설 4개
s_old_tanks = [f"S{i}" for i in range(109, 114)] # 구설 5개

# 레이아웃 시작
html_layout = '<div class="main-layout">'

# SVG 선 그리기 로직 (상상도 기반 좌표)
svg_paths = ""
for b in b_tanks:
    b_info = data_dict.get(b)
    # 신설 사일로 연결
    for s_n in s_new_tanks:
        sn_info = data_dict.get(s_n)
        is_active = "active-path" if (b_info and sn_info and b_info['p'] == sn_info['p']) else ""
        # 실제로는 좌표 계산이 필요하나 시각적 구조 표현을 위해 클래스 분기만 처리
        # (이 데모에서는 시각적 구조를 위해 active 여부만 html에 포함)
    
# 상단 그룹
html_layout += '<div class="row-container"><div class="silo-group">'
for b in b_tanks: html_layout += draw_silo_html(b, 80)
html_layout += '</div></div>'

# 하단 그룹 (신설 & 구설)
st.markdown('<div class="section-title">Lower: New & Old Silos (Receiving)</div>', unsafe_allow_html=True)
html_layout += '<div class="row-container">'
html_layout += '<div class="silo-group">'
for s in s_new_tanks:
    # 제품명 비교하여 테두리 강조 추가
    is_match = any(data_dict.get(b, {}).get('p') == data_dict.get(s, {}).get('p') for b in b_tanks if data_dict.get(s))
    style = "border:3px solid #007bff; box-shadow: 0 0 10px rgba(0,123,255,0.3);" if is_match else ""
    html_layout += f'<div style="{style}">{draw_silo_html(s, 40)}</div>'
html_layout += '</div>'

html_layout += '<div class="silo-group">'
for s in s_old_tanks:
    is_match = any(data_dict.get(b, {}).get('p') == data_dict.get(s, {}).get('p') for b in b_tanks if data_dict.get(s))
    style = "border:3px solid #007bff; box-shadow: 0 0 10px rgba(0,123,255,0.3);" if is_match else ""
    html_layout += f'<div style="{style}">{draw_silo_html(s, 18)}</div>'
html_layout += '</div></div>'

html_layout += '</div>'
st.markdown(html_layout, unsafe_allow_html=True)

# 하단 정보 가이드
st.info("💡 상단(Buffer)과 하단(New/Old)의 제품명이 일치하면 파란색 테두리로 연결 경로를 강조합니다.")