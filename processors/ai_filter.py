"""第 5 层:LLM 中文精读 —— 生成中文简介 + 价值亮点 + 编辑点评。

提示词从 prompt_file 加载(per-brief 可定制,不写死在代码里),{items} 处填入项目数据。
LLM 配置(LLM_API_BASE / LLM_MODEL / LLM_API_KEY)从环境变量读,便于 GitHub Actions 用 Secrets。
未配置 LLM、缺 prompt_file 或调用失败时降级(回退英文 description),不影响发送。
放在 score_rank 之后:只对入选的项目翻译,省 LLM 调用。
"""
from __future__ import annotations
import json
import os
import requests

from core.registry import register_processor
from core.base import Processor


@register_processor("ai_filter")
class AiFilter(Processor):
    def __init__(self, prompt_file: str = "", max_readme_chars: int = 1500,
                 timeout: int = 90, temperature: float = 0.3):
        self.prompt_file = prompt_file
        self.max_readme_chars = max_readme_chars
        self.timeout = timeout
        self.temperature = temperature

    def process(self, projects):
        api_base = os.environ.get("LLM_API_BASE", "").rstrip("/")
        model = os.environ.get("LLM_MODEL", "")
        key = os.environ.get("LLM_API_KEY", "")
        if not (api_base and model and key):
            print("[ai_filter] 未配置 LLM_API_BASE/LLM_MODEL/LLM_API_KEY,跳过中文精读(回退英文简介)")
            return projects
        if not self.prompt_file:
            print("[ai_filter] 未配置 prompt_file,跳过中文精读(回退英文简介)")
            return projects
        if not projects:
            return projects
        try:
            prompt_template = self._load_prompt()
        except Exception as e:
            print(f"[ai_filter] 加载提示词失败({self.prompt_file}),降级为英文简介: {e}")
            return projects

        items = [self._item(p) for p in projects]
        try:
            results = self._call_llm(api_base, model, key, prompt_template, items)
        except Exception as e:
            print(f"[ai_filter] LLM 调用失败,降级为英文简介: {e}")
            return projects

        by_name = {r.get("name", ""): r for r in results}
        filled = 0
        for p in projects:
            r = by_name.get(p.name)
            if not r:
                continue
            s = (r.get("summary_cn") or "").strip()
            hs = r.get("highlights") or []
            if isinstance(hs, list):
                hs = [h.strip() for h in hs if isinstance(h, str) and h.strip()]
            else:
                hs = []
            en = (r.get("editor_note") or "").strip()
            if s:
                p.summary_cn = s
                filled += 1
            if hs:
                p.highlights = hs
            if en:
                p.editor_note = en
        print(f"[ai_filter] 中文精读完成: {filled}/{len(projects)}")
        return projects

    def _load_prompt(self) -> str:
        path = self.prompt_file
        if not os.path.isabs(path):
            # 相对项目根(brief/)解析:processors/ 的上两级
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            path = os.path.join(base, path)
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _item(self, p):
        excerpt = (p.readme_excerpt or "")[: self.max_readme_chars]
        return {
            "name": p.name,
            "description": p.description,
            "language": p.language,
            "topics": p.topics,
            "stars": p.stars_total,
            "readme_excerpt": excerpt,
        }

    def _call_llm(self, api_base, model, key, prompt_template, items):
        # 用 replace 而非 format,避免提示词里的 JSON 示例 { } 被当占位符
        user_prompt = prompt_template.replace("{items}", json.dumps(items, ensure_ascii=False))
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": self.temperature,
        }
        # DeepSeek V4 默认开启思考模式(耗 token、慢,且 temperature 不生效);
        # 精读不需深度推理,关闭思考以省 token + 加快 + 让 temperature 生效。
        # 仅对 DeepSeek 传此参数,其他厂商不传(避免 unknown parameter 报错)。
        if "deepseek" in api_base or "deepseek" in model:
            payload["thinking"] = {"type": "disabled"}
        url = f"{api_base}/chat/completions"
        r = requests.post(url, headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed.get("results", []) if isinstance(parsed, dict) else []
