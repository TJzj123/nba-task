import numpy as np
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

st.markdown("---")
row2_col1, row2_col2 = st.columns([1, 1])

# ==========================================
# 图表3：热力地图 (按球队显示相对排名)
# ==========================================
with row2_col1:
    st.markdown("**🔥 球队高阶数据热力图 (指标相对排名)**")
    # 计算各球队的平均值
    team_avg = df.groupby('Tm')[['PER', 'WS', 'BPM']].mean().reset_index()
    # 数据标准化（为了让热力图的颜色对比更明显）
    for col in ['PER', 'WS', 'BPM']:
        team_avg[col] = (team_avg[col] - team_avg[col].min()) / (team_avg[col].max() - team_avg[col].min())
    
    # 转换为适合画热力图的格式
    team_melted = team_avg.melt(id_vars='Tm', var_name='指标', value_name='相对排名 (0-1)')
    
    heatmap = alt.Chart(team_melted).mark_rect().encode(
        x=alt.X('Tm:N', title='球队'),
        y=alt.Y('指标:N', title='指标'),
        color=alt.Color('相对排名 (0-1):Q', scale=alt.Scale(scheme='redblue'), title='相对强弱'),
        tooltip=['Tm', '指标', '相对排名 (0-1)']
    ).properties(height=250)
    
    st.altair_chart(heatmap, use_container_width=True)

# ==========================================
# 图表4：时间序列 (多赛季成长曲线)
# ==========================================
with row2_col2:
    st.markdown("**📊 球员与同位置球员数据对比**")
    
    # 筛选出同位置的所有球员
    pos_df = df[df['Pos_main'] == player_pos]
    
    # 转换成 Altair 喜欢的格式
    pos_melted = pos_df.melt(id_vars=['Player', 'Tm'], value_vars=['PER', 'WS', 'BPM'], var_name='指标', value_name='数值')
    
    # 画柱状图
    bar_chart = alt.Chart(pos_melted).mark_bar().encode(
        x=alt.X('Player:N', title='球员', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('数值:Q', title='数据数值'),
        color=alt.Color('指标:N', title='指标'),
        xOffset='指标:N', # 把三个指标的柱子并排
        tooltip=['Player', 'Tm', '指标', '数值']
    ).properties(height=250)
    
    # 高亮显示当前选中的球员（用透明度降低其他人）
    highlight = alt.Chart(pos_melted).mark_bar().encode(
        x=alt.X('Player:N'),
        y=alt.Y('数值:Q'),
        color=alt.Color('指标:N'),
        xOffset='指标:N',
        opacity=alt.condition(
            alt.datum.Player == selected_player,
            alt.value(1),  # 选中的球员不透明
            alt.value(0.3) # 其他人变半透明
        )
    )
    
    st.altair_chart(highlight, use_container_width=True)
