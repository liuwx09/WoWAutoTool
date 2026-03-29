# GitHub Actions 自动编译指南

由于 macOS 无法直接编译 Windows exe，请按照以下步骤使用 GitHub Actions 自动编译：

## 步骤 1: 创建 GitHub 账号

访问 https://github.com 注册账号

## 步骤 2: 创建新仓库

1. 点击右上角 "+" → "New repository"
2. Repository name: `WoWAutoTool`
3. 选择 Private（私有）
4. 点击 "Create repository"

## 步骤 3: 上传代码

在新仓库页面：
1. 点击 "uploading an existing file"
2. 将 `WoWAutoTool` 文件夹里的**所有内容**拖拽上传
3. 点击 "Commit changes"

## 步骤 4: 运行编译

1. 点击仓库上方的 "Actions" 标签
2. 点击左侧 "Build Windows Executable"
3. 点击右侧 "Run workflow" → 绿色按钮
4. 等待 5-10 分钟编译完成

## 步骤 5: 下载 exe

1. 编译完成后，点击 "Build Windows Executable"
2. 点击顶部的 artifact "WoWAutoTool-Windows"
3. 下载 zip 文件

## 步骤 6: 使用

解压后，运行 `WoWAutoTool.exe`

---

## 完整流程图

```
1. GitHub 注册
       ↓
2. 创建仓库 WoWAutoTool
       ↓
3. 上传代码（拖拽文件）
       ↓
4. Actions → Build Windows Executable → Run workflow
       ↓
5. 等待 5-10 分钟编译
       ↓
6. 下载 artifact: WoWAutoTool-Windows
       ↓
7. 解压 → 运行 WoWAutoTool.exe
```

---

## 注意事项

- GitHub Actions 每月有免费额度（2000分钟）
- 编译大约需要 5-10 分钟
- 下载的 artifact 有效期 7 天

---

如果遇到问题，随时问我！
