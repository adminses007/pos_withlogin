import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'pos_system.db'
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 28800))  # 8小时
    DEBUG = False

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SESSION_TIMEOUT = 3600  # 1小时

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SESSION_TIMEOUT = 28800  # 8小时
    
    # 生产环境必须设置这些
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置 SECRET_KEY 环境变量")

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    DATABASE_PATH = 'test_pos_system.db'
    SESSION_TIMEOUT = 1800  # 30分钟

# 根据环境变量选择配置
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config():
    """获取当前环境配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)() 