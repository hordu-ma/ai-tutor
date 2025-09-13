#!/usr/bin/env python3
import requests
import json
import sys
from pathlib import Path

def test_homework_grading():
    """全面测试作业批改API"""
    
    # 测试基本健康检查
    print("🔍 1. 测试健康检查...")
    try:
        health_response = requests.get('http://localhost:8000/health')
        print(f"   健康检查状态: {health_response.status_code}")
        print(f"   响应: {health_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        return False
    
    # 测试API文档
    print("\n🔍 2. 测试API文档...")
    try:
        docs_response = requests.get('http://localhost:8000/docs')
        print(f"   API文档状态: {docs_response.status_code}")
    except Exception as e:
        print(f"   ❌ API文档访问失败: {e}")
    
    # 测试作业批改API
    print("\n🔍 3. 测试作业批改API...")
    
    # 检查测试图片
    test_image = Path('test_math_homework.jpg')
    if not test_image.exists():
        print("   ❌ 测试图片不存在")
        return False
    
    # 发送请求
    try:
        with open(test_image, 'rb') as f:
            files = {'file': ('test_math_homework.jpg', f, 'image/jpeg')}
            data = {
                'subject': 'math',
                'provider': 'qwen'
            }
            
            print("   📤 发送批改请求...")
            response = requests.post(
                'http://localhost:8000/api/v1/homework/grade',
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"   状态码: {response.status_code}")
            print(f"   响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 请求成功!")
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                
                # 检查数据结构
                if 'data' in result:
                    data = result['data']
                    print(f"   OCR Text Length: {len(data.get('ocr_text', ''))}")
                    print(f"   Questions: {len(data.get('correction', {}).get('questions', []))}")
                    print(f"   Overall Score: {data.get('correction', {}).get('overall_score')}")
                    return True
                else:
                    print(f"   ❌ 响应中缺少data字段")
                    return False
            else:
                print(f"   ❌ 请求失败!")
                print(f"   错误响应: {response.text}")
                return False
                
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")
        return False

def test_frontend_elements():
    """测试前端相关组件"""
    print("\n🔍 4. 测试前端组件...")
    
    # 测试主页
    try:
        response = requests.get('http://localhost:8000/')
        print(f"   主页状态: {response.status_code}")
        
        # 检查关键元素
        html_content = response.text
        key_elements = [
            'homeworkForm',
            'fileUploadArea', 
            'submitBtn',
            'resultSection',
            '/static/js/main.js'
        ]
        
        missing_elements = []
        for element in key_elements:
            if element not in html_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"   ❌ 缺少关键元素: {missing_elements}")
            return False
        else:
            print("   ✅ 前端关键元素完整")
            return True
            
    except Exception as e:
        print(f"   ❌ 前端测试失败: {e}")
        return False

def test_static_resources():
    """测试静态资源"""
    print("\n🔍 5. 测试静态资源...")
    
    resources = [
        '/static/js/main.js',
        '/static/css/style.css',
    ]
    
    all_good = True
    for resource in resources:
        try:
            response = requests.get(f'http://localhost:8000{resource}')
            if response.status_code == 200:
                print(f"   ✅ {resource}: OK")
            else:
                print(f"   ❌ {resource}: {response.status_code}")
                all_good = False
        except Exception as e:
            print(f"   ❌ {resource}: 请求失败 - {e}")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🚀 开始全面测试AI Tutor系统...")
    
    success_count = 0
    total_tests = 4
    
    if test_homework_grading():
        success_count += 1
    
    if test_frontend_elements():
        success_count += 1
    
    if test_static_resources():
        success_count += 1
    
    print(f"\n📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过! 系统运行正常")
        sys.exit(0)
    else:
        print("❌ 存在问题需要修复")
        sys.exit(1)
