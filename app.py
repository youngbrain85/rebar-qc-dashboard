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
# 1. 배경을 화이트(#ffffff)로 변경하고 글자색을 다크(#1e293b)로 조정
# 2. 전반적인 폰트 크기 상향 조정
# 3. LH Green & Blue 포인트 유지
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

    /* 메인 컨테이너 여백 최적화 */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* LH 브랜드 헤더 스타일 */
    .lh-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #009944; /* LH Green 포인트 강화 */
    }
    .lh-logo-text {
        font-size: 2rem; /* 크기 상향 */
        font-weight: 900;
        letter-spacing: -1px;
        display: flex;
        align-items: center;
    }
    .lh-green { color: #009944; }
    .lh-blue { color: #0055a6; }
    .project-name {
        font-size: 1.2rem; /* 크기 상향 */
        font-weight: 500;
        color: #64748b;
        margin-left: 15px;
    }
    .system-status {
        font-size: 0.8rem; /* 크기 상향 */
        background: rgba(0, 153, 68, 0.1);
        color: #009944;
        border: 1px solid #009944;
        padding: 5px 15px;
        border-radius: 99px;
        font-weight: 700;
    }

    /* 지표 카드 (White Style) */
    div[data-testid="stMetric"] {
        background-color: #f8fafc !important;
        padding: 20px 25px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important; /* 크기 상향 */
        color: #64748b !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem !important; /* 크기 상향 */
        font-weight: 800 !important;
        color: #0f172a !important;
    }

    /* 범례 박스 스타일 */
    .legend-box {
        font-size: 0.85rem; /* 크기 상향 */
        color: #475569;
        background: #f8fafc;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 테이블(DataFrame) 스타일링 */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 섹션 제목 스타일 */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: #0f172a;
        border-left: 5px solid #009944;
        padding-left: 12px;
    }
    
    /* 스크롤바 커스터마이징 (화이트 테마용) */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
    """, unsafe_allow_html=True)

# LH 브랜드 헤더 섹션
st.markdown("""
    <div class="lh-header">
        <div class="lh-logo-text">
            <span class="lh-blue">L</span><span class="lh-green">H</span>
            <span style="font-size:1.6rem; color:#0f172a; margin-left:10px; font-weight:800;">한국토지주택공사</span>
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
                <div style="font-weight: 800; color: #009944; margin-bottom: 5px; font-size: 0.95rem;">LH 시공 품질 가이드라인</div>
                <div style="line-height: 1.6; color: #475569;">
                    ⚪ <b style="color:#0f172a">PASS</b>: <20mm (정상 시공)<br>
                    🟢 <b style="color:#009944">CAUTION</b>: 20-30mm (주의 필요)<br>
                    🟠 <b style="color:#f59e0b">ERROR</b>: >30mm (재시공 권고)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. 메인 인터페이스
    left_col, right_col = st.columns([6, 4])

    with left_col:
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # 3D 모델 뷰어 (화이트 배경 최적화)
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: #ffffff; border-radius: 15px; border: 1px solid #e2e8f0;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.1"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=660)

    with right_col:
        # 화이트 테마에 맞춘 통계 차트
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
            showlegend=False, height=240, margin=dict(l=0, r=20, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#475569", xaxis_title="", yaxis_title="",
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), 
            yaxis=dict(showgrid=False),
            font=dict(size=13)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 개별 상세 검측 로그
        st.markdown("<div class='section-title'>📋 개별 철근 검측 상세 데이터</div>", unsafe_allow_html=True)
        
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
        df_view.columns = ['ID', '오차(mm)', '검측결과', '레이어']
        
        # 정렬 로직
        df_view['temp_sort'] = pd.to_numeric(df_view['오차(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='temp_sort', ascending=False).drop(columns=['temp_sort'])

        # Streamlit Native DataFrame (White Theme)
        st.dataframe(df_view, use_container_width=True, height=380)

else:
    st.error("데이터 파일을 찾을 수 없습니다. (final_qc_report_detailed.csv)")
