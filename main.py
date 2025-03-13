# -*- coding: utf-8 -*-
"""
Main Streamlit application with Supabase integration
@author: 33952
"""

import streamlit as st
import database as db
from config_initialization import initialize_groups, initialize_users
from scoring import calculate_scores
from visualization import plot_group_comparison, plot_individual_comparison, plot_scoring_trends, plot_scoring_details
import pandas as pd
import io

# 初始化数据（仅在首次运行时）
if 'db_initialized' not in st.session_state:
    # 假设 Supabase 表已手动创建，此处仅初始化示例数据
    initialize_groups()
    initialize_users()
    st.session_state.db_initialized = True

def login_page():
    st.title("登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    if st.button("登录"):
        user = db.get_user(username)
        if user and user['password'] == password:
            st.session_state.user = user
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("用户名或密码错误")

def register_page():
    st.title("注册")
    with st.form("register_form"):
        username = st.text_input("用户名*")
        realname = st.text_input("真实姓名*")
        roles = st.multiselect("身份", ["Student", "Teacher", "Admin"])
        group = st.selectbox("组别", ["Undefined"] + db.get_groups()) if "Student" not in roles else st.selectbox("组别", db.get_groups())
        password = st.text_input("初始密码", value="1234")
        if st.form_submit_button("提交注册"):
            if db.create_user(username, realname, ",".join(roles), group, password):
                st.success("注册成功！请登录")
            else:
                st.error("用户名已存在")

def change_password():
    st.title("修改密码")
    user = st.session_state.user
    with st.form("change_password_form", clear_on_submit=True):
        old_pwd = st.text_input("原密码", type="password")
        new_pwd = st.text_input("新密码", type="password")
        confirm_pwd = st.text_input("确认新密码", type="password")
        if st.form_submit_button("确认修改"):
            if old_pwd == user['password']:
                if new_pwd == confirm_pwd:
                    db.update_password(user['username'], new_pwd)
                    st.session_state.user['password'] = new_pwd
                    st.success("密码修改成功！请重新登录")
                    st.session_state.logged_in = False
                    st.rerun()
                else:
                    st.error("新密码与确认密码不一致")
            else:
                st.error("原密码错误")

def admin_panel():
    st.title("管理员后台")
    admin_pwd = st.text_input("管理员密码", type="password")
    if admin_pwd != "OK":
        st.error("管理员密码错误")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["组别管理", "用户管理", "数据管理", "数据可视化"])

    with tab1:
        st.subheader("组别管理")
        new_group = st.text_input("新建组别名称")
        if st.button("添加组别"):
            if db.create_group(new_group):
                st.success(f"组别 {new_group} 已添加")
            else:
                st.error("组别已存在")

        groups = db.get_groups()
        selected_group = st.selectbox("选择要删除的组别", groups)
        if st.button("删除组别"):
            db.delete_group(selected_group)
            st.success(f"组别 {selected_group} 已删除")

    with tab2:
        st.subheader("用户管理")
        users = db.get_all_users()
        selected_user = st.selectbox("选择用户", [u['username'] for u in users])
        new_pwd = st.text_input("新密码", type="password")
        if st.button("重置密码"):
            if new_pwd:
                db.update_password(selected_user, new_pwd)
                st.success(f"{selected_user} 的密码已重置")
            else:
                st.error("请输入新密码")

    with tab3:
        st.subheader("数据管理")
        if st.button("下载所有数据为Excel"):
            users_df = pd.DataFrame(db.get_all_users())
            scores_df = pd.DataFrame(db.get_all_scores())
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                users_df.to_excel(writer, sheet_name='Users', index=False)
                scores_df.to_excel(writer, sheet_name='Scores', index=False)
            st.download_button("下载Excel文件", buffer.getvalue(), "data_export.xlsx",
                              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        uploaded_file = st.file_uploader("上传数据文件（Excel）", type=["xlsx"])
        if uploaded_file:
            with pd.ExcelFile(uploaded_file) as xls:
                if 'Users' in xls.sheet_names:
                    users_df = pd.read_excel(xls, sheet_name='Users')
                    for _, row in users_df.iterrows():
                        db.create_user(row['username'], row['realname'], row['roles'], row['group'], row['password'])
                if 'Scores' in xls.sheet_names:
                    scores_df = pd.read_excel(xls, sheet_name='Scores')
                    for _, row in scores_df.iterrows():
                        db.save_scores(row['rater'], {row['target']: row['score']})
            st.success("数据已上传并保存")

    with tab4:
        visualize_page()

def scoring_page(user):
    st.title("评分页面")
    if "Student" in user['roles']:
        targets = db.get_students_exclude_group(user['group'])
        max_score = 10
    else:
        targets = [u for u in db.get_all_users() if "Student" in u['roles']]
        max_score = 15

    scores = {}
    for target in targets:
        scores[target['username']] = st.slider(f"{target['realname']} 评分", 1, max_score, key=target['username'])

    if st.button("提交评分"):
        if all(value > 0 for value in scores.values()):
            confirm = st.radio("确认提交？", ["确认", "再想想"])
            if confirm == "确认":
                db.save_scores(user['username'], scores)
                st.success("评分已成功提交！")
        else:
            st.warning("请完成所有评分")

def visualize_page():
    st.header("数据可视化")
    scores = db.get_all_scores()
    df = calculate_scores(scores)

    tab1, tab2, tab3, tab4 = st.tabs(["组间比较", "个人比较", "趋势分析", "评分详情"])
    with tab1:
        st.plotly_chart(plot_group_comparison(df))
    with tab2:
        st.plotly_chart(plot_individual_comparison(df))
    with tab3:
        st.plotly_chart(plot_scoring_trends())
    with tab4:
        selected_user = st.selectbox("选择查看用户", df['username'].unique())
        st.plotly_chart(plot_scoring_details(selected_user))

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        if st.button("前往注册"):
            register_page()
        return

    user = st.session_state.user
    st.sidebar.title(f"欢迎，{user['realname']}")

    if "Admin" in user['roles']:
        if st.sidebar.button("管理员面板"):
            st.session_state.page = "admin"

    if hasattr(st.session_state, 'page') and st.session_state.page == "admin":
        admin_panel()
        if st.button("返回"):
            del st.session_state.page
        return

    if st.sidebar.button("修改密码"):
        change_password()

    if st.sidebar.button("退出登录"):
        st.session_state.logged_in = False
        st.rerun()

    if "Student" in user['roles'] or "Teacher" in user['roles']:
        scoring_page(user)

    if st.sidebar.button("查看结果"):
        visualize_page()

if __name__ == "__main__":
    main()

