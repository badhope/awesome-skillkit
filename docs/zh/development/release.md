# 发布流程

AI-SKILL 遵循 [语义化版本](https://semver.org/lang/zh-CN/)。
发布由维护者从 `main` 分支切出。

## 何时发布

- **Major** —— REST API、SDK 公共接口或数据模型的不兼容变更，会
  强制自托管者执行迁移
- **Minor** —— 新功能、新端点、新 SDK 方法
- **Patch** —— 缺陷修复、依赖升级、文档修复

拿不定主意时，按 minor 发布。

## 发布前清单

1. `main` 分支上 **所有 CI 全绿**
2. **CHANGELOG.md** 已更新 —— Unreleased 部分已移入带日期的标题下
3. 代码库 **没有未处理的安全公告**
4. **Docker 镜像** 已构建并推送（CI 在打 tag 时执行）

## 执行发布

```bash
# 1. 切到 main，拉到最新，工作区干净
git checkout main
git pull --ff-only
git status   # 应当显示 "nothing to commit, working tree clean"

# 2. 在相关文件中更新版本号
#    （使用 `make bump-version` 助手，或手工编辑）
make bump-version VERSION=1.2.0

# 3. 更新 CHANGELOG.md
$EDITOR CHANGELOG.md
#    将 "Unreleased" 下的条目移到带今天日期的标题下，
#    并在文件末尾追加版本对比链接。

# 4. 提交并打 tag
git add -A
git commit -m "chore(release): bump to 1.2.0"
git tag -s -a 1.2.0 -m "Release 1.2.0"
git push origin main
git push origin 1.2.0
```

## 推送 tag 时的 CI

推送 tag 会触发 `deploy.yml`，它将：

1. 运行完整测试套件
2. 构建 Docker 镜像（backend、frontend）
3. 将其推送至 GitHub Container Registry，并打上以下 tag：
   - `latest`
   - 该 tag 的名称
   - 短 SHA
4. 基于该 tag 创建一个 **draft** GitHub Release
5. 在配置后，将 Python SDK 的 wheel + sdist 上传到包注册中心

随后维护者：

1. 审阅 draft Release 说明
2. 按需编辑
3. 发布 Release

## 紧急修复（Hotfix）

对于生产环境的严重 Bug：

```bash
# 1. 从发布 tag 拉出分支
git checkout -b hotfix/critical-bug 1.2.0

# 2. 修复并提交
$EDITOR …
git commit -m "fix(backend): address the critical bug"

# 3. 升级 patch 版本
make bump-version VERSION=1.2.1

# 4. 打 tag 并推送
git tag -s -a 1.2.1 -m "Hotfix 1.2.1"
git push origin hotfix/critical-bug
git push origin 1.2.1

# 5. 合并回 main
git checkout main
git merge --no-ff hotfix/critical-bug
git push origin main
```

## 预发布

对于 RC 或 beta：

```bash
git tag -s -a 1.3.0-rc.1 -m "Release candidate"
git push origin 1.3.0-rc.1
```

CI 工作流会同时给镜像打上 `1.3.0-rc.1` 与 `next` 两个 tag，
beta 测试者可拉取同一 tag。

## 弃用策略

- 在某个 minor 版本标记为 deprecated 的功能，必须在至少下一个
  minor 版本中继续可用。
- 弃用警告附带 `Sunset` 头，标明移除日期。
- 移除动作只能发生在某个 major 版本中。

## 接下来去哪里

- [路线图](../community/roadmap.md) —— 已规划内容
- [更新日志](../community/changelog.md) —— 已发布内容
- [部署](../deployment.md) —— 将构建产物推进到生产
