import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. Cấu hình trang & Ép CSS để loại bỏ khoảng trắng thừa (vừa vặn 1 màn hình)
st.set_page_config(page_title="UNU Macau Demo", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        h3 { margin-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🌐 UNU Macau 2026: Shared Capacity Command Center")
st.caption("💡 **The Concept:** Autonomous AI often gets stuck in endless error loops (wasting money/tokens). This demo shows a system that safely pauses the AI upon error, allowing human correction at **zero additional compute cost**.")

# 2. Khởi tạo Trạng thái Phiên (Session State)
if 'step' not in st.session_state:
    st.session_state.step = 2  
    st.session_state.telemetry = [
        {"step": 1, "layer": "Agent Layer (Non-Det)", "status": "Loop Trap", "cum_tokens": 1600, "cum_time_sec": 1.55},
        {"step": 2, "layer": "Sensor Layer (Det)", "status": "Blocked", "cum_tokens": 1850, "cum_time_sec": 1.85}
    ]

df = pd.DataFrame(st.session_state.telemetry)

# 3. Bố cục 2 cột gọn gàng (Biểu đồ bên trái, Điều khiển bên phải)
col_chart, col_control = st.columns([1.5, 1], gap="large")

with col_chart:
    # Biểu đồ thu gọn chiều cao để không bị cuộn
    fig = go.Figure()

    # Trục Token
    fig.add_trace(go.Scatter(
        x=df['step'], y=df['cum_tokens'], name="Token Draw (Cost)", mode='lines+markers',
        line=dict(color='#2c3e50', width=3), marker=dict(size=8)
    ))

    # Trục Thời gian
    fig.add_trace(go.Scatter(
        x=df['step'], y=df['cum_time_sec'], name="Latency (Time)", mode='lines+markers', yaxis="y2",
        line=dict(color='#e74c3c', width=3, dash='dash'), marker=dict(size=8, symbol='square')
    ))

    # ĐÃ SỬA LỖI PLOTLY Ở ĐÂY: Sử dụng cấu trúc từ điển lồng nhau cho trục tọa độ
    fig.update_layout(
        xaxis=dict(title=dict(text="Workflow Step"), tickmode='linear', range=[0.8, 4.2]),
        yaxis=dict(title=dict(text="Tokens Consumed", font=dict(color="#2c3e50")), tickfont=dict(color="#2c3e50"), range=[1000, 2300]),
        yaxis2=dict(title=dict(text="Seconds", font=dict(color="#e74c3c")), tickfont=dict(color="#e74c3c"), anchor="x", overlaying="y", side="right", range=[0, 8]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5), # Legend nằm ngang ở trên
        height=380, # Ép chiều cao cố định
        margin=dict(l=0, r=0, t=10, b=0)
    )

    # Vẽ vạch ranh giới can thiệp của con người
    if st.session_state.step >= 2:
        fig.add_shape(type="line", x0=3, x1=3, y0=0, y1=1, xref="x", yref="paper", line=dict(color="gray", width=2, dash="dot"))
        fig.add_annotation(x=3.05, y=0.5, xref="x", yref="paper", text="Human Override", showarrow=False, textangle=-90, font=dict(color="gray"))

    st.plotly_chart(fig, use_container_width=True)

with col_control:
    # Hộp KPI nhỏ gọn
    st.markdown("**System Diagnostics**")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Tokens", int(df['cum_tokens'].max()), delta="0 (While Paused)" if st.session_state.step >= 3 else None, delta_color="inverse", help="API cost accumulated")
    kpi2.metric("Total Time", f"{df['cum_time_sec'].max():.2f} s", help="System processing + Human thinking time")
    kpi3.metric("Status", df['status'].iloc[-1], delta="Action Req." if st.session_state.step == 2 else "Secure", delta_color="normal" if st.session_state.step == 4 else "inverse")
    
    st.divider()

    # Khu vực Staging (Tương tác)
    st.markdown("**Interactive Staging Area**")
    
    if st.session_state.step == 2:
        st.error("🚨 **AI Error:** Agent attempted to use unauthorized Port `9999`.")
        st.caption("System is frozen. Notice the chart stopped. Please correct the port to the secure standard (`5432`) to resume.")
        
        with st.form("intervention_form", border=True):
            new_port = st.number_input("Override Gateway Port:", value=9999, step=1)
            submit_override = st.form_submit_button("Approve & Resume Workflow", type="primary", use_container_width=True)
            
            if submit_override:
                if new_port == 9999:
                    st.warning("Please enter the correct secure port (5432)!")
                else:
                    # Ghi nhận thời gian con người can thiệp (Step 3) và Kết quả (Step 4)
                    st.session_state.telemetry.extend([
                        {"step": 3, "layer": "Human UI", "status": "Overridden", "cum_tokens": 1850, "cum_time_sec": 6.85},
                        {"step": 4, "layer": "Sensor", "status": "Resolved", "cum_tokens": 2100, "cum_time_sec": 6.97}
                    ])
                    st.session_state.step = 4
                    st.rerun()
                    
    elif st.session_state.step == 4:
        st.success("✅ **Success:** System safely connected via Port `5432`.")
        st.caption("Look at the chart: The dark line (Tokens) stayed completely flat between Step 2 and 3. You saved compute resources by intervening!")
        if st.button("🔄 Reset Simulation", use_container_width=True):
            st.session_state.step = 2
            st.session_state.telemetry = st.session_state.telemetry[:2]
            st.rerun()

# 4. Giấu dữ liệu thô vào Expander để tiết kiệm chỗ
with st.expander("🔍 View Raw Event Logs (CHAP Protocol Auditing)"):
    st.dataframe(df[['step', 'layer', 'status', 'cum_tokens', 'cum_time_sec']], use_container_width=True, hide_index=True)
