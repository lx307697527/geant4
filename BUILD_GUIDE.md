# Geant4 静态编译 & 分发指南

## 前提

- Windows 10/11
- Visual Studio Build Tools 2022（或 Visual Studio 2022）已安装
  - 必须勾选 **"使用 C++ 的桌面开发"** 工作负载
- 需要约 **10 GB** 磁盘空间（编译 + 数据文件）
- 网络连接（CMake 会自动下载 Geant4 数据文件 ~1.5 GB）

## 编译步骤

### 1. 打开正确的命令行

在开始菜单搜索 **"x64 Native Tools Command Prompt for VS 2022"**，打开它。

> ⚠️ 必须用这个命令行，普通 PowerShell/cmd 找不到 MSVC 编译器。

### 2. 进入项目目录

```cmd
cd /d D:\Code_Space\geant4-cli
```

### 3. 运行一键编译脚本

```cmd
build_geant4.bat
```

脚本会自动完成：
1. CMake 配置（静态编译）
2. Release 编译（约 20-40 分钟）
3. 安装到 `install/` 目录
4. 编译示例程序
5. 打包到 `geant4-portable/` 目录

### 4. 如果脚本出错，手动执行

```cmd
:: 配置
cmake -S . -B build ^
  -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_INSTALL_PREFIX=%cd%\install ^
  -DBUILD_SHARED_LIBS=OFF ^
  -DGEANT4_BUILD_EXAMPLES=ON ^
  -DGEANT4_USE_OPENGL_WIN32=ON ^
  -DGEANT4_INSTALL_DATA=ON

:: 编译
cmake --build build --config Release

:: 安装
cmake --build build --config Release --target install

:: 编译示例
cmake -S examples -B examples\build ^
  -G "Visual Studio 17 2022" -A x64 ^
  -DCMAKE_PREFIX_PATH=%cd%\install
cmake --build examples\build --config Release
```

## 打包分发给朋友

编译完成后，`geant4-portable/` 目录就是要分发的全部内容：

```
geant4-portable/
├── bin/
│   ├── exampleB1.exe      ← 自包含，无需 DLL
│   ├── exampleB2a.exe
│   └── ...
├── data/                   ← 物理数据文件 (~1.5 GB)
│   ├── G4EMLOW8.5/
│   ├── G4NDL4.7/
│   └── ...
├── setup_env.bat           ← 一键设置环境变量
└── README.txt
```

### 给朋友的使用步骤

1. 把 `geant4-portable/` 文件夹拷贝到朋友的电脑（任意位置）
2. 朋友打开 PowerShell，设置环境变量：

```powershell
# 替换为实际路径
[Environment]::SetEnvironmentVariable("GEANT4_EXECUTABLE", "D:\geant4-portable\bin\exampleB1.exe", "User")
[Environment]::SetEnvironmentVariable("G4DATA", "D:\geant4-portable\data", "User")
```

3. 安装 CLI 工具：

```powershell
pip install cli-anything-geant4
```

4. 验证：

```powershell
cli-anything-geant4 --json check
# 应该输出: {"installed": true, ...}
```

5. 开始使用：

```powershell
cli-anything-geant4 --json session new --name sim -o sim.json
cli-anything-geant4 -s sim.json source set -p gamma -e 6 --energy-unit MeV
cli-anything-geant4 -s sim.json run set -n 1000
cli-anything-geant4 -s sim.json macro generate -o run.mac
cli-anything-geant4 exec --macro run.mac
```

## 注意事项

| 事项 | 说明 |
|------|------|
| 静态编译 | `BUILD_SHARED_LIBS=OFF` 使 exe 自包含，无需 DLL |
| 数据文件 | `geant4-portable/data/` 约 1.5 GB，不可省略 |
| 只能用已有示例 | macro 控制粒子源/物理，但几何体由 C++ 硬编码在 exe 中 |
| 64 位 | 编译为 x64，不支持 32 位系统 |
| MSVC 运行时 | 朋友需要 [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)（通常已有） |
