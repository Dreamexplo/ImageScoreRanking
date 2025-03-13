# -*- coding: utf-8 -*-
"""
Initial configuration for users and groups
@author: 33952
"""

from database import create_user, create_group, get_groups, get_all_users
import streamlit as st

def initialize_groups():
    existing_groups = get_groups()
    groups = ['第一组', '第二组', '第三组']
    for group in groups:
        if group not in existing_groups:
            if create_group(group):
                st.write(f"成功创建组别: {group}")
            else:
                st.error(f"创建组别 {group} 失败")

def initialize_users():
    existing_users = [u['username'] for u in get_all_users()]
    for i in range(1, 16):
        username = f"student{i}"
        if username not in existing_users:
            group = ['第一组', '第二组', '第三组'][(i-1)//5]
            if create_user(username, f"学生{i}", "Student", group, "1234"):
                st.write(f"成功创建用户: {username}")
            else:
                st.error(f"创建用户 {username} 失败")
    
    if "admin1" not in existing_users:
        if create_user("admin1", "管理员1", "Admin", "Undefined", "1234"):
            st.write("成功创建管理员: admin1")
        else:
            st.error("创建管理员 admin1 失败")
    if "teacher1" not in existing_users:
        if create_user("teacher1", "老师1", "Teacher", "Undefined", "1234"):
            st.write("成功创建教师: teacher1")
        else:
            st.error("创建教师 teacher1 失败")

def initialize_all():
    st.write("开始初始化数据...")
    initialize_groups()
    initialize_users()
    st.write("初始化完成！")
