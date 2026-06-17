#!/usr/bin/env python3
"""Test the Freelancer Tool API endpoints."""
import json
import urllib.request
import urllib.error

def test_usage():
    r = urllib.request.urlopen("http://localhost:9000/api/usage")
    data = json.loads(r.read())
    print(f"Usage: {data}")
    assert data["limit"] == 3
    print("  PASS")

def test_contract():
    body = json.dumps({
        "contract_type": "服务合同",
        "party_a": "张三",
        "party_b": "李四",
        "terms": "项目周期30天，分三期付款"
    }).encode()
    req = urllib.request.Request(
        "http://localhost:9000/api/generate-contract",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    r = urllib.request.urlopen(req, timeout=60)
    data = json.loads(r.read())
    print(f"Contract generation: success={data.get('success')}, content_len={len(data.get('content',''))}, usage={data.get('usage')}")
    assert data["success"] is True
    assert len(data["content"]) > 100
    print("  PASS")

def main():
    print("=== Testing Freelancer Tool API ===")
    test_usage()
    test_contract()
    print("=== All tests passed! ===")

if __name__ == "__main__":
    main()
