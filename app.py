import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import json
import os

# 1. 페이지 설정 및 전문적인 테마 적용
st.set_page_config(page_title="Rebar QC Professional", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f1f5f9; }
    .stMetric { background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #e2e8f0; }
    div[data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    .sidebar-header { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    h1 { color: #0f172a; font-weight: 800; letter-spacing: -1px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Rebar Quality Control Integrated System")
st.write("3D Digital Twin 기반 시공 품질 검측 및 데이터 분석 플랫폼")

csv_file = "final_qc_report_detailed.csv"
glb_file = "construction_qc_model.glb"

if os.path.exists(csv_file):
    # 데이터 로드
    df = pd.read_csv(csv_file)
    
    # 2. 사이드바 필터링 시스템
    st.sidebar.markdown("<p class='sidebar-header'>Inspection Filters</p>", unsafe_allow_html=True)
    
    # 상태 필터
    all_status = df['Status'].unique().tolist()
    sel_status = st.sidebar.multiselect("검측 상태 (Status)", all_status, default=all_status)
    
    # 레이어 필터
    all_layers = df['Layer'].unique().tolist()
    sel_layers = st.sidebar.multiselect("배근 레이어 (Layer)", all_layers, default=all_layers)
    
    # 방향 필터
    all_dirs = df['Direction'].unique().tolist()
    sel_dirs = st.sidebar.multiselect("철근 방향 (Direction)", all_dirs, default=all_dirs)

    # 데이터 필터링 적용
    filtered_df = df[
        (df['Status'].isin(sel_status)) & 
        (df['Layer'].isin(sel_layers)) & 
        (df['Direction'].isin(sel_dirs))
    ]
    
    # 가시성 제어를 위한 ID 리스트 추출 (JS로 전달용)
    visible_ids = filtered_df['Rebar_ID'].tolist()

    # 3. 메인 지표 레이아웃
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Filtered Elements", len(filtered_df))
    with m2: st.metric("Pass Count", len(filtered_df[filtered_df['Status'] == 'PASS']))
    with m3: st.metric("Critical Issues", len(filtered_df[filtered_df['Status'].isin(['ERROR', 'MISSING'])]))
    with m4:
        avg_err = filtered_df[filtered_df['Error_mm'] != '-']['Error_mm'].astype(float).mean() if not filtered_df.empty else 0
        st.metric("Avg Error", f"{avg_err:.2f} mm")

    st.divider()

    # 4. 3D 뷰어 및 분석 차트
    left_col, right_col = st.columns([6, 4])

    with left_col:
        st.subheader("🌐 Interactive 3D Digital Twin")
        
        if os.path.exists(glb_file):
            with open(glb_file, "rb") as f:
                b64_glb = base64.b64encode(f.read()).decode()
            
            # JavaScript를 통한 실시간 모델 가시성 제어
            # filtered_ids에 포함되지 않은 메시들은 투명도 0.1로 처리하여 숨김 효과를 줍니다.
            model_viewer_html = f"""
            <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.3.0/model-viewer.min.js"></script>
            <div style="background-color: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
                <model-viewer id="rebar-viewer"
                              src="data:model/gltf-binary;base64,{b64_glb}" 
                              style="width: 100%; height: 600px;"
                              camera-controls 
                              touch-action="pan-y" 
                              shadow-intensity="1"
                              orientation="-90deg -90deg -90deg"
                              exposure="1.0">
                </model-viewer>
            </div>
            
            <script>
                const viewer = document.querySelector('#rebar-viewer');
                const visibleIds = {json.dumps(visible_ids)};
                
                viewer.addEventListener('load', () => {{
                    const model = viewer.model;
                    // 모든 메시를 순회하며 필터링 리스트에 없는 항목은 숨김(투명화) 처리
                    model.materials.forEach(mat => {{
                        const isVisible = visibleIds.some(id => mat.name.includes(id));
                        if (isVisible) {{
                            mat.setAlphaMode("OPAQUE");
                            mat.setBaseColorFactor([1, 1, 1, 1]);
                        }} else {{
                            mat.setAlphaMode("BLEND");
                            mat.setBaseColorFactor([1, 1, 1, 0.05]); // 거의 투명하게 설정
                        }}
                    }});
                }});
            </script>
            """
            st.components.v1.html(model_viewer_html, height=650)
            
            st.caption("※ 3D 뷰어는 사이드바의 필터링 조건에 따라 실시간으로 업데이트됩니다.")
        else:
            st.warning("GLB 파일을 찾을 수 없습니다.")

    with right_col:
        st.subheader("📊 Statistics & Raw Data")
        
        # 가로 막대 그래프 (필터링된 데이터 기준)
        status_summary = filtered_df['Status'].value_counts().reset_index()
        status_summary.columns = ['Status', 'Count']
        
        fig_bar = px.bar(status_summary, x='Count', y='Status', orientation='h',
                         color='Status',
                         color_discrete_map={{'PASS': '#94a3b8', 'CAUTION': '#22c55e', 
                                            'ERROR': '#f59e0b', 'MISSING': '#ef4444'}},
                         template="plotly_white")
        
        fig_bar.update_layout(showlegend=False, height=250, margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.write("🔍 **Individual Inspection Details**")
        # 표시용 테이블 (한글화)
        table_df = filtered_df[['Rebar_ID', 'Layer', 'Direction', 'Error_mm', 'Status']].copy()
        table_df.columns = ['철근 ID', '레이어', '방향', '오차(mm)', '상태']
        
        st.dataframe(table_df, use_container_width=True, height=350)

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
