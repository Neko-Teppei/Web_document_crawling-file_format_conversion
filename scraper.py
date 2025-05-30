from nibabel.brikhead import filepath
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import time
import requests
import os
import re
# import fitz  # PyMuPDF
# import mammoth  # For docx to markdown
from io import BytesIO
from docx2pdf import convert


os.environ['NO_PROXY'] = '*'

SEARCH_OPTIONS = {
    "this phrase": "3",
    "these words in any order": "2",
    "any of these words": "1",
    "Parties of Judgment": "7",
    "Coram of Judgment": "6",
    "Neutral Citation Number of Judgment": "10",
    "Case Number of Judgment": "4",
    "Representation": "8",
    "Date of Judgment": "5",
    "Offence": "9",
    "Reported Citation": "12"
}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制


def convert_all_docx_to_pdf(folder):
    for file in os.listdir(folder):
        if file.lower().endswith(".docx"):
            docx_path = os.path.join(folder, file)
            pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
            if not os.path.exists(pdf_path):
                try:
                    convert(docx_path, pdf_path)
                    print(f"📄 已转换为PDF: {pdf_path}")
                except Exception as e:
                    print(f"⚠️ 转换失败 {file}: {e}")

# 文件类型判断
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'docx']


# PDF -> Markdown（文本、图表、图片用文本代替）
# def convert_pdf_to_markdown(file_stream):
#     text = ""
#     try:
#         doc = fitz.open(stream=file_stream.read(), filetype="pdf")
#         for page in doc:
#             text += page.get_text("text") + "\n\n"
#         text = text.replace("\n", "  \n")  # Markdown换行
#     except Exception as e:
#         raise ValueError(f"PDF解析失败: {str(e)}")
#     return text


# DOCX -> Markdown（文本内容）
# def convert_docx_to_markdown(file_stream):
#     try:
#         result = mammoth.convert_to_markdown(file_stream)
#         return result.value
#     except Exception as e:
#         raise ValueError(f"DOCX解析失败: {str(e)}")


# REST API endpoint
@app.route('/api/parse-X', methods=['POST'])
def parse_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        file_stream = BytesIO(file.read())
        file_ext = file.filename.rsplit('.', 1)[1].lower()

        if file_ext == 'pdf':
            markdown = convert_pdf_to_markdown(file_stream)
        elif file_ext == 'docx':
            file_stream.seek(0)  # 重置指针
            markdown = convert_docx_to_markdown(file_stream)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        return jsonify({"markdown": markdown})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_scraper(search_type_text, search_value):
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # 开启浏览器自动化界面（调试用）
    driver = webdriver.Chrome(options=chrome_options)

    print("\U0001F50D 打开搜索页面...")
    try:
        driver.get(
            "https://legalref.judiciary.hk/lrs/common/search/search_result.jsp?stem=1&txtselectopt=1&selDatabase=JU&selDatabase=RV&selDatabase=RS&selDatabase=PD&selall=1&isadvsearch=1&selallct=1")

        # 处理选择框
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "selBoolean"))
        )
        Select(select_element).select_by_value(SEARCH_OPTIONS[search_type_text])

        # 输入搜索词
        input_element = driver.find_element(By.NAME, "txtSearch")
        input_element.clear()
        input_element.send_keys(search_value)

        # 点击搜索按钮
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "GO!")]'))
        ).click()

        # 等待结果加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-caseno"))
        )

        # 创建下载目录
        safe_search_value = re.sub(r'[\\/*?:"<>|]', '_', search_value)
        folder_name = os.path.join("downloads", safe_search_value)
        os.makedirs(folder_name, exist_ok=True)

        # 处理搜索结果
        case_links = driver.find_elements(By.CLASS_NAME, "result-caseno")
        for idx, link in enumerate(case_links, 1):
            try:
                print(f"\n--- 处理第 {idx}/{len(case_links)} 篇 ---")
                link.click()

                # 切换到内容frame
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.NAME, "topFrame"))
                )

                # 查找下载链接
                try:
                    # 优先查找Word链接
                    download_link = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[contains(., "Word")]'))
                    )
                    file_type = "Word"
                except:
                    # 如果没有Word链接，查找PDF链接
                    download_link = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[contains(., "PDF")]'))
                    )
                    file_type = "PDF"

                file_url = download_link.get_attribute("href")
                print(f"找到 {file_type} 文件: {file_url}")

                # 下载文件
                headers = {
                    "User-Agent": "Mozilla/5.0",
                    "Referer": driver.current_url
                }
                response = requests.get(file_url, headers=headers, timeout=30)

                if response.status_code != 200:
                    raise ValueError(f"下载失败: HTTP {response.status_code}")

                # 保存文件
                file_ext = "docx" if "Word" in file_type else "pdf"
                # filename = f"case_{idx}.{file_ext}"
                # 🔍 提取 URL 中最后一段文件名（不带 query 参数）
                filename = file_url.split("/")[-1].split("?")[0]

                filepath = os.path.join(folder_name, filename)

                with open(filepath, "wb") as f:
                    f.write(response.content)
                print(f"✅ 保存成功: {filepath}")

            except Exception as e:
                print(f"❌ 第 {idx} 篇失败: {str(e)}")
            finally:
                # 返回结果页
                driver.switch_to.default_content()
                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "result-caseno"))
                )

    except Exception as e:
        print(f"❌ 主流程错误: {str(e)}")
    finally:
        # ⬅️ 下载完成后，自动转 docx -> pdf
        convert_all_docx_to_pdf(folder_name)

        # ⬅️ 然后将 pdf 批量发送给 MinerU API 转 Markdown
        batch_convert_pdf_with_mineru(folder_name, mineru_api_url="http://localhost:8888/file_parse")

        driver.quit()

