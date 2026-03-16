import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 레이아웃 및 스타일 설정
st.set_page_config(page_title="Rebar QC Analysis Platform", layout="wide")

# [Professional Styling] 커스텀 CSS 적용
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; padding: 20px; border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e9ecef;
    }
    .css-1r6slb0 { background-color: white; padding: 2rem; border-radius: 1rem; }
    h1 { color: #1e293b; font-weight: 800; }
    h3 { color: #334155; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; }
    .legend-box {
        padding: 15px; background-color: #ffffff; border-radius: 8px;
        border-left: 5px solid #3b82f6; margin-bottom: 20px; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 헤더 섹션
st.title("철근검측 결과 대시보드")
st.markdown("---")

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 상단 핵심 지표 (Metric Cards)
    total = len(df)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Elements", f"{total}")
    with m2: st.metric("Pass (Normal)", f"{status_counts.get('PASS', 0)}", "Verified", delta_color="normal")
    with m3: 
        caution_error = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
        st.metric("Total Issues", f"{caution_error}", f"-{caution_error}", delta_color="inverse")
    with m4: st.metric("Missing", f"{status_counts.get('MISSING', 0)}", "Critical", delta_color="inverse")

    st.write("") # 간격 조절

    # 3. 메인 분석 섹션
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3D Inspection Digital Twin")
        
        # 색상 범례 가이드 (카드 스타일)
        st.markdown("""
        <div class="legend-box">
            <b>검측 상태 범례:</b><br>
            ⚪ <b>PASS</b>: 시공 오차 20mm 미만 | 🟢 <b>CAUTION</b>: 주의 (20-30mm) | 
            🟠 <b>ERROR</b>: 오시공 (30mm 초과) | 🔴 <b>MISSING</b>: 미시공/누락
        </div>
        """, unsafe_allow_html=True)

        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [교수님 요청 사항: 축 회전 로직 상세 주석]
            # orientation="-90deg -90deg -90deg"의 의미:
            # 1. 첫 번째 (-90deg, X축): BIM/CAD의 Z-Up 좌표계를 웹의 Y-Up 환경에 맞추기 위해 모델을 뒤로 90도 눕힙니다.
            # 2. 두 번째 (-90deg, Y축): 위아래를 관통하는 축을 기준으로 시계 방향으로 90도 회전시킵니다. (평면도상 회전)
            # 3. 세 번째 (-90deg, Z축): 앞뒤를 관통하는 축을 기준으로 시계 방향으로 90도 회전시킵니다. (정면도상 회전)
            
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: #ffffff; border-radius: 15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1.5"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.1"
                          environment-image="neutral">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=670)
        else:
            st.warning("3D 모델 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📊 Statistics & Detailed Data")
        
        # 가로 막대 그래프 (Plotly 전문 테마 적용)
        bar_data = pd.DataFrame({
            '상태': ['Pass', 'Caution', 'Error', 'Missing'],
            'Count': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), 
                     status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_data, x='Count', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map={'PASS': '#94a3b8', 'CAUTION': '#22c55e', 
                                            'ERROR': '#f59e0b', 'MISSING': '#ef4444'},
                         text_auto=True)
        
        fig_bar.update_layout(
            showlegend=False, height=280, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Number of Rebars", yaxis_title=""
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 상세 리스트 (높이 확장 및 스타일 최적화)
        st.write("🔍 **Individual Inspection Details**")
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer', 'Direction']].copy()
        df_view['sort'] = pd.to_numeric(df_view['Error_mm'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='sort', ascending=False).drop(columns=['sort'])
        
        # 가독성을 위한 데이터프레임 스타일링
        st.dataframe(df_view, use_container_width=True, height=420)

else:
    st.error("분석 결과 데이터(CSV)를 찾을 수 없습니다.")
