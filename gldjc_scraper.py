"""
广材网 (gldjc.com) 材料价格抓取工具
第一步：登录并保存 cookie
第二步：用 cookie 查询材料价格
"""
import os
import json
import time
from playwright.sync_api import sync_playwright

COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gldjc_cookies.json")
BASE_URL = "https://www.gldjc.com"


def login_and_save_cookies():
    """打开浏览器，手动登录广材网，成功后保存 cookie"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print("=" * 50)
        print("正在打开广材网登录页面...")
        page.goto(f"{BASE_URL}/login", wait_until="networkidle", timeout=30000)
        print("页面已加载！")
        print()
        print(">>> 请在浏览器中手动完成以下操作：")
        print("    1. 输入账号: 18039237003@mufengchun")
        print("    2. 输入密码: 1234AAAA")
        print("    3. 完成验证码（如有）")
        print("    4. 点击登录")
        print()
        print(">>> 登录成功后，按这里继续...")

        # 等待用户手动登录（最多等 5 分钟）
        try:
            # 等待登录成功后跳转或出现用户信息
            page.wait_for_function(
                """() => {
                    const user = localStorage.getItem('userInfo');
                    return user && user.includes('loginName');
                }""",
                timeout=300000
            )
        except Exception:
            # 也可能登录后重定向了，检查 URL
            pass

        # 尝试获取 localStorage 中的用户信息
        user_info = page.evaluate("() => localStorage.getItem('userInfo')")
        token = page.evaluate("() => localStorage.getItem('token') || localStorage.getItem('access_token') || ''")
        # 广材网可能用不同的 key，全部导出
        all_storage = page.evaluate("""() => {
            const items = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return items;
        }""")

        print(f"localStorage keys: {list(all_storage.keys())}")

        # 保存 cookies
        cookies = context.cookies()
        cookie_dicts = [{
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c["path"],
        } for c in cookies]

        # 保存到文件
        data = {
            "cookies": cookie_dicts,
            "localStorage": all_storage,
            "url": page.url,
        }
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Cookie 已保存到: {COOKIE_FILE}")
        print(f"   共 {len(cookie_dicts)} 个 cookie, {len(all_storage)} 个 localStorage 项")

        browser.close()


def search_material(keyword, region=""):
    """用已保存的 cookie 查询材料价格"""
    if not os.path.exists(COOKIE_FILE):
        print("❌ 未找到 cookie 文件，请先运行 login_and_save_cookies()")
        return []

    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        saved = json.load(f)

    cookies = saved["cookies"]
    storage = saved["localStorage"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()

        # 恢复 localStorage
        page.goto(BASE_URL, wait_until="domcontentloaded")
        for key, val in storage.items():
            page.evaluate(f"localStorage.setItem('{key}', '{val}')")

        # 搜索材料
        search_url = f"{BASE_URL}/scj/search?keyword={keyword}"
        if region:
            search_url += f"&area={region}"
        print(f"🔍 搜索: {keyword}")
        page.goto(search_url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(2000)  # 等 JS 加载完

        # 尝试从 Network 响应中提取价格
        # 先看看页面结构
        title = page.title()
        print(f"   页面标题: {title}")

        # 监听 API 响应来获取价格数据
        prices = []
        try:
            # 广材网价格一般在搜索结果里的 .price 或表格里
            price_elements = page.locator('[class*="price"]').all()
            for el in price_elements[:10]:
                text = el.inner_text().strip()
                if text and any(c.isdigit() for c in text):
                    prices.append(text)
                    print(f"   价格: {text}")
        except Exception as e:
            print(f"   提取失败: {e}")

        # 也尝试拦截 API 响应
        browser.close()
        return prices


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
    else:
        cmd = "login"

    if cmd == "login":
        login_and_save_cookies()

    elif cmd == "search":
        if len(sys.argv) < 3:
            print("用法: python gldjc_scraper.py search <材料名称> [地区]")
        else:
            kw = sys.argv[2]
            region = sys.argv[3] if len(sys.argv) > 3 else ""
            results = search_material(kw, region)
            if not results:
                print("未找到价格，可能需要重新登录或材料不存在")
    else:
        print("用法:")
        print("  python gldjc_scraper.py login          # 登录并保存cookie")
        print("  python gldjc_scraper.py search <材料名>  # 查询价格")
