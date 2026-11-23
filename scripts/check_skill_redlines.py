#!/usr/bin/env python3
"""Skill 红线检查器（Skill Redlines Evaluator）。

基于 Claude / OpenAI / agentskills.io 渐进披露原则，对 skill 执行 L1 确定性红线检查：
- R01_FRONTMATTER / R01_NAME_FORMAT / R01_NAME_MISMATCH：YAML frontmatter 与名称契约
- R02_DESCRIPTION_FORMAT / R02_DESCRIPTION_CHARS / R02_DESCRIPTION_TOKENS：description 预算红线
- R03_BODY_EMPTY / R03_BODY_LINES / R03_BODY_TOKENS：SKILL.md 正文行数与 token 红线
- R04_BROKEN_LINK：SKILL.md 内本地相对文件链接有效性

退出码：0 表示全部通过，1 表示触发至少一条红线，2 表示调用参数错误。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_LIMITS = {
    "max_name_chars": 64,
    "max_description_chars": 300,
    "max_description_tokens": 120,
    "max_body_lines": 300,
    "max_body_tokens": 3000,
}

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
UPSTREAM_ENTRY_RE = re.compile(r'SKILL_FILES\["([^"]+)"\]=')
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")

try:
    import tiktoken

    _ENCODER = tiktoken.get_encoding("o200k_base")
    TOKEN_COUNTER_NAME = "tiktoken:o200k_base"
except Exception:
    _ENCODER = None
    TOKEN_COUNTER_NAME = "heuristic"


@dataclass
class Limits:
    max_name_chars: int = DEFAULT_LIMITS["max_name_chars"]
    max_description_chars: int = DEFAULT_LIMITS["max_description_chars"]
    max_description_tokens: int = DEFAULT_LIMITS["max_description_tokens"]
    max_body_lines: int = DEFAULT_LIMITS["max_body_lines"]
    max_body_tokens: int = DEFAULT_LIMITS["max_body_tokens"]


@dataclass
class Violation:
    rule_id: str
    skill: str
    file: str
    actual: Any
    limit: Any
    message: str


def count_tokens(text: str) -> int:
    """计算文本 token 数（优先 tiktoken o200k_base，缺失时用中英文加权估算兜底）。"""
    if not text:
        return 0
    if _ENCODER is not None:
        return len(_ENCODER.encode(text))
    cjk = len(CJK_RE.findall(text))
    other = len(text) - cjk
    return math.ceil(cjk * 0.8 + other / 4.0)


def detect_upstream_skills(repo_root: Path) -> set[str]:
    """从 update-upstream.sh 自动识别上游同步的 skill 目录名。"""
    script = repo_root / "update-upstream.sh"
    if not script.is_file():
        return set()
    content = script.read_text(encoding="utf-8")
    return set(UPSTREAM_ENTRY_RE.findall(content))


def parse_skill_markdown(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    """拆分 YAML frontmatter 与正文，返回 (frontmatter, body, error_msg)。"""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text, "缺少合法的 YAML frontmatter（需以 --- 包裹）"

    raw_fm = match.group(1)
    body = text[match.end() :].lstrip("\r\n")
    try:
        parsed = yaml.safe_load(raw_fm)
    except yaml.YAMLError as exc:
        return None, body, f"YAML frontmatter 解析失败: {exc}"

    if not isinstance(parsed, dict):
        return None, body, "YAML frontmatter 必须是键值对映射"
    return parsed, body, None


def extract_local_links(body: str) -> list[str]:
    """提取正文中非代码块的相对文件路径链接（去除 #anchor）。"""
    cleaned = FENCED_CODE_RE.sub("", body)
    cleaned = INLINE_CODE_RE.sub("", cleaned)

    links: list[str] = []
    for raw_target in MD_LINK_RE.findall(cleaned):
        if raw_target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        path_part = raw_target.split("#", 1)[0].strip()
        if path_part:
            links.append(path_part)
    return links


