from flask import Flask, request, jsonify, send_from_directory, render_template_string, session
from flask_cors import CORS
from database import POSDatabase
import os
import sys
import secrets
import time
from datetime import datetime, timedelta

# 获取应用根目录（支持exe环境）
def get_app_root():
    if getattr(sys, 'frozen', False):
        # 如果是exe环境
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        return os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 设置session密钥
CORS(app)

# 设置应用根目录
app_root = get_app_root()
app.static_folder = os.path.join(app_root, 'static')

db = POSDatabase()

# 改进的用户会话存储（包含过期时间）
user_sessions = {}

def cleanup_expired_sessions():
    """清理过期的会话"""
    current_time = time.time()
    expired_tokens = []
    
    for token, session_data in user_sessions.items():
        if current_time > session_data['expires_at']:
            expired_tokens.append(token)
    
    for token in expired_tokens:
        del user_sessions[token]

def create_session(user_info):
    """创建新会话"""
    token = secrets.token_hex(32)
    expires_at = time.time() + (8 * 60 * 60)  # 8小时过期
    
    user_sessions[token] = {
        'user_id': user_info['id'],
        'username': user_info['username'],
        'role': user_info['role'],
        'created_at': time.time(),
        'expires_at': expires_at
    }
    
    return token

def get_session_user(token):
    """获取会话用户信息"""
    if token not in user_sessions:
        return None
    
    session_data = user_sessions[token]
    if time.time() > session_data['expires_at']:
        del user_sessions[token]
        return None
    
    return session_data

def validate_input(data, required_fields=None, string_fields=None, numeric_fields=None):
    """输入验证函数"""
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    # 检查必需字段
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
    
    # 验证字符串字段
    if string_fields:
        for field in string_fields:
            if field in data and data[field]:
                if not isinstance(data[field], str) or len(data[field].strip()) == 0:
                    return False, f"Field {field} must be a valid string"
                # 防止SQL注入
                if any(char in data[field] for char in ["'", '"', ';', '--', '/*', '*/']):
                    return False, f"Field {field} contains invalid characters"
    
    # 验证数字字段
    if numeric_fields:
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    return False, f"Field {field} must be a valid number"
    
    return True, "Validation passed"

