import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="Rebar QC Dashboard", layout="wide")

st.title("🏗️ Rebar Construction Quality Dashboard")
st.info("Indiana State University - Built Environment | PI: Prof. Jisoo Park")

# 파일 경로 (GitHub 저장소 내 파일명)
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    # 데이터 로드
    df = pd.read_csv(csv_file)
    
    # 2. 상단 핵심 지표 (Metrics)
    total = len(df)
    status_counts = df['Status'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rebars", f"{total}")
    col2.metric("PASS (합격)", f"{status_counts.get('PASS', 0)}")
    issue_count = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
    col3.metric("CAUTION/ERROR", f"{issue_count}", delta_color="inverse")
    col4.metric("MISSING (누락)", f"{status_counts.get('MISSING', 0)}")

    # 3. 메인 레이아웃 (좌: 3D 모델 / 우: 상세 오차 테이블)
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3D Inspection Model (X: Up-Down Alignment)")
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [축 방향 수정] orientation="90deg 0 90deg"
            # X축을 위아래(Vertical), Z축을 좌우(Horizontal), Y축을 앞뒤(Depth)로 매핑
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 650px; background-color: #f0f2f6; border-radius: 15px;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          orientation="90deg 0 90deg"
                          exposure="1.2">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=670)
        else:
            st.warning("GLB 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📋 Detailed Rebar Error Table")
        
        # 데이터 정렬: 오차가 큰 순서대로 (ERROR -> CAUTION -> PASS)
        # Error_mm의 '-' 값을 처리하기 위해 숫자 변환
        df_display = df.copy()
        df_display['sort_val'] = pd.to_numeric(df_display['Error_mm'], errors='coerce').fillna(-1)
        df_display = df_display.sort_values(by='sort_val', ascending=False).drop(columns=['sort_val'])

        # 교수님 요청에 따른 전체 오차 테이블 배치
        st.dataframe(
            df_display[['Rebar_ID', 'Error_mm', 'Status', 'Layer', 'Direction']], 
            use_container_width=True, 
            height=450
        )

        # 상태 분포 시각화 (보조)
        fig_pie = px.pie(df, names='Status', color='Status',
                         color_discrete_map={
                             'PASS': '#808080', 
                             'CAUTION': '#008000', 
                             'ERROR': '#FFA500', 
                             'MISSING': '#FF0000'
                         })
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=200, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.error(f"데이터 파일을 찾을 수 없습니다: {csv_file}")
