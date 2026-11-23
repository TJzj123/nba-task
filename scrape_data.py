"""
任务5 - 数据抓取脚本
功能：抓取 Basketball Reference 指定球员的高级数据（Advanced Stats）
技术：requests + BeautifulSoup4 + pandas
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_advanced_stats(player_url):
    """抓取单个球员的高级数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(player_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 核心技巧：Basketball Reference 把高级数据表藏在 HTML 的注释节点中
        # 遍历所有字符串节点，寻找带有 id="advanced" 的注释内容
        for comment in soup.find_all(string=lambda text: isinstance(text, str)):
            if 'id="advanced"' in str(comment):
                # 找到注释后，将其重新解析为 BeautifulSoup 对象
                comment_soup = BeautifulSoup(str(comment), 'html.parser')
                table = comment_soup.find('table', {'id': 'advanced'})
                
                if table:
                    # 使用 Pandas 直接读取表格
                    df = pd.read_html(str(table))[0]
                    # 清理掉表头重复行
                    df = df[df['Player'] != 'Player']
                    return df
    except Exception as e:
        print(f"抓取失败 {player_url}: {e}")
        return None
    return None

def main():
    # 这里填入你需要抓取的球员 URL 列表（以 2022-2023 赛季为例，各位置挑代表）
    player_urls = [
        'https://www.basketball-reference.com/players/j/jokicni01.html', # 约基奇 C
        'https://www.basketball-reference.com/players/e/embiijo01.html', # 恩比德 C
        'https://www.basketball-reference.com/players/g/giannisa01.html',# 字母哥 PF
        'https://www.basketball-reference.com/players/d/doncilu01.html', # 东契奇 PG
        'https://www.basketball-reference.com/players/t/tatumja01.html', # 塔图姆 SF
        'https://www.basketball-reference.com/players/c/curryst01.html', # 库里 PG
        'https://www.basketball-reference.com/players/b/bookede01.html', # 布克 SG
        'https://www.basketball-reference.com/players/m/mitchdo01.html'  # 米切尔 SG
    ]
    
    all_data = []
    
    print("开始抓取数据...")
    for url in player_urls:
        print(f"正在抓取: {url.split('/')[-1]}")
        df = scrape_advanced_stats(url)
        if df is not None:
            all_data.append(df)
        else:
            print("解析失败，可能网页结构已变或遭遇反爬。")
        
        # 抓取间隔，防止被封 IP
        time.sleep(3)
        
    if all_data:
        # 合并所有球员数据
        final_df = pd.concat(all_data, ignore_index=True)
        
        # 数据清洗：只保留我们需要的列
        columns_needed = ['Player', 'Pos', 'PER', 'WS', 'TS%', 'G', 'MP', 'BPM', 'Tm']
        # 如果某些列不存在，用 0 填充（容错）
        for col in columns_needed:
            if col not in final_df.columns:
                final_df[col] = 0
                
        final_df = final_df[columns_needed]
        
        # 保存为 CSV 文件
        final_df.to_csv('players_advanced.csv', index=False)
        print("\n抓取完成！数据已保存为 players_advanced.csv")
    else:
        print("未抓取到任何数据。")

if __name__ == '__main__':
    main()