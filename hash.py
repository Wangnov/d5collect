from werkzeug.security import generate_password_hash
import getpass

def create_password_hash():
    """安全地生成密码的哈希值"""
    try:
        # 使用 getpass 可以在输入密码时不显示字符，更加安全
        password = getpass.getpass("请输入您要设置的新密码: ")
        password_confirm = getpass.getpass("请再次输入以确认: ")

        if password != password_confirm:
            print("\n[错误] 两次输入的密码不一致，请重新运行脚本。")
            return

        if not password:
            print("\n[错误] 密码不能为空。")
            return

        # 生成密码哈希
        password_hash = generate_password_hash(password)

        print("\n" + "="*50)
        print("密码哈希已成功生成！")
        print("请将下面的哈希值完整地复制到 app/config.py 文件中：")
        print("\n" + password_hash)
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n生成哈希时出错: {e}")

if __name__ == '__main__':
    create_password_hash()