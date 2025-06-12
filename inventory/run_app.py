#!/usr/bin/env python3
"""
快速启动脚本 - SKU 80814094 库存销售分析系统
"""

import sys
import subprocess
import os
from pathlib import Path

def check_requirements():
    """检查所需的依赖包"""
    required_packages = ['streamlit', 'pandas', 'plotly', 'openpyxl', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def check_data_file():
    """检查数据文件是否存在"""
    data_file = Path('save.xlsx')
    return data_file.exists()

def install_packages(packages):
    """安装缺失的包"""
    print("正在安装缺失的依赖包...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 启动 SKU 80814094 库存销售分析系统")
    print("=" * 50)
    
    # 检查数据文件
    print("📁 检查数据文件...")
    if not check_data_file():
        print("❌ 错误: 找不到 save.xlsx 数据文件")
        print("请确保 save.xlsx 文件位于当前目录")
        return
    print("✅ 数据文件检查通过")
    
    # 检查依赖包
    print("📦 检查依赖包...")
    missing = check_requirements()
    
    if missing:
        print(f"⚠️  缺少以下依赖包: {', '.join(missing)}")
        response = input("是否自动安装? (y/n): ").lower()
        
        if response == 'y':
            if install_packages(missing):
                print("✅ 依赖包安装完成")
            else:
                print("❌ 依赖包安装失败，请手动安装:")
                print(f"pip install {' '.join(missing)}")
                return
        else:
            print("请手动安装依赖包后重新运行:")
            print(f"pip install {' '.join(missing)}")
            return
    else:
        print("✅ 所有依赖包已安装")
    
    # 启动Streamlit应用
    print("🌐 启动Web应用...")
    print("应用将在浏览器中自动打开 http://localhost:8501")
    print("按 Ctrl+C 停止应用")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py'])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 