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
    for col in ['PER', 'WS', 'TS%', 'G', 'MP', 'BPM']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df.dropna(subset=['PER', 'WS', 'TS%', 'BPM'])

df = load_data()
pos_avg = df.groupby('Pos_main')[['PER', 'WS', 'TS%']].mean().reset_index()

st.sidebar.header("交互控制面板")
selected_player = st.sidebar.selectbox("选择球员", df['Player'].unique())

player_row = df[df['Player'] == selected_player].iloc[0]
player_pos = player_row['Pos_main']
pos_row = pos_avg[pos_avg['Pos_main'] == player_pos].iloc[0]

st.markdown("---")
col_img, col_info = st.columns([1, 4])

with col_img:
    player_photo_ids = {
        "Nikola Jokić": "203999",
        "Joel Embiid": "203954",
        "Giannis Antetokounmpo": "203507",
        "Luka Dončić": "1629029",
        "Jayson Tatum": "1628369",
        "Stephen Curry": "201939",
        "Devin Booker": "1626164",
        "Donovan Mitchell": "1628378"
    }
    photo_id = player_photo_ids.get(selected_player, "2544") 
    img_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{photo_id}.png"
    st.image(img_url, width=200, caption=selected_player)

with col_info:
    st.markdown(f"### 👤 {selected_player}")
    st.markdown(f"**球队:** {player_row['Tm']} | **位置:** {player_pos}")
    
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("PER (效率值)", f"{player_row['PER']:.1f}")
    m2.metric("WS (胜利贡献)", f"{player_row['WS']:.1f}")
    m3.metric("BPM (正负值)", f"{player_row['BPM']:.1f}")
    m4.metric("TS% (真实命中率)", f"{player_row['TS%']:.3f}")
    m5.metric("G (出场数)", f"{player_row['G']:.0f}")
    m6.metric("MP (总时间)", f"{player_row['MP']:.0f}")

st.markdown("---")

row1_col1, row1_col2 = st.columns([1, 1])

with row1_col1:
    st.markdown("**🕸️ 球员能力雷达图 (对比同位置平均)**")
    
    categories = ['PER', 'WS', 'TS%']
    
    # 提取球员的绝对数值和位置平均的绝对数值
    player_values = [player_row[c] for c in categories]
    avg_values = [pos_row[c] for c in categories]
    
    fig_radar = go.Figure()
    
    # 画球员的数据（蓝色实线，有填充）
    fig_radar.add_trace(go.Scatterpolar(
        r=player_values, 
        theta=categories, 
        fill='toself', 
        name=selected_player,
        line_color='#1f77b4'
    ))
    
    # 画位置平均的数据（橙色虚线，无填充，方便看底下的球员数据）
    fig_radar.add_trace(go.Scatterpolar(
        r=avg_values, 
        theta=categories, 
        fill='toself', 
        name=f'{player_pos} 位置平均',
        line=dict(dash='dot', color='#ff7f0e'),
        opacity=0.4
    ))
    
    # 让雷达图的圈圈根据最大值自动缩放，这样三条轴都能撑满
    max_val = max(player_values + avg_values)
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val * 1.1])
        ), 
        margin=dict(t=30, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with row1_col2:
    st.markdown("**📍 联盟散点图 (TS% vs PER)**")
    scatter = alt.Chart(df).mark_circle(size=100, opacity=0.8).encode(
        x=alt.X('PER:Q', title='PER (效率值)'),
        y=alt.Y('TS%:Q', title='TS% (真实命中率)'),
        color=alt.Color('Pos_main:N', title='位置', scale=alt.Scale(domain=['PG', 'SG', 'SF', 'PF', 'C'])),
        tooltip=['Player', 'Pos_main', 'PER', 'TS%']
    ).interactive()
    st.altair_chart(scatter, use_container_width=True)
