#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import sys

def fetch_canvas_api_docs():
    """获取 Canvas API 关于 quiz questions 的文档"""

    url = "https://canvas.instructure.com/doc/api/quiz_questions.html"

    try:
        print(f"正在获取 Canvas API 文档: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找关于 list quiz questions 的信息
        print("\n" + "="*60)
        print("查找 List questions in a quiz 相关信息")
        print("="*60)

        # 查找所有的方法定义
        methods = soup.find_all('div', class_='method')

        for method in methods:
            # 查找方法标题
            title = method.find('h3')
            if title and 'list' in title.text.lower() and 'question' in title.text.lower():
                print(f"\n📋 找到方法: {title.text.strip()}")

                # 查找HTTP方法和URL
                url_info = method.find('div', class_='method_details')
                if url_info:
                    print(f"详情: {url_info.text.strip()}")

                # 查找权限信息
                auth_info = method.find('div', class_='auth')
                if auth_info:
                    print(f"🔐 权限要求: {auth_info.text.strip()}")

                # 查找描述
                description = method.find('div', class_='description')
                if description:
                    print(f"📝 描述: {description.text.strip()}")

                # 查找参数
                params = method.find('div', class_='params')
                if params:
                    print(f"📊 参数: {params.text.strip()}")

                print("-" * 40)

        # 如果没找到特定方法，尝试查找所有相关内容
        if not any('list' in method.text.lower() and 'question' in method.text.lower() for method in methods):
            print("\n没有找到 list questions 方法，查找所有相关内容...")

            # 查找包含 "question" 的所有内容
            all_text = soup.get_text()
            lines = all_text.split('\n')

            relevant_lines = []
            for i, line in enumerate(lines):
                if 'question' in line.lower() and ('list' in line.lower() or 'get' in line.lower() or 'permission' in line.lower()):
                    # 获取上下文
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    context = '\n'.join(lines[start:end])
                    relevant_lines.append(context)

            for context in relevant_lines[:5]:  # 只显示前5个相关结果
                print(f"\n相关内容:\n{context}")
                print("-" * 40)

        # 查找权限相关的通用信息
        print("\n" + "="*60)
        print("查找权限相关的通用信息")
        print("="*60)

        auth_sections = soup.find_all(['div', 'p', 'section'], string=lambda text: text and 'permission' in text.lower())

        for section in auth_sections[:3]:  # 只显示前3个
            print(f"\n权限信息: {section.text.strip()}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False

def check_quiz_questions_endpoint():
    """检查 quiz questions 端点的具体信息"""

    print("\n" + "="*60)
    print("Canvas Quiz Questions API 分析")
    print("="*60)

    print("\n🔍 根据常见的 Canvas API 模式分析:")

    print("\n1. 端点: GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions")
    print("   - 这是获取测验题目列表的标准端点")

    print("\n2. 可能的权限要求:")
    print("   - 学生: 可能只能在测验开始后查看题目")
    print("   - 教师: 可以随时查看和编辑题目")
    print("   - 管理员: 完全访问权限")

    print("\n3. 常见的 401 错误原因:")
    print("   - Token 无效或过期")
    print("   - 用户没有访问该课程的权限")
    print("   - 用户没有查看测验题目的权限")
    print("   - 测验未发布或不可访问")

    print("\n4. 可能的解决方案:")
    print("   - 使用有效的管理员或教师token")
    print("   - 确保用户已注册到课程")
    print("   - 确保测验已发布")
    print("   - 检查 Canvas 实例的权限设置")

if __name__ == "__main__":
    print("Canvas Quiz Questions API 权限分析工具")
    print("="*60)

    # 尝试获取在线文档
    success = fetch_canvas_api_docs()

    # 无论是否成功，都提供基于经验的分析
    check_quiz_questions_endpoint()

    print("\n" + "="*60)
    print("分析完成")
    print("="*60)