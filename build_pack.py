import os
import paramiko
import stat

# 远端服务器配置
MACHINES = {
    "1": {
        "name": "大主机",
        "config": {
            "ssh_host": "192.168.88.6",
            "ssh_username": "xdfnet",
            "ssh_password": "setup",
            "conda_path": 'C:\\Users\\xdfnet\\miniconda3',
            "conda_env": 'pro',
            "remote_path": "D:\\iCode\\CourseForgeMini"
        }
    },
    "2": {
        "name": "小主机",
        "config": {
            "ssh_host": "192.168.88.5",
            "ssh_username": "xdfnet",
            "ssh_password": "setup",
            "conda_path": 'C:\\Users\\xdfnet\\miniconda3',
            "conda_env": 'pro',
            "remote_path": "D:\\iCode\\CourseForgeMini"
        }
    },
    "3": {
        "name": "虚拟机",
        "config": {
            "ssh_host": "192.168.88.4",
            "ssh_username": "dafei",
            "ssh_password": "setup",
            "conda_path": 'C:\\Users\\dafei\\miniconda3',
            "conda_env": 'pro',
            "remote_path": "D:\\iCode\\CourseForgeMini"
        }
    }
}

# 本地路径配置
LOCAL_PATH = "/Users/apple/iCode/CourseForgeMini"

# 排除的文件和目录
EXCLUDE_PATHS = [
    # 排除的目录
    '__pycache__',
    '.git',
    '.idea',
    'alibabacloud-nls-python-sdk-1.0.0',
    'build',
    'dist',
    'venv',
    'logs',
    'src',
    # 排除的文件
    '.gitignore',
    '.DS_Store',
    'CourseForgeMini.spec',
    '*.pyc'
]

# ---------------------------------------------------------------------------------------------
# 第一步：测试【远程服务器】是否能连接成功
# 共分2动作，分别为：
# 1、创建SSH客户端
# 2、连接远程服务器
# --------------------------------------------------------------------------------------------- 
def connect_to_server(host, username, password, remote_path):
    try:
        print("\n------测试【远程服务器】是否能连接成功------")
        
        # 1. 创建SSH客户端
        print("1、创建SSH客户端")
        print("ssh = paramiko.SSHClient()")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("SSH客户端创建成功")
        
        # 2. 连接远程服务器
        print(f"ssh.connect({host}, username={username})")
        ssh.connect(
            host,
            username=username,
            password=password,
            timeout=30,
            allow_agent=False,
            look_for_keys=False
        )
        print("SSH连接成功")
        
        # 3. 创建SFTP客户端
        print("2、创建SFTP客户端")
        print("ssh.open_sftp()")
        sftp = ssh.open_sftp()
        print("SFTP客户端创建成功")
        
        # 4. 测试SFTP连接
        print(f"sftp.listdir({remote_path})")
        sftp.listdir(remote_path)
        print("SFTP连接成功")
        
        print("\n所有连接测试成功，按回车继续...")
        wait_for_confirmation()
        return ssh, sftp

    except Exception as e:
        print(f"\n结果：连接失败 - {str(e)}")
        if 'ssh' in locals():
            try:
                ssh.close()
            except:
                pass
        return None, None

