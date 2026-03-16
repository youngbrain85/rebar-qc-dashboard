import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import trimesh
import os
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="철근 시공 품질 대시보드", layout="wide")

st.title("🏗️ 철근 시공 품질 검측 대시보드")
st.info("Indiana State University - Built Environment | 박지수 교수 연구실")

# 파일 경로
csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file) and os.path.exists(glb_file):
    # 데이터 로드
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 상단 핵심 지표
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 철근", f"{len(df)}개")
    col2.metric("합격 (PASS)", f"{status_counts.get('PASS', 0)}개")
    issue_count = status_counts.get('CAUTION', 0) + status_counts.get('ERROR', 0)
    col3.metric("주의/오류", f"{issue_count}개", delta_color="inverse")
    col4.metric("누락 (MISSING)", f"{status_counts.get('MISSING', 0)}개")

    # 3. 메인 레이아웃 (좌: 3D 모델 / 우: 분석 차트)
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3차원 품질 검측 모델")
        
        # 색상 범례 가이드
        st.markdown("""
        **[범례]** ⚪ 회색: 합격 | 🟢 녹색: 주의 | 🟠 주황: 오류 | 🔴 빨강: 누락
        """)

        # [뷰어 교체] Plotly를 이용한 Z-Up 3D 시각화
        try:
            # GLB 파일 로드
            scene = trimesh.load(glb_file)
            fig_3d = go.Figure()

            # Scene 내의 모든 Mesh를 Plotly 데이터로 변환
            if isinstance(scene, trimesh.Scene):
                for name, mesh in scene.geometry.items():
                    # 색상 추출 (PASS/CAUTION 등 상태별 색상 반영)
                    color = "gray"
                    if hasattr(mesh.visual, 'main_color'):
                        c = mesh.visual.main_color
                        color = f'rgb({c[0]},{c[1]},{c[2]})'
                    
                    fig_3d.add_trace(go.Mesh3d(
                        x=mesh.vertices[:, 0],
                        y=mesh.vertices[:, 1],
                        z=mesh.vertices[:, 2],
                        i=mesh.faces[:, 0],
                        j=mesh.faces[:, 1],
                        k=mesh.faces[:, 2],
                        color=color,
                        name=name,
                        opacity=1.0,
                        lighting=dict(ambient=0.5, diffuse=0.8, roughness=0.5)
                    ))
            
            # [축 방향 설정] Z: 상하(높이), X: 좌우, Y: 앞뒤
            fig_3d.update_layout(
                scene=dict(
                    xaxis=dict(title='X (좌우)'),
                    yaxis=dict(title='Y (앞뒤)'),
                    zaxis=dict(title='Z (상하)'),
                    aspectmode='data', # 실제 비율 유지
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)) # 초기 카메라 시점
                ),
                margin=dict(l=0, r=0, b=0, t=0),
                height=600
            )
            st.plotly_chart(fig_3d, use_container_width=True)
        except Exception as e:
            st.error(f"3D 모델 로딩 중 오류 발생: {e}")

    with right_col:
        st.subheader("📊 품질 상태별 분포")
        
        # [교체] 원 그래프 대신 가로 막대 그래프
        bar_df = pd.DataFrame({
            '상태': ['합격', '주의', '오류', '누락'],
            '개수': [
                status_counts.get('PASS', 0),
                status_counts.get('CAUTION', 0),
                status_counts.get('ERROR', 0),
                status_counts.get('MISSING', 0)
            ],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_df, x='개수', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map={
                             'PASS': '#808080', 'CAUTION': '#008000', 
                             'ERROR': '#FFA500', 'MISSING': '#FF0000'
                         },
                         text='개수')
        
        fig_bar.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10))
        fig_bar.update_xaxes(title="철근 수")
        fig_bar.update_yaxes(title="")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 철근별 상세 데이터")
        # 데이터프레임 한글화 및 오차 정렬
        view_df = df.copy()
        view_df.columns = ['철근 ID', '레이어', '방향', '오차(mm)', '상태']
        # 오차순으로 정렬 (주의/오류 우선 확인)
        view_df['sort'] = pd.to_numeric(view_df['오차(mm)'], errors='coerce').fillna(-1)
        view_df = view_df.sort_values(by='sort', ascending=False).drop(columns=['sort'])
        
        st.dataframe(view_df, use_container_width=True, height=300)

else:
    st.error("데이터 파일(CSV/GLB)을 찾을 수 없습니다. 깃허브 저장소를 확인해 주세요.")
