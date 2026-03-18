import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import os

# 1. 페이지 설정 및 LH 브랜드 테마 적용
st.set_page_config(
    page_title="LH | Rebar QC Analysis Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 파일을 Base64로 인코딩하는 함수 (이미지 및 모델 로드용)
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# 로고 HTML 생성
lh_logo_path = "lh_logo.png"
logo_b64 = get_base64_of_bin_file(lh_logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="lh-logo-img">' if logo_b64 else '<span style="font-size:2.5rem; font-weight:900;"><span style="color:#0055a6;">L</span><span style="color:#009944;">H</span></span>'

# [LH Enterprise Dashboard CSS - 최종 확정 디자인 유지]
st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    div[data-testid="stStatusWidget"] {{display: none !important;}}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    .stApp {{
        background-color: #ffffff;
        color: #1e293b;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }}

    .stApp::before {{
        content: ''; position: fixed; top: 0; left: 0; width: 450px; height: 350px;
        background-color: #b1d632; clip-path: polygon(0 0, 100% 0, 0 85%); z-index: -2; opacity: 0.9; pointer-events: none;
    }}
    .stApp::after {{
        content: ''; position: fixed; bottom: 0; right: 0; width: 450px; height: 350px;
        background-color: #b1d632; clip-path: polygon(100% 15%, 100% 100%, 0 100%); z-index: -2; opacity: 0.9; pointer-events: none;
    }}
    .main {{ background: transparent !important; }}

    .main .block-container {{
        position: relative; z-index: 10; padding-top: 0.5rem !important; padding-bottom: 0rem !important;
        padding-left: 3rem !important; padding-right: 3rem !important; margin-top: -35px;
    }}

    .lh-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; padding-bottom: 0.5rem; border-bottom: 4px solid #009944; }}
    .lh-brand-box {{ display: flex; align-items: center; gap: 15px; }}
    .lh-logo-img {{ height: 75px; width: auto; margin-top: -10px; }}
    .project-name {{ font-size: 2.8rem; font-weight: 900; color: #0f172a; margin-left: 15px; border-left: 5px solid #e2e8f0; padding-left: 25px; letter-spacing: -2px; }}
    .system-status {{ font-size: 0.9rem; background: white; color: #009944; border: 2px solid #009944; padding: 8px 20px; border-radius: 99px; font-weight: 800; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}

    div[data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.96) !important; padding: 15px 25px !important; border-radius: 15px !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08) !important; backdrop-filter: blur(10px);
    }}
    .section-title {{ font-size: 1.7rem; font-weight: 800; margin-bottom: 10px; color: #0f172a; border-left: 8px solid #009944; padding-left: 18px; }}
    .stDataFrame {{ border: 1px solid #e2e8f0; border-radius: 15px; overflow: hidden; background-color: #ffffff !important; box-shadow: 0 10px 20px -5px rgba(0,0,0,0.05); z-index: 20; }}
    </style>
    """, unsafe_allow_html=True)

# 2. 공통 헤더 섹션
st.markdown(f"""
    <div class="lh-header">
        <div class="lh-brand-box">
            {logo_html}
            <div class="project-name">철근 배근 시공 품질 자동 검측 엔진</div>
        </div>
        <div class="system-status">● SYSTEM MONITORING</div>
    </div>
    """, unsafe_allow_html=True)

# 3. 상단 탭 네비게이션
tabs = ["철근 시공오차 분석", "스캔 데이터 분석", "3D 모델링", "실시간 협업"]
selected_tab = st.pills("", tabs, selection_mode="single", default="철근 시공오차 분석", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# 4. 페이지 분기 로직
if selected_tab == "철근 시공오차 분석":
    csv_file = "final_qc_report_detailed.csv"
    glb_file = "construction_qc_model.glb"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        status_counts = df['Status'].value_counts()
        m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.4])
        with m1: st.metric("전체 검측", f"{len(df)}EA")
        with m2: st.metric("정상 (PASS)", f"{status_counts.get('PASS', 0)}")
        with m3: st.metric("이슈 (ISSUE)", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
        with m4: st.metric("미탐지 (MISS)", f"{status_counts.get('MISSING', 0)}")
        with m5:
            st.markdown("""
                <div style="font-size: 1.05rem; color: #1e293b; background: rgba(255, 255, 255, 0.98); padding: 12px 20px; border-radius: 15px; border: 2.5px solid #009944; height: 100%; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08);">
                    <div style="font-weight: 900; color: #009944; margin-bottom: 4px; font-size: 1.25rem; border-bottom: 2.5px solid #e2e8f0; padding-bottom: 4px;">QC 품질 기준</div>
                    <div style="line-height: 1.8; color: #1e293b;">⚪ <b>PASS</b>: <20mm | 🟢 <b>CAUTION</b>: 20-30mm | 🟠 <b>ERROR</b>: >30mm</div>
                </div>""", unsafe_allow_html=True)
        left_col, right_col = st.columns([6, 4])
        with left_col:
            if os.path.exists(glb_file):
                b64_glb = get_base64_of_bin_file(glb_file)
                st.components.v1.html(f"""<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script><model-viewer src="data:model/gltf-binary;base64,{b64_glb}" style="width: 100%; height: 650px; background-color: white; border-radius: 20px; border: 1px solid #e2e8f0;" camera-controls touch-action="pan-y" shadow-intensity="1" orientation="-90deg -90deg -90deg" exposure="1.2" environment-image="neutral"></model-viewer>""", height=670)
        with right_col:
            bar_data = pd.DataFrame({'상태': ['Pass', 'Caution', 'Error', 'Missing'], 'Count': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)], 'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']})
            fig_bar = px.bar(bar_data, x='Count', y='상태', orientation='h', color='Status', color_discrete_map={'PASS': '#94a3b8', 'CAUTION': '#009944', 'ERROR': '#f59e0b', 'MISSING': '#ef4444'}, text='Count')
            fig_bar.update_layout(showlegend=False, height=230, margin=dict(l=0, r=20, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#0f172a", xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), font=dict(size=16, weight='bold'))
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("<div class='section-title'>📋 개별 검측 상세 데이터</div>", unsafe_allow_html=True)
            df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
            df_view.columns = ['ID', '오차(mm)', '결과', '레이어']
            st.dataframe(df_view, use_container_width=True, height=360)

elif selected_tab == "스캔 데이터 분석":
    st.markdown("<div class='section-title'>🔍 포인트 클라우드 분석 및 피크 탐지</div>", unsafe_allow_html=True)
    
    # 깃허브에 올리신 실제 파일들
    raw_path = "raw_cloud.parquet"
    seg_path = "segmented_rebars.parquet"
    peak_img_path = "peak_finding_results.png"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. 원본 데이터 (Raw Point Cloud)")
        if os.path.exists(raw_path):
            df_raw = pd.read_parquet(raw_path)
            fig_raw = go.Figure(data=[go.Scatter3d(
                x=df_raw['x'], y=df_raw['y'], z=df_raw['z'], 
                mode='markers', 
                marker=dict(size=1.2, color='#94a3b8', opacity=0.4)
            )])
            fig_raw.update_layout(height=600, margin=dict(l=0, r=0, b=0, t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_raw, use_container_width=True)
        else:
            st.warning("'raw_cloud.parquet' 파일을 찾을 수 없습니다.")

    with col2:
        st.subheader("2. 개별 객체 분할 (Segmented Rebars)")
        if os.path.exists(seg_path):
            df_seg = pd.read_parquet(seg_path)
            # rebar_id별로 다른 색상을 입혀 시각화
            fig_seg = px.scatter_3d(df_seg, x='x', y='y', z='z', color='rebar_id', size_max=2, opacity=0.8)
            fig_seg.update_layout(height=600, margin=dict(l=0, r=0, b=0, t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_seg, use_container_width=True)
        else:
            st.warning("'segmented_rebars.parquet' 파일을 찾을 수 없습니다.")

    st.markdown("---")
    st.subheader("3. 포인트 밀도 기반 피크 탐지 결과 (Peak Finding Analysis)")
    
    if os.path.exists(peak_img_path):
        # 깃허브에 올린 분석 결과 이미지 표시
        st.image(peak_img_path, caption="[Smoothing] Density Histogram & Peak Detection Logic", use_container_width=True)
    else:
        st.info("💡 'peak_finding_results.png' 이미지를 찾을 수 없어 기본 차트를 표시합니다.")
        # 이미지가 없을 경우를 대비한 대체 차트
        st.line_chart(pd.DataFrame({"Density": [0, 100, 50, 200, 300, 50, 10]}, index=range(7)))

else:
    st.markdown(f"<div style='height: 600px; background: rgba(248, 250, 252, 0.8); border: 2px dashed #cbd5e1; border-radius: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8;'><h1 style='font-size: 3rem; font-weight: 900; margin-bottom: 20px;'>{selected_tab}</h1><p style='font-size: 1.2rem;'>해당 기능은 현재 구현 준비 중입니다.</p><div style='margin-top: 30px; font-size: 5rem; opacity: 0.2;'>🏗️</div></div>", unsafe_allow_html=True)