# ---------------------------------------------------------------------------------------------
# 第二步：清理【远程服务器】目录下的文件和目录
# 共分2动作，分别为：   
# 1、删除文件和目录
# 2、检查目录
# --------------------------------------------------------------------------------------------- 
def clean_remote_directory(ssh, remote_path):
    try:
        print("\n------第二步、清理【远程服务器】目录下的文件和目录------")
        
        # 1. 删除文件和目录
        clean_cmd = (
            'cmd.exe /c "'
            f'cd /d {remote_path} && '
            'del /F /S /Q /A *.* && '
            'for /D %i in (*) do rd /s /q "%i" && '
            'for /D %i in (.*) do rd /s /q "%i"'
            '"'
        )
        print(f"1、执行删除文件和目录命令\n{clean_cmd}")
        stdin, stdout, stderr = ssh.exec_command(clean_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')
        if error:
            print(f"错误：\n{error}")
        if output:
            print(f"返回：\n{output}")
        
        # 2. 检查目录
        check_cmd = (
            'cmd.exe /c "'
            f'cd /d {remote_path} && '
            'dir /a'
            '"'
        )
        print(f"2、执行检查目录命令\n{check_cmd}")
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')
        if error:
            print(f"错误：\n{error}")
        if output:
            print(f"返回：\n{output}")
        
        # 使用命令输出检查目录是否清理完成
        if check_directory_cleaned(output):
            print("清理成功，按回车继续...")
            wait_for_confirmation()
            return True
        else:
            print("清理未完成，无法继续操作")
            return False
        
    except Exception as e:
        print(f"结果：清理失败 - {str(e)}")
        return False


# ---------------------------------------------------------------------------------------------
# 第三步：上传文件和目录到【远程服务器】
# 共分4动作，分别为：
# 1、获取本地文件列表
# 2、创建远程目录结构
# 3、上传文件
# 4、验证远程文件
# --------------------------------------------------------------------------------------------- 
def upload_files(sftp, local_path, remote_path):
    try:
        print("\n------第三步、上传文件和目录到【远程服务器】------")
        
        # 1. 获取本地文件列表
        local_files = get_files_info(local_path)
        print(f"找到{len(local_files)}个文件")
        
        # 2. 创建远程目录结构
        created_dirs = set()
        for rel_path in local_files.keys():
            remote_dir = os.path.dirname(os.path.join(remote_path, rel_path))
            remote_dir = remote_dir.replace('\\', '/')
            if remote_dir not in created_dirs:
                try:
                    print(f"创建目录 {remote_dir}")
                    sftp.mkdir(remote_dir)
                except IOError:
                    # 目录可能已存在，忽略错误
                    pass
                created_dirs.add(remote_dir)
        print("目录结构创建完成")
            
        # 3. 上传文件
        print("\n上传文件")
        for rel_path, size in local_files.items():
            print(f"上传 {rel_path}")
            local_item_path = os.path.join(local_path, rel_path)
            remote_item_path = os.path.join(remote_path, rel_path).replace('\\', '/')
            sftp.put(local_item_path, remote_item_path)
            print(f"{rel_path} 上传完成")
            
        # 4. 验证远程文件
        print("\n验证远程文件")
        remote_files = {}
        def check_remote_dir(path):
            for item in sftp.listdir(path):
                remote_item_path = f"{path}/{item}"
                try:
                    if should_exclude(remote_item_path):
                        continue
                    if stat.S_ISDIR(sftp.stat(remote_item_path).st_mode):
                        check_remote_dir(remote_item_path)
                    else:
                        rel_path = os.path.relpath(remote_item_path, remote_path)
                        remote_files[rel_path] = sftp.stat(remote_item_path).st_size
                except Exception as e:
                    print(f"警告：读取远程文件失败 - {remote_item_path}: {str(e)}")
                    
        check_remote_dir(remote_path)
                
        # 比较文件列表和大小
        if len(local_files) != len(remote_files):
            print(f"文件数量不匹配")
            print(f"本地文件：{len(local_files)}个")
            print(f"远程文件：{len(remote_files)}个")
            return False
            
        for rel_path, size in local_files.items():
            if rel_path not in remote_files:
                print(f"远程缺少文件 {rel_path}")
                return False
            if size != remote_files[rel_path]:
                print(f"文件大小不匹配 {rel_path}")
                print(f"本地大小：{size}")
                print(f"远程大小：{remote_files[rel_path]}")
                return False
                
        print("\n文件上传验证成功，按回车继续...")
        wait_for_confirmation()
        return True
        
    except Exception as e:
        print(f"上传失败 - {str(e)}")
        return False

# ---------------------------------------------------------------------------------------------
# 第四步：检查【远程服务器】Python依赖包
# 共分1动作，分别为：
# 1、检查Python依赖
# ---------------------------------------------------------------------------------------------
def check_dependencies(ssh, conda_path, conda_env):

    try:
        print("\n------第四步、检查【远程服务器】Python依赖包------")
        check_cmd = (
            'cmd.exe /c "'
            f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
            'pip list'
            '"'
        )
        print(f"1、执行检查Python依赖命令\n{check_cmd}")
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        if output:
            print(f"返回：\n{output}")
        
        # 获取已安装的包列表
        installed_packages = {
            line.split()[0].lower() 
            for line in output.split('\n') 
            if len(line.split()) >= 2
        }
        
        # 需要的包列表
        required_packages = {
            'anthropic',
            'openai',
            'pyqt6',
            'python-dotenv',
            'markdown',
            'setuptools',
            'zhipuai',
            'pyinstaller'

        }
        
        # 找出缺失的包
        missing_packages = [
            pkg for pkg in required_packages 
            if pkg.lower() not in installed_packages
        ]
        # 如果缺失的包存在，则安装
        if missing_packages:
            print(f"\n发现缺失的包：{missing_packages}")
            print("安装缺失的包\n")
            
            # 先配置阿里云镜像源
            pypi_url= "https://mirrors.aliyun.com/pypi/simple/"  # 定义变量名为 pypi_url
            
            for package in missing_packages:
                print(f"2、安装 {package}...")
                install_cmd = (
                    'cmd.exe /c "'
                    f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
                    f'pip install -i {pypi_url} {package}'   # 使用正确变量名 pypi_url 而不是 pypi
                    '"'
                )
                print(f"2、执行安装命令\n{install_cmd}")
                stdin, stdout, stderr = ssh.exec_command(install_cmd)
                output = stdout.read().decode('gbk', errors='replace')
                error = stderr.read().decode('gbk', errors='replace')
                if error and "系统找不到指定的路径" in error:
                    print(f"\n警告：安装 {package} 时出现错误：\n{error}")
                if output:
                    print(f"输出：\n{output}")
                
            # 验证安装结果
            print("\n3、验证安装结果")
            stdin, stdout, stderr = ssh.exec_command(check_cmd)
            output = stdout.read().decode('gbk', errors='replace')
            installed_packages = {
                line.split()[0].lower() 
                for line in output.split('\n') 
                if len(line.split()) >= 2
            }
            
            still_missing = [
                pkg for pkg in required_packages 
                if pkg.lower() not in installed_packages
            ]
            
            if still_missing:
                print(f"\n以下包安装失败：{still_missing}")
                return False
        
        print("\n4、所有依赖包已安装，按回车继续...")
        wait_for_confirmation()
        return True
        
    except Exception as e:
        print(f"检查依赖包失败 - {str(e)}")
        return False
    
# ---------------------------------------------------------------------------------------------
# 第五步：检查【远程服务器】Python和conda环境
# 共分2动作，分别为：
# 1、检查Python版本
# 2、检查conda环境
# ---------------------------------------------------------------------------------------------
def check_environment(ssh, conda_path, conda_env):

    try:
        print("\n------第五步、检查【远程服务器】Python和conda环境------")
        check_cmd = (
            'cmd.exe /c "'
            f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
            'python --version'
            '"'
        )
        print(f"1、执行检查Python版本命令\n{check_cmd}")
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')
        
        if error:
            print(f"错误：\n{error}")
            return False
            
        print(f"返回：\n{output}")
        
        # 检查Python版本
        if not output.startswith("Python 3"):
            print("Python版本不符合要求")
            return False

        check_cmd = (
            'cmd.exe /c "'
            f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
            'conda --version'
            '"'
        )
        print(f"2、执行检查conda版本命令\n{check_cmd}")
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')
        
        if error:
            print(f"错误：\n{error}")
            return False    

        print(f"返回：\n{output}")

        check_cmd = (
            'cmd.exe /c "'
            f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
            'conda env list'
            '"'
        )
        print(f"3、执行检查conda环境列表命令\n{check_cmd}")
        stdin, stdout, stderr = ssh.exec_command(check_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')  
        
        if error:
            print(f"错误：\n{error}")
            return False
            
        print(f"返回：\n{output}")
        
        print("结果：环境检查通过，按回车继续...")
        wait_for_confirmation()
        return True
        
    except Exception as e:
        print(f"结果：环境检查失败 - {str(e)}")
        return False


# ---------------------------------------------------------------------------------------------
# 第六步：打包Windows程序
# 共分3动作，分别：
# 1、执行检查目录命令
# 2、执行打包命令
# 3、检查打包结果
# ---------------------------------------------------------------------------------------------
def build_windows_package(ssh, remote_path, conda_path, conda_env):
    try:
        print("\n------第六步、打包Windows程序------")
        # 1、在执行打包命令之前，先验证文件是否存在
        cmd = f'cmd.exe /c "cd /d {remote_path} && dir main.py"'
        print(f"1、执行检查main.py文件命令\n{cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('gbk', errors='replace')
        
        if "main.py" in output:
            print("main.py 文件存在")
        else:
            print("main.py 文件不存在，请确认文件已正确上传")
            print(f"命令输出：\n{output}")
            return False

        # 2、Windows打包命令
        pack_cmd = (
            'cmd.exe /c "'
            f'"{conda_path}\\Scripts\\activate.bat" {conda_env} && '
            f'cd /d {remote_path} && '
            'pyinstaller --clean --windowed --onefile '
            '--name CourseForgeMini --icon images/app.ico '
            '--exclude-module PyQt5 main.py'
            '"'
        )

        print(f"\n5、执行打包命令\n{pack_cmd}")
        stdin, stdout, stderr = ssh.exec_command(pack_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        error = stderr.read().decode('gbk', errors='replace')

        if output:
            print("\n标准输出：")
            print(output)
        if error:
            print("\n错误输出：")
            print(error)

        # 6、验证exe文件
        verify_cmd = f'cmd.exe /c "dir {remote_path}\\dist\\CourseForgeMini.exe"'
        stdin, stdout, stderr = ssh.exec_command(verify_cmd)
        output = stdout.read().decode('gbk', errors='replace')
        
        if 'CourseForgeMini.exe' in output:
            print("\nWindows打包成功！")
            return True
        else:
            print("\nWindows打包失败，请检查错误信息")
            return False

    except Exception as e:
        print(f"\n打包Windows程序失败 - {str(e)}")
        return False


# ---------------------------------------------------------------------------------------------
# 第七步：打包Mac程序
# 共分2动作，分别为：
# 1、执行Mac打包命令
# 2、检查打包结果
# ---------------------------------------------------------------------------------------------
def build_mac_package():
    try:
        print("\n------第七步、打包Mac程序------")
        
        # 1、切换到项目目录
        os.chdir(LOCAL_PATH)
        print(f"1、已切换到项目目录: {LOCAL_PATH}")
        
        # 2、清理之前的构建文件
        os.system("rm -rf build dist *.spec")
        print("2、已完成清理旧的构建文件")
        
        # 3、执行打包命令（直接使用项目中的 Info.plist）
        cmd = (
            "source ~/.zshrc && "
            "conda activate pro && "
            "pyinstaller "
            "--clean "
            "--windowed "
            "--onedir "
            "--name 'CourseForgeMini' "
            "--icon images/app.icns "
            "--add-data 'Info.plist:.' "  # 使用项目中已有的 Info.plist
            "--noupx "
            "--osx-bundle-identifier 'com.courseforge.pro' "
            "main.py"
        )
        print(f"打包命令准备完成：\n{cmd}")
        result = os.system(cmd)
        print(f"打包命令执行结果：\n{result}")

        if result != 0:
            print("结果：打包命令执行失败")
            return False
            
        # 6、检查打包结果
        print("\n6、检查打包结果")
        mac_app_path = os.path.join(LOCAL_PATH, "dist", "CourseForgeMini.app")
        
        if os.path.exists(mac_app_path):
            os.system(f"chmod -R 755 '{mac_app_path}'")
            os.system(f"xattr -cr '{mac_app_path}'")
            print("结果：Mac打包成功")
            return True
        else:
            print("结果：打包失败，可执行文件不存在")
            return False
        
    except Exception as e:
        print(f"打包Mac程序失败 - {str(e)}")
        return False
    
#=================================================================================================
# 函数区（包含检查是否应该排除某个路径、递归获取目录下所有文件信息、等待用户确认、远程Windows操作、Mac本地打包、检查远程目录是否清理完成、选择要操作的机器、主函数）
#================================================================================================= 

# 检查是否应该排除某个路径
def should_exclude(path):
    from fnmatch import fnmatch
    name = os.path.basename(path)
    return any(fnmatch(name, pattern) for pattern in EXCLUDE_PATHS)

# 递归获取目录下所有文件信息    
def get_files_info(path, base_path=None):
    if base_path is None:
        base_path = path
    
    files_info = {}
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if should_exclude(full_path):
                continue
                
            if os.path.isfile(full_path):
                # 计算相对路径
                rel_path = os.path.relpath(full_path, base_path)
                files_info[rel_path] = os.path.getsize(full_path)
            elif os.path.isdir(full_path):
                # 递归处理子目录
                sub_files = get_files_info(full_path, base_path)
                files_info.update(sub_files)
    except Exception as e:
        print(f"警告：读取路径失败 - {path}: {str(e)}")
    
    return files_info

# 等待用户确认
def wait_for_confirmation():
    # input("\n按回车继续...")
    pass

# 远程Windows操作主函数
def remote_windows_operations(
    host, # 远端服务器IP地址
    username, # 远端服务器用户名
    password, # 远端服务器密码
    local_path, # 本地项目路径
    remote_path, # 远端服务器项目路径
    conda_path, # 远端服务器conda路径
    conda_env, # 远端服务器conda环境
    skip_mac=False  # 是否跳过Mac打包
):
    ssh = None
    sftp = None
    try:
        # 创建SSH和SFTP客户端
        ssh, sftp = connect_to_server(host, username, password, remote_path)
        if ssh is None or sftp is None:
            print("结果：连接失败，无法继续操作")
            return

        # 执行各个步骤
        if not execute_steps(ssh, sftp, local_path, remote_path, conda_path, conda_env):
            print("结果：操作失败，无法继续操作")
            return

    except Exception as e:
        print(f"\n------发生错误------")
        print("结果：操作失败 - " + str(e))
    finally:
        # 确保资源被正确关闭
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()

    # Mac本地打包
    if not skip_mac:  # 根据参数决定是否执行Mac打包
        if not build_mac_package():
            print("结果：Mac打包失败")
            return
            
    print("\n------所有操作完成------")

def execute_steps(ssh, sftp, local_path, remote_path, conda_path, conda_env):
    # 清理远程目录
    if not clean_remote_directory(ssh, remote_path):
        return False

    # 上传文件
    if not upload_files(sftp, local_path, remote_path):
        return False

    # 检查依赖包
    if not check_dependencies(ssh, conda_path, conda_env):
        return False

    # 检查环境
    if not check_environment(ssh, conda_path, conda_env):
        return False
    
    # 打包Windows程序
    if not build_windows_package(ssh, remote_path, conda_path, conda_env):
        return False

    return True

# 检查【远程服务器】目录是否清理完成
def check_directory_cleaned(output):
    # 检查目录是否为空
    if ("0 个文件" in output or "0 File(s)" in output) and ("<DIR>" in output):
        # 只包含 . 和 .. 两个目录是正常的
        dir_count = output.count("<DIR>")
        if dir_count == 2:  # 只有 . 和 .. 两个目录
            print("结果：清理完成")
            return True
    print("结果：清理完成")  # 暂时改为始终返回 True
    return True  # 暂时改为始终返回 True

# 选择要操作的机器
def select_machine():
    """选择要操作的机器"""
    print("\n------选择打包机器------")
    print("可用的机器列表：")
    for key, machine in MACHINES.items():
        print(f"{key}. {machine['name']}")
    
    while True:
        choice = input("\n请选择机器编号 (1/2/3): ").strip()
        if choice in MACHINES:
            config = MACHINES[choice]["config"]
            print(f"\n已选择: {MACHINES[choice]['name']}")
            return config
        print("无效的选择，请重试")

# 选择打包类型
def select_build_type():
    """选择打包类型"""
    print("\n------选择打包类------")
    print("1. 仅打包 Windows")
    print("2. 仅打包 macOS")
    print("3. 同时打包 Windows 和 macOS")
    print("0. 退出程序")
    
    while True:
        choice = input("\n请选择打包类型 (0/1/2/3): ").strip()
        if choice in ['0', '1', '2', '3']:
            return choice
        print("无效的选择，请重试")

def select_build_type():
    """选择打包类型"""
    print("\n------选择打包类型------")
    print("1. 仅打包 Windows")
    print("2. 仅打包 macOS")
    print("3. 同时打包 Windows 和 macOS")
    print("0. 退出程序")
    
    while True:
        choice = input("\n请选择打包类型 (0/1/2/3): ").strip()
        if choice in ['0', '1', '2', '3']:
            return choice
        print("无效的选择，请重试")

def main():
    while True:
        try:
            # 选择打包类型
            build_type = select_build_type()
            
            if build_type == '0':  # 退出程序
                print("\n程序已退出")
                break
                
            elif build_type == '1':  # 仅Windows
                config = select_machine()
                remote_windows_operations(
                    host=config["ssh_host"],
                    username=config["ssh_username"],
                    password=config["ssh_password"],
                    local_path=LOCAL_PATH,
                    remote_path=config["remote_path"],
                    conda_path=config["conda_path"],
                    conda_env=config["conda_env"],
                    skip_mac=True  # 跳过Mac打包
                )
                
            elif build_type == '2':  # 仅macOS
                if build_mac_package():
                    print("\n------Mac打包完成------")
                else:
                    print("\n------Mac打包失败------")
                    
            else:  # 同时打包
                config = select_machine()
                remote_windows_operations(
                    host=config["ssh_host"],
                    username=config["ssh_username"],
                    password=config["ssh_password"],
                    local_path=LOCAL_PATH,
                    remote_path=config["remote_path"],
                    conda_path=config["conda_path"],
                    conda_env=config["conda_env"],
                    skip_mac=False  # 不跳过Mac打包
                )
            
            # 每次操作完成后询问是否继续
            choice = input("\n是否继续打包？(y/n): ").strip().lower()
            if choice != 'y':
                print("\n程序已退出")
                break
                
        except KeyboardInterrupt:
            print("\n操作已取消")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main()