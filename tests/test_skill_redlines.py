import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_skill_redlines.py"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import check_skill_redlines as redlines  # noqa: E402


def write_skill(root: Path, dirname: str, content: str) -> Path:
    skill_dir = root / dirname
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return skill_dir


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def make_skill_md(
    name: str = "demo-skill",
    description: str = "一个用于验证红线机制的示例技能。",
    body: str = "# Demo\n\n正文内容。\n",
) -> str:
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}"


def build_text_with_exact_tokens(target_tokens: int, unit: str = " word", max_lines: int = 200) -> str:
    """构造精确等于 target_tokens 且行数不超过 max_lines 的测试文本。"""
    words_per_line = max(1, (target_tokens // max(1, max_lines - 1)) + 1)
    tokens_list = ["alpha"] * target_tokens
    lines = [
        " ".join(tokens_list[i : i + words_per_line])
        for i in range(0, len(tokens_list), words_per_line)
    ]
    text = "\n".join(lines)
    # 按实际 tokenizer 微调到精确目标值
    while redlines.count_tokens(text) < target_tokens:
        text += " beta"
    while redlines.count_tokens(text) > target_tokens:
        text = text.rsplit(" ", 1)[0]
    assert redlines.count_tokens(text) == target_tokens
    return text


class TestSkillRedlinesCLI:
    """L1 黑盒契约验证：直接调用 CLI 验证红线规则、退出码与机器可读诊断输出。"""

    def test_valid_skill_passes_with_zero_exit_and_metrics(self, tmp_path: Path):
        skill_dir = write_skill(tmp_path, "demo-skill", make_skill_md())
        res = run_cli(str(skill_dir), "--json")
        assert res.returncode == 0, res.stdout + res.stderr

        payload = json.loads(res.stdout)
        assert payload["passed"] is True
        assert payload["violations"] == []
        assert payload["token_counter"]
        assert len(payload["skills"]) == 1
        metrics = payload["skills"][0]["metrics"]
        assert metrics["description_chars"] == len("一个用于验证红线机制的示例技能。")
        assert metrics["description_tokens"] > 0
        assert metrics["body_lines"] >= 1
        assert metrics["body_tokens"] > 0

    @pytest.mark.parametrize(
        ("desc_len", "expect_pass"),
        [
            (300, True),   # 边界值：刚好等于字符上限应通过
            (301, False),  # 超出 1 字符即触发 R02_DESCRIPTION_CHARS 红线
        ],
    )
    def test_description_chars_boundary(self, tmp_path: Path, desc_len: int, expect_pass: bool):
        # 重复单字母 token 数极低，确保只测试字符红线边界
        skill_dir = write_skill(
            tmp_path,
            "demo-skill",
            make_skill_md(description="a" * desc_len),
        )
        res = run_cli(str(skill_dir), "--json")
        payload = json.loads(res.stdout)

        if expect_pass:
            assert res.returncode == 0
            assert payload["passed"] is True
        else:
            assert res.returncode != 0
            v = next(v for v in payload["violations"] if v["rule_id"] == "R02_DESCRIPTION_CHARS")
            assert v["actual"] == 301
            assert v["limit"] == 300

    @pytest.mark.parametrize(
        ("desc_tokens", "expect_pass"),
        [
            (120, True),   # 边界值：刚好 120 tokens 应通过
            (121, False),  # 超出 1 token 即触发 R02_DESCRIPTION_TOKENS 红线
        ],
    )
    def test_description_tokens_boundary(self, tmp_path: Path, desc_tokens: int, expect_pass: bool):
        # 用不重复中文汉字构造高 token 密度但字符数 < 300 的描述
        chars = [chr(0x4E00 + i) for i in range(280)]
        desc = ""
        for ch in chars:
            if redlines.count_tokens(desc + ch) <= desc_tokens:
                desc += ch
            if redlines.count_tokens(desc) == desc_tokens:
                break
        assert redlines.count_tokens(desc) == desc_tokens
        assert len(desc) <= 300

        skill_dir = write_skill(tmp_path, "demo-skill", make_skill_md(description=desc))
        res = run_cli(str(skill_dir), "--json")
        payload = json.loads(res.stdout)

        if expect_pass:
            assert res.returncode == 0
            assert payload["passed"] is True
        else:
            assert res.returncode != 0
            assert any(v["rule_id"] == "R02_DESCRIPTION_TOKENS" for v in payload["violations"])

    def test_description_angle_brackets_rejected(self, tmp_path: Path):
        skill_dir = write_skill(
            tmp_path,
            "demo-skill",
            make_skill_md(description="不能包含 <tag> 尖括号"),
        )
        res = run_cli(str(skill_dir), "--json")
        payload = json.loads(res.stdout)
        assert res.returncode != 0
        assert any(v["rule_id"] == "R02_DESCRIPTION_FORMAT" for v in payload["violations"])

    @pytest.mark.parametrize(
        ("line_count", "expect_pass"),
        [
            (300, True),   # 边界值：刚好 300 行应通过
            (301, False),  # 超出 1 行即触发 R03_BODY_LINES 红线
        ],
    )
    def test_body_lines_boundary(self, tmp_path: Path, line_count: int, expect_pass: bool):
        body = "\n".join(f"x{i}" for i in range(line_count)) + "\n"
        skill_dir = write_skill(tmp_path, "demo-skill", make_skill_md(body=body))
        res = run_cli(str(skill_dir), "--json")
        payload = json.loads(res.stdout)

        if expect_pass:
            assert res.returncode == 0
            assert payload["passed"] is True
        else:
            assert res.returncode != 0
            assert any(v["rule_id"] == "R03_BODY_LINES" for v in payload["violations"])

    @pytest.mark.parametrize(
        ("token_count", "expect_pass"),
        [
            (3000, True),   # 边界值：刚好 3000 tokens 应通过
            (3001, False),  # 超出 1 token 即触发 R03_BODY_TOKENS 红线
        ],
    )
    def test_body_tokens_boundary(self, tmp_path: Path, token_count: int, expect_pass: bool):
        body = build_text_with_exact_tokens(token_count, max_lines=200)
        assert len(body.splitlines()) <= 300

        skill_dir = write_skill(tmp_path, "demo-skill", make_skill_md(body=body))
        res = run_cli(str(skill_dir), "--json")
        payload = json.loads(res.stdout)

        if expect_pass:
            assert res.returncode == 0
            assert payload["passed"] is True
        else:
            assert res.returncode != 0
            assert any(v["rule_id"] == "R03_BODY_TOKENS" for v in payload["violations"])

    def test_frontmatter_missing_or_name_mismatch(self, tmp_path: Path):
        no_fm = write_skill(tmp_path, "no-fm", "# 没有 frontmatter\n")
        res1 = run_cli(str(no_fm), "--json")
        assert res1.returncode != 0
        assert any(v["rule_id"] == "R01_FRONTMATTER" for v in json.loads(res1.stdout)["violations"])

        mismatch = write_skill(
            tmp_path,
            "dir-name",
            make_skill_md(name="other-name"),
        )
        res2 = run_cli(str(mismatch), "--json")
        assert res2.returncode != 0
        assert any(v["rule_id"] == "R01_NAME_MISMATCH" for v in json.loads(res2.stdout)["violations"])

    def test_local_links_validation_and_code_fence_ignored(self, tmp_path: Path):
        body = (
            "# Demo\n\n"
            "有效链接：[存在](references/ok.md)\n"
            "锚点与外链：[标题](#demo) [官网](https://example.com)\n\n"
            "```markdown\n"
            "[代码块内示例链接不误报](references/not-a-real-file.md)\n"
            "```\n\n"
            "死链：[缺失](references/missing.md)\n"
        )
        skill_dir = write_skill(tmp_path, "demo-skill", make_skill_md(body=body))
        (skill_dir / "references").mkdir()
        (skill_dir / "references" / "ok.md").write_text("ok", encoding="utf-8")

        res = run_cli(str(skill_dir), "--json")
        payload = json.loads(res.stdout)
        assert res.returncode != 0
        link_violations = [v for v in payload["violations"] if v["rule_id"] == "R04_BROKEN_LINK"]
        assert len(link_violations) == 1
        assert "references/missing.md" in link_violations[0]["actual"]

    def test_custom_limits_override_via_cli(self, tmp_path: Path):
        skill_dir = write_skill(
            tmp_path,
            "demo-skill",
            make_skill_md(description="a" * 50),
        )
        res = run_cli(str(skill_dir), "--max-desc-chars", "40", "--json")
        assert res.returncode != 0
        assert any(v["rule_id"] == "R02_DESCRIPTION_CHARS" for v in json.loads(res.stdout)["violations"])

    def test_repo_skills_dogfood_all_pass(self):
        """对当前仓库所有真实自研 skills 执行红线回归，确保仓库现状全部合规。"""
        res = run_cli("--json")
        payload = json.loads(res.stdout)
        assert res.returncode == 0, json.dumps(payload, ensure_ascii=False, indent=2)
        assert payload["passed"] is True
        checked_names = {s["skill"] for s in payload["skills"]}
        assert {"add-user-memory", "goal-to-prompt", "harness"}.issubset(checked_names)
