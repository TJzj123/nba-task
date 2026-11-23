import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

st.set_page_config(page_title="NBA 球员表现仪表盘", layout="wide")
st.title("🏀 NBA 球员赛季表现分析仪表盘")

@st.cache_data
def load_data():
    df = pd.read_csv('players_advanced.csv')
    df['Pos_main'] = df['Pos'].astype(str).str.split('-').str[0]
    for col in ['PER', 'WS', 'TS%', 'G', 'MP']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df.dropna(subset=['PER', 'WS', 'TS%'])

df = load_data()
pos_avg = df.groupby('Pos_main')[['PER', 'WS', 'TS%']].mean().reset_index()

st.sidebar.header("交互控制面板")
selected_player = st.sidebar.selectbox("选择球员", df['Player'].unique())

player_row = df[df['Player'] == selected_player].iloc[0]
player_pos = player_row['Pos_main']
pos_row = pos_avg[pos_avg['Pos_main'] == player_pos].iloc[0]

st.subheader(f"👤 球员档案: {selected_player} ({player_pos})")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("PER (效率值)", f"{player_row['PER']:.1f}")
col2.metric("WS (胜利贡献)", f"{player_row['WS']:.1f}")
col3.metric("TS% (真实命中率)", f"{player_row['TS%']:.3f}")
col4.metric("G (出场数)", f"{player_row['G']:.0f}")
col5.metric("MP (总时间)", f"{player_row['MP']:.0f}")

st.divider()

row1_col1, row1_col2 = st.columns([1, 1])

with row1_col1:
    st.markdown("**🕸️ 球员能力雷达图 (对比同位置平均)**")
    categories = ['PER', 'WS', 'TS%']
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[player_row[c] for c in categories], theta=categories, fill='toself', name=selected_player))
    fig_radar.add_trace(go.Scatterpolar(r=[pos_row[c] for c in categories], theta=categories, fill='toself', name=f'{player_pos} 平均', line=dict(dash='dot')))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), margin=dict(t=30, b=30))
    st.plotly_chart(fig_radar, use_container_width=True)

with row1_col2:
    st.markdown("**📍 联盟散点图 (TS% vs PER)**")
    scatter = alt.Chart(df).mark_circle(size=100, opacity=0.8).encode(
        x=alt.X('PER:Q', title='PER (效率值)'),
        y=alt.Y('TS%:Q', title='TS% (真实命中率)'),
        color=alt.Color('Pos_main:N', title='位置'),
        tooltip=['Player', 'Pos_main', 'PER', 'TS%']
    ).interactive()
    st.altair_chart(scatter, use_container_width=True)
