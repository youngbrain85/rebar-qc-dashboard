import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 설정 및 전문가용 다크 테마 적용
st.set_page_config(
    page_title="Rebar QC Analysis Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [Professional Dashboard CSS]
# 1. 상단 흰색 바(Header) 및 메뉴 완벽 제거
# 2. 메인 컨테이너 여백 최적화 (FHD/QHD 모니터 꽉 차게 설정)
# 3. 테이블 및 위젯 디자인 커스터마이징
st.markdown("""
    <style>
    /* 상단 메뉴바, 헤더, 푸터 강제 제거 */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* 전체 배경 및 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    /* 메인 영역 상단 여백 제거 및 스크롤 방지 */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* 제목 및 상태 태그 스타일 */
    .main-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .status-tag {
        font-size: 0.65rem;
        background: #0ea5e9;
        color: white;
        padding: 3px 10px;
        border-radius: 4px;
        font-weight: 600;
        letter-spacing: 0.05rem;
    }

    /* 지표 카드 스타일 (Metircs) */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        padding: 15px 20px !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    /* 범례 박스 스타일 */
    .legend-box {
        font-size: 0.75rem;
        color: #cbd5e1;
        background: #1e293b;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #334155;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 데이터프레임(테이블) 배경 설정 */
    .stDataFrame {
        background: #1e293b;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# 헤더 섹션
st.markdown("""
    <div class="main-title">
        <div>🏗️ Rebar Quality Control Engine <span style="color:#64748b; font-size:1.1rem; font-weight:400; margin-left:12px;">| 정밀 시공 품질 분석 대시보드</span></div>
        <div class="status-tag">REAL-TIME CONNECTED</div>
    </div>
    """, unsafe_allow_html=True)

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    # 데이터 로드
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 지표 행 (Metrics & Legend)
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.2])
    with m1: st.metric("전체 철근 수", f"{len(df)}")
    with m2: st.metric("정상 시공 (PASS)", f"{status_counts.get('PASS', 0)}")
    with m3: st.metric("주의/오류 (ISSUE)", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
    with m4: st.metric("미시공 (MISSING)", f"{status_counts.get('MISSING', 0)}")
    with m5:
        st.markdown("""
            <div class="legend-box">
                <div style="font-weight: 800; color: #38bdf8; margin-bottom: 4px; font-size: 0.8rem;">검측 임계치 기준</div>
                <div style="line-height: 1.4;">
                    ⚪ <b>PASS</b>: <20mm | 🟢 <b>CAUTION</b>: 20-30mm<br>
                    🟠 <b>ERROR</b>: >30mm | 🔴 <b>MISSING</b>: 미탐지
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. 메인 콘텐츠
    left_col, right_col = st.columns([6, 4])

    with left_col:
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [Orientation] -90deg -90deg -90deg 반영
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: #0f172a; border-radius: 15px; border: 1px solid #1e293b;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="2"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.2"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=660)

    with right_col:
        # 상태 요약 차트
        bar_data = pd.DataFrame({
            '상태': ['Pass', 'Caution', 'Error', 'Missing'],
            'Count': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), 
                     status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_data, x='Count', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map={
                             'PASS': '#94a3b8', 'CAUTION': '#008000', 
                             'ERROR': '#FFA500', 'MISSING': '#FF0000'
                         },
                         text='Count')
        
        fig_bar.update_layout(
            showlegend=False, height=240, margin=dict(l=0, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#94a3b8", xaxis_title="", yaxis_title=""
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 상세 로그 테이블
        st.markdown("<div style='font-size:1rem; font-weight:700; margin-bottom:8px; color:#f1f5f9;'>📋 Individual Inspection Log</div>", unsafe_allow_html=True)
        
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
        df_view.columns = ['REBAR ID', '오차(mm)', '상태', 'LAYER']
        
        # 정렬 로직
        df_view['temp_sort'] = pd.to_numeric(df_view['오차(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='temp_sort', ascending=False).drop(columns=['temp_sort'])

        st.dataframe(df_view, use_container_width=True, height=380)

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
