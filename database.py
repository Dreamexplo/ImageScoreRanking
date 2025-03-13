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
url = st.secrets.get("supabase", {}).get("https://klktoorwaidyziqxyaoh.supabase.co", "")
key = st.secrets.get("supabase", {}).get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtsa3Rvb3J3YWlkeXppcXh5YW9oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE4MzQ2MjIsImV4cCI6MjA1NzQxMDYyMn0.-iABpnkMLbZiorz50nyZAmstk9dT2-UyFXTVty5YtBQ", "")


# 加密密钥（通过环境变量或 secrets 配置）
ENCRYPTION_KEY = os.environ.get("iqlcwN7Dx8p1Pi8AR7z-xyBKEW5IGQneCunqfYQCe2Q=", Fernet.generate_key())
cipher = Fernet(ENCRYPTION_KEY)

# 全局变量，延迟初始化
supabase = None

def get_supabase_client():
    global supabase
    if supabase is None:
        if not url or not key:
            st.error(f"Supabase configuration invalid - URL: {url}, Key: {key[:10]}...")
            raise ValueError("Supabase URL or Key is missing")
        supabase = create_client(url, key)
    return supabase

def initialize():
    pass  # Supabase 不需要本地初始化

def create_user(username, realname, roles, group, password):
    encrypted_pwd = cipher.encrypt(password.encode()).decode()
    data = {
        "username": username, "realname": realname, "roles": roles,
        "group_name": group, "password": encrypted_pwd, "modified": 0
    }
    try:
        response = supabase.table("users").insert(data).execute()
        return bool(response.data)
    except:
        return False

def get_user(username):
    response = supabase.table("users").select("*").eq("username", username).execute()
    if response.data:
        user = response.data[0]
        user["password"] = cipher.decrypt(user["password"].encode()).decode()
        user["roles"] = user["roles"].split(",")
        return user
    return None

def update_password(username, new_password):
    encrypted_pwd = cipher.encrypt(new_password.encode()).decode()
    response = supabase.table("users").update({"password": encrypted_pwd, "modified": 1}).eq("username", username).execute()
    return bool(response.data)

def create_group(group_name):
    try:
        response = supabase.table("groups").insert({"group_name": group_name}).execute()
        return bool(response.data)
    except:
        return False

def get_groups():
    response = supabase.table("groups").select("group_name").execute()
    return [row["group_name"] for row in response.data]

def delete_group(group_name):
    supabase.table("groups").delete().eq("group_name", group_name).execute()

def save_scores(rater, scores):
    for target, score in scores.items():
        data = {"rater": rater, "target": target, "score": score}
        supabase.table("scores").upsert(data).execute()

def get_all_users():
    response = supabase.table("users").select("*").execute()
    return [
        {
            "username": row["username"], "realname": row["realname"],
            "roles": row["roles"].split(","), "group": row["group_name"],
            "password": cipher.decrypt(row["password"].encode()).decode()
        }
        for row in response.data
    ]

def get_students_exclude_group(group):
    response = supabase.table("users").select("username, realname, group_name").neq("group_name", group).ilike("roles", "%Student%").execute()
    return [{"username": row["username"], "realname": row["realname"], "group": row["group_name"]} for row in response.data]

def get_all_scores():
    response = supabase.table("scores").select("*").execute()
    return [{"rater": row["rater"], "target": row["target"], "score": row["score"], "timestamp": row["timestamp"]} for row in response.data]
