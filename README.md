# Web_document_crawling-file_format_conversion
Web legal document crawling and file format conversion tools


# 法律文档爬取与转换工具

一个自动化爬取香港司法机构网站法律文档并将其转换为结构化Markdown的工具。

## 功能特性

- ✅ 自动爬取香港司法机构网站的法律文档(PDF/DOCX)
- ✅ 自动将DOCX转换为PDF
- ✅ 通过MinerU API将PDF转换为结构化Markdown
- ✅ 支持多种搜索条件(案件号、当事人、判决日期等)
- ✅ 自动创建分类文件夹保存结果

## 快速开始

### 前置要求

- Python 3.8+
- Chrome浏览器
- ChromeDriver (与浏览器版本匹配)

# 提示：
### tips1.   MinerU本地化部署可以参考：https://zhuanlan.zhihu.com/p/1908942870666282723 、 https://www.bilibili.com/video/BV1zCXhYbE2p/?spm_id_from=333.337.search-card.all.click&vd_source=c414af4780348b902d1d9d8bf1ba7692。
### tips2.   本地部署后的API化需要下载MinerU官网包,克隆地址：https://github.com/opendatalab/MinerU.git  ,API化可参考上面的知乎博客（按照视频操作会有问题）。
### tips3.   本人只用了一个conda环境（MinerU）,且为了保护我的本地tourch环境，只用了CPU进行训练。本机CPU:笔记本版的i7-12400H+32G运行内存。
### tips4.   如果不需要配置本地API环境，直接在cmd(管理员模式)下运行conda环境后：

   ```bash
   cd “pdf所在文件夹”
   magic-pdf -p 要转格式的.pdf -o ./output
   
   ```

### tips5.   MinerU框架
![图片](https://github.com/user-attachments/assets/df0c33b6-8be4-4ded-b334-436f74294fea)


### 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/legal-doc-scraper.git
   cd legal-doc-scraper
   
   ```




2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 下载并配置ChromeDriver：
   - 下载地址：https://chromedriver.chromium.org/
   - 将chromedriver.exe放在项目目录或系统PATH中

### 使用方法

1. 运行主程序：
   ```bash
   python main.py


   ```

2. 按照提示选择搜索类型和输入关键词

3. 结果将保存在`downloads/[关键词]`目录下，包括：
   - 原始文档(PDF/DOCX)
   - 转换后的Markdown文件
   - API返回的JSON数据(可选)

## 项目结构

```
legal-doc-scraper/
├── downloads/              # 下载文件存储目录
   └── /                    # 文件夹名称为查询的关键词
      └── markdown_output/  # 文件转化为Md文件之后所储存的位置
├── scraper.py              # 主爬虫逻辑
├── main.py                 # 用户交互入口
├── requirements.txt        # Python依赖
├── README.md               # 项目文档
├── MinerU-master           # 从github上克隆下来的MinerU官网包、克隆地址：https://github.com/opendatalab/MinerU.git
└── examples/               # 示例输出

```

## API配置

如需使用MinerU API转换PDF，请确保：
1. MinerU服务运行在`http://localhost:8888`
2. 或修改`scraper.py`中的`mineru_api_url`变量

## 常见问题

**Q: ChromeDriver版本不匹配**
A: 请确保ChromeDriver版本与已安装的Chrome浏览器版本一致

**Q: DOCX转换PDF失败**
A: 确保已安装Microsoft Word或LibreOffice

**Q: API请求超时**
A: 增大`scraper.py`中的timeout值(CPU训练默认900秒，GPU训练时间会更短可自行设定)

## 贡献指南

欢迎提交Pull Request！请确保：
1. 代码符合PEP8规范
2. 添加适当的单元测试
3. 更新相关文档

## 许可证

MIT License
