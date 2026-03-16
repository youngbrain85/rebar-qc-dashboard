import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="Rebar QC Analysis Dashboard", layout="wide")

# [Professional Look] 불필요한 정보 삭제 및 깔끔한 헤더 적용
st.title("🏗️ Rebar Construction Quality Integrated Dashboard")
st.markdown("---")

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    # 데이터 로드
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 상단 핵심 요약 (KPI Metrics)
    total = len(df)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Rebars", f"{total}EA")
    with m2: st.metric("Pass (Normal)", f"{status_counts.get('PASS', 0)}")
    with m3: 
        issue_count = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
        st.metric("Caution/Error", f"{issue_count}", delta_color="inverse")
    with m4: st.metric("Missing", f"{status_counts.get('MISSING', 0)}")

    st.write("") # 간격 조절

    # 3. 메인 레이아웃 (좌: 3D 모델 / 우: 차트 및 데이터)
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3D Digital Twin Inspection Model")
        
        # 색상 범례 가이드
        st.markdown("""
        **[Inspection Legend]**
        - ⚪ **PASS**: 정상 시공 | 🟢 **CAUTION**: 주의 (20-30mm)
        - 🟠 **ERROR**: 오류 (30mm 초과) | 🔴 **MISSING**: 철근 누락
        """)

        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [교수님 요청 회전 로직 주석]
            # orientation="-90deg -90deg -90deg" 설정 이유:
            # 1. X축 -90deg: BIM 좌표계(Z-up)를 웹 표준(Y-up)에 맞춰 모델을 수직으로 세움.
            # 2. Y축 -90deg: 위아래 수직축을 기준으로 모델을 시계 방향으로 90도 회전.
            # 3. Z축 -90deg: 앞뒤 수평축을 기준으로 모델을 시계 방향으로 90도 회전하여 최종 정렬.
            
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 600px; background-color: #f8f9fa; border-radius: 15px;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          orientation="-90deg -90deg -90deg"
                          exposure="1.0">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=620)
        else:
            st.warning("3D Model (GLB) 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📊 Quality Statistics")
        
        # 가로 막대 그래프 (Plotly 전문 테마)
        bar_data = pd.DataFrame({
            'Status': ['Pass', 'Caution', 'Error', 'Missing'],
            'Count': [
                status_counts.get('PASS', 0),
                status_counts.get('CAUTION', 0),
                status_counts.get('ERROR', 0),
                status_counts.get('MISSING', 0)
            ],
            'Color': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_data, x='Count', y='Status', orientation='h',
                         color='Color',
                         color_discrete_map={
                             'PASS': '#94a3b8', 'CAUTION': '#22c55e', 
                             'ERROR': '#f59e0b', 'MISSING': '#ef4444'
                         },
                         text='Count')
        
        fig_bar.update_layout(
            showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Rebar Count", yaxis_title=""
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 Inspection Data List")
        
        # 데이터프레임 정리 (필요한 컬럼만 깔끔하게 표시)
        df_view = df[['Rebar_ID', 'Error_mm', 'Status', 'Layer', 'Direction']].copy()
        df_view.columns = ['ID', 'Error(mm)', 'Status', 'Layer', 'Direction']
        
        # 오차순으로 정렬
        df_view['sort'] = pd.to_numeric(df_view['Error(mm)'], errors='coerce').fillna(-1)
        df_view = df_view.sort_values(by='sort', ascending=False).drop(columns=['sort'])

        st.dataframe(df_view, use_container_width=True, height=350)

else:
    st.error("분석 데이터(CSV)를 찾을 수 없습니다. 파일명을 확인해 주세요.")
