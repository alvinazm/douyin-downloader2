"""
端到端验证：缺本地配置时，FastAPI app 仍能成功构建并对外暴露主要 endpoint。

使用 fastapi.testclient.TestClient 直接驱动 ASGI，不需要监听端口（沙箱里禁止
bind）。覆盖以下不变量：
1. /openapi.json 200（路由完整）
2. 主要爬虫路由的 path 都出现在 openapi 中（说明 import 链全通）
3. 任何一条 warning 都不能升级为未捕获异常
"""
import importlib
import os
import pathlib
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
IGNORED_LOCAL_CONFIGS = [
    REPO_ROOT / "crawlers" / "tiktok" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "tiktok" / "app" / "config.yaml",
    REPO_ROOT / "crawlers" / "douyin" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "bilibili" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "instagram" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "youtube" / "web" / "config.yaml",
]

EXPECTED_PATHS = [
    "/api/tiktok/web/fetch_one_video",
    "/api/tiktok/app/fetch_one_video",
    "/api/douyin/web/fetch_one_video",
    "/api/bilibili/web/fetch_one_video",
    "/api/hybrid/video_data",
    "/api/ios/shortcut",
    "/api/config/config",
    "/api/log/parser",
]


class AppEndpointsLoaded(unittest.TestCase):
    def setUp(self):
        self._backup = {}
        for p in IGNORED_LOCAL_CONFIGS:
            if p.exists():
                self._backup[p] = p.read_bytes()
                p.unlink()

    def tearDown(self):
        for p, content in self._backup.items():
            p.write_bytes(content)

    def test_app_openapi_lists_main_endpoints(self):
        # 必须在缺本地配置时也能 import 整个 vue_main
        os.environ["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")
        import app.vue_main as vm  # noqa: F401

        from fastapi.testclient import TestClient

        client = TestClient(vm.app)
        resp = client.get("/openapi.json")
        self.assertEqual(resp.status_code, 200, msg=resp.text)
        spec = resp.json()
        paths = set(spec.get("paths", {}).keys())
        for expected in EXPECTED_PATHS:
            self.assertIn(expected, paths, f"missing endpoint: {expected}")

        # 前端首页可访问
        home = client.get("/")
        self.assertIn(home.status_code, (200, 304), msg=home.text[:200])


if __name__ == "__main__":
    unittest.main()