def evaluate_skill(skill_dir: Path, limits: Limits) -> tuple[dict[str, Any], list[Violation]]:
    """对单个 skill 目录执行全部红线检查，返回 (度量摘要, 违例列表)。"""
    skill_name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    rel_file = str(skill_md)
    violations: list[Violation] = []

    if not skill_md.is_file():
        violations.append(
            Violation(
                rule_id="R01_FRONTMATTER",
                skill=skill_name,
                file=rel_file,
                actual="missing",
                limit="SKILL.md required",
                message="目录中缺少 SKILL.md",
            )
        )
        return {"skill": skill_name, "file": rel_file, "metrics": {}, "passed": False}, violations

    text = skill_md.read_text(encoding="utf-8")
    fm, body, fm_err = parse_skill_markdown(text)

    body_lines = len(body.splitlines())
    body_chars = len(body)
    body_tokens = count_tokens(body)
    desc_chars = 0
    desc_tokens = 0

    if fm_err or fm is None:
        violations.append(
            Violation(
                rule_id="R01_FRONTMATTER",
                skill=skill_name,
                file=rel_file,
                actual="invalid",
                limit="valid YAML frontmatter",
                message=fm_err or "无效 frontmatter",
            )
        )
    else:
        # R01: name 校验
        raw_name = fm.get("name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            violations.append(
                Violation(
                    rule_id="R01_FRONTMATTER",
                    skill=skill_name,
                    file=rel_file,
                    actual=raw_name,
                    limit="non-empty string",
                    message="frontmatter 缺少非空 name 字段",
                )
            )
        else:
            name = raw_name.strip()
            if not KEBAB_CASE_RE.match(name) or len(name) > limits.max_name_chars:
                violations.append(
                    Violation(
                        rule_id="R01_NAME_FORMAT",
                        skill=skill_name,
                        file=rel_file,
                        actual=name,
                        limit=f"kebab-case and <= {limits.max_name_chars} chars",
                        message=f"name '{name}' 须为 kebab-case 且长度不超过 {limits.max_name_chars}",
                    )
                )
            if name != skill_name:
                violations.append(
                    Violation(
                        rule_id="R01_NAME_MISMATCH",
                        skill=skill_name,
                        file=rel_file,
                        actual=name,
                        limit=skill_name,
                        message=f"frontmatter name '{name}' 与目录名 '{skill_name}' 不一致",
                    )
                )

        # R02: description 校验（常驻上下文，控制字符与 token 双红线）
        raw_desc = fm.get("description")
        if not isinstance(raw_desc, str) or not raw_desc.strip():
            violations.append(
                Violation(
                    rule_id="R01_FRONTMATTER",
                    skill=skill_name,
                    file=rel_file,
                    actual=raw_desc,
                    limit="non-empty string",
                    message="frontmatter 缺少非空 description 字段",
                )
            )
        else:
            desc = raw_desc.strip()
            desc_chars = len(desc)
            desc_tokens = count_tokens(desc)
            if "<" in desc or ">" in desc:
                violations.append(
                    Violation(
                        rule_id="R02_DESCRIPTION_FORMAT",
                        skill=skill_name,
                        file=rel_file,
                        actual="contains < or >",
                        limit="no angle brackets",
                        message="description 不允许包含尖括号 < 或 >",
                    )
                )
            if desc_chars > limits.max_description_chars:
                violations.append(
                    Violation(
                        rule_id="R02_DESCRIPTION_CHARS",
                        skill=skill_name,
                        file=rel_file,
                        actual=desc_chars,
                        limit=limits.max_description_chars,
                        message=(
                            f"description 长度 {desc_chars} 字符超过上限 {limits.max_description_chars}，"
                            "请精简触发词与摘要"
                        ),
                    )
                )
            if desc_tokens > limits.max_description_tokens:
                violations.append(
                    Violation(
                        rule_id="R02_DESCRIPTION_TOKENS",
                        skill=skill_name,
                        file=rel_file,
                        actual=desc_tokens,
                        limit=limits.max_description_tokens,
                        message=(
                            f"description 占用 {desc_tokens} tokens 超过上限 {limits.max_description_tokens}，"
                            "避免常驻 metadata 挤占上下文"
                        ),
                    )
                )

    # R03: 正文行数与 token 红线
    if body_chars == 0:
        violations.append(
            Violation(
                rule_id="R03_BODY_EMPTY",
                skill=skill_name,
                file=rel_file,
                actual=0,
                limit="> 0",
                message="SKILL.md 正文不能为空",
            )
        )
    if body_lines > limits.max_body_lines:
        violations.append(
            Violation(
                rule_id="R03_BODY_LINES",
                skill=skill_name,
                file=rel_file,
                actual=body_lines,
                limit=limits.max_body_lines,
                message=(
                    f"正文行数 {body_lines} 超过上限 {limits.max_body_lines} 行，"
                    "请将详细规范或流程拆入 references/ 按需加载"
                ),
            )
        )
    if body_tokens > limits.max_body_tokens:
        violations.append(
            Violation(
                rule_id="R03_BODY_TOKENS",
                skill=skill_name,
                file=rel_file,
                actual=body_tokens,
                limit=limits.max_body_tokens,
                message=(
                    f"正文占用 {body_tokens} tokens 超过上限 {limits.max_body_tokens}，"
                    "请遵循渐进披露原则将详规拆入 references/"
                ),
            )
        )

    # R04: 本地相对链接校验
    for link in extract_local_links(body):
        target_path = (skill_dir / link).resolve()
        if not target_path.exists():
            violations.append(
                Violation(
                    rule_id="R04_BROKEN_LINK",
                    skill=skill_name,
                    file=rel_file,
                    actual=link,
                    limit="existing local file/directory",
                    message=f"本地相对链接目标不存在: {link}",
                )
            )

    summary = {
        "skill": skill_name,
        "file": rel_file,
        "metrics": {
            "description_chars": desc_chars,
            "description_tokens": desc_tokens,
            "body_lines": body_lines,
            "body_chars": body_chars,
            "body_tokens": body_tokens,
        },
        "passed": len(violations) == 0,
    }
    return summary, violations


