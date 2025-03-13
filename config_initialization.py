# -*- coding: utf-8 -*-
"""
Initial configuration for users and groups
@author: 33952
"""

from database import create_user, create_group, get_groups, get_all_users

def initialize_groups():
    existing_groups = get_groups()
    groups = ['第一组', '第二组', '第三组']
    for group in groups:
        if group not in existing_groups:
            create_group(group)

def initialize_users():
    existing_users = [u['username'] for u in get_all_users()]
    for i in range(1, 16):
        username = f"student{i}"
        if username not in existing_users:
            group = ['第一组', '第二组', '第三组'][(i-1)//5]
            create_user(username, f"学生{i}", "Student", group, "1234")
    
    if "admin1" not in existing_users:
        create_user("admin1", "管理员1", "Admin", "Undefined", "1234")
    if "teacher1" not in existing_users:
        create_user("teacher1", "老师1", "Teacher", "Undefined", "1234")