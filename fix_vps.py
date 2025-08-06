#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPS快速修复脚本
自动修复常见的VPS部署问题
"""

import os
import sys
import sqlite3
import bcrypt
import subprocess
import time
import socket

def fix_database():
    """修复数据库问题"""
    print("🔧 修复数据库...")
    
    try:
        # 删除旧的数据库文件
        if os.path.exists("pos_system.db"):
            os.remove("pos_system.db")
            print("✅ 删除旧数据库文件")
        
        # 重新初始化数据库
        from database import POSDatabase
        db = POSDatabase()
        print("✅ 重新初始化数据库")
        
        # 验证用户
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users")
        users = cursor.fetchall()
        conn.close()
        
        print(f"✅ 创建了 {len(users)} 个用户")
        
        # 测试登录
        for username, password in users:
            user = db.authenticate_user(username, username)
            if user:
                print(f"✅ {username} 用户登录测试成功")
            else:
                print(f"❌ {username} 用户登录测试失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    
    try:
        # 检查端口是否被占用
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("✅ 端口5000已被占用，服务器可能已在运行")
            return True
        
        # 启动服务器
        print("正在启动服务器...")
        process = subprocess.Popen(['python3', 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(5)
        
        # 检查服务器是否启动成功
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("✅ 服务器启动成功")
            return True
        else:
            print("❌ 服务器启动失败")
            return False
            
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return False

def test_api():
    """测试API"""
    print("🧪 测试API...")
    
    try:
        import requests
        
        # 测试登录API
        response = requests.post('http://localhost:5000/api/login', 
                               json={'username': 'root', 'password': 'root'},
                               timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 登录API测试成功")
                return True
            else:
                print(f"❌ 登录API返回错误: {data.get('error')}")
                return False
        else:
            print(f"❌ 登录API返回状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 VPS POS系统快速修复工具")
    print("=" * 50)
    
    # 检查当前目录
    print(f"📁 当前目录: {os.getcwd()}")
    
    # 检查必要文件
    required_files = ['app.py', 'database.py', 'requirements.txt']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
            return
    
    # 修复数据库
    if not fix_database():
        print("❌ 数据库修复失败，退出")
        return
    
    # 启动服务器
    if not start_server():
        print("❌ 服务器启动失败，退出")
        return
    
    # 测试API
    if not test_api():
        print("❌ API测试失败")
        return
    
    print("\n" + "=" * 50)
    print("✅ 修复完成！")
    print("🌐 现在可以访问: http://your-vps-ip:5000")
    print("👤 使用 root/root 登录")

if __name__ == "__main__":
    main() 