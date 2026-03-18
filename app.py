import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import numpy as np

# 1. 페이지 설정 및 브랜드 테마
st.set_page_config(
    page_title="LH | Digital Twin Rebar QC", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 파일 로딩을 위한 헬퍼 함수
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# 로고 설정
lh_logo_path = "lh_logo.png"
logo_b64 = get_base64_of_bin_file(lh_logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="lh-logo-img">' if logo_b64 else '<span style="font-size:1.5rem; font-weight:900;"><span style="color:#0055a6;">L</span><span style="color:#009944;">H</span></span>'

# [LH Enterprise Dashboard CSS - 콤팩트 헤더 버전]
st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    .stApp {{ background-color: #ffffff; color: #1e293b; font-family: 'Inter', 'Noto Sans KR', sans-serif; }}
    .stApp::before {{ content: ''; position: fixed; top: 0; left: 0; width: 350px; height: 250px; background-color: #b1d632; clip-path: polygon(0 0, 100% 0, 0 85%); z-index: -2; opacity: 0.8; pointer-events: none; }}
    .stApp::after {{ content: ''; position: fixed; bottom: 0; right: 0; width: 350px; height: 250px; background-color: #b1d632; clip-path: polygon(100% 15%, 100% 100%, 0 100%); z-index: -2; opacity: 0.8; pointer-events: none; }}
    
    .main .block-container {{ padding-top: 1rem !important; margin-top: -45px; padding-left: 2rem !important; padding-right: 2rem !important; }}
    
    .lh-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #009944; padding-bottom: 5px; margin-bottom: 15px; }}
    .lh-logo-img {{ height: 45px; width: auto; }}
    .project-name {{ font-size: 1.8rem; font-weight: 900; color: #0f172a; border-left: 3px solid #e2e8f0; padding-left: 15px; margin-left: 15px; letter-spacing: -1px; }}
    .section-title {{ font-size: 1.4rem; font-weight: 800; margin: 20px 0 10px 0; border-left: 6px solid #009944; padding-left: 12px; color: #0f172a; }}
    .analysis-container {{ background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 헤더
st.markdown(f"""
    <div class="lh-header">
        <div style="display:flex; align-items:center;">
            {logo_html}
            <div class="project-name">철근 배근 시공 품질 자동 검측 엔진</div>
        </div>
        <div style="font-size:0.8rem; background:white; color:#009944; border:1.5px solid #009944; padding:5px 15px; border-radius:99px; font-weight:800;">● SYSTEM CONNECTED</div>
    </div>
    """, unsafe_allow_html=True)

# 3. 탭 네비게이션
tabs = ["철근 시공오차 분석", "스캔 데이터 분석", "3D 모델링", "실시간 협업"]
selected_tab = st.pills("", tabs, selection_mode="single", default="철근 시공오차 분석", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# [TAB 1] 철근 시공오차 분석
# ------------------------------------------------------------------
if selected_tab == "철근 시공오차 분석":
    csv_file = "final_qc_report_detailed.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        status_counts = df['Status'].value_counts()
        
        m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.5])
        m1.metric("전체 검측", f"{len(df)}EA")
        m2.metric("정상 (PASS)", f"{status_counts.get('PASS', 0)}")
        m3.metric("이슈 (ISSUE)", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
        m4.metric("미탐지 (MISS)", f"{status_counts.get('MISSING', 0)}")
        with m5:
            st.markdown('<div style="font-size:0.85rem; padding:10px; border:2px solid #009944; border-radius:10px;"><b>품질 기준:</b> PASS < 20mm | ERROR > 30mm</div>', unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>📋 검측 데이터 상세</div>", unsafe_allow_html=True)
        st.dataframe(df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']], use_container_width=True, height=450)
    else:
        st.warning("'final_qc_report_detailed.csv' 파일이 필요합니다.")

# ------------------------------------------------------------------
# [TAB 2] 스캔 데이터 분석
# ------------------------------------------------------------------
elif selected_tab == "스캔 데이터 분석":
    st.markdown("<div class='section-title'>🔍 포인트 클라우드 분석 및 피크 탐지</div>", unsafe_allow_html=True)
    
    raw_p, seg_p = "raw_cloud.parquet", "segmented_rebars.parquet"
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("1. 원본 데이터 (Raw)")
        if os.path.exists(raw_p):
            df_raw = pd.read_parquet(raw_p)
            fig_raw = go.Figure(data=[go.Scatter3d(x=df_raw['x'], y=df_raw['y'], z=df_raw['z'], mode='markers', marker=dict(size=0.8, color='#94a3b8', opacity=0.4))])
            fig_raw.update_layout(height=450, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_raw, use_container_width=True)
            
    with c2:
        st.subheader("2. 객체 분할 (Segmented)")
        if os.path.exists(seg_p):
            df_seg = pd.read_parquet(seg_p)
            fig_seg = px.scatter_3d(df_seg, x='x', y='y', z='z', color='rebar_id', opacity=0.8)
            fig_seg.update_traces(marker=dict(size=0.7))
            fig_seg.update_layout(showlegend=False, height=450, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_seg, use_container_width=True)

    st.markdown("---")
    st.subheader("3. 포인트 밀도 분석 로그 (Peak Finding)")
    ic1, ic2 = st.columns(2)
    with ic1:
        for img in ["top v_x.png", "bottom v_x.png"]:
            if os.path.exists(img): st.image(img, use_container_width=True)
    with ic2:
        for img in ["top h_z.png", "bottom h_z.png"]:
            if os.path.exists(img): st.image(img, use_container_width=True)

# ------------------------------------------------------------------
# [TAB 3] 3D 모델링 (디지털 트윈 정합)
# ------------------------------------------------------------------
elif selected_tab == "3D 모델링":
    st.markdown("<div class='section-title'>🏗️ 설계-시공 통합 디지털 트윈 모델</div>", unsafe_allow_html=True)
    
    mesh_path = "design_mesh.parquet"
    vec_path = "rebar_vectors.parquet"
    vec_aligned_path = "rebar_vectors_aligned.parquet"
    
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    l_col, r_col = st.columns([7.5, 2.5])
    
    with r_col:
        st.subheader("🛠️ 시각화 설정")
        ly_design = st.checkbox("BIM 설계 모델 (Mesh)", value=True)
        ly_raw = st.checkbox("정렬 전 시공 모델 (Scan)", value=False)
        ly_aligned = st.checkbox("정렬 후 시공 모델 (Aligned)", value=True)
        
        if os.path.exists(vec_aligned_path):
            df_a = pd.read_parquet(vec_aligned_path)
            st.markdown("---")
            st.metric("ICP Fitness", f"{df_a['fitness'].iloc[0]:.4f}")
            st.metric("Mean RMSE", f"{df_a['rmse'].iloc[0]:.2f} mm")
            
        if os.path.exists("icp_process.gif"):
            st.markdown("---")
            st.subheader("🎬 정합 프로세스")
            st.image("icp_process.gif")

    with l_col:
        fig_3d = go.Figure()
        
        # [A] 설계 모델
        if ly_design and os.path.exists(mesh_path):
            df_m = pd.read_parquet(mesh_path)
            m_data = df_m['mesh_json'].iloc[0] if 'mesh_json' in df_m.columns else df_m['data'].iloc[0]
            v, f = np.array(m_data['vertices']), np.array(m_data['faces'])
            fig_3d.add_trace(go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='lightcyan', opacity=0.3, name='Design'))

        # [B] 정렬 전 시공 모델
        if ly_raw and os.path.exists(vec_path):
            df_v = pd.read_parquet(vec_path)
            for _, r in df_v.iterrows():
                fig_3d.add_trace(go.Scatter3d(x=[r['start_x'], r['end_x']], y=[r['start_y'], r['end_y']], z=[r['start_z'], r['end_z']], mode='lines', line=dict(width=5, color='gray'), opacity=0.4))

        # [C] 정렬 후 시공 모델 (최종)
        if ly_aligned and os.path.exists(vec_aligned_path):
            df_a = pd.read_parquet(vec_aligned_path)
            c_map = {'상면_V': 'red', '상면_H': 'orange', '하면_V': 'blue', '하면_H': 'cyan'}
            for _, r in df_a.iterrows():
                fig_3d.add_trace(go.Scatter3d(x=[r['start_x'], r['end_x']], y=[r['start_y'], r['end_y']], z=[r['start_z'], r['end_z']], mode='lines', line=dict(width=10, color=c_map.get(r['label'], 'green')), name=r['rebar_id']))

        fig_3d.update_layout(height=700, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data', bgcolor='white'))
        st.plotly_chart(fig_3d, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# [TAB 4] 실시간 협업
# ------------------------------------------------------------------
else:
    st.markdown("<div style='height: 500px; display: flex; align-items: center; justify-content: center; border: 2px dashed #e2e8f0; border-radius: 20px; color: #94a3b8;'><h1>🏗️ 현장 협업 모듈 (구현 준비 중)</h1></div>", unsafe_allow_html=True)
