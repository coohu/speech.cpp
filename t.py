import json
import subprocess
import urllib.request

# 1. 启动 speech.cpp 的 live 模式，请求输出 JSON 格式
cmd = [
    "./speech", "asr", "qwen3-asr-0.6b", 
    "--vad", "silero-vad", 
    "--live", 
    "--format", "json"
]

process = subprocess.Popen(
    cmd, 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT, 
    text=True, 
    bufsize=1  # 开启行缓冲，确保实时拿到输出
)

def translate_text(text):
    """在此处接入你的翻译接口（例如 Ollama 本地接口或外部 API）"""
    # 示例：假设你本地跑了 Ollama (端口 11434)，使用 qwen 或 llava 模型翻译成中文
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "translategemma:4b",  # 换成你本地的翻译模型
        "prompt": f"将以下英文翻译成中文，直接输出翻译结果，不要有多余解释:\n{text}",
        "stream": False
    }
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode("utf-8"), 
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res.get("response", "").strip()
    except Exception as e:
        return f"[翻译请求失败: {e}]"

print("正在监听音频并准备实时翻译... 按 Ctrl+C 退出")

try:
    for line in process.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            # 过滤出识别完成的最终文本块（避免打印未完成的中间状态）
            if data.get("type", "").endswith(".completed"):
                transcript = data.get("transcript", "").strip()
                if transcript:
                    print(f"\n[原文]: {transcript}")
                    # 调用翻译接口
                    translated = translate_text(transcript)
                    print(f"[译文]: {translated}")
        except json.JSONDecodeError:
            # 忽略非 JSON 的初始化日志行
            pass
except KeyboardInterrupt:
    process.terminate()
    print("\n已安全退出。")

# 1、brew install blackhole-2ch

# 2、打开 macOS 的“音频 MIDI 设置” (Audio MIDI Setup)。
# 点击左下角的 + 号，创建一个“多输出设备” (Multi-Output Device)。
# 在右侧勾选你的日常耳机/外放，同时勾选 BlackHole 2ch。这样声音既能进你的耳朵，也能流进虚拟通道。

# 3、打开 macOS 系统设置 > 声音 > 输出，将声音输出切换为刚刚创建的这个“多输出设备”。

# 4、python tr.py

# ./speech asr qwen3-asr-0.6b --vad silero-vad --live --format json | jq -r 'select(.type | endswith(".completed")) | .transcript' | while IFS= read -r t; do translate --to zh "$t"; done


# ./speech asr qwen3-asr-0.6b --vad silero-vad --live
