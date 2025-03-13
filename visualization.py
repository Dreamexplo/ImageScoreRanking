# -*- coding: utf-8 -*-
"""
Data visualization with Plotly
@author: 33952
"""

import plotly.express as px
import pandas as pd
from database import get_all_scores

import plotly.io as pio
pio.templates.default = "plotly_white"

def plot_group_comparison(df):
    fig = px.bar(df, x='group', y='final_score', color='group',
                 title="组间比较", labels={'group': '组别', 'final_score': '最终分数'})
    fig.update_layout(font=dict(family="SimHei", size=12))
    return fig

def plot_individual_comparison(df):
    fig = px.bar(df.sort_values('final_score'), x='realname', y='final_score', color='group',
                 title="个人比较", labels={'realname': '姓名', 'final_score': '最终分数'})
    fig.update_layout(font=dict(family="SimHei", size=12))
    return fig

def plot_scoring_trends():
    scores = pd.DataFrame(get_all_scores())
    if not scores.empty:
        scores['date'] = pd.to_datetime(scores['timestamp']).dt.date
        trend = scores.groupby(['date', 'target'])['score'].mean().reset_index()
        fig = px.line(trend, x='date', y='score', color='target',
                      title="评分趋势", labels={'date': '日期', 'score': '分数', 'target': '被评分者'})
        fig.update_layout(font=dict(family="SimHei", size=12))
        return fig
    return px.scatter(title="暂无数据", labels={'x': '日期', 'y': '分数'})

def plot_scoring_details(target_user):
    scores = pd.DataFrame(get_all_scores())
    if not scores.empty:
        filtered = scores[scores['target'] == target_user].sort_values('score', ascending=False)
        fig = px.bar(filtered, x='rater', y='score',
                     title=f"{target_user} 的评分详情", labels={'rater': '评分者', 'score': '分数'})
        fig.update_layout(font=dict(family="SimHei", size=12))
        return fig
    return px.scatter(title="暂无数据", labels={'x': '评分者', 'y': '分数'})

