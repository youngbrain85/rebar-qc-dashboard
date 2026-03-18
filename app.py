import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 설정 및 LH 브랜드 테마 적용 (배경 디자인 최적화)
st.set_page_config(
    page_title="LH | Rebar QC Analysis Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 로고 파일을 Base64로 인코딩하는 함수
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# 로고 HTML 생성 (깃허브에 올리신 lh_logo.png 우선 사용)
logo_html = ""
lh_logo_path = "lh_logo.png"
b64 = get_base64_of_bin_file(lh_logo_path)
if b64:
    logo_html = f'<img src="data:image/png;base64,{b64}" class="lh-logo-img">'
else:
    # 파일이 없을 경우 텍스트 로고로 대체
    logo_html = '<span style="font-size:2.5rem; font-weight:900;"><span style="color:#0055a6;">L</span><span style="color:#009944;">H</span></span>'

# [LH Enterprise Dashboard CSS - Premium White Version]
st.markdown(f"""
    <style>
    /* 상단 Streamlit 헤더/메뉴 제거 */
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    
    /* 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    /* 배경 디자인 구현 (상하단 연두색 포인트 블록) */
    .stApp {{
        background-color: #ffffff;
        background-image: none;
        color: #1e293b;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }}
    
    /* 왼쪽 상단 연두색 블록 - z-index를 -1로 내려서 가려짐 방지 */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 400px;
        height: 300px;
        background-color: #b1d632;
        clip-path: polygon(0 0, 100% 0, 0 85%);
        z-index: -1;
        opacity: 0.9;
        pointer-events: none;
    }}
    
    /* 오른쪽 하단 연두색 블록 - z-index를 -1로 내려서 가려짐 방지 */
    .stApp::after {{
        content: '';
        position: fixed;
        bottom: 0;
        right: 0;
        width: 400px;
        height: 300px;
        background-color: #b1d632;
        clip-path: polygon(100% 15%, 100% 100%, 0 100%);
        z-index: -1;
        opacity: 0.9;
        pointer-events: none;
    }}

    /* 메인 컨테이너 설정 (콘텐츠가 배경보다 위에 오도록 명시) */
    .main .block-container {{
        position: relative;
        z-index: 1;
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }}

    /* LH 브랜드 헤더 스타일 */
    .lh-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 4px solid #009944;
    }}
    .lh-brand-box {{
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    .lh-logo-img {{
        height: 65px; /* 로고 크기 살짝 확대 */
        width: auto;
    }}
    .project-name {{
        font-size: 2.2rem; /* 타이틀 글자 크기 대폭 확대 */
        font-weight: 900;
        color: #0f172a;
        margin-left: 15px;
        border-left: 4px solid #e2e8f0;
        padding-left: 25px;
        letter-spacing: -1px;
    }}
    .system-status {{
        font-size: 0.9rem;
        background: white;
        color: #009944;
        border: 2px solid #009944;
        padding: 8px 20px;
        border-radius: 99px;
        font-weight: 800;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}

    /* 지표 카드 */
    div[data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08) !important;
        backdrop-filter: blur(8px);
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 1.2rem !important;
        color: #475569 !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        color: #0f172a !important;
    }}

    /* 범례 박스 스타일 */
    .legend-box {{
        font-size: 1rem;
        color: #1e293b;
        background: rgba(255, 255, 255, 0.98);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #009944;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.08);
    }}

    /* 테이블(DataFrame) 스타일링 */
    .stDataFrame {{
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        overflow: hidden;
        background: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    /* 섹션 제목 스타일 */
    .section-title {{
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 15px;
        color: #0f172a;
        border-left: 8px solid #009944;
        padding-left: 18px;
    }}
    </style>
    """, unsafe_allow_html=True)

# LH 브랜드 헤더 섹션
st.markdown(f"""
    <div class="lh-header">
        <div class="lh-brand-box">
            {logo_html}
            <div class="project-name">철근 배근 시공 품질 자동 검측 엔진</div>
        </div>
        <div class="system-status">● SYSTEM MONITORING</div>
    </div>
    """, unsafe_allow_html=True)

# 데이터 로드
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 지표 행
    m1, m2, m3, m4, m5 = st.columns([1, 1, 1, 1, 1.4])
    with m1: st.metric("전체 검측", f"{len(df)}EA")
    with m2: st.metric("정상 (PASS)", f"{status_counts.get('PASS', 0)}")
    with m3: st.metric("이슈 (ISSUE)", f"{status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)}")
    with m4: st.metric("미탐지 (MISS)", f"{status_counts.get('MISSING', 0)}")
    with m5:
        st.markdown("""
            <div class="legend-box">
                <div style="font-weight: 900; color: #009944; margin-bottom: 8px; font-size: 1.2rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px;">QC 품질 기준</div>
                <div style="line-height: 1.8; color: #1e293b;">
                    ⚪ <b>PASS</b>: <20mm (정상 범위)<br>
                    🟢 <b>CAUTION</b>: 20-30mm (정밀 관찰)<br>
                    🟠 <b>ERROR</b>: >30mm (재시공 검토)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. 메인 인터페이스
    left_col, right_col = st.columns([6, 4])

    with left_col:
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # 3D 모델 뷰어
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: white; border-radius: 20px; border: 1px solid #e2e8f0; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.05);"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.2"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=670)

    with right_col:
        # 통계 차트
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
            showlegend=False, height=250, margin=dict(l=0, r=20, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color="#0f172a", xaxis_title="", yaxis_title="",
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), 
            font=dict(size=15, weight='bold')
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 상세 리스트
        st.markdown("<div class='section-title'>📋 개별 검측 상세 데이터</div>", unsafe_allow_html=True)
        
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer']].copy()
        df_view.columns = ['ID', '오차(mm)', '결과', '레이어']
        
        df_view['sort'] = pd.to_numeric(df_view['오차(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='sort', ascending=False).drop(columns=['sort'])

        st.dataframe(df_view, use_container_width=True, height=360)

else:
    st.error("분석 데이터가 존재하지 않습니다. (final_qc_report_detailed.csv)")
