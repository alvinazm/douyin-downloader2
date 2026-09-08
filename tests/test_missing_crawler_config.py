"""
回归测试：保证缺失爬虫本地配置（crawlers/*/web/config.yaml，被 .gitignore 忽略）
时 FastAPI 应用仍可正常 import，并在运行时给出明确警告。

背景：这些本地 config.yaml 用于保存每个平台的 Cookie / msToken / ttwid / 代理等
敏感凭据，正常情况下不会进入仓库。修复前 `crawlers/tiktok/web/utils.py` 在
import 阶段就 `open(f"{path}/config.yaml")`，文件一缺失就导致整个
`uvicorn app.vue_main:app` 启动失败。

本测试只覆盖「应用可 import + 关键兜底值存在」两个不变量；
真实爬虫功能仍需要用户提供本地 config.yaml 才能工作（由运行期 TokenManager
返回空 dict / None 来体现）。
"""

import importlib
import os
import subprocess
import sys
import unittest
from pathlib import Path

# 仓库根目录 = 本文件父目录的父目录
REPO_ROOT = Path(__file__).resolve().parent.parent
# 五个会被 .gitignore 忽略的本地配置文件
IGNORED_LOCAL_CONFIGS = [
    REPO_ROOT / "crawlers" / "tiktok" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "tiktok" / "app" / "config.yaml",
    REPO_ROOT / "crawlers" / "douyin" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "bilibili" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "instagram" / "web" / "config.yaml",
    REPO_ROOT / "crawlers" / "youtube" / "web" / "config.yaml",
]


class MissingConfigRobustness(unittest.TestCase):
    """缺本地配置时应用必须能 import，且 TokenManager 给空兜底。"""

    def setUp(self):
        # 确保仓库内没有遗留的本地 config（仓库默认没有，但 worker 目录可能残留）
        self._backup: dict[Path, bytes] = {}
        for p in IGNORED_LOCAL_CONFIGS:
            if p.exists():
                self._backup[p] = p.read_bytes()
                p.unlink()

    def tearDown(self):
        for p, content in self._backup.items():
            p.write_bytes(content)

    def test_tiktok_utils_import_without_config(self):
        """即便没有 crawlers/tiktok/web/config.yaml，TikTok 工具仍可 import。"""
        from crawlers.tiktok.web import utils as tiktok_utils

        self.assertIsInstance(tiktok_utils.TokenManager.proxies, dict)
        self.assertIn("http://", tiktok_utils.TokenManager.proxies)
        self.assertIn("https://", tiktok_utils.TokenManager.proxies)
        # msToken / ttwid / odin_tt 节点为空字典，后续调用会进入降级分支
        self.assertIsInstance(tiktok_utils.TokenManager.token_conf, dict)
        self.assertIsInstance(tiktok_utils.TokenManager.ttwid_conf, dict)
        self.assertIsInstance(tiktok_utils.TokenManager.odin_tt_conf, dict)

    def test_other_crawlers_import_without_config(self):
        """其他爬虫模块也要在本地 config 缺失时不抛 FileNotFoundError。"""
        for module_name in [
            "crawlers.douyin.web.utils",
            "crawlers.tiktok.web.web_crawler",
            "crawlers.tiktok.app.app_crawler",
            "crawlers.douyin.web.web_crawler",
            "crawlers.bilibili.web.web_crawler",
            "crawlers.instagram.web.utils",
            "crawlers.youtube.web.utils",
        ]:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)

    def test_vue_main_imports_in_subprocess(self):
        """完整 FastAPI app 必须在子进程里能 import，否则 uvicorn 一启动就崩。"""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", "import app.vue_main; print('ok')"],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=(
                "app.vue_main import failed:\n"
                f"stdout={result.stdout}\nstderr={result.stderr}"
            ),
        )
        self.assertIn("ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