def discover_skill_dirs(
    targets: list[str], repo_root: Path, include_upstream: bool
) -> tuple[list[Path], list[str]]:
    """确定待检查的 skill 目录列表与被跳过的上游目录名。"""
    if targets:
        return [Path(t).resolve() for t in targets], []

    upstream = set() if include_upstream else detect_upstream_skills(repo_root)
    dirs: list[Path] = []
    skipped: list[str] = []
    for child in sorted(repo_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if not (child / "SKILL.md").is_file():
            continue
        if child.name in upstream:
            skipped.append(child.name)
            continue
        dirs.append(child)
    return dirs, skipped


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="检查 skill 红线（frontmatter、token/行数上限、本地链接）")
    parser.add_argument(
        "targets",
        nargs="*",
        help="可选：指定一个或多个 skill 目录；不传则扫描仓库全部自研 skills",
    )
    parser.add_argument(
        "--max-desc-chars",
        type=int,
        default=DEFAULT_LIMITS["max_description_chars"],
        help=f"description 最大字符数（默认 {DEFAULT_LIMITS['max_description_chars']}）",
    )
    parser.add_argument(
        "--max-desc-tokens",
        type=int,
        default=DEFAULT_LIMITS["max_description_tokens"],
        help=f"description 最大 token 数（默认 {DEFAULT_LIMITS['max_description_tokens']}）",
    )
    parser.add_argument(
        "--max-body-lines",
        type=int,
        default=DEFAULT_LIMITS["max_body_lines"],
        help=f"正文最大行数（默认 {DEFAULT_LIMITS['max_body_lines']}）",
    )
    parser.add_argument(
        "--max-body-tokens",
        type=int,
        default=DEFAULT_LIMITS["max_body_tokens"],
        help=f"正文最大 token 数（默认 {DEFAULT_LIMITS['max_body_tokens']}）",
    )
    parser.add_argument(
        "--include-upstream",
        action="store_true",
        help="一并检查 update-upstream.sh 中维护的上游 skills",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="输出机器可读 JSON 报告（供 Agent 自闭环读取）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    limits = Limits(
        max_description_chars=args.max_desc_chars,
        max_description_tokens=args.max_desc_tokens,
        max_body_lines=args.max_body_lines,
        max_body_tokens=args.max_body_tokens,
    )

    skill_dirs, skipped_upstream = discover_skill_dirs(
        args.targets, REPO_ROOT, args.include_upstream
    )
    if not skill_dirs:
        print("未找到任何待检查的 skill 目录。", file=sys.stderr)
        return 2

    skill_summaries: list[dict[str, Any]] = []
    all_violations: list[Violation] = []
    for skill_dir in skill_dirs:
        summary, violations = evaluate_skill(skill_dir, limits)
        skill_summaries.append(summary)
        all_violations.extend(violations)

    passed = len(all_violations) == 0
    report = {
        "passed": passed,
        "token_counter": TOKEN_COUNTER_NAME,
        "limits": asdict(limits),
        "skipped_upstream": skipped_upstream,
        "skills": skill_summaries,
        "violations": [asdict(v) for v in all_violations],
    }

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for s in skill_summaries:
            m = s["metrics"]
            status = "PASS" if s["passed"] else "FAIL"
            print(
                f"[{status}] {s['skill']}: "
                f"desc={m.get('description_tokens', '-')}/{limits.max_description_tokens} tok "
                f"({m.get('description_chars', '-')}/{limits.max_description_chars} chars), "
                f"body={m.get('body_tokens', '-')}/{limits.max_body_tokens} tok "
                f"({m.get('body_lines', '-')}/{limits.max_body_lines} lines)"
            )
        if skipped_upstream:
            print(f"[SKIP] upstream skills (use --include-upstream to check): {', '.join(skipped_upstream)}")
        if all_violations:
            print("\nRedline violations:")
            for v in all_violations:
                print(f"  - [{v.rule_id}] {v.skill}: {v.message} (actual={v.actual}, limit={v.limit})")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
