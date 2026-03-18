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
# 2. 상단 흰색 바 제거 및 LH 공식 로고 배치 최적화
st.markdown("""
    <style>
    /* 상단 Streamlit 헤더 제거 */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none !important;}
    
    /* 폰트 및 배경 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    .stApp {
        background-color: #020617;
        color: #f8fafc;
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
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #009944;
    }
    .lh-brand-box {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .lh-logo-img {
        height: 45px; /* 로고 높이 조절 */
        filter: brightness(1.1); /* 다크모드에서 시인성 확보 */
    }
    .project-name {
        font-size: 1.2rem;
        font-weight: 400;
        color: #94a3b8;
        border-left: 1px solid #334155;
        padding-left: 15px;
        margin-left: 5px;
    }
    .system-status {
        font-size: 0.8rem;
        background: rgba(0, 153, 68, 0.2);
        color: #4ade80;
        border: 1px solid #009944;
        padding: 5px 15px;
        border-radius: 99px;
        font-weight: 700;
    }

    /* 지표 카드 (LH Style) */
    div[data-testid="stMetric"] {
        background-color: #0f172a !important;
        padding: 20px 25px !important;
        border-radius: 12px !important;
        border: 1px solid #1e293b !important;
        box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    /* 범례 박스 스타일 */
    .legend-box {
        font-size: 0.85rem;
        color: #cbd5e1;
        background: #0f172a;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* 섹션 타이틀 */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: #f8fafc;
        border-left: 5px solid #009944;
        padding-left: 12px;
    }

    /* 스크롤바 커스터마이징 */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# LH 공식 로고 URL (공공데이터/공식홈페이지 기반 경로)
# 사용자가 직접 파일을 업로드한 경우 'lh_logo.png' 등으로 경로 수정 가능
lh_logo_url = "https://www.lh.or.kr/images/common/logo.png" 

# LH 브랜드 헤더 섹션 (이미지 로고 포함)
st.markdown(f"""
    <div class="lh-header">
        <div class="lh-brand-box">
            <img src="{lh_logo_url}" class="lh-logo-img" alt="LH Logo">
            <span style="font-size:1.6rem; color:#f8fafc; font-weight:800; margin-left:5px;">한국토지주택공사</span>
            <span class="project-name">철근 배근 시공 품질 자동 검측 엔진</span>
        </div>
        <div class="system-status">● ANALYSIS SYSTEM ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
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
                <div style="line-height: 1.6; color: #94a3b8;">
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
        bar_data = pd.DataFrame({
            '상태': ['Pass', 'Caution', 'Error', 'Missing'],
            'Count': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), 
                     status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_data, x='Count', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map={
                             'PASS': '#94a3b8',
                             'CAUTION': '#009944',
                             'ERROR': '#f59e0b',
                             'MISSING': '#ef4444'
                         },
                         text='Count')
        
        fig_bar.update_layout(
            showlegend=False, height=240, margin=dict(l=0, r=20, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#94a3b8", xaxis_title="", yaxis_title="",
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<div class='section-title'>📋 개별 철근 검측 상세 데이터</div>", unsafe_allow_html=True)
        
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
        df_view.columns = ['ID', '오차(mm)', '검측결과', '레이어']
        
        df_view['temp_sort'] = pd.to_numeric(df_view['오차(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='temp_sort', ascending=False).drop(columns=['temp_sort'])

        st.dataframe(df_view, use_container_width=True, height=380)

else:
    st.error("데이터 파일(CSV)을 찾을 수 없습니다.")
