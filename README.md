# ✍ Freelancer Tool - AI 自由职业者工具

一款基于 AI 的自由职业者辅助工具，支持 **AI 合同生成** 和 **AI 报价单生成**，帮助自由职业者告别繁琐的文书工作。

## 功能

- **📄 AI 合同生成** — 输入合同类型、签约方和条款，AI 自动生成专业的中文合同文本。支持服务合同、劳务合同、合作协议等多种类型。
- **💰 AI 报价生成** — 描述你的服务内容和报价金额，AI 自动生成正式、美观的报价单。
- **⚡ 即时生成** — 基于 DeepSeek AI 大模型，几十秒内即可生成高质量文档。
- **🔌 RESTful API** — 提供完整的 API 接口，方便集成到你的工作流中。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 DeepSeek API Key
export DEEPSEEK_API_KEY="your-api-key"

# 启动服务
python main.py

# 打开浏览器访问
open http://localhost:8000
```

## 技术栈

- **后端**: Python / FastAPI
- **AI**: DeepSeek API
- **前端**: 原生 HTML / CSS (无框架)
- **部署**: 支持 Windows / Linux / Docker

## 项目结构

```
freelancer-tool/
├── main.py              # FastAPI 应用入口
├── tunnel.py            # 内网穿透支持
├── deploy_windows.bat   # Windows 一键部署
├── test_api.py          # API 测试
├── static/              # 前端静态文件
│   ├── index.html       # 主页
│   ├── style.css        # 样式
│   ├── contract.html    # 合同生成页
│   └── quote.html       # 报价生成页
└── README.md            # 本文件
```

## License

MIT

---

## 支持我们 🙏

如果你觉得这个工具有帮助，欢迎通过以下方式支持我们的创作：

- **🛍️ Gumroad 商店**: [evestudio.gumroad.com/l/agent-skills-pack](https://evestudio.gumroad.com/l/agent-skills-pack)
  — AI Agent Skills 精选包：50 个精选 Hermes Agent 技能 + 一键安装脚本，$29

- **📰 小报童专栏**: [xiaobot.net/p/solo-money](https://xiaobot.net/p/solo-money)
  — 独立开发者 / 一人企业赚钱实战指南（即将上线）

你的支持是我们持续更新的最大动力！❤️
