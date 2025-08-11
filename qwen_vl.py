import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载.env文件
load_dotenv()

client = OpenAI(
    # 从.env文件中读取API key
    api_key=os.getenv("qwen_api_key"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-max-latest",
    messages=[
        {"role": "system",
         "content": [{"type": "text","text": "You are a helpful assistant."}]},
        {"role": "user","content": [{
            # 直接传入视频文件时，请将type的值设置为video_url
            # 使用OpenAI SDK时，视频文件默认每间隔0.5秒抽取一帧，且不支持修改，如需自定义抽帧频率，请使用DashScope SDK.
            "type": "video_url",            
            "video_url": {"url": "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241115/cqqkru/1.mp4"}},
            {"type": "text","text": "这段视频的内容是什么?请你详细描述"}]
         }]
)
print(completion.choices[0].message.content)