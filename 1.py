from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 目标小说URL
start_url = 'https://www.02a418d2.cfd/#/book/1901/315.html'

# 配置Chrome选项
chrome_options = Options()
chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
chrome_options.add_argument('--no-sandbox')  # 禁用沙箱
chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

try:
    print(f'正在使用Selenium爬取小说页面: {start_url}\n')
    
    # 初始化Chrome驱动
    driver = webdriver.Chrome(options=chrome_options)
    print('Chrome驱动初始化成功！')
    
    # 打开起始页面
    driver.get(start_url)
    print('起始网页打开成功！')
    
    # 等待页面加载完成
    time.sleep(5)  # 等待5秒，让JavaScript有足够时间渲染页面
    
    # 初始化变量
    start_chapter = 30  # 从第30章开始爬取
    target_chapters = 40  # 目标爬取40章内容
    chapter_count = 0  # 已爬取章节计数器
    current_chapter = 1  # 当前页面章节号
    has_next_chapter = True
    
    # 定义可能的下一章链接定位方式（提前定义，用于跳过章节）
    next_chapter_selectors = [
        # 方式1: 通过id查找
        (By.ID, 'nextchapter'),
        # 方式2: 通过class查找
        (By.CLASS_NAME, 'next-chapter'),
        (By.CLASS_NAME, 'next'),
        (By.CLASS_NAME, 'nextChapter'),
        # 方式3: 通过文本查找
        (By.XPATH, '//a[contains(text(), "下一章")]'),
        (By.XPATH, '//a[contains(text(), "下一页")]'),
        (By.XPATH, '//a[contains(@href, "chapter") and (contains(text(), "下") or contains(@class, "next"))]')
    ]
    
    # 打开文件，准备追加写入
    with open('小说完整内容.txt', 'w', encoding='utf-8') as f:
        f.write('小说完整内容\n')
        f.write('=' * 50 + '\n\n')
    
    # 首先跳过前面的章节，直到达到开始章节
    print(f'\n准备跳过前面章节，直到第 {start_chapter} 章')
    while current_chapter < start_chapter and has_next_chapter:
        print(f'跳过第 {current_chapter} 章...')
        
        # 查找下一章链接
        next_chapter_link = None
        for selector_type, selector_value in next_chapter_selectors:
            try:
                next_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                next_href = next_element.get_attribute('href')
                if next_href and len(next_href) > 0:
                    next_chapter_link = next_href
                    break
            except Exception as e:
                continue
        
        if next_chapter_link:
            driver.get(next_chapter_link)
            time.sleep(5)
            current_chapter += 1
        else:
            print(f'\n未找到下一章链接，无法跳过到第 {start_chapter} 章')
            has_next_chapter = False
    
    # 循环爬取目标章节数
    while has_next_chapter and chapter_count < target_chapters:
        chapter_count += 1
        print(f'\n' + '=' * 50)
        print(f'开始爬取第 {current_chapter} 章')
        print('=' * 50)
        
        # 尝试获取页面标题
        page_title = driver.title
        print(f'页面标题: {page_title}')
        
        # 尝试查找小说内容
        print('\n尝试查找小说内容...')
        
        # 可能的内容元素定位方式
        content_selectors = [
            # 方式1: 通过id查找
            (By.ID, 'chaptercontent'),
            # 方式2: 通过class查找
            (By.CLASS_NAME, 'chapter-content'),
            (By.CLASS_NAME, 'content'),
            # 方式3: 通过xpath查找包含大量文本的div
            (By.XPATH, '//div[contains(@id, "content") or contains(@class, "content") or contains(@class, "chapter")]')
        ]
        
        novel_content = None
        novel_title = page_title
        
        for selector_type, selector_value in content_selectors:
            try:
                print(f'\n尝试使用选择器: {selector_type}={selector_value}')
                
                # 等待元素加载
                content_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                
                # 获取元素文本
                content_text = content_element.text.strip()
                
                # 检查文本长度，只有长度足够才认为是小说内容
                if len(content_text) > 200:
                    novel_content = content_text
                    print(f'✓ 找到小说内容！')
                    print(f'小说内容长度: {len(novel_content)} 字符')
                    break
                else:
                    print(f'✗ 找到的内容太短，可能不是小说正文')
                    
            except Exception as e:
                print(f'✗ 未找到符合条件的元素: {e}')
        
        # 如果找到了小说内容，保存到文件
        if novel_content:
            # 尝试提取更准确的标题，可能在h1标签中
            try:
                title_element = driver.find_element(By.TAG_NAME, 'h1')
                if title_element.text.strip():
                    novel_title = title_element.text.strip()
            except Exception:
                pass
            
            print(f'\n小说标题: {novel_title}')
            print('\n小说内容预览:')
            print('=' * 50)
            print(novel_content[:500] + '...')
            print('=' * 50)
            
            # 保存小说内容到文件，追加模式
            with open('小说完整内容.txt', 'a', encoding='utf-8') as f:
                f.write(novel_title + '\n\n')
                f.write(novel_content)
                f.write('\n\n')
                f.write('=' * 50 + '\n\n')
            print(f'\n✓ 第 {chapter_count} 章已追加到 "小说完整内容.txt" 文件')
        else:
            print('\n✗ 未找到小说内容')
            break
        
        # 查找下一章链接
        print('\n尝试查找下一章链接...')
        
        next_chapter_link = None
        
        for selector_type, selector_value in next_chapter_selectors:
            try:
                print(f'\n尝试使用选择器: {selector_type}={selector_value}')
                
                # 等待元素加载
                next_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                
                # 获取链接
                next_href = next_element.get_attribute('href')
                if next_href and len(next_href) > 0:
                    next_chapter_link = next_href
                    print(f'✓ 找到下一章链接: {next_chapter_link}')
                    break
                else:
                    print(f'✗ 找到的链接为空')
                    
            except Exception as e:
                print(f'✗ 未找到符合条件的下一章元素: {e}')
        
        # 如果找到了下一章链接，点击跳转到下一章
        if next_chapter_link:
            print('\n跳转到下一章...')
            driver.get(next_chapter_link)
            time.sleep(5)  # 等待页面加载
            current_chapter += 1  # 更新当前章节号
        else:
            # 尝试通过JavaScript事件获取下一章
            print('\n尝试通过JavaScript事件获取下一章...')
            try:
                # 执行JavaScript查找下一章按钮并点击
                driver.execute_script("document.querySelector('.next-chapter').click();")
                time.sleep(5)  # 等待页面加载
                
                # 检查URL是否变化
                if driver.current_url != next_chapter_link:
                    print(f'✓ 通过JavaScript跳转到下一章，新URL: {driver.current_url}')
                    current_chapter += 1  # 更新当前章节号
                else:
                    print(f'✗ JavaScript跳转失败，URL未变化')
                    has_next_chapter = False
            except Exception as e:
                print(f'✗ JavaScript跳转失败: {e}')
                has_next_chapter = False
        
        # 检查是否还有下一章
        if not next_chapter_link:
            print('\n✗ 未找到下一章链接，爬取结束')
            has_next_chapter = False
    
    # 关闭浏览器
    driver.quit()
    print('\n' + '=' * 50)
    print(f'爬取完成！')
    print(f'从第 {start_chapter} 章开始，共成功爬取 {chapter_count} 章内容')
    print(f'爬取范围：第 {start_chapter} 章 - 第 {current_chapter - 1} 章')
    print('小说完整内容已保存到 "小说完整内容.txt" 文件')
    print('=' * 50)
    
except Exception as e:
    print(f'\n爬取过程中发生错误: {e}')
    import traceback
    traceback.print_exc()
    # 关闭浏览器
    try:
        driver.quit()
    except:
        pass
