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

# 품질 상태별 색상 정의 (Hex)
color_map_hex = {
    'PASS': '#808080',     # 회색
    'CAUTION': '#008000',  # 녹색
    'ERROR': '#FFA500',    # 주황색
    'MISSING': '#FF0000'   # 빨간색
}

if os.path.exists(csv_file) and os.path.exists(glb_file):
    df = pd.read_csv(csv_file)
    status_counts = df['Status'].value_counts()
    
    # 2. 상단 지표
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
        st.markdown("**[범례]** ⚪ 회색: 합격 | 🟢 녹색: 주의 | 🟠 주황: 오류 | 🔴 빨강: 누락")

        try:
            # GLB 파일 로드
            scene = trimesh.load(glb_file)
            fig_3d = go.Figure()

            if isinstance(scene, trimesh.Scene):
                for name, geom in scene.geometry.items():
                    target_color = '#808080' # 기본값 회색
                    
                    # [오류 해결 포인트] 재질 이름을 안전하게 가져오기
                    mat_name = ""
                    if hasattr(geom.visual, 'material') and geom.visual.material is not None:
                        # name이 None인 경우를 대비해 str()로 감싸고 처리
                        raw_name = getattr(geom.visual.material, 'name', "")
                        mat_name = str(raw_name if raw_name is not None else "").upper()
                    
                    # 1. 재질 이름으로 색상 매핑
                    found_status = False
                    for status in color_map_hex.keys():
                        if status in mat_name:
                            target_color = color_map_hex[status]
                            found_status = True
                            break
                    
                    # 2. 메시 자체의 이름(name)으로도 한 번 더 확인
                    if not found_status:
                        obj_name = str(name).upper()
                        for status in color_map_hex.keys():
                            if status in obj_name:
                                target_color = color_map_hex[status]
                                found_status = True
                                break

                    # Plotly Mesh3d 추가
                    fig_3d.add_trace(go.Mesh3d(
                        x=geom.vertices[:, 0],
                        y=geom.vertices[:, 1],
                        z=geom.vertices[:, 2],
                        i=geom.faces[:, 0],
                        j=geom.faces[:, 1],
                        k=geom.faces[:, 2],
                        color=target_color,
                        name=name,
                        opacity=1.0,
                        flatshading=True,
                        lighting=dict(ambient=0.6, diffuse=0.8, specular=0.2)
                    ))
            
            # Z-Up 좌표계 유지
            fig_3d.update_layout(
                scene=dict(
                    xaxis=dict(title='X (좌우)'),
                    yaxis=dict(title='Y (앞뒤)'),
                    zaxis=dict(title='Z (상하)'),
                    aspectmode='data',
                    camera=dict(up=dict(x=0, y=0, z=1), eye=dict(x=1.8, y=1.8, z=1.8))
                ),
                margin=dict(l=0, r=0, b=0, t=0), height=600
            )
            st.plotly_chart(fig_3d, use_container_width=True)
            
        except Exception as e:
            st.error(f"3D 모델 시각화 중 오류 발생: {e}")

    with right_col:
        st.subheader("📊 품질 상태 분포")
        
        bar_df = pd.DataFrame({
            '상태': ['합격', '주의', '오류', '누락'],
            '개수': [status_counts.get('PASS', 0), status_counts.get('CAUTION', 0), 
                   status_counts.get('ERROR', 0), status_counts.get('MISSING', 0)],
            'Status': ['PASS', 'CAUTION', 'ERROR', 'MISSING']
        })
        
        fig_bar = px.bar(bar_df, x='개수', y='상태', orientation='h',
                         color='Status',
                         color_discrete_map=color_map_hex,
                         text='개수')
        
        fig_bar.update_layout(showlegend=False, height=250, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 상세 검측 리스트")
        view_df = df.copy()
        view_df.columns = ['철근 ID', '레이어', '방향', '오차(mm)', '상태']
        # 오차순 정렬 (숫자로 변환하여 정렬)
        view_df['sort_val'] = pd.to_numeric(view_df['오차(mm)'], errors='coerce').fillna(-1)
        view_df = view_df.sort_values(by='sort_val', ascending=False).drop(columns=['sort_val'])
        
        st.dataframe(view_df, use_container_width=True, height=350)

else:
    st.error("데이터 파일을 찾을 수 없습니다. GitHub 저장소의 파일명을 확인해주세요.")
