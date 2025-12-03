# 调拨单和维修单关系检查服务

## 项目简介

此服务主要用于检查调拨单和维修单之间的关系数据一致性，特别是监控批次号和运单号的匹配情况。当发现不匹配的情况时，系统会自动发送电子邮件通知相关人员。

## 功能特点

- 定时自动检查调拨单和维修单的批次号和运单号是否匹配
- **按日期自动分割日志文件**，便于日志管理和查看
- 自动清理过期日志文件，避免占用过多磁盘空间
- 将检查结果记录到日志文件
- 当发现不匹配记录时，自动发送邮件通知
- 支持自定义检查频率和邮件接收人

## 技术架构

- **编程语言**: Python
- **定时任务**: schedule 库
- **数据库连接**: PyMySQL
- **邮件发送**: smtplib

## 安装要求

- Python 3.6+
- 依赖包：
  - schedule==1.2.0
  - pymysql==1.1.0

## 安装步骤

1. 克隆或下载项目到本地

2. 安装所需依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 根据需要修改配置文件 `config.py`

## 配置说明

所有配置项都在 `config.py` 文件中：

### 数据库配置

```python
DB_CONFIG = {
    'host': '数据库地址',
    'port': 数据库端口,
    'user': '用户名',
    'password': '密码',
    'database': '数据库名',
    'charset': 'utf8mb4'
}
```

### 邮件配置

```python
EMAIL_CONFIG = {
    'smtp_server': 'SMTP服务器地址',
    'smtp_port': SMTP端口,
    'sender_email': '发件人邮箱',
    'sender_password': '发件人邮箱密码或授权码',
    'receiver_email': '收件人邮箱'
}
```

### 日志配置

```python
LOG_CONFIG = {
    'dir': '日志目录',
    'file': '日志文件名',
    'level': '日志级别',
    'format': '日志格式',
    # 日志轮转配置
    'rotation': {
        'when': 'D',        # 按天轮转 ('D'=天, 'H'=小时, 'M'=分钟)
        'interval': 1,      # 每1天轮转一次
        'backup_count': 30, # 保留30个历史文件
        'encoding': 'utf-8'
    }
}
```

#### 日志轮转功能说明

- **自动分割**: 系统会每天自动创建新的日志文件
- **文件命名**: 分割后的文件命名格式为 `check_batch_no_YYYY-MM-DD.log`
- **自动清理**: 超过30天的日志文件会自动删除
- **灵活配置**: 可修改 `when`、`interval` 和 `backup_count` 参数来调整轮转策略

示例日志文件结构：
```
logs/
├── check_batch_no.log           # 当前日志
├── check_batch_no_2025-06-07.log # 昨天的日志
├── check_batch_no_2025-06-06.log # 前天的日志
└── ...
```

### 定时任务配置

```python
SCHEDULE_CONFIG = {
    'check_time': '12:00'  # 每天中午12点执行
}
```

## 使用方法

### 手动运行

```bash
python check_batch_no.py
```

### 作为系统服务运行（Linux）

1. 修改 `batch_check.service` 文件中的路径为实际安装路径

2. 将服务文件复制到系统服务目录：

   ```bash
   sudo cp batch_check.service /etc/systemd/system/
   ```

3. 启用并启动服务：

   ```bash
   sudo systemctl enable batch_check.service
   sudo systemctl start batch_check.service
   ```

4. 查看服务状态：
   ```bash
   sudo systemctl status batch_check.service
   ```

## 日志查看

日志文件默认保存在 `./logs/check_batch_no.log`，可通过以下命令查看：

```bash
tail -f ./logs/check_batch_no.log
```

## 主要文件说明

- `check_batch_no.py`: 主程序文件，包含检查逻辑和邮件发送功能
- `config.py`: 配置文件，包含数据库、邮件、日志和定时任务配置
- `batch_check.service`: Linux 系统服务配置文件
- `requirements.txt`: 项目依赖列表

## 维护与支持

如有问题或需要支持，请联系系统管理员。

## 最后更新

最后更新日期: 2025 年 06 月 08 日
