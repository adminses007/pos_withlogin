# POS系统 - 数据库版本

这是一个基于Flask和SQLite的POS（销售点）系统，替代了原来的localStorage版本。

## 功能特性

- **用户认证和权限管理**
  - 登录系统，支持三种用户角色：root、admin、user
  - 基于角色的权限控制
  - 用户管理功能（仅root可用）
  - 密码修改功能
- 产品管理（添加、修改、删除产品）
- 销售记录管理
- 临时销售功能
- 库存管理
- 数据持久化存储（SQLite数据库）
- RESTful API接口

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

有两种方式启动服务器：

#### 方式一：使用启动脚本（推荐）
```bash
python start_server.py
```

#### 方式二：直接运行Flask应用
```bash
python app.py
```

### 3. 访问系统

服务器启动后，在浏览器中访问：
- http://localhost:5000 - 登录页面
- http://localhost:5000/product-management - 产品管理页面（需要root权限）
- http://localhost:5000/pos.html - 销售页面（需要root或admin权限）
- http://localhost:5000/temp_pos.html - 临时销售页面（所有用户可用）

### 4. 默认用户账户

系统预置了三个默认用户账户：

| 用户名 | 密码 | 角色 | 权限 |
|--------|------|------|------|
| root | root | Root管理员 | 所有功能，包括用户管理 |
| admin | admin | Admin管理员 | POS页面和临时POS页面 |
| user | user | User用户 | 仅临时POS页面 |

**注意：** 只有root用户可以创建新用户账户。

## 数据库结构

系统使用SQLite数据库，包含以下表：

### users（用户表）
- id: 主键
- username: 用户名（唯一）
- password: 密码
- role: 角色（root/admin/user）
- created_at: 创建时间
- updated_at: 更新时间

### products（产品表）
- id: 主键
- barcode: 条码（唯一）
- name: 产品名称
- category: 类别
- quantity: 库存数量
- cost_price: 成本价
- selling_price: 售价
- profit_margin: 利润率
- created_at: 创建时间
- updated_at: 更新时间

### sales（销售记录表）
- id: 主键
- barcode: 条码
- name: 产品名称
- quantity: 销售数量
- price: 销售价格
- total_price: 总价
- cost_price: 成本价
- date: 销售日期

### temp_sales（临时销售表）
- id: 主键
- barcode: 条码
- name: 产品名称
- quantity: 销售数量
- price: 销售价格
- total_price: 总价
- date: 销售日期

## API接口

### 用户认证
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户退出
- `GET /api/user/profile` - 获取用户信息
- `POST /api/change-password` - 修改密码

### 用户管理（仅root可用）
- `GET /api/users` - 获取所有用户
- `POST /api/users` - 添加新用户
- `PUT /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户

### 产品管理
- `GET /api/products` - 获取所有产品
- `POST /api/products` - 添加产品
- `PUT /api/products/{id}` - 更新产品
- `DELETE /api/products/{id}` - 删除产品
- `GET /api/products/barcode/{barcode}` - 根据条码获取产品
- `POST /api/products/update-quantity` - 更新产品数量

### 销售管理
- `GET /api/sales` - 获取所有销售记录
- `POST /api/sales` - 添加销售记录

### 临时销售管理
- `GET /api/temp-sales` - 获取临时销售记录
- `POST /api/temp-sales` - 添加临时销售记录
- `POST /api/temp-sales/clear` - 清除临时销售记录

## 主要改进

相比localStorage版本，数据库版本有以下改进：

1. **用户认证和权限管理**: 完整的登录系统和基于角色的权限控制
2. **数据持久化**: 数据存储在SQLite数据库中，不会因浏览器关闭而丢失
3. **多用户支持**: 可以支持多个用户同时使用
4. **数据安全**: 数据存储在服务器端，更安全
5. **扩展性**: 可以轻松添加新功能，如用户管理、权限控制等
6. **数据备份**: 可以轻松备份和恢复数据
7. **API接口**: 提供了RESTful API，可以与其他系统集成

## 注意事项

1. 确保端口5000没有被其他程序占用
2. 首次运行时会自动创建数据库文件 `pos_system.db`
3. 数据库文件会保存在项目根目录下
4. 建议定期备份数据库文件

## 故障排除

如果遇到问题：

1. 检查是否安装了所有依赖：`pip install -r requirements.txt`
2. 检查端口5000是否被占用
3. 检查数据库文件是否有写入权限
4. 查看控制台错误信息

## 技术支持

如有问题，请检查：
- Python版本（建议3.7+）
- Flask版本（2.3.3）
- 网络连接状态
- 浏览器控制台错误信息 