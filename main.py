import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotAdapter
import config

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(OnebotAdapter)

# 加载内置插件
nonebot.load_builtin_plugins("echo")

# 无条件加载核心插件
nonebot.load_plugins("kernel")

# 按照插件列表加载可选插件
for model in config.modules:
    nonebot.load_plugin("plugins." + model)

if __name__ == "__main__":
    nonebot.run()