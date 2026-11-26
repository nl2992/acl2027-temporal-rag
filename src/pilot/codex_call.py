"""One non-interactive Codex call with no shell, file, web or app tools, run from an empty folder, so the model sees only the prompt."""
import os, json, re, shutil, subprocess, tempfile

CODEX = os.environ.get("CODEX_BIN") or shutil.which("codex") or "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
OFF = ["shell_tool", "unified_exec", "apps", "plugins", "multi_agent", "browser_use", "browser_use_external", "computer_use",
       "in_app_browser", "image_generation", "view_image"]

def call(path, prompt, model, effort="medium"):
    """Write {answers, model, raw, prompt_chars} to path; skip if it exists. Returns True on success."""
    if os.path.exists(path): return True
    with tempfile.TemporaryDirectory() as empty:
        last = os.path.join(empty, "last.txt")
        cmd = [CODEX, "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "-s", "read-only",
               "-m", model, "-c", f'model_reasoning_effort="{effort}"', "-c", 'web_search="disabled"', "-o", last]
        for f in OFF: cmd += ["--disable", f]
        p = subprocess.run(cmd + ["-"], input=prompt, capture_output=True, text=True, cwd=empty, timeout=1200)
        try:
            raw = open(last).read()
            ans = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
        except Exception as e:
            print("FAILED", path, p.returncode, str(e)[:150], p.stderr[-400:]); return False
    json.dump({"answers": ans, "model": model, "effort": effort, "raw": raw, "prompt_chars": len(prompt)}, open(path, "w"), indent=1)
    return True
