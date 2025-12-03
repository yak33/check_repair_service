#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志轮转功能测试脚本
用于验证TimedRotatingFileHandler是否正常工作
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from config import LOG_CONFIG

def test_log_rotation():
    print("开始测试日志轮转功能...")
    
    # 确保日志目录存在
    LOG_DIR = LOG_CONFIG['dir']
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 创建测试logger
    test_logger = logging.getLogger('test_rotation')
    test_logger.setLevel(logging.INFO)
    
    # 清除现有handlers
    test_logger.handlers.clear()
    
    # 日志文件路径
    log_filepath = os.path.join(LOG_DIR, "test_rotation")
    
    # 获取轮转配置
    rotation_config = LOG_CONFIG.get('rotation', {})
    
    # 创建TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        filename=f"{log_filepath}.log",
        when=rotation_config.get('when', 'D'),
        interval=rotation_config.get('interval', 1),
        backupCount=rotation_config.get('backup_count', 30),
        encoding=rotation_config.get('encoding', 'utf-8'),
        delay=False,
        utc=False
    )
    
    # 设置日志文件名格式
    file_handler.suffix = "%Y-%m-%d.log"
    
    # 设置格式
    formatter = logging.Formatter(LOG_CONFIG['format'])
    file_handler.setFormatter(formatter)
    
    # 添加handler
    test_logger.addHandler(file_handler)
    
    # 写入测试日志
    print(f"当前时间: {datetime.now()}")
    test_logger.info("=== 日志轮转功能测试开始 ===")
    test_logger.info(f"当前时间: {datetime.now()}")
    test_logger.info(f"日志配置: {rotation_config}")
    test_logger.info(f"预期行为: 按{rotation_config.get('when', 'D')}轮转，间隔{rotation_config.get('interval', 1)}")
    
    # 检查文件是否创建
    current_log = f"{log_filepath}.log"
    if os.path.exists(current_log):
        print(f"✅ 日志文件已创建: {current_log}")
        print(f"📁 文件大小: {os.path.getsize(current_log)} 字节")
    else:
        print(f"❌ 日志文件未创建: {current_log}")
    
    # 列出logs目录中的所有文件
    print("\n📂 当前logs目录内容:")
    for file in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"  📄 {file} (大小: {size} 字节, 修改时间: {mtime})")
    
    print("\n📝 重要说明:")
    print("1. 日志轮转只在时间边界触发 (如午夜00:00)")
    print("2. 当前只有一个日志文件是正常的")
    print("3. 只有在跨天时才会看到带日期后缀的文件")
    print("4. 可以等到明天再检查是否生成了今天的备份文件")
    
    # 清理测试文件
    test_logger.removeHandler(file_handler)
    file_handler.close()
    
    # 删除测试日志文件
    if os.path.exists(current_log):
        os.remove(current_log)
        print(f"\n🧹 已清理测试文件: {current_log}")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    test_log_rotation()