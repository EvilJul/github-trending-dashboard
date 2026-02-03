#!/usr/bin/env python3
"""
GitHub Trending 项目完整测试脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    print("   ✅ 健康检查通过")
    return True

def test_get_projects():
    """测试获取项目列表"""
    print("🔍 测试获取项目列表...")
    r = requests.get(f"{BASE_URL}/api/projects/")  # 注意尾部斜杠
    if r.status_code != 200:
        raise Exception(f"状态码错误: {r.status_code}, 内容: {r.text[:200]}")
    try:
        data = r.json()
    except Exception as e:
        raise Exception(f"JSON解析错误: {e}, 内容: {r.text[:200]}")
    if "projects" not in data:
        raise Exception(f"返回数据格式错误: {data}")
    print(f"   ✅ 获取到 {data.get('total_count', len(data['projects']))} 个项目")
    print(f"   ✅ 最后更新: {data['last_updated'][:19]}")
    return data

def test_refresh_projects():
    """测试刷新项目数据"""
    print("🔍 测试刷新项目数据...")
    r = requests.post(f"{BASE_URL}/api/projects/refresh")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] == True
    assert "projects_count" in data
    print(f"   ✅ 刷新成功，获取 {data['projects_count']} 个新项目")
    return data

def test_get_history():
    """测试获取历史记录"""
    print("🔍 测试获取历史记录...")
    r = requests.get(f"{BASE_URL}/api/history/")  # 注意尾部斜杠
    if r.status_code != 200:
        raise Exception(f"状态码错误: {r.status_code}, 内容: {r.text[:200]}")
    try:
        data = r.json()
    except Exception as e:
        raise Exception(f"JSON解析错误: {e}, 内容: {r.text[:200]}")
    if "history" not in data:
        raise Exception(f"返回数据格式错误: {data}")
    print(f"   ✅ 获取到 {len(data['history'])} 条历史记录")
    return data

def test_get_stats():
    """测试获取统计信息"""
    print("🔍 测试获取统计信息...")
    r = requests.get(f"{BASE_URL}/api/projects/stats/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_projects" in data
    print(f"   ✅ 项目总数: {data['total_projects']}")
    print(f"   ✅ 总 Stars: {data['total_stars']}")
    return data

def test_frontend():
    """测试前端页面"""
    print("🔍 测试前端页面...")
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200
    assert "text/html" in r.headers.get("Content-Type", "")
    assert "dashboard.js" in r.text
    print("   ✅ 主页面正常加载")
    
    r = requests.get(f"{BASE_URL}/history.html")
    assert r.status_code == 200
    print("   ✅ 历史页面正常加载")
    return True

def main():
    print("=" * 50)
    print("🚀 GitHub Trending API 完整测试")
    print("=" * 50)
    print()
    
    tests = [
        ("健康检查", test_health),
        ("获取项目", test_get_projects),
        ("刷新数据", test_refresh_projects),
        ("获取历史", test_get_history),
        ("获取统计", test_get_stats),
        ("前端页面", test_frontend),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, result))
        except Exception as e:
            print(f"   ❌ {name} 失败: {e}")
            results.append((name, False, str(e)))
        print()
    
    print("=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    passed = 0
    for name, success, _ in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {status} - {name}")
        if success:
            passed += 1
    
    print()
    print(f"总计: {passed}/{len(results)} 项测试通过")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
