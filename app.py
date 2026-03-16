import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

st.set_page_config(page_title="Rebar QC Dashboard", layout="wide")

st.title("🏗️ Rebar Construction Quality Dashboard")
st.info("Indiana State University - Department of Built Environment")

# ⭐ 교수님이 가지고 계신 파일명으로 수정했습니다.
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

# 데이터 로드 확인
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
    
    # 상단 지표 계산
    total = len(df)
    status_counts = df['Status'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rebars", f"{total}")
    col2.metric("PASS", f"{status_counts.get('PASS', 0)}")
    # CAUTION과 ERROR를 합쳐서 주의가 필요한 항목으로 표시
    caution_error = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
    col3.metric("CAUTION/ERROR", f"{caution_error}")
    col4.metric("MISSING", f"{status_counts.get('MISSING', 0)}")

    # 레이아웃 구성
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3D Inspection Model")
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # 구글 model-viewer를 이용한 3D 시각화
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 500px; background-color: #f0f2f6;"
                          camera-controls touch-action="pan-y" auto-rotate shadow-intensity="1">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=520)
        else:
            st.warning("GLB 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📊 Quality Statistics")
        fig_pie = px.pie(df, names='Status', color='Status',
                         color_discrete_map={{
                             'PASS': '#808080', 
                             'CAUTION': '#008000', 
                             'ERROR': '#FFA500', 
                             'MISSING': '#FF0000'
                         }})
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Detailed Inspection List")
    st.dataframe(df, use_container_width=True)
else:
    st.error(f"파일을 찾을 수 없습니다: {{csv_file}}")
    st.info("깃허브 저장소에 'final_qc_report_detailed.csv' 파일이 있는지 확인해주세요.")