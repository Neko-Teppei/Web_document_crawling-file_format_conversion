from scraper import run_scraper, SEARCH_OPTIONS

def main():
    print("📘 请选择搜索条件：")
    options = list(SEARCH_OPTIONS.keys())
    for idx, opt in enumerate(options):
        print(f"{idx + 1}. {opt}")
    idx = int(input("输入对应数字: ")) - 1
    if idx < 0 or idx >= len(options):
        print("❌ 无效选项")
        return

    search_type = options[idx]
    search_text = input(f"🔎 输入用于 [{search_type}] 的关键词: ").strip()

    run_scraper(search_type, search_text)

#sound global ltd.

if __name__ == "__main__":
    main()

