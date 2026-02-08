# 通义千问API密钥问题排查指南

## ❌ 错误信息

```
AI服务错误: Access denied, please make sure your account is in good standing. 
For details, see: https://help.aliyun.com/zh/model-studio/error-code#overdue-payment
```

## 🔍 问题原因

这个错误通常由以下原因引起：

1. **账户欠费**：阿里云账户余额不足
2. **API密钥无效**：API密钥已过期或被禁用
3. **账户状态异常**：账户被限制使用
4. **API配额用尽**：免费额度或付费配额已用完

## ✅ 解决方案

### 方案1：检查并充值阿里云账户

1. 登录 [阿里云控制台](https://ecs.console.aliyun.com/)
2. 检查账户余额
3. 如果余额不足，请充值
4. 等待几分钟后重试

### 方案2：检查API密钥

1. 访问 [阿里云模型服务控制台](https://dashscope.console.aliyun.com/)
2. 检查API密钥状态
3. 如果密钥无效，创建新的API密钥
4. 更新配置文件中的密钥

**更新API密钥步骤**：

```bash
# 编辑 .env 文件
cd backend
nano .env  # 或使用其他编辑器

# 修改 DASHSCOPE_API_KEY 的值
DASHSCOPE_API_KEY=你的新API密钥
```

### 方案3：检查API配额

1. 访问 [通义千问控制台](https://dashscope.console.aliyun.com/)
2. 查看API调用配额和剩余额度
3. 如果配额用完，可以：
   - 等待配额重置（免费用户通常有月度配额）
   - 升级到付费套餐

### 方案4：验证API密钥格式

确保API密钥格式正确：
- 应该以 `sk-` 开头
- 长度通常为 40-50 个字符
- 示例：`sk-40838326b1f240418cb8475371d435ee`

## 🔧 配置检查

### 检查当前配置

```bash
cd backend
python3 -c "
from config import settings
key = settings.DASHSCOPE_API_KEY
print(f'API密钥: {key[:10]}...{key[-10:] if len(key) > 20 else key}')
print(f'密钥长度: {len(key)}')
"
```

### 更新API密钥

**方法1：通过.env文件（推荐）**

```bash
# 编辑 .env 文件
cd backend
nano .env

# 添加或修改：
DASHSCOPE_API_KEY=你的新API密钥
```

**方法2：通过config.py（不推荐，仅用于测试）**

编辑 `backend/config.py` 文件，修改第19行：

```python
DASHSCOPE_API_KEY: str = "你的新API密钥"
```

## 📝 获取新的API密钥

1. 访问 [阿里云模型服务控制台](https://dashscope.console.aliyun.com/)
2. 登录您的阿里云账号
3. 进入"API-KEY管理"
4. 点击"创建新的API-KEY"
5. 复制生成的API密钥
6. 更新到 `.env` 文件中

## 🧪 测试API密钥

创建测试脚本：

```python
# test_api.py
import dashscope
from config import settings

dashscope.api_key = settings.DASHSCOPE_API_KEY

try:
    from dashscope import Generation
    response = Generation.call(
        model='qwen-turbo',
        messages=[{'role': 'user', 'content': '你好'}],
        result_format='message'
    )
    if response.status_code == 200:
        print("✅ API密钥有效！")
        print(f"响应: {response.output.choices[0].message.content}")
    else:
        print(f"❌ API调用失败: {response.message}")
except Exception as e:
    print(f"❌ 错误: {str(e)}")
```

运行测试：

```bash
cd backend
python3 test_api.py
```

## ⚠️ 临时解决方案

如果暂时无法解决API问题，系统仍可以正常使用其他功能：

- ✅ 用户登录/注册
- ✅ 用户管理
- ✅ 收藏管理
- ✅ 数据查看
- ❌ AI对话（需要API）
- ❌ 教学设计生成（需要API）
- ❌ 题目生成（需要API）

## 📞 获取帮助

如果以上方法都无法解决问题，可以：

1. 查看 [阿里云帮助文档](https://help.aliyun.com/zh/model-studio/)
2. 联系阿里云客服
3. 检查 [错误代码说明](https://help.aliyun.com/zh/model-studio/error-code#overdue-payment)

## 🔄 重启服务

更新API密钥后，需要重启后端服务：

```bash
# 停止当前服务（Ctrl+C）
# 重新启动
cd backend
python3 main.py
```

---

**注意**：API密钥是敏感信息，请妥善保管，不要提交到代码仓库。

