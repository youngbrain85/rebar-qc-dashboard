import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 설정 및 LH 브랜드 테마 적용
st.set_page_config(
    page_title="LH | Rebar QC Analysis Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [LH Enterprise Dashboard CSS]
# 1. LH 로고 색상 반영: LH Green (#009944), LH Blue (#0055a6)
# 2. 상단 헤더 및 불필요한 Streamlit 요소 제거
# 3. 프리미엄 다크 네이비 배경과 LH 브랜드 컬러의 조화
st.markdown("""
    <style>
    /* 상단 Streamlit 헤더/메뉴 제거 */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* 폰트 및 배경 설정 (LH 전용 Deep Navy & Slate) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    .stApp {
        background-color: #020617;
        color: #f8fafc;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }

    /* 메인 컨테이너 여백 최적화 */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* LH 브랜드 헤더 스타일 */
    .lh-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #009944; /* LH Green 포인트 */
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
        font-weight: 400;
        color: #94a3b8;
        margin-left: 15px;
    }
    .system-status {
        font-size: 0.7rem;
        background: rgba(0, 153, 68, 0.2);
        color: #4ade80;
        border: 1px solid #009944;
        padding: 4px 12px;
        border-radius: 99px;
        font-weight: 700;
    }

    /* 지표 카드 (LH Style) */
    div[data-testid="stMetric"] {
        background-color: #0f172a !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        border: 1px solid #1e293b !important;
        box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    /* 범례 박스 스타일 */
    .legend-box {
        font-size: 0.75rem;
        color: #cbd5e1;
        background: #0f172a;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 테이블(DataFrame) 세련된 스타일링 */
    .stDataFrame {
        border: 1px solid #1e293b;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* 스크롤바 커스터마이징 */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# LH 브랜드 헤더 섹션
st.markdown("""
    <div class="lh-header">
        <div class="lh-logo-text">
            <span class="lh-blue">L</span><span class="lh-green">H</span>
            <span style="font-size:1.4rem; color:#f8fafc; margin-left:8px; font-weight:700;">한국토지주택공사</span>
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
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.2])
    with m1: st.metric("전체 검측 수", f"{len(df)}")
    with m2: st.metric("정상 (PASS)", f"{status_counts.get('PASS', 0)}")
    with m3: st.metric("주의/오류 (ISSUE)", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
    with m4: st.metric("미시공 (MISSING)", f"{status_counts.get('MISSING', 0)}")
    with m5:
        st.markdown("""
            <div class="legend-box">
                <div style="font-weight: 800; color: #009944; margin-bottom: 4px; font-size: 0.85rem;">LH 시공 품질 가이드라인</div>
                <div style="line-height: 1.5; color: #94a3b8;">
                    ⚪ <b>PASS</b>: <20mm (정상 시공)<br>
                    🟢 <b>CAUTION</b>: 20-30mm (주의 필요)<br>
                    🟠 <b>ERROR</b>: >30mm (재시공 권고)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. 메인 인터페이스
    left_col, right_col = st.columns([6, 4])

    with left_col:
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # 3D 모델 뷰어 (LH 최적화 설정)
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: #020617; border-radius: 15px; border: 1px solid #1e293b;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1.5"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.3"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=660)

    with right_col:
        # LH 브랜드 컬러가 적용된 통계 차트
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
            font_color="#94a3b8", xaxis_title="", yaxis_title="",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 개별 상세 검측 로그 (세련된 테이블)
        st.markdown("<div style='font-size:1rem; font-weight:700; margin-bottom:10px; color:#f8fafc; border-left:4px solid #009944; padding-left:10px;'>📋 개별 철근 검측 상세 데이터</div>", unsafe_allow_html=True)
        
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
        df_view.columns = ['ID', '오차(mm)', '검측결과', '레이어']
        
        # 정렬 로직
        df_view['temp_sort'] = pd.to_numeric(df_view['오차(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='temp_sort', ascending=False).drop(columns=['temp_sort'])

        # Streamlit Native DataFrame
        st.dataframe(df_view, use_container_width=True, height=380)

else:
    st.error("데이터 파일을 찾을 수 없습니다. (final_qc_report_detailed.csv)")
