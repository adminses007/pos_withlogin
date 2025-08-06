#!/usr/bin/env python3
"""
POS系统启动脚本
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        print("✓ Dependencies check passed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_server():
    """启动服务器"""
    print("=== POS system started ===")
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    print(f"Working directory: {current_dir}")
    print("Starting Flask server...")
    
    try:
        # 启动Flask应用
        from app import app
        
        print("Server started successfully!")
        print("Access address:")
        print("  - Login page: http://localhost:5000")
        print("  - Product management: http://localhost:5000/product-management (requires root permission)")
        print("  - Sales page: http://localhost:5000/pos.html (requires root or admin permission)")
        print("  - Temporary sales: http://localhost:5000/temp_pos.html (all users available)")
        print("\nDefault user accounts:")
        print("  - root/root (Root administrator)")
        print("  - admin/admin (Admin administrator)")
        print("  - user/user (User user)")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # 启动服务器（生产环境关闭调试模式）
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Start failed: {e}")
        print("Please check if port 5000 is occupied")

if __name__ == "__main__":
    start_server() 