# -*- coding: utf-8 -*-
"""
Score calculation logic
@author: 33952
"""

import pandas as pd
from database import get_all_users

def calculate_scores(scores_data):
    df = pd.DataFrame(scores_data)
    if df.empty:
        users = pd.DataFrame(get_all_users())
        return pd.DataFrame({
            'username': users['username'], 'realname': users['realname'],
            'group': users['group'], 'final_score': [0] * len(users)
        })

    teacher_scores = df[df['rater'].str.contains('teacher', case=False)].groupby('target')['score'].mean() * (10/15)
    student_scores = df[df['rater'].str.contains('student', case=False)].groupby('target')['score'].mean()

    personal_scores = {}
    for target in set(teacher_scores.index).union(student_scores.index):
        t_score = teacher_scores.get(target, 0)
        s_score = student_scores.get(target, 0)
        personal_scores[target] = (t_score + s_score) / 2 if t_score and s_score else t_score or s_score

    users = pd.DataFrame(get_all_users())
    group_avg = {}
    for group in users['group'].unique():
        group_users = users[users['group'] == group]['username']
        group_scores = [personal_scores.get(u, 0) for u in group_users]
        group_avg[group] = sum(group_scores) / len(group_scores) if group_scores else 0

    final_scores = {}
    for user in users.itertuples():
        personal = personal_scores.get(user.username, 0)
        group_score = group_avg.get(user.group, 0)
        final_scores[user.username] = (personal * 0.5 + group_score * 0.5)

    return pd.DataFrame({
        'username': users['username'], 'realname': users['realname'],
        'group': users['group'], 'final_score': [final_scores.get(u, 0) for u in users['username']]
    })