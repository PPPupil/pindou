# 拼豆图生成器

一个将普通图片转换成固定尺寸拼豆网格的 Python 桌面应用原型。

## 当前功能

- 导入 JPG、PNG 等常见图片
- 输入成品的横向、纵向豆数
- 使用 `mard_221_approx_from_chart.json` 中的 221 个色号匹配图片颜色
- 显示拼豆网格和各颜色用量
- 导出 PNG 拼豆示意图
- 保存、读取作品数据的基础服务

221 色数据来自图片色卡近似提取，适合原型开发，不代表实物豆的标准测色结果。H1 被标记为透明色，会显示在色板中，但不会参与普通图片的自动颜色匹配。若 221 色文件不存在，程序会回退到 `default.json` 演示色板。

## 环境与启动

推荐使用 Python 3.12。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## 运行测试

```powershell
python -m pytest
```

## 项目结构

- `app/ui`：桌面界面与网格绘制
- `app/core`：图片处理、颜色匹配和作品模型
- `app/services`：色板读取、导出和工程存储
- `app/resources/palettes`：可扩展的 JSON 色板
- `tests`：核心功能测试

