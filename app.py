import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import numpy as np

# 1. 페이지 설정 및 브랜드 테마
st.set_page_config(
    page_title="LH | Rebar Digital Twin QC Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 파일 로딩을 위한 헬퍼 함수 (Base64 인코딩)
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# 로고 설정 (lh_logo.png가 없을 경우 텍스트로 대체)
lh_logo_path = "lh_logo.png"
logo_b64 = get_base64_of_bin_file(lh_logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="lh-logo-img">' if logo_b64 else '<span style="font-size:2.5rem; font-weight:900;"><span style="color:#0055a6;">L</span><span style="color:#009944;">H</span></span>'

# [LH Enterprise Custom CSS]
st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    .stApp {{ background-color: #ffffff; color: #1e293b; font-family: 'Inter', 'Noto Sans KR', sans-serif; }}
    .stApp::before {{ content: ''; position: fixed; top: 0; left: 0; width: 450px; height: 350px; background-color: #b1d632; clip-path: polygon(0 0, 100% 0, 0 85%); z-index: -2; opacity: 0.9; pointer-events: none; }}
    .stApp::after {{ content: ''; position: fixed; bottom: 0; right: 0; width: 450px; height: 350px; background-color: #b1d632; clip-path: polygon(100% 15%, 100% 100%, 0 100%); z-index: -2; opacity: 0.9; pointer-events: none; }}
    
    .main .block-container {{ padding-top: 1rem !important; margin-top: -30px; }}
    
    .lh-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 4px solid #009944; padding-bottom: 10px; margin-bottom: 15px; }}
    .project-name {{ font-size: 2.4rem; font-weight: 900; color: #0f172a; border-left: 5px solid #e2e8f0; padding-left: 20px; letter-spacing: -1.5px; }}
    .section-title {{ font-size: 1.6rem; font-weight: 800; margin: 25px 0 15px 0; border-left: 8px solid #009944; padding-left: 15px; color: #0f172a; }}
    .analysis-container {{ background: rgba(255, 255, 255, 0.9); border-radius: 20px; padding: 25px; border: 1px solid #e2e8f0; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); }}
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 헤더 레이아웃
st.markdown(f"""
    <div class="lh-header">
        <div style="display:flex; align-items:center; gap:15px;">
            {logo_html}
            <div class="project-name">철근 배근 시공 품질 자동 검측 엔진</div>
        </div>
        <div style="font-size:0.85rem; background:white; color:#009944; border:2px solid #009944; padding:7px 18px; border-radius:99px; font-weight:800;">● SYSTEM LIVE</div>
    </div>
    """, unsafe_allow_html=True)

# 3. 탭 네비게이션
tabs = ["철근 시공오차 분석", "스캔 데이터 분석", "3D 모델링", "실시간 협업"]
selected_tab = st.pills("", tabs, selection_mode="single", default="철근 시공오차 분석", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB 1: 철근 시공오차 분석 (종합 리포트)
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
            st.markdown('<div style="font-size:0.9rem; background:white; padding:10px; border:2.5px solid #009944; border-radius:12px;"><b>QC 기준:</b><br>PASS < 20mm | ERROR > 30mm</div>', unsafe_allow_html=True)
        
        st.markdown("<div class='section-title'>📋 세부 검측 내역</div>", unsafe_allow_html=True)
        st.dataframe(df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']], use_container_width=True, height=450)
    else:
        st.warning("'final_qc_report_detailed.csv' 파일이 필요합니다.")

# ------------------------------------------------------------------
# TAB 2: 스캔 데이터 분석 (포인트 클라우드 & 피크 탐지)
# ------------------------------------------------------------------
elif selected_tab == "스캔 데이터 분석":
    st.markdown("<div class='section-title'>🔍 포인트 클라우드 분석 프로세스</div>", unsafe_allow_html=True)
    
    # [1] 데이터 로드
    raw_path, seg_path = "raw_cloud.parquet", "segmented_rebars.parquet"
    col_pc1, col_pc2 = st.columns(2)
    
    with col_pc1:
        st.subheader("1. 원본 데이터 (Raw)")
        if os.path.exists(raw_path):
            df_raw = pd.read_parquet(raw_path)
            fig_raw = go.Figure(data=[go.Scatter3d(x=df_raw['x'], y=df_raw['y'], z=df_raw['z'], mode='markers', marker=dict(size=1, color='#94a3b8', opacity=0.4))])
            fig_raw.update_layout(height=500, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_raw, use_container_width=True)
            
    with col_pc2:
        st.subheader("2. 객체 분할 결과 (Segmented)")
        if os.path.exists(seg_path):
            df_seg = pd.read_parquet(seg_path)
            fig_seg = px.scatter_3d(df_seg, x='x', y='y', z='z', color='rebar_id', opacity=0.8)
            fig_seg.update_traces(marker=dict(size=0.8))
            fig_seg.update_layout(showlegend=False, height=500, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_seg, use_container_width=True)

    # [2] 피크 탐지 이미지 로그
    st.markdown("---")
    st.subheader("3. 밀도 기반 피크 탐지 분석 (Peak Finding Logs)")
    img_c1, img_c2 = st.columns(2)
    with img_c1:
        if os.path.exists("top v_x.png"): st.image("top v_x.png", caption="Top Layer - Vertical")
        if os.path.exists("bottom v_x.png"): st.image("bottom v_x.png", caption="Bottom Layer - Vertical")
    with img_c2:
        if os.path.exists("top h_z.png"): st.image("top h_z.png", caption="Top Layer - Horizontal")
        if os.path.exists("bottom h_z.png"): st.image("bottom h_z.png", caption="Bottom Layer - Horizontal")

# ------------------------------------------------------------------
# TAB 3: 3D 모델링 (설계 vs 시공 정합)
# ------------------------------------------------------------------
elif selected_tab == "3D 모델링":
    st.markdown("<div class='section-title'>🏗️ 설계-시공 통합 디지털 트윈 분석</div>", unsafe_allow_html=True)
    
    mesh_p = "design_mesh.parquet"
    vec_p = "rebar_vectors.parquet"
    vec_a_p = "rebar_vectors_aligned.parquet"
    
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    ctrl_col, view_col = st.columns([2.5, 7.5])
    
    with ctrl_col:
        st.subheader("🛠️ 시각화 레이어")
        ly_design = st.checkbox("BIM 설계 모델 (Design)", value=True)
        ly_raw = st.checkbox("정렬 전 시공 모델 (Initial)", value=False)
        ly_aligned = st.checkbox("정렬 후 시공 모델 (Aligned)", value=True)
        
        st.markdown("---")
        if os.path.exists(vec_a_p):
            df_a = pd.read_parquet(vec_a_p)
            st.metric("정합 성공률 (Fitness)", f"{df_a['fitness'].iloc[0]:.4f}")
            st.metric("평균 정밀도 (RMSE)", f"{df_a['rmse'].iloc[0]:.2f} mm")

    with view_col:
        fig_3d = go.Figure()
        
        # [A] 설계 모델 복원
        if ly_design and os.path.exists(mesh_p):
            df_m = pd.read_parquet(mesh_p)
            m_data = df_m['mesh_json'].iloc[0] if 'mesh_json' in df_m.columns else df_m['data'].iloc[0]
            v, f = np.array(m_data['vertices']), np.array(m_data['faces'])
            fig_3d.add_trace(go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='lightcyan', opacity=0.3, name='Design BIM'))

        # [B] 정렬 전 벡터
        if ly_raw and os.path.exists(vec_p):
            df_v = pd.read_parquet(vec_p)
            for _, r in df_v.iterrows():
                fig_3d.add_trace(go.Scatter3d(x=[r['start_x'], r['end_x']], y=[r['start_y'], r['end_y']], z=[r['start_z'], r['end_z']], mode='lines', line=dict(width=5, color='gray'), opacity=0.4))

        # [C] 정렬 후 벡터 (최종 결과)
        if ly_aligned and os.path.exists(vec_a_p):
            df_a = pd.read_parquet(vec_a_p)
            c_map = {'상면_V': 'red', '상면_H': 'orange', '하면_V': 'blue', '하면_H': 'cyan'}
            for _, r in df_a.iterrows():
                fig_3d.add_trace(go.Scatter3d(x=[r['start_x'], r['end_x']], y=[r['start_y'], r['end_y']], z=[r['start_z'], r['end_z']], mode='lines', line=dict(width=9, color=r.get('color', c_map.get(r['label'], 'green'))), name=r['rebar_id']))

        fig_3d.update_layout(height=750, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data', bgcolor='white'))
        st.plotly_chart(fig_3d, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB 4: 실시간 협업 (구현 예정 프레임)
# ------------------------------------------------------------------
else:
    st.markdown("<div style='height: 500px; display: flex; align-items: center; justify-content: center; border: 2px dashed #e2e8f0; border-radius: 20px; color: #94a3b8;'><h1>🏗️ 실시간 현장 협업 모듈 준비 중</h1></div>", unsafe_allow_html=True)
