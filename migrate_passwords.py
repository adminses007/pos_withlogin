#!/usr/bin/env python3
"""
密码迁移脚本
将现有明文密码转换为哈希密码
"""

import sqlite3
import bcrypt
import os

def hash_password(password):
    """哈希密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def migrate_passwords():
    """迁移密码"""
    db_path = "pos_system.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，无需迁移")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有用户
        cursor.execute('SELECT id, username, password, role FROM users')
        users = cursor.fetchall()
        
        migrated_count = 0
        
        for user in users:
            user_id, username, password, role = user
            
            # 检查密码是否已经是哈希格式
            if isinstance(password, bytes) or (isinstance(password, str) and password.startswith('$2b$')):
                print(f"用户 {username} 的密码已经是哈希格式，跳过")
                continue
            
            # 哈希密码
            hashed_password = hash_password(password)
            
            # 更新数据库
            cursor.execute('''
                UPDATE users 
                SET password = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (hashed_password, user_id))
            
            migrated_count += 1
            print(f"已迁移用户 {username} 的密码")
        
        conn.commit()
        conn.close()
        
        print(f"\n迁移完成！共迁移了 {migrated_count} 个用户的密码")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=== 密码迁移脚本 ===")
    print("此脚本将把现有明文密码转换为安全的哈希密码")
    
    confirm = input("确认要执行密码迁移吗？(y/N): ")
    if confirm.lower() == 'y':
        migrate_passwords()
    else:
        print("取消迁移") 