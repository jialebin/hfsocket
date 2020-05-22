setting = dict(
    template_path="templates",  # 设置模板路径
    static_path="statics",  # 设置静态文件路径
    xscf_cookies=True,  # 开启scf
    login_url="/login",  # 重定向到登录页面
pycket={
        "engine": "redis",  # 配置存储类型
        "storage": {
            "host": "localhost",
            "port": 6379,
            "db_sessions": 5,
            "db_notifications": 11,
            "max_connections": 2 ** 31
        },
        "cookies": {
            "expires_days": 30,
            "max_age": 60 * 60 * 5  # 一小时无操作过期
        }
    },
    cookie_secret="aaa",  # 对cookie进行签名的字符串
)

# 注册数据表
INSTALLED_MODELS = [
    'models.chat_log',
]
