#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPS调试脚本
用于诊断VPS上的POS系统问题
"""

import os
import sys
import sqlite3
import bcrypt
from datetime import datetime

def check_database():
    """检查数据库状态"""
    print("=== 数据库检查 ===")
    
    db_path = "pos_system.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"✅ 数据库文件存在: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 数据库表: {[table[0] for table in tables]}")
        
        # 检查用户表
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 用户数量: {user_count}")
        
        # 检查用户详情
        cursor.execute("SELECT id, username, role, created_at FROM users")
        users = cursor.fetchall()
        print("📝 用户列表:")
        for user in users:
            print(f"  - ID: {user[0]}, 用户名: {user[1]}, 角色: {user[2]}, 创建时间: {user[3]}")
        
        # 检查密码哈希
        cursor.execute("SELECT username, password FROM users LIMIT 1")
        sample_user = cursor.fetchone()
        if sample_user:
            password_hash = sample_user[1]
            print(f"🔐 密码哈希示例 (用户: {sample_user[0]}): {password_hash[:20]}...")
            
            # 测试密码验证
            try:
                if bcrypt.checkpw(b'root', password_hash.encode('utf-8')):
                    print("✅ 密码哈希验证正常")
                else:
                    print("❌ 密码哈希验证失败")
            except Exception as e:
                print(f"❌ 密码哈希验证错误: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("\n=== 环境检查 ===")
    
    # 检查Python版本
    print(f"🐍 Python版本: {sys.version}")
    
    # 检查当前目录
    print(f"📁 当前目录: {os.getcwd()}")
    
    # 检查文件权限
    db_path = "pos_system.db"
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        print(f"📄 数据库文件权限: {oct(stat.st_mode)[-3:]}")
    
    # 检查端口占用
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        if result == 0:
            print("✅ 端口5000正在使用")
        else:
            print("❌ 端口5000未使用")
        sock.close()
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")

def test_login():
    """测试登录功能"""
    print("\n=== 登录测试 ===")
    
    try:
        from database import POSDatabase
        db = POSDatabase()
        
        # 测试root用户登录
        user = db.authenticate_user('root', 'root')
        if user:
            print(f"✅ root用户登录成功: {user}")
        else:
            print("❌ root用户登录失败")
        
        # 测试admin用户登录
        user = db.authenticate_user('admin', 'admin')
        if user:
            print(f"✅ admin用户登录成功: {user}")
        else:
            print("❌ admin用户登录失败")
        
        # 测试user用户登录
        user = db.authenticate_user('user', 'user')
        if user:
            print(f"✅ user用户登录成功: {user}")
        else:
            print("❌ user用户登录失败")
            
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")

def fix_database():
    """修复数据库问题"""
    print("\n=== 数据库修复 ===")
    
    try:
        from database import POSDatabase
        db = POSDatabase()
        
        # 重新初始化默认用户
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # 删除现有用户
        cursor.execute("DELETE FROM users")
        
        # 重新创建默认用户
        default_users = [
            ('root', 'root', 'root'),
            ('admin', 'admin', 'admin'),
            ('user', 'user', 'user')
        ]
        
        for username, password, role in default_users:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, role))
        
        conn.commit()
        conn.close()
        
        print("✅ 数据库修复完成")
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")

def main():
    """主函数"""
    print("🔧 VPS POS系统调试工具")
    print("=" * 50)
    
    # 检查环境
    check_environment()
    
    # 检查数据库
    db_ok = check_database()
    
    # 测试登录
    test_login()
    
    # 如果数据库有问题，询问是否修复
    if not db_ok:
        print("\n❌ 数据库存在问题")
        response = input("是否要修复数据库? (y/n): ")
        if response.lower() == 'y':
            fix_database()
            print("\n🔄 重新测试登录...")
            test_login()
    
    print("\n" + "=" * 50)
    print("调试完成")

if __name__ == "__main__":
    main() 