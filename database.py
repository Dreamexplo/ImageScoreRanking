# -*- coding: utf-8 -*-
"""
Supabase database operations for Streamlit Cloud
@author: 33952
"""

from supabase import create_client
import streamlit as st
import pandas as pd
from cryptography.fernet import Fernet
import os

# 从 Streamlit secrets 获取 Supabase 配置
try:
    url = st.secrets["supabase"]["https://klktoorwaidyziqxyaoh.supabase.co"]
    key = st.secrets["supabase"]["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtsa3Rvb3J3YWlkeXppcXh5YW9oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE4MzQ2MjIsImV4cCI6MjA1NzQxMDYyMn0.-iABpnkMLbZiorz50nyZAmstk9dT2-UyFXTVty5YtBQ"]
    ENCRYPTION_KEY = st.secrets["supabase"]["iqlcwN7Dx8p1Pi8AR7z-xyBKEW5IGQneCunqfYQCe2Q="]
except KeyError as e:
    st.error(f"Secrets 配置错误: 缺少 {e} 键。请检查 Streamlit Secrets 设置。")
    url = key = ENCRYPTION_KEY = None

if not all([url, key, ENCRYPTION_KEY]):
    st.error("Supabase 配置不完整，无法初始化客户端。")
    raise ValueError("Missing required Supabase configuration")

cipher = Fernet(ENCRYPTION_KEY)
supabase = None

def get_supabase_client():
    global supabase
    if supabase is None:
        try:
            supabase = create_client(url, key)
        except Exception as e:
            st.error(f"Failed to initialize Supabase client: {e}")
            raise
    return supabase

def initialize():
    pass

def create_user(username, realname, roles, group, password):
    encrypted_pwd = cipher.encrypt(password.encode()).decode()
    data = {
        "username": username, "realname": realname, "roles": roles,
        "group_name": group, "password": encrypted_pwd, "modified": 0
    }
    try:
        client = get_supabase_client()
        response = client.table("users").insert(data).execute()
        return bool(response.data)
    except Exception as e:
        if hasattr(e, 'code') and e.code == '23505':  # 主键冲突
            st.warning(f"用户 {username} 已存在，跳过创建")
            return False
        st.error(f"Error creating user {username}: {e}")
        return False

def get_user(username):
    try:
        client = get_supabase_client()
        response = client.table("users").select("*").eq("username", username).execute()
        if response.data:
            user = response.data[0]
            user["password"] = cipher.decrypt(user["password"].encode()).decode()
            user["roles"] = user["roles"].split(",")
            return user
        return None
    except Exception as e:
        st.error(f"Error fetching user {username}: {e}")
        return None

def update_password(username, new_password):
    encrypted_pwd = cipher.encrypt(new_password.encode()).decode()
    try:
        client = get_supabase_client()
        response = client.table("users").update({"password": encrypted_pwd, "modified": 1}).eq("username", username).execute()
        return bool(response.data)
    except Exception as e:
        st.error(f"Error updating password for {username}: {e}")
        return False

def create_group(group_name):
    try:
        client = get_supabase_client()
        response = client.table("groups").insert({"group_name": group_name}).execute()
        return bool(response.data)
    except Exception as e:
        if hasattr(e, 'code') and e.code == '23505':
            st.warning(f"组别 {group_name} 已存在，跳过创建")
            return False
        st.error(f"Error creating group {group_name}: {e}")
        return False

def get_groups():
    try:
        client = get_supabase_client()
        response = client.table("groups").select("group_name").execute()
        return [row["group_name"] for row in response.data]
    except Exception as e:
        st.error(f"Error fetching groups: {e}")
        return []

def delete_group(group_name):
    try:
        client = get_supabase_client()
        client.table("groups").delete().eq("group_name", group_name).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting group {group_name}: {e}")
        return False

def save_scores(rater, scores):
    try:
        client = get_supabase_client()
        for target, score in scores.items():
            data = {"rater": rater, "target": target, "score": score}
            client.table("scores").upsert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error saving scores for {rater}: {e}")
        return False

def get_all_users():
    try:
        client = get_supabase_client()
        response = client.table("users").select("*").execute()
        if not response.data:
            st.warning("用户表为空")
            return []
        return [
            {
                "username": row["username"], "realname": row["realname"],
                "roles": row["roles"].split(","), "group": row["group_name"],
                "password": cipher.decrypt(row["password"].encode()).decode()
            }
            for row in response.data
        ]
    except Exception as e:
        st.error(f"Error fetching all users: {e}")
        return []

def get_students_exclude_group(group):
    try:
        client = get_supabase_client()
        response = client.table("users").select("username, realname, group_name").neq("group_name", group).ilike("roles", "%Student%").execute()
        return [{"username": row["username"], "realname": row["realname"], "group": row["group_name"]} for row in response.data]
    except Exception as e:
        st.error(f"Error fetching students excluding group {group}: {e}")
        return []

def get_all_scores():
    try:
        client = get_supabase_client()
        response = client.table("scores").select("*").execute()
        return [{"rater": row["rater"], "target": row["target"], "score": row["score"], "timestamp": row["timestamp"]} for row in response.data]
    except Exception as e:
        st.error(f"Error fetching all scores: {e}")
        return []
