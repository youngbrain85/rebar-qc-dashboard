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

    # 3. 메인 레이아웃
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 3차원 품질 검측 모델")
        st.markdown("""
        **[범례]** ⚪ 회색: 합격 | 🟢 녹색: 주의 | 🟠 주황: 오류 | 🔴 빨강: 누락
        """)

        try:
            # GLB 파일 로드
            scene = trimesh.load(glb_file)
            fig_3d = go.Figure()

            # Scene 내의 모든 Geometry 탐색
            if isinstance(scene, trimesh.Scene):
                for name, geom in scene.geometry.items():
                    # [핵심 수정] 색상 추출 로직 강화
                    color = 'rgb(128, 128, 128)' # 기본값 회색
                    
                    # 1. 재질(Material) 정보가 있는 경우 확산색(diffuse) 추출
                    if hasattr(geom.visual, 'material'):
                        mat = geom.visual.material
                        if hasattr(mat, 'diffuse'):
                            c = mat.diffuse
                            color = f'rgb({c[0]},{c[1]},{c[2]})'
                    
                    # 2. 재질 정보가 없고 정점/면 색상이 있는 경우
                    elif hasattr(geom.visual, 'vertex_colors') and len(geom.visual.vertex_colors) > 0:
                        c = geom.visual.vertex_colors[0]
                        color = f'rgb({c[0]},{c[1]},{c[2]})'
                    
                    # Plotly Mesh3d 추가
                    fig_3d.add_trace(go.Mesh3d(
                        x=geom.vertices[:, 0],
                        y=geom.vertices[:, 1],
                        z=geom.vertices[:, 2],
                        i=geom.faces[:, 0],
                        j=geom.faces[:, 1],
                        k=geom.faces[:, 2],
                        color=color,
                        name=name,
                        opacity=1.0,
                        flatshading=True,
                        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.1)
                    ))
            
            # Z-Up 좌표계 및 카메라 설정
            fig_3d.update_layout(
                scene=dict(
                    xaxis=dict(title='X (좌우)'),
                    yaxis=dict(title='Y (앞뒤)'),
                    zaxis=dict(title='Z (상하)'),
                    aspectmode='data',
                    camera=dict(
                        up=dict(x=0, y=0, z=1), # Z축을 위로 설정
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    )
                ),
                margin=dict(l=0, r=0, b=0, t=0),
                height=600
            )
            st.plotly_chart(fig_3d, use_container_width=True)
            
        except Exception as e:
            st.error(f"3D 모델을 시각화하는 중 오류가 발생했습니다: {e}")

    with right_col:
        st.subheader("📊 품질 상태 분포")
        
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
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 상세 검측 리스트")
        view_df = df.copy()
        view_df.columns = ['철근 ID', '레이어', '방향', '오차(mm)', '상태']
        view_df['sort'] = pd.to_numeric(view_df['오차(mm)'], errors='coerce').fillna(-1)
        view_df = view_df.sort_values(by='sort', ascending=False).drop(columns=['sort'])
        
        st.dataframe(view_df, use_container_width=True, height=300)

else:
    st.error("데이터 파일을 찾을 수 없습니다. GitHub 저장소의 파일명을 확인해주세요.")
