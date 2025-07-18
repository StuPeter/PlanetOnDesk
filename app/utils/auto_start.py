import subprocess
import logging
import sys
import os

# --- 操作系统检测 ---
# 明确判断当前运行的操作系统
IS_WINDOWS = sys.platform.startswith('win')
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')  # 适用于大部分基于Linux的桌面环境，如Ubuntu (GNOME), Fedora, Deepin等

logger = logging.getLogger(__name__)

# --- 导入特定平台的模块（如果可用） ---
if IS_WINDOWS:
    try:
        import winreg  # 用于注册表操作
        import winshell  # 用于创建和删除Windows快捷方式
    except ImportError:
        logger.warning("警告：未找到 'winreg' 或 'winshell' 模块。Windows 上的自启动功能可能受限。")
        IS_WINDOWS = False  # 如果导入失败，则认为Windows功能不可用
elif IS_MACOS:
    # macOS 主要依赖 subprocess 执行 'launchctl' 命令和处理 .plist 文件
    pass
elif IS_LINUX:
    # Linux 主要依赖 subprocess 执行命令和处理 .desktop 文件
    pass


class StartupManager:
    """
    管理应用程序在 Windows、macOS 和 Linux (基于XDG标准，如GNOME、KDE) 上的开机自启动功能。
    """

    def __init__(self, app_name: str, app_path: str):
        """
        初始化自启动管理器。

        :param app_name: 应用程序的名称 (例如："PlanetOnDesktop")。
        :param app_path: 应用程序可执行文件的绝对路径。
        """
        self.app_name = app_name
        # 确保应用路径是绝对路径，这对于跨平台非常重要
        self.app_path = os.path.abspath(app_path)

        if not os.path.exists(self.app_path):
            logger.error(f"错误：应用程序可执行文件未找到，路径：{self.app_path}")
            raise FileNotFoundError(f"应用程序可执行文件未找到：{self.app_path}")

        logger.info(f"StartupManager 已初始化。应用名称：'{self.app_name}'，路径：'{self.app_path}'")

    def enable_auto_start(self) -> bool:
        """
        根据当前操作系统启用应用程序的开机自启动。
        """
        logger.info(f"尝试为应用程序 '{self.app_name}' 启用开机自启。")
        if IS_WINDOWS:
            return self._enable_windows_startup()
        elif IS_MACOS:
            return self._enable_macos_startup()
        elif IS_LINUX:
            return self._enable_linux_startup()
        else:
            logger.error("错误：当前操作系统不支持开机自启动功能。")
            print("错误", "不支持的操作系统。")
            return False

    def disable_auto_start(self) -> bool:
        """
        根据当前操作系统禁用应用程序的开机自启动。
        """
        logger.info(f"尝试为应用程序 '{self.app_name}' 禁用开机自启。")
        if IS_WINDOWS:
            return self._disable_windows_startup()
        elif IS_MACOS:
            return self._disable_macos_startup()
        elif IS_LINUX:
            return self._disable_linux_startup()
        else:
            logger.error("错误：当前操作系统不支持开机自启动功能。")
            print("错误", "不支持的操作系统。")
            return False

    def check_auto_start_status(self) -> bool:
        """
        检查应用程序的开机自启动状态。
        """
        logger.info(f"检查应用程序 '{self.app_name}' 的自启动状态。")
        if IS_WINDOWS:
            return self._check_windows_startup_status()
        elif IS_MACOS:
            return self._check_macos_startup_status()
        elif IS_LINUX:
            return self._check_linux_startup_status()
        else:
            logger.warning("警告：当前操作系统不支持检查自启动状态。")
            return False

    # --- Windows 专用方法 ---
    def _get_windows_startup_shortcut_path(self) -> str:
        """获取 Windows 自启动文件夹中快捷方式的完整路径。"""
        # APPDATA 环境变量指向用户AppData\Roaming目录
        startup_dir = os.path.join(
            os.environ.get("APPDATA"),
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
        )
        # 确保自启动目录存在
        os.makedirs(startup_dir, exist_ok=True)
        return os.path.join(startup_dir, f"{self.app_name}.lnk")

    def _enable_windows_startup(self) -> bool:
        """通过创建快捷方式启用 Windows 上的开机自启动。"""
        if not IS_WINDOWS: return False  # 确保只在Windows上运行

        shortcut_path = self._get_windows_startup_shortcut_path()
        try:
            # winshell 库简化了快捷方式的创建
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = self.app_path
                shortcut.working_directory = os.path.dirname(self.app_path)
                shortcut.description = f"{self.app_name} 应用程序自启动快捷方式"
            logger.info(f"成功：Windows 快捷方式已创建于 '{shortcut_path}'。")
            print("成功", "已启用开机自启 (Windows)！")
            return True
        except Exception as e:
            logger.error(f"错误：创建 Windows 自启动快捷方式失败：{e}")
            print("错误", f"启用失败 (Windows)：{str(e)}")
            return False

    def _disable_windows_startup(self) -> bool:
        """通过删除快捷方式禁用 Windows 上的开机自启动。"""
        if not IS_WINDOWS: return False  # 确保只在Windows上运行

        shortcut_path = self._get_windows_startup_shortcut_path()
        try:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                logger.info(f"成功：Windows 自启动快捷方式已删除：'{shortcut_path}'。")
                print("成功", "已禁用开机自启 (Windows)！")
                return True
            else:
                logger.warning(f"警告：Windows 自启动快捷方式不存在：'{shortcut_path}'。")
                print("错误", "未找到自启动项 (Windows)。")
                return False
        except Exception as e:
            logger.error(f"错误：删除 Windows 自启动快捷方式失败：{e}")
            print("错误", f"禁用失败 (Windows)：{str(e)}")
            return False

    def _check_windows_startup_status(self) -> bool:
        """检查 Windows 自启动状态 (通过检查快捷方式是否存在)。"""
        if not IS_WINDOWS: return False
        return os.path.exists(self._get_windows_startup_shortcut_path())

    # --- macOS 专用方法 ---
    def _get_macos_launch_agent_path(self) -> str:
        """获取 macOS Launch Agent .plist 文件的完整路径。"""
        # Launch Agents 位于用户Library/LaunchAgents目录
        launch_agents_dir = os.path.join(os.path.expanduser("~"), "Library", "LaunchAgents")
        os.makedirs(launch_agents_dir, exist_ok=True)
        # .plist 文件名通常使用反向域名格式，例如 com.yourcompany.appname.plist
        return os.path.join(launch_agents_dir, f"com.{self.app_name.lower()}.plist")

    def _generate_macos_plist_content(self) -> str:
        """生成 macOS Launch Agent .plist 文件的 XML 内容。"""
        # ProgramArguments 必须是可执行文件的完整路径
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.{self.app_name.lower()}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{self.app_path}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
                <key>KeepAlive</key>
                <false/>
                </dict>
            </plist>"""
        return plist_content

    def _enable_macos_startup(self) -> bool:
        """通过创建并加载 Launch Agent .plist 文件启用 macOS 上的开机自启动。"""
        if not IS_MACOS: return False  # 确保只在macOS上运行

        plist_path = self._get_macos_launch_agent_path()
        try:
            with open(plist_path, "w") as f:
                f.write(self._generate_macos_plist_content())

            # 使用 launchctl 命令加载 Launch Agent，使其立即生效并注册为自启动
            # -w 参数用于将配置文件写入到磁盘，确保重启后也有效
            subprocess.run(["launchctl", "load", "-w", plist_path], check=True, capture_output=True)
            logger.info(f"成功：macOS Launch Agent 已创建并加载于 '{plist_path}'。")
            print("成功", "已启用开机自启 (macOS)！")
            return True
        except subprocess.CalledProcessError as e:
            # 捕获 launchctl 错误输出
            logger.error(f"错误：加载 macOS Launch Agent 失败：{e.stderr.decode().strip()}")
            print("错误", f"启用失败 (macOS)：{str(e.stderr.decode().strip())}")
            return False
        except Exception as e:
            logger.error(f"错误：创建或加载 macOS Launch Agent 失败：{e}")
            print("错误", f"启用失败 (macOS)：{str(e)}")
            return False

    def _disable_macos_startup(self) -> bool:
        """通过卸载并删除 Launch Agent .plist 文件禁用 macOS 上的开机自启动。"""
        if not IS_MACOS: return False  # 确保只在macOS上运行

        plist_path = self._get_macos_launch_agent_path()
        try:
            if os.path.exists(plist_path):
                # 先卸载 Launch Agent
                subprocess.run(["launchctl", "unload", "-w", plist_path], check=True, capture_output=True)
                os.remove(plist_path)
                logger.info(f"成功：macOS Launch Agent 已卸载并删除：'{plist_path}'。")
                print("成功", "已禁用开机自启 (macOS)！")
                return True
            else:
                logger.warning(f"警告：macOS Launch Agent 文件不存在：'{plist_path}'。")
                print("错误", "未找到自启动项 (macOS)。")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"错误：卸载 macOS Launch Agent 失败：{e.stderr.decode().strip()}")
            print("错误", f"禁用失败 (macOS)：{str(e.stderr.decode().strip())}")
            return False
        except Exception as e:
            logger.error(f"错误：删除 macOS Launch Agent 失败：{e}")
            print("错误", f"禁用失败 (macOS)：{str(e)}")
            return False

    def _check_macos_startup_status(self) -> bool:
        """检查 macOS 自启动状态 (通过检查 .plist 文件是否存在)。"""
        if not IS_MACOS: return False
        return os.path.exists(self._get_macos_launch_agent_path())

    # --- Linux 专用方法 (适用于基于 XDG Desktop Entry Standard 的桌面环境，如 GNOME, KDE, XFCE) ---
    def _get_linux_autostart_desktop_file_path(self) -> str:
        """获取 Linux .desktop 自启动文件的完整路径。"""
        # XDG 规范的自启动目录
        autostart_dir = os.path.join(os.path.expanduser("~"), ".config", "autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        return os.path.join(autostart_dir, f"{self.app_name}.desktop")

    def _generate_linux_desktop_file_content(self) -> str:
        """生成 Linux .desktop 自启动文件的内容。"""
        # .desktop 文件是一个INI风格的文件，用于描述应用程序
        desktop_content = f"""[Desktop Entry]
            Type=Application
            Exec={self.app_path}
            Hidden=false
            NoDisplay=false
            X-GNOME-Autostart-enabled=true
            Name={self.app_name}
            Comment=在登录时启动 {self.app_name}
            """
        return desktop_content

    def _enable_linux_startup(self) -> bool:
        """通过创建 .desktop 文件启用 Linux 上的开机自启动。"""
        if not IS_LINUX: return False  # 确保只在Linux上运行

        desktop_file_path = self._get_linux_autostart_desktop_file_path()
        try:
            with open(desktop_file_path, "w") as f:
                f.write(self._generate_linux_desktop_file_content())

            # 通常不需要手动设置为可执行，但为了兼容性可以加上
            # os.chmod(desktop_file_path, 0o755)

            logger.info(f"成功：Linux .desktop 文件已创建于 '{desktop_file_path}'。")
            print("成功", "已启用开机自启 (Linux)！")
            return True
        except Exception as e:
            logger.error(f"错误：创建 Linux .desktop 文件失败：{e}")
            print("错误", f"启用失败 (Linux)：{str(e)}")
            return False

    def _disable_linux_startup(self) -> bool:
        """通过删除 .desktop 文件禁用 Linux 上的开机自启动。"""
        if not IS_LINUX: return False  # 确保只在Linux上运行

        desktop_file_path = self._get_linux_autostart_desktop_file_path()
        try:
            if os.path.exists(desktop_file_path):
                os.remove(desktop_file_path)
                logger.info(f"成功：Linux .desktop 文件已删除：'{desktop_file_path}'。")
                print("成功", "已禁用开机自启 (Linux)！")
                return True
            else:
                logger.warning(f"警告：Linux .desktop 文件不存在：'{desktop_file_path}'。")
                print("错误", "未找到自启动项 (Linux)。")
                return False
        except Exception as e:
            logger.error(f"错误：删除 Linux .desktop 文件失败：{e}")
            print("错误", f"禁用失败 (Linux)：{str(e)}")
            return False

    def _check_linux_startup_status(self) -> bool:
        """检查 Linux 自启动状态 (通过检查 .desktop 文件是否存在)。"""
        if not IS_LINUX: return False
        return os.path.exists(self._get_linux_autostart_desktop_file_path())


if __name__ == '__main__':
    # --- 请根据你的实际应用和操作系统修改以下路径 ---
    APP_NAME = "PlanetOnDesktop"  # 你的应用程序名称

    # 示例：根据当前操作系统设置应用路径
    # 如果你的应用是打包后的可执行文件，请将其替换为实际的打包路径
    if IS_WINDOWS:
        # 假设在Windows上，你的应用被打包成 .exe
        # 请替换为你的实际 .exe 路径
        APP_PATH = r"C:\YourAppPath\PlanetOnDesktop.exe"
        # 或者如果你直接运行Python脚本，可以使用：APP_PATH = sys.executable + " D:\\path\\to\\your_script.py"
    elif IS_MACOS:
        # 假设在macOS上，你的应用是 .app bundle
        # 请替换为你的实际 .app/Contents/MacOS/Executable 路径
        APP_PATH = os.path.join(os.path.expanduser("~"), "Applications", "PlanetOnDesktop.app", "Contents", "MacOS",
                                "PlanetOnDesktop")
        # 或者如果你直接运行Python脚本，可以使用：APP_PATH = sys.executable
        # 如果是Python脚本，LaunchAgent的ProgramArguments需要是 ['/usr/bin/python3', '/path/to/your_script.py']
        # 对于打包的.app，只需指向其内部的Unix可执行文件
    elif IS_LINUX:
        # 假设在Linux上，你的应用是放在某个bin目录下的可执行文件
        # 请替换为你的实际可执行文件路径
        APP_PATH = os.path.join(os.path.expanduser("~"), ".local", "bin", "PlanetOnDesktop")
        # 或者如果你直接运行Python脚本，可以使用：APP_PATH = sys.executable + " /path/to/your_script.py"
    else:
        # 默认回退到当前脚本的解释器路径，但不推荐用于生产环境
        APP_PATH = sys.executable
        logger.warning("当前操作系统未知，APP_PATH 默认设置为 Python 解释器路径。请手动修改为您的应用程序路径。")

    try:
        # 实例化自启动管理器
        startup_manager = StartupManager(APP_NAME, APP_PATH)

        # --- 示例操作 ---
        # 1. 检查当前自启动状态
        status = startup_manager.check_auto_start_status()
        print(f"当前自启动状态：{'已启用' if status else '未启用'}")

        # 2. 启用开机自启（取消注释来测试）
        # logger.info("测试：正在尝试启用开机自启...")
        # success_enable = startup_manager.enable_auto_start()
        # print(f"启用操作结果：{'成功' if success_enable else '失败'}")

        # 3. 禁用开机自启（取消注释来测试）
        logger.info("测试：正在尝试禁用开机自启...")
        success_disable = startup_manager.disable_auto_start()
        print(f"禁用操作结果：{'成功' if success_disable else '失败'}")

        # 4. 再次检查操作后的状态
        status_after_op = startup_manager.check_auto_start_status()
        print(f"操作后自启动状态：{'已启用' if status_after_op else '未启用'}")

    except FileNotFoundError as e:
        print(f"致命错误：应用程序路径配置不正确，请检查 APP_PATH。详情：{e}")
    except Exception as e:
        print(f"程序执行过程中发生未预期错误：{e}")
        logger.critical(f"程序执行异常终止：{e}", exc_info=True)