def require_auth(required_role=None):
    """权限验证装饰器"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            # 从请求头获取token
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'success': False, 'error': 'No token provided'}), 401
            
            user_info = get_session_user(token)
            
            if not user_info:
                return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
            
            if required_role and user_info['role'] != required_role:
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

@app.route('/login.html')
def login():
    try:
        login_path = os.path.join(app_root, 'login.html')
        if os.path.exists(login_path):
            return send_from_directory(app_root, 'login.html')
        else:
            return "login.html not found", 404
    except Exception as e:
        return f"Error loading login.html: {str(e)}", 500

@app.route('/')
def index():
    try:
        # 重定向到登录页面
        return send_from_directory(app_root, 'login.html')
    except Exception as e:
        return f"Error loading login.html: {str(e)}", 500

@app.route('/product-management')
def product_management():
    try:
        index_path = os.path.join(app_root, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app_root, 'index.html')
        else:
            return "index.html not found", 404
    except Exception as e:
        return f"Error loading index.html: {str(e)}", 500

@app.route('/pos.html')
def pos():
    try:
        pos_path = os.path.join(app_root, 'pos.html')
        if os.path.exists(pos_path):
            return send_from_directory(app_root, 'pos.html')
        else:
            return "pos.html not found", 404
    except Exception as e:
        return f"Error loading pos.html: {str(e)}", 500

@app.route('/temp_pos.html')
def temp_pos():
    try:
        temp_pos_path = os.path.join(app_root, 'temp_pos.html')
        if os.path.exists(temp_pos_path):
            return send_from_directory(app_root, 'temp_pos.html')
        else:
            return "temp_pos.html not found", 404
    except Exception as e:
        return f"Error loading temp_pos.html: {str(e)}", 500

@app.route('/Profit Calc.html')
def profit_calc():
    try:
        profit_calc_path = os.path.join(app_root, 'Profit Calc.html')
        if os.path.exists(profit_calc_path):
            return send_from_directory(app_root, 'Profit Calc.html')
        else:
            return "Profit Calc.html not found", 404
    except Exception as e:
        return f"Error loading Profit Calc.html: {str(e)}", 500

@app.route('/test_pos.html')
def test_pos():
    try:
        test_pos_path = os.path.join(app_root, 'test_pos.html')
        if os.path.exists(test_pos_path):
            return send_from_directory(app_root, 'test_pos.html')
        else:
            return "test_pos.html not found", 404
    except Exception as e:
        return f"Error loading test_pos.html: {str(e)}", 500

@app.route('/debug.html')
def debug():
    try:
        debug_path = os.path.join(app_root, 'debug.html')
        if os.path.exists(debug_path):
            return send_from_directory(app_root, 'debug.html')
        else:
            return "debug.html not found", 404
    except Exception as e:
        return f"Error loading debug.html: {str(e)}", 500

@app.route('/debug_temp_pos.html')
def debug_temp_pos():
    try:
        debug_path = os.path.join(app_root, 'debug_temp_pos.html')
        if os.path.exists(debug_path):
            return send_from_directory(app_root, 'debug_temp_pos.html')
        else:
            return "debug_temp_pos.html not found", 404
    except Exception as e:
        return f"Error loading debug_temp_pos.html: {str(e)}", 500

@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        static_dir = os.path.join(app_root, 'static')
        if os.path.exists(os.path.join(static_dir, filename)):
            return send_from_directory(static_dir, filename)
        else:
            return f"Static file {filename} not found", 404
    except Exception as e:
        return f"Error loading static file {filename}: {str(e)}", 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = db.get_all_products()
        return jsonify({'success': True, 'data': products})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        print(f"Add product request data: {data}")  # 调试日志
        
        # 验证数据
        required_fields = ['barcode', 'name', 'category', 'quantity', 'cost_price', 'selling_price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        success = db.add_product(
            data.get('barcode'), data.get('name'), data.get('category'),
            data.get('quantity'), data.get('cost_price'), data.get('selling_price')
        )
        
        if success:
            print(f"Product added successfully: {data.get('barcode')}")  # 调试日志
            return jsonify({'success': True, 'message': 'Product added successfully'})
        else:
            print(f"Product added failed: {data.get('barcode')}")  # 调试日志
            return jsonify({'success': False, 'error': 'The product already exists or failed to be added'}), 400
    except Exception as e:
        print(f"Add product exception: {str(e)}")  # 调试日志
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.json
        success = db.update_product(
            product_id, data.get('barcode'), data.get('name'), data.get('category'),
            data.get('quantity'), data.get('cost_price'), data.get('selling_price')
        )
        if success:
            return jsonify({'success': True, 'message': 'Product updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Product update failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        success = db.delete_product(product_id)
        if success:
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Product deletion failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/barcode/<barcode>', methods=['GET'])
def get_product_by_barcode(barcode):
    try:
        product = db.get_product_by_barcode(barcode)
        if product:
            return jsonify({'success': True, 'data': product})
        else:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/update-quantity', methods=['POST'])
@require_auth()
def update_product_quantity():
    try:
        data = request.json
        success = db.update_product_quantity(data.get('barcode'), data.get('quantity_change'))
        if success:
            return jsonify({'success': True, 'message': 'Quantity updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Quantity update failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sales', methods=['GET'])
@require_auth()
def get_sales():
    try:
        sales = db.get_all_sales()
        return jsonify({'success': True, 'data': sales})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sales', methods=['POST'])
@require_auth()
def add_sale():
    try:
        data = request.json
        success = db.add_sale(
            data.get('barcode'), data.get('name'), data.get('quantity'),
            data.get('price'), data.get('total_price'), data.get('cost_price')
        )
        if success:
            return jsonify({'success': True, 'message': 'Sale record added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Sale record addition failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@require_auth()
def delete_sale(sale_id):
    try:
        success = db.delete_sale(sale_id)
        if success:
            return jsonify({'success': True, 'message': 'Sale record deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Sale record deletion failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/temp-sales', methods=['GET'])
@require_auth()
def get_temp_sales():
    try:
        temp_sales = db.get_temp_sales()
        return jsonify({'success': True, 'data': temp_sales})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/temp-sales', methods=['POST'])
@require_auth()
def add_temp_sale():
    try:
        data = request.json
        success = db.add_temp_sale(
            data.get('barcode'), data.get('name'), data.get('quantity'),
            data.get('price'), data.get('total_price')
        )
        if success:
            return jsonify({'success': True, 'message': 'Temporary sale record added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Temporary sale record addition failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/temp-sales/clear', methods=['POST'])
@require_auth()
def clear_temp_sales():
    try:
        success = db.clear_temp_sales()
        if success:
            return jsonify({'success': True, 'message': 'Temporary sale record cleared successfully'})
        else:
            return jsonify({'success': False, 'error': 'Temporary sale record clearing failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/temp-sales/cleanup', methods=['POST'])
@require_auth()
def cleanup_temp_sales():
    try:
        cleaned_count = db.cleanup_old_temp_sales()
        return jsonify({
            'success': True, 
            'message': f'Cleaned up {cleaned_count} old temporary sale records',
            'cleaned_count': cleaned_count
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/temp-sales/<int:temp_sale_id>', methods=['DELETE'])
@require_auth()
def delete_temp_sale(temp_sale_id):
    try:
        success = db.delete_temp_sale(temp_sale_id)
        if success:
            return jsonify({'success': True, 'message': 'Temporary sale record deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Temporary sale record deletion failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 登录相关API
@app.route('/api/login', methods=['POST'])
def login_api():
    try:
        data = request.json
        
        # 输入验证
        is_valid, error_msg = validate_input(
            data, 
            required_fields=['username', 'password'],
            string_fields=['username', 'password']
        )
        
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # 验证用户
        user = db.authenticate_user(username, password)
        
        if user:
            # 生成token
            token = create_session(user)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user,
                'token': token
            })
        else:
            return jsonify({'success': False, 'error': 'Username or password error'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout_api():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token in user_sessions:
            del user_sessions[token]
        
        return jsonify({'success': True, 'message': 'Logout successful'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        user_info = get_session_user(token)
        
        if not user_info:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        return jsonify({'success': True, 'data': user_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 用户管理API（仅root可用）
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        user_info = get_session_user(token)
        
        if not user_info:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        if user_info['role'] != 'root':
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        users = db.get_all_users()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        user_info = get_session_user(token)
        
        if not user_info:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        if user_info['role'] != 'root':
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not username or not password or not role:
            return jsonify({'success': False, 'error': 'Username, password and role cannot be empty'}), 400
        
        if role not in ['root', 'admin', 'user']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        success = db.add_user(username, password, role)
        
        if success:
            return jsonify({'success': True, 'message': 'User added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Username already exists or addition failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        user_info = get_session_user(token)
        
        if not user_info:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        if user_info['role'] != 'root':
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        if not username or not role:
            return jsonify({'success': False, 'error': 'Username and role cannot be empty'}), 400
        
        if role not in ['root', 'admin', 'user']:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        success = db.update_user(user_id, username, password, role)
        
        if success:
            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Username already exists or update failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        user_info = get_session_user(token)
        
        if not user_info:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        if user_info['role'] != 'root':
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
        
        success = db.delete_user(user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Cannot delete default user or deletion failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        user_info = get_session_user(token)
        
        if not user_info:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        data = request.json
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'success': False, 'error': 'Old password and new password cannot be empty'}), 400
        
        success = db.change_password(user_info['user_id'], old_password, new_password)
        
        if success:
            return jsonify({'success': True, 'message': 'Password changed successfully'})
        else:
            return jsonify({'success': False, 'error': 'Old password error or modification failed'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=== POS system started ===")
    print(f"Application root: {app_root}")
    print(f"Static file directory: {app.static_folder}")
    print("Starting server...")
    print("Access address: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print()
    
    # VPS部署时使用生产模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000) 