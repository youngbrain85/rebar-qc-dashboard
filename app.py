import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 설정 및 고정 레이아웃 최적화
st.set_page_config(
    page_title="Rebar QC Analysis Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [Professional Single-Screen CSS] 
# 상단 여백 제거 및 컴포넌트 간격 최소화
st.markdown("""
    <style>
    /* 메인 컨테이너 여백 최소화 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    /* 헤더 및 위젯 간격 조절 */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem !important;
    }
    /* 배경색 및 폰트 설정 */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    /* 지표 카드 스타일 */
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    /* 제목 스타일 */
    .main-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .status-tag {
        font-size: 0.7rem;
        background: #0ea5e9;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 400;
    }
    </style>
    """, unsafe_allow_html=True)

# 헤더 섹션 (압축형)
st.markdown("""
    <div class="main-title">
        <div>🏗️ Rebar Quality Control Engine <span style="color:#64748b; font-size:1rem; font-weight:400; margin-left:10px;">| Analysis Dashboard</span></div>
        <div class="status-tag">SYSTEM ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 상단 지표 영역 (가로로 얇게 배치)
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.5])
    with m1: st.metric("Total Rebars", f"{len(df)}")
    with m2: st.metric("Normal (PASS)", f"{status_counts.get('PASS', 0)}")
    with m3: st.metric("Critical Errors", f"{status_counts.get('ERROR', 0)}", delta_color="inverse")
    with m4: st.metric("Missing", f"{status_counts.get('MISSING', 0)}", delta_color="inverse")
    
    # 범례 가이드 (Metrics 옆 공간 활용)
    with m5:
        st.markdown("""
        <div style="font-size: 0.7rem; color: #94a3b8; background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155;">
            <b>Inspection Legend:</b><br>
            ⚪ PASS (<20mm) | 🟢 CAUTION (20-30mm) | 🟠 ERROR (>30mm) | 🔴 MISSING
        </div>
        """, unsafe_allow_html=True)

    # 3. 메인 분석 섹션 (높이 고정으로 스크롤 방지)
    left_col, right_col = st.columns([6, 4])

    with left_col:
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [최적화] height를 650px 정도로 조절하여 1080p 화면에서 잘리지 않게 함
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: #0f172a; border-radius: 12px; border: 1px solid #1e293b;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="2"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.2"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=660)
        else:
            st.warning("GLB Model not found.")

    with right_col:
        # 통계 차트 (높이 축소)
        bar_data = pd.DataFrame({
            'Status': ['Pass', 'Caution', 'Error', 'Missing'],
            'Count': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), 
                     status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
            'Color': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_data, x='Count', y='Status', orientation='h',
                         color='Color',
                         color_discrete_map={'PASS': '#94a3b8', 'CAUTION': '#22c55e', 
                                            'ERROR': '#f59e0b', 'MISSING': '#ef4444'})
        
        fig_bar.update_layout(
            showlegend=False, height=220, margin=dict(l=0, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#94a3b8", xaxis_title="", yaxis_title=""
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 상세 데이터 테이블 (높이 최적화)
        st.markdown("<div style='font-size:0.9rem; font-weight:700; margin-bottom:5px;'>📋 Detailed Inspection Log</div>", unsafe_allow_html=True)
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer', 'Direction']].copy()
        df_view.columns = ['ID', 'Error(mm)', 'Stat', 'Lyr', 'Dir']
        
        # 오차순 정렬
        df_view['s'] = pd.to_numeric(df_view['Error(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='s', ascending=False).drop(columns=['s'])

        st.dataframe(df_view, use_container_width=True, height=360)

else:
    st.error("Analysis data (CSV) missing.")
