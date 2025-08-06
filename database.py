import sqlite3
import json
import os
import bcrypt
from datetime import datetime

class POSDatabase:
    def __init__(self, db_path="pos_system.db"):
        self.db_path = db_path
        self.init_database()
    
    @staticmethod
    def hash_password(password):
        """哈希密码"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password, hashed):
        """验证密码"""
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('root', 'admin', 'user')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建产品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                profit_margin REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建销售记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total_price REAL NOT NULL,
                cost_price REAL NOT NULL,
                date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        ''')
        
        # 创建临时销售表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                total_price REAL NOT NULL,
                date TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        ''')
        
        # 初始化默认用户
        self.init_default_users(cursor)
        
        conn.commit()
        conn.close()
    
    def init_default_users(self, cursor):
        """初始化默认用户"""
        # 检查是否已存在默认用户
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # 创建默认用户（使用哈希密码）
            default_users = [
                ('root', 'root', 'root'),
                ('admin', 'admin', 'admin'),
                ('user', 'user', 'user')
            ]
            
            for username, password, role in default_users:
                hashed_password = self.hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, password, role)
                    VALUES (?, ?, ?)
                ''', (username, hashed_password, role))
    
    def add_product(self, barcode, name, category, quantity, cost_price, selling_price):
        """添加产品"""
        try:
            profit_margin = ((selling_price - cost_price) / selling_price) * 100
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO products (barcode, name, category, quantity, cost_price, selling_price, profit_margin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (barcode, name, category, quantity, cost_price, selling_price, profit_margin))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # 条码重复
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
    
    def get_all_products(self):
        """获取所有产品"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products ORDER BY category, name')
        products = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'id': p[0],
                'barcode': p[1],
                'name': p[2],
                'category': p[3],
                'quantity': p[4],
                'cost_price': p[5],
                'selling_price': p[6],
                'profit_margin': p[7]
            }
            for p in products
        ]
    
    def update_product(self, product_id, barcode, name, category, quantity, cost_price, selling_price):
        """更新产品"""
        try:
            profit_margin = ((selling_price - cost_price) / selling_price) * 100
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE products 
                SET barcode=?, name=?, category=?, quantity=?, cost_price=?, selling_price=?, profit_margin=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (barcode, name, category, quantity, cost_price, selling_price, profit_margin, product_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Update product error: {e}")
            return False
    
    def delete_product(self, product_id):
        """删除产品"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    def get_product_by_barcode(self, barcode):
        """根据条码获取产品"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products WHERE barcode=?', (barcode,))
        product = cursor.fetchone()
        
        conn.close()
        
        if product:
            return {
                'id': product[0],
                'barcode': product[1],
                'name': product[2],
                'category': product[3],
                'quantity': product[4],
                'cost_price': product[5],
                'selling_price': product[6],
                'profit_margin': product[7]
            }
        return None
    
    def update_product_quantity(self, barcode, quantity_change):
        """更新产品库存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE products 
                SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
                WHERE barcode = ?
            ''', (quantity_change, barcode))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating product quantity: {e}")
            return False
    
    def add_sale(self, barcode, name, quantity, price, total_price, cost_price):
        """添加销售记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sales (barcode, name, quantity, price, total_price, cost_price, date)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            ''', (barcode, name, quantity, price, total_price, cost_price))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding sale record: {e}")
            return False
    
    def get_all_sales(self):
        """获取所有销售记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sales ORDER BY date DESC')
        sales = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'id': s[0],
                'barcode': s[1],
                'name': s[2],
                'quantity': s[3],
                'price': s[4],
                'total_price': s[5],
                'cost_price': s[6],
                'date': s[7]
            }
            for s in sales
        ]
    
    def delete_sale(self, sale_id):
        """删除销售记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 先获取销售记录信息，用于恢复库存
            cursor.execute('SELECT barcode, quantity FROM sales WHERE id = ?', (sale_id,))
            sale = cursor.fetchone()
            
            if not sale:
                conn.close()
                return False
            
            # 删除销售记录
            cursor.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting sale record: {e}")
            return False
    
    def add_temp_sale(self, barcode, name, quantity, price, total_price):
        """添加临时销售记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO temp_sales (barcode, name, quantity, price, total_price, date)
                VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
            ''', (barcode, name, quantity, price, total_price))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding temporary sale record: {e}")
            return False
    
    def get_temp_sales(self):
        """获取临时销售记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM temp_sales ORDER BY date DESC')
        temp_sales = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'id': s[0],
                'barcode': s[1],
                'name': s[2],
                'quantity': s[3],
                'price': s[4],
                'total_price': s[5],
                'date': s[6]
            }
            for s in temp_sales
        ]
    
    def clear_temp_sales(self):
        """清空临时销售记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM temp_sales')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing temporary sales: {e}")
            return False
    
    def delete_temp_sale(self, temp_sale_id):
        """删除单个临时销售记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM temp_sales WHERE id = ?', (temp_sale_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting temporary sale record: {e}")
            return False
    
    def cleanup_old_temp_sales(self, hours=24):
        """清理过期的临时销售记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除超过指定小时数的临时销售记录
            cursor.execute('''
                DELETE FROM temp_sales 
                WHERE datetime(date) < datetime('now', '-{} hours')
            '''.format(hours))
            
            cleaned_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            return cleaned_count
        except Exception as e:
            print(f"Error cleaning up old temporary sales: {e}")
            return 0
    
    def backup_data(self):
        """备份数据"""
        try:
            products = self.get_all_products()
            sales = self.get_all_sales()
            
            backup_data = {
                'products': products,
                'sales': sales,
                'backup_date': datetime.now().isoformat()
            }
            
            with open('pos_backup.json', 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error backing up data: {e}")
            return False
    
    def restore_data(self, backup_file):
        """恢复数据"""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 清空现有数据
            cursor.execute('DELETE FROM products')
            cursor.execute('DELETE FROM sales')
            
            # 恢复产品数据
            for product in backup_data.get('products', []):
                cursor.execute('''
                    INSERT INTO products (barcode, name, category, quantity, cost_price, selling_price, profit_margin)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product['barcode'], product['name'], product['category'], 
                     product['quantity'], product['cost_price'], product['selling_price'], product['profit_margin']))
            
            # 恢复销售数据
            for sale in backup_data.get('sales', []):
                cursor.execute('''
                    INSERT INTO sales (barcode, name, quantity, price, total_price, cost_price, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (sale['barcode'], sale['name'], sale['quantity'], 
                     sale['price'], sale['total_price'], sale['cost_price'], sale['date']))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error restoring data: {e}")
            return False

    # 用户管理方法
    def authenticate_user(self, username, password):
        """验证用户登录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 先获取用户信息（包括密码哈希）
            cursor.execute('SELECT id, username, password, role FROM users WHERE username = ?', 
                         (username,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user and self.verify_password(password, user[2]):
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[3]
                }
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """根据ID获取用户信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self):
        """获取所有用户（仅root可用）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, username, role, created_at FROM users ORDER BY created_at DESC')
            users = cursor.fetchall()
            
            conn.close()
            
            return [
                {
                    'id': u[0],
                    'username': u[1],
                    'role': u[2],
                    'created_at': u[3]
                }
                for u in users
            ]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def add_user(self, username, password, role):
        """添加新用户（仅root可用）"""
        try:
            if role not in ['root', 'admin', 'user']:
                return False
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 哈希密码
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, role))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # 用户名重复
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def update_user(self, user_id, username, password, role):
        """更新用户信息（仅root可用）"""
        try:
            if role not in ['root', 'admin', 'user']:
                return False
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if password:
                # 哈希新密码
                hashed_password = self.hash_password(password)
                cursor.execute('''
                    UPDATE users 
                    SET username=?, password=?, role=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (username, hashed_password, role, user_id))
            else:
                cursor.execute('''
                    UPDATE users 
                    SET username=?, role=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (username, role, user_id))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # 用户名重复
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id):
        """删除用户（仅root可用）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否为默认用户
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if user and user[0] in ['root', 'admin', 'user']:
                conn.close()
                return False  # 不允许删除默认用户
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def change_password(self, user_id, old_password, new_password):
        """修改密码"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取当前密码哈希
            cursor.execute('SELECT password FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False
            
            # 验证旧密码
            if not self.verify_password(old_password, user[0]):
                conn.close()
                return False
            
            # 哈希新密码并更新
            hashed_new_password = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (hashed_new_password, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False

# 创建数据库实例
db = POSDatabase() 