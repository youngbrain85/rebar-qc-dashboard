import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="철근 시공 품질 대시보드", layout="wide")

st.title("🏗️ 철근 시공 품질 검측 대시보드")
st.info("Indiana State University - Built Environment | 연구 책임자: 박지수 교수")

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    # 데이터 로드
    df = pd.read_csv(csv_file)
    
    # 2. 상단 핵심 지표 (한글화)
    total = len(df)
    status_counts = df['Status'].value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 철근 수", f"{total}개")
    col2.metric("합격 (PASS)", f"{status_counts.get('PASS', 0)}개")
    issue_count = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
    col3.metric("주의/오류", f"{issue_count}개", delta_color="inverse")
    col4.metric("누락 (MISSING)", f"{status_counts.get('MISSING', 0)}개")

    # 3. 메인 레이아웃 (좌: 3D 모델 / 우: 차트 및 리스트)
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3D 검측 시각화 모델")
        
        # 색상 범례 가이드 추가
        st.markdown("""
        **[색상 범례 가이드]**
        - ⚪ **회색 (PASS)**: 시공 오차 20mm 미만 (정상)
        - 🟢 **녹색 (CAUTION)**: 시공 오차 20mm ~ 30mm (주의)
        - 🟠 **주황 (ERROR)**: 시공 오차 30mm 초과 (오류)
        - 🔴 **빨강 (MISSING)**: 철근 누락 (미발견)
        """)

        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # [축 방향 초기화] orientation 속성을 삭제하여 초기 상태로 복구
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64_glb}" 
                          style="width: 100%; height: 600px; background-color: #f0f2f6; border-radius: 15px;"
                          camera-controls 
                          touch-action="pan-y" 
                          shadow-intensity="1"
                          exposure="1.2">
            </model-viewer>
            """
            st.components.v1.html(model_viewer_html, height=620)
        else:
            st.warning("GLB 모델 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📊 품질 상태별 분포 (가로 막대)")
        
        # 가로 막대 그래프 데이터 준비
        chart_data = pd.DataFrame({
            '상태': ['합격', '주의', '오류', '누락'],
            '개수': [
                status_counts.get('PASS', 0),
                status_counts.get('CAUTION', 0),
                status_counts.get('ERROR', 0),
                status_counts.get('MISSING', 0)
            ],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(chart_data, x='개수', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map={
                             'PASS': '#808080', 
                             'CAUTION': '#008000', 
                             'ERROR': '#FFA500', 
                             'MISSING': '#FF0000'
                         },
                         text='개수')
        
        fig_bar.update_layout(showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 철근별 상세 오차 목록")
        
        # 데이터 테이블 정렬 및 한글화 반영
        df_display = df.copy()
        df_display.columns = ['철근 ID', '레이어', '방향', '오차(mm)', '상태']
        
        # 오차가 큰 순서대로 정렬 (숫자 변환 필요)
        df_display['sort_val'] = pd.to_numeric(df_display['오차(mm)'], errors='coerce').fillna(-1)
        df_display = df_display.sort_values(by='sort_val', ascending=False).drop(columns=['sort_val'])

        st.dataframe(df_display, use_container_width=True, height=350)

else:
    st.error("데이터 파일(CSV)을 찾을 수 없습니다.")
