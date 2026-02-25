#!/usr/bin/env python3
"""
数据清洗工具 - 处理CSV/Excel文件中的常见数据质量问题
功能：
  1. 读取CSV/Excel文件
  2. 处理缺失值（数值列用中位数，分类列用众数）
  3. 删除完全重复的行
  4. 日期格式标准化
  5. 保存清洗后数据
用法：
  python data_cleaner.py input.csv output.csv
"""

import pandas as pd
import numpy as np
import argparse
import os
import logging
from datetime import datetime

# 配置日志（专业实践）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_cleaner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataCleaner")

def read_data(file_path):
    """智能读取CSV/Excel文件"""
    _, ext = os.path.splitext(file_path.lower())
    
    try:
        if ext in ['.csv']:
            return pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    except Exception as e:
        logger.error(f"读取文件失败: {str(e)}")
        raise

def handle_missing_values(df):
    """智能处理缺失值"""
    logger.info("处理缺失值...")
    
    # 数值列：用中位数填充（抗异常值影响）
    num_cols = df.select_dtypes(include=['number']).columns
    for col in num_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.info(f"  列 '{col}': 用中位数 {median_val:.2f} 填充 {df[col].isnull().sum()} 个缺失值")
    
    # 分类列：用众数填充
    cat_cols = df.select_dtypes(exclude=['number']).columns
    for col in cat_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col].fillna(mode_val, inplace=True)
            logger.info(f"  列 '{col}': 用众数 '{mode_val}' 填充 {df[col].isnull().sum()} 个缺失值")
    
    return df

def remove_duplicates(df):
    """删除完全重复的行"""
    initial_count = len(df)
    df.drop_duplicates(inplace=True)
    removed = initial_count - len(df)
    if removed > 0:
        logger.info(f"删除 {removed} 行完全重复数据")
    return df

def standardize_dates(df):
    """尝试标准化所有可能的日期列"""
    logger.info("标准化日期格式...")
    
    # 常见日期列名模式
    date_patterns = ['date', 'time', 'timestamp', 'dob', 'created', 'updated']
    
    for col in df.columns:
        if any(pattern in col.lower() for pattern in date_patterns):
            try:
                # 尝试转换为标准日期格式
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # 填充转换失败的值（保留原始数据）
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    logger.warning(f"  列 '{col}': {null_count} 个值无法转换为日期")
            except Exception as e:
                logger.warning(f"  列 '{col}' 日期转换失败: {str(e)}")
    
    return df

def save_cleaned_data(df, output_path):
    """保存清洗后数据"""
    try:
        # 保留原始文件格式
        _, ext = os.path.splitext(output_path.lower())
        if ext in ['.csv']:
            df.to_csv(output_path, index=False)
        elif ext in ['.xlsx', '.xls']:
            df.to_excel(output_path, index=False)
        
        logger.info(f"清洗后数据已保存至: {output_path}")
        logger.info(f"最终数据形状: {df.shape[0]} 行, {df.shape[1]} 列")
        return True
    except Exception as e:
        logger.error(f"保存数据失败: {str(e)}")
        return False

def main():
    """主流程"""
    parser = argparse.ArgumentParser(description='数据清洗工具')
    parser.add_argument('input', help='输入文件路径 (CSV/Excel)')
    parser.add_argument('output', help='输出文件路径 (CSV/Excel)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='日志级别 (默认: INFO)')
    
    args = parser.parse_args()
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    start_time = datetime.now()
    logger.info(f"=== 数据清洗开始 === 输入: {args.input}, 输出: {args.output}")
    
    try:
        # 1. 读取数据
        df = read_data(args.input)
        logger.info(f"原始数据形状: {df.shape[0]} 行, {df.shape[1]} 列")
        
        # 2. 处理缺失值
        df = handle_missing_values(df)
        
        # 3. 删除重复值
        df = remove_duplicates(df)
        
        # 4. 标准化日期
        df = standardize_dates(df)
        
        # 5. 保存结果
        success = save_cleaned_data(df, args.output)
        
        if success:
            logger.info("✅ 数据清洗成功完成!")
        else:
            logger.error("❌ 数据清洗失败")
            return 1
            
    except Exception as e:
        logger.exception(f"处理过程中发生未预期错误: {str(e)}")
        return 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"⏱️  总耗时: {duration:.2f} 秒")
    return 0

if __name__ == "__main__":
    exit(main())