import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

st.set_page_config(page_title="Rebar QC Dashboard", layout="wide")

st.title("🏗️ Rebar Construction Quality Dashboard")
st.info("Indiana State University - Department of Built Environment")

csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    
    # 1. 상단 지표 계산
    total = len(df)
    status_counts = df['Status'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rebars", f"{total}")
    col2.metric("PASS", f"{status_counts.get('PASS', 0)}")
    caution_error = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
    col3.metric("CAUTION/ERROR", f"{caution_error}")
    col4.metric("MISSING", f"{status_counts.get('MISSING', 0)}")

    # 2. 메인 레이아웃 (좌: 3D 모델 / 우: 통계 데이터)
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3D Inspection Model (Z-Up)")
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [수정] orientation="-90deg 0 0" 추가하여 Z축을 위로 고정
            # [수정] auto-rotate 삭제하여 움직임 고정
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 550px; background-color: #f0f2f6;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          orientation="-90deg 0 0"
                          exposure="1">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=570)
        else:
            st.warning("GLB 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📊 Quality Statistics")
        
        # [추가] 통계 요약 표 (Table)
        summary_df = pd.DataFrame({
            "Quality Status": ["PASS", "CAUTION", "ERROR", "MISSING"],
            "Count": [
                status_counts.get('PASS', 0),
                status_counts.get('CAUTION', 0),
                status_counts.get('ERROR', 0),
                status_counts.get('MISSING', 0)
            ],
            "Percentage": [
                f"{(status_counts.get('PASS', 0)/total)*100:.1f}%",
                f"{(status_counts.get('CAUTION', 0)/total)*100:.1f}%",
                f"{(status_counts.get('ERROR', 0)/total)*100:.1f}%",
                f"{(status_counts.get('MISSING', 0)/total)*100:.1f}%"
            ]
        })
        st.table(summary_df) # 깔끔한 표 형태로 출력

        # 파이 차트
        fig_pie = px.pie(df, names='Status', color='Status',
                         color_discrete_map={
                             'PASS': '#808080', 
                             'CAUTION': '#008000', 
                             'ERROR': '#FFA500', 
                             'MISSING': '#FF0000'
                         })
        fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 3. 하단 상세 리스트
    st.subheader("📋 Detailed Inspection List")
    st.dataframe(df, use_container_width=True)
else:
    st.error(f"파일을 찾을 수 없습니다: {csv_file}")