def batch_convert_pdf_with_mineru(folder, mineru_api_url="http://localhost:8888/file_parse"):
    output_dir = os.path.join(folder, "markdown_output")
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(folder):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder, file)
            with open(pdf_path, "rb") as f:
                try:
                    print(f"\n--- 正在处理: {file} ---")
                    response = requests.post(
                        mineru_api_url,

                        files={"file": (file, f, "application/pdf")},

                        data={
                            "is_json_md_dump": "true",  # ✅ 要生成 markdown
                            "parse_method": "auto",  # ✅ 推荐添加
                            "return_images": "true",  # ✅ 图像提取
                            "return_layout": "true",  # ✅ layout.pdf
                            "return_info": "true",  # ✅ info
                            "return_content_list": "true",  # ✅ JSON 内容结构
                            "output_dir": output_dir,  # ✅ 可选，让它存在你指定的目录
                        },
                        timeout=900
                    )
                    if response.ok:
                        result = response.json()
                        md_text = result.get("md_content", "")
                        md_filename = os.path.splitext(file)[0] + ".md"
                        md_path = os.path.join(output_dir, md_filename)

                        with open(md_path, "w", encoding="utf-8") as out_f:
                            # out_f.write(response.json().get("markdown", ""))
                            out_f.write(md_text)

                        print(f"✅ 生成 Markdown: {md_path}")
                        print(f"✅ API 响应状态码: {response.status_code}")
                        print(f"📄 返回内容预览: {md_text[:200]}..." if md_text else "📭 内容为空")
                        # print(f"📄 返回内容: {response.text[:300]}...")  # 避免打印太长

                    else:
                        print(f"❌ MinerU API 错误 ({response.status_code})：{file}")
                        print(f"🔴 错误内容: {response.text[:300]}")

                except Exception as e:
                    print(f"⚠️ MinerU 请求失败: {file} -> {e}")



if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("temp_uploads", exist_ok=True)

    # 启动Flask应用
    app.run(host='0.0.0.0', port=3000, debug=True)