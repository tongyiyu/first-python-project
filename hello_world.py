# ========================================
# 文件: hello_world.py
# 日期: 2024-02-07
# 描述: 我的第一个 Python 程序
# ========================================

def greet(name):
    """
    生成欢迎消息
    :param name: 用户名
    :return: 欢迎字符串
    """
    return f"🌟 Hello, {name}! Welcome to Python programming. 🌟"

if __name__ == "__main__":
    # 主程序入口
    user_name = "AI Learner"
    message = greet(user_name)
    print(message)
    print(f"\n✅ 程序执行成功！当前时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")