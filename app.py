import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import numpy as np
import json

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

# 로고 설정 (lh_logo.png)
lh_logo_path = "lh_logo.png"
logo_b64 = get_base64_of_bin_file(lh_logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="lh-logo-img">' if logo_b64 else '<span style="font-size:1.5rem; font-weight:900;"><span style="color:#0055a6;">L</span><span style="color:#009944;">H</span></span>'

# [LH Enterprise Dashboard CSS]
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
    div[data-testid="stMetric"] {{ background-color: white !important; padding: 10px 20px !important; border-radius: 12px !important; border: 1px solid #e2e8f0 !important; }}
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

tabs = ["철근 시공오차 분석", "스캔 데이터 분석", "3D 모델링", "실시간 협업"]
selected_tab = st.pills("", tabs, selection_mode="single", default="철근 시공오차 분석", label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# [TAB 1] 철근 시공오차 분석 (고정)
# ------------------------------------------------------------------
if selected_tab == "철근 시공오차 분석":
    csv_file = "final_qc_report_detailed.csv"
    glb_file = "construction_qc_model.glb"
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        status_counts = df['Status'].value_counts()
        m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.5])
        m1.metric("전체 검측", f"{len(df)}EA")
        m2.metric("정상 (PASS)", f"{status_counts.get('PASS', 0)}")
        m3.metric("주의/오류", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
        m4.metric("미탐지", f"{status_counts.get('MISSING', 0)}")
        with m5: st.markdown('<div style="font-size:0.85rem; padding:10px; border:2px solid #009944; border-radius:10px; background:white;"><b>품질 기준:</b> PASS < 20mm | ERROR > 30mm</div>', unsafe_allow_html=True)
        left_col, right_col = st.columns([6, 4])
        with left_col:
            st.markdown("<div class='section-title'>🏗️ 검측 결과 3D 하이라이트</div>", unsafe_allow_html=True)
            if os.path.exists(glb_file):
                b64_glb = get_base64_of_bin_file(glb_file)
                st.components.v1.html(f"""
                    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
                    <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                                  style="width: 100%; height: 600px; background-color: #f8fafc; border-radius: 15px; border: 1px solid #e2e8f0;" 
                                  camera-controls touch-action="pan-y" shadow-intensity="1" 
                                  orientation="-90deg -90deg -90deg"
                                  exposure="1.2" environment-image="neutral"></model-viewer>
                """, height=610)
        with right_col:
            st.markdown("<div class='section-title'>📊 시공 품질 상태 분포</div>", unsafe_allow_html=True)
            bar_data = pd.DataFrame({
                '상태': ['Pass', 'Caution', 'Error', 'Missing'],
                '개수': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
                'Color': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
            })
            fig_bar = px.bar(bar_data, x='개수', y='상태', orientation='h', color='Color',
                             color_discrete_map={'PASS': '#94a3b8', 'CAUTION': '#009944', 'ERROR': '#f59e0b', 'MISSING': '#ef4444'}, text='개수')
            fig_bar.update_layout(showlegend=False, height=250, margin=dict(l=0,r=10,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("<div class='section-title'>📋 개별 검측 상세 데이터</div>", unsafe_allow_html=True)
            st.dataframe(df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']], use_container_width=True, height=280)

# ------------------------------------------------------------------
# [TAB 2] 스캔 데이터 분석 (고정)
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
        st.subheader("2. 객체 분할 결과 (Segmented)")
        if os.path.exists(seg_p):
            df_seg = pd.read_parquet(seg_p)
            fig_seg = px.scatter_3d(df_seg, x='x', y='y', z='z', color='rebar_id', opacity=0.8)
            fig_seg.update_traces(marker=dict(size=0.7))
            fig_seg.update_layout(showlegend=False, height=450, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data'))
            st.plotly_chart(fig_seg, use_container_width=True)
    st.markdown("---")
    st.subheader("3. 피크 탐지 분석 로그")
    ic1, ic2 = st.columns(2)
    with ic1:
        for img in ["top v_x.png", "bottom v_x.png"]:
            if os.path.exists(img): st.image(img, use_container_width=True)
    with ic2:
        for img in ["top h_z.png", "bottom h_z.png"]:
            if os.path.exists(img): st.image(img, use_container_width=True)

# ------------------------------------------------------------------
# [TAB 3] 3D 모델링 (개별 시각화 및 로딩 강화 버전)
# ------------------------------------------------------------------
elif selected_tab == "3D 모델링":
    st.markdown("<div class='section-title'>🏗️ 디지털 트윈 단계별 모델 분석</div>", unsafe_allow_html=True)
    mesh_path = "design_mesh.parquet"
    vec_raw_path = "rebar_vectors.parquet"
    vec_aligned_path = "rebar_vectors_aligned.parquet"
    
    # 3.1 설계 모델 (BIM) - 시각화 강화
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    st.subheader("1. BIM 설계 모델 (Design Mesh)")
    if os.path.exists(mesh_path):
        try:
            df_m = pd.read_parquet(mesh_path)
            # 파일 내 mesh_json 컬럼 확인 
            m_data = df_m['mesh_json'].iloc[0]
            
            # JSON/Dict 처리 로직
            if isinstance(m_data, str): 
                m_data = json.loads(m_data)
            
            # 정점 및 면 데이터 추출 및 2D 구조화 강제 적용 
            v = np.array(m_data['vertices']).reshape(-1, 3)
            f = np.array(m_data['faces']).reshape(-1, 3)
            
            if len(v) > 0:
                # 가시성을 위해 색상을 'steelblue'로 변경하고 평면 셰이딩 적용
                fig_design = go.Figure(data=[go.Mesh3d(
                    x=v[:,0], y=v[:,1], z=v[:,2], 
                    i=f[:,0], j=f[:,1], k=f[:,2], 
                    color='steelblue',   # 더 잘 보이는 색상으로 변경
                    opacity=1.0,         # 투명도 제거하여 확실히 보이게 설정
                    flatshading=True,    # 면의 굴곡이 잘 보이도록 설정
                    name='Design BIM'
                )])
                fig_design.update_layout(
                    height=600, margin=dict(l=0,r=0,b=0,t=0),
                    scene=dict(aspectmode='data', bgcolor='#f8fafc') # 배경색을 살짝 어둡게 변경
                )
                st.plotly_chart(fig_design, use_container_width=True)
                st.success(f"✅ 설계 모델 로드 완료: 정점 {len(v)}개, 면 {len(f)}개")
            else:
                st.warning("⚠️ 설계 모델 데이터는 로드되었으나 정점 정보가 비어 있습니다.")
                
        except Exception as e:
            st.error(f"❌ 설계 모델 로딩 중 오류 발생: {e}")
    else:
        st.info("💡 설계 모델 파일(design_mesh.parquet)이 없습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3.2 시공 모델 (초기 스캔 - start_x 등 컬럼명 반영) [cite: 3]
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    st.subheader("2. 시공 모델 (Initial Scan Model)")
    if os.path.exists(vec_raw_path):
        df_v = pd.read_parquet(vec_raw_path)
        fig_raw_v = go.Figure()
        for _, r in df_v.iterrows():
            fig_raw_v.add_trace(go.Scatter3d(
                x=[r['start_x'], r['end_x']], 
                y=[r['start_y'], r['end_y']], 
                z=[r['start_z'], r['end_z']], 
                mode='lines', line=dict(width=6, color='gray'), showlegend=False
            ))
        fig_raw_v.update_layout(height=500, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data', bgcolor='white'))
        st.plotly_chart(fig_raw_v, use_container_width=True)
    else:
        st.info("💡 시공 초기 모델 파일(rebar_vectors.parquet)이 없습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3.3 시공/설계 정합 모델 (최종 - p1_x 등 컬럼명 반영) [cite: 1]
    st.markdown("<div class='analysis-container'>", unsafe_allow_html=True)
    st.subheader("3. 시공/설계 정합 모델 (Aligned Digital Twin)")
    if os.path.exists(vec_aligned_path):
        df_a = pd.read_parquet(vec_aligned_path)
        c_map = {'상면_V': 'red', '상면_H': 'orange', '하면_V': 'blue', '하면_H': 'cyan'}
        fig_aligned_v = go.Figure()
        for _, r in df_a.iterrows():
            fig_aligned_v.add_trace(go.Scatter3d(
                x=[r['p1_x'], r['p2_x']], 
                y=[r['p1_y'], r['p2_y']], 
                z=[r['p1_z'], r['p2_z']], 
                mode='lines', line=dict(width=10, color=c_map.get(r['label'], 'green')),
                name=r['rebar_id']
            ))
        fig_aligned_v.update_layout(height=500, margin=dict(l=0,r=0,b=0,t=0), scene=dict(aspectmode='data', bgcolor='white'), showlegend=False)
        st.plotly_chart(fig_aligned_v, use_container_width=True)
    else:
        st.info("💡 정합 모델 파일(rebar_vectors_aligned.parquet)이 없습니다.")
    st.markdown("</div>", unsafe_allow_html=True)
