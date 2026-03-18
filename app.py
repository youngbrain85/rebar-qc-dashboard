import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 설정 및 LH 브랜드 테마 적용 (화이트 배경 최적화)
st.set_page_config(
    page_title="LH | Rebar QC Analysis Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [LH Enterprise Dashboard CSS - White Version]
# 1. 상단 여백 및 헤더 간격 최소화 (Single-screen 최적화)
# 2. 3D 뷰어와 테이블 하단 높이 정렬
st.markdown("""
    <style>
    /* 상단 Streamlit 헤더/메뉴 제거 */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* 폰트 및 배경 설정 (Clean White) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    .stApp {
        background-color: #ffffff;
        color: #1e293b;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }

    /* 메인 컨테이너 상단 여백 최소화 */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* LH 브랜드 헤더 스타일 (간격 축소) */
    .lh-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #009944;
    }
    .lh-logo-text {
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: -1px;
        display: flex;
        align-items: center;
    }
    .lh-green { color: #009944; }
    .lh-blue { color: #0055a6; }
    .project-name {
        font-size: 1.1rem;
        font-weight: 500;
        color: #64748b;
        margin-left: 12px;
    }
    .system-status {
        font-size: 0.75rem;
        background: rgba(0, 153, 68, 0.1);
        color: #009944;
        border: 1px solid #009944;
        padding: 3px 12px;
        border-radius: 99px;
        font-weight: 700;
    }

    /* 지표 카드 (압축형) */
    div[data-testid="stMetric"] {
        background-color: #f8fafc !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #64748b !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }

    /* 범례 박스 스타일 */
    .legend-box {
        font-size: 0.8rem;
        color: #475569;
        background: #f8fafc;
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 테이블(DataFrame) 스타일링 */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* 섹션 제목 스타일 */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.5rem;
        margin-bottom: 8px;
        color: #0f172a;
        border-left: 5px solid #009944;
        padding-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# LH 브랜드 헤더 섹션
st.markdown("""
    <div class="lh-header">
        <div class="lh-logo-text">
            <span class="lh-blue">L</span><span class="lh-green">H</span>
            <span style="font-size:1.5rem; color:#0f172a; margin-left:8px; font-weight:800;">한국토지주택공사</span>
            <span class="project-name">| 철근 배근 시공 품질 자동 검측 엔진</span>
        </div>
        <div class="system-status">● ANALYSIS SYSTEM ONLINE</div>
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
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.3])
    with m1: st.metric("전체 검측 수", f"{len(df)}")
    with m2: st.metric("정상 (PASS)", f"{status_counts.get('PASS', 0)}")
    with m3: st.metric("주의/오류 (ISSUE)", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
    with m4: st.metric("미시공 (MISSING)", f"{status_counts.get('MISSING', 0)}")
    with m5:
        st.markdown("""
            <div class="legend-box">
                <div style="font-weight: 800; color: #009944; margin-bottom: 3px; font-size: 0.85rem;">LH 시공 품질 가이드라인</div>
                <div style="line-height: 1.5; color: #475569;">
                    ⚪ <b style="color:#0f172a">PASS</b>: <20mm | 🟢 <b style="color:#009944">CAUTION</b>: 20-30mm<br>
                    🟠 <b style="color:#f59e0b">ERROR</b>: >30mm | 🔴 <b style="color:#ef4444">MISSING</b>: 미탐지
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. 메인 인터페이스 (높이 밸런스 조정)
    # 전체 뷰포트 높이에 맞추기 위해 높이 값을 정밀 조정함
    left_col, right_col = st.columns([6, 4])

    with left_col:
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # 3D 모델 뷰어 높이 고정
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 620px; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.1"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=630)

    with right_col:
        # 통계 차트 영역
        bar_data = pd.DataFrame({
            '상태': ['Pass', 'Caution', 'Error', 'Missing'],
            'Count': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), 
                     status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_data, x='Count', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map={
                             'PASS': '#94a3b8',   # 회색
                             'CAUTION': '#009944', # LH Green
                             'ERROR': '#f59e0b',   # 주황
                             'MISSING': '#ef4444'  # 빨강
                         },
                         text='Count')
        
        fig_bar.update_layout(
            showlegend=False, height=210, margin=dict(l=0, r=20, t=5, b=5),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#475569", xaxis_title="", yaxis_title="",
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), 
            yaxis=dict(showgrid=False),
            font=dict(size=12)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 개별 상세 검측 로그 (높이 축소하여 좌측 3D 뷰어 하단과 맞춤)
        st.markdown("<div class='section-title'>📋 개별 철근 검측 상세 데이터</div>", unsafe_allow_html=True)
        
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
        df_view.columns = ['ID', '오차(mm)', '검측결과', '레이어']
        
        # 정렬 로직
        df_view['temp_sort'] = pd.to_numeric(df_view['오차(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='temp_sort', ascending=False).drop(columns=['temp_sort'])

        # 테이블 높이를 340으로 조정하여 좌측 3D 뷰어와 하단 정렬 맞춤
        st.dataframe(df_view, use_container_width=True, height=340)

else:
    st.error("데이터 파일을 찾을 수 없습니다. (final_qc_report_detailed.csv)")
