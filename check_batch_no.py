import schedule
import time
import pymysql
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from config import DB_CONFIG, EMAIL_CONFIG, LOG_CONFIG, SCHEDULE_CONFIG

# 确保日志目录存在
LOG_DIR = LOG_CONFIG['dir']
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
LOG_FILE = os.path.join(LOG_DIR, LOG_CONFIG['file'])

logging.basicConfig(
    level=getattr(logging, LOG_CONFIG['level']),
    format=LOG_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def check_batch_no():
    try:
        logging.info("开始执行调拨单和维修单关系检查...")
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 执行查询
        sql = """
        SELECT 
            r.REPAIR_NO AS 维修单号,
            c.TRANSFER_NO AS 调拨单号,
            r.BATCH_NO AS 维修单批次号,
            c.BATCH_NO AS 调拨单批次号,
            r.BILL_NO AS 维修单运单号,
            c.BILL_NO AS 调拨单运单号,
            c.CREATE_DATE AS 调拨单创建时间
        FROM 
            storage_repair_order r
        JOIN 
            storage_transfer t ON r.REPAIR_NO = t.REL_REPAIR_NO
        JOIN storage_transfer_detail c ON c.TRANSFER_NO = t.TRANSFER_NO
        WHERE
            ( r.BATCH_NO != c.BATCH_NO OR r.BILL_NO != c.BILL_NO ) 
            AND c.CREATE_DATE >= '2025-01-01 00:00:00';
        """
        
        cursor.execute(sql)
        results = cursor.fetchall()

        # 检查是否有结果
        if results:
           # 获取列名
            columns = [desc[0] for desc in cursor.description]
            
            # 将结果打印到日志
            logging.info(f"共检索到 {len(results)} 条记录")
            logging.info("结果详情：")
            for i, row in enumerate(results):
                row_data = dict(zip(columns, row))
                logging.info(f"记录 {i+1}: {row_data}")
            
            # 构建邮件内容
            rows_html = []
            for row in results:
                rows_html.append("<tr>" + "".join([f"<td style='padding:8px;'>{str(cell)}</td>" for cell in row]) + "</tr>")
            
            table_html = f"""
            <table border="1" cellspacing="0" cellpadding="5" style="width:100%; border-collapse:collapse; table-layout:fixed;">
                <tr>{"".join([f"<th style='padding:8px; background-color:#f2f2f2; min-width:150px;'>{col}</th>" for col in columns])}</tr>
                {"".join(rows_html)}
            </table>
            """
            
            email_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
            <h2>调拨单和维修单关系检查结果</h2>
            <p>时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>以下是调拨单和维修单的关系数据：</p>
            {table_html}
            </body>
            </html>
            """
            
            # 发送邮件
            send_email("调拨单和维修单关系检查结果", email_content, is_html=True)
            logging.info(f"已发送提醒邮件，共发现{len(results)}条记录")
        else:
            logging.info("检查完成，没有发现数据")

    except Exception as e:
        logging.error(f"发生错误: {str(e)}")
        send_email("调拨单维修单检查错误提醒", f"检查过程中发生错误：{str(e)}")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def send_email(subject, content, is_html=False):
    try:
        msg = MIMEText(content, 'html' if is_html else 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['receiver_email']

        # 使用SSL连接
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        logging.info("邮件发送成功")
    except Exception as e:
        logging.error(f"发送邮件失败: {str(e)}")

def main():
    # 设置每小时整点执行一次
    schedule.every().hour.at(":00").do(check_batch_no)
    
    logging.info("服务已启动，将在每小时整点执行检查...")
    
    # 立即执行一次检查
    # check_batch_no()

    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()