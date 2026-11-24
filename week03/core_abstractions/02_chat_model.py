"""
第 3 周 · 核心抽象 02：ChatModel（聊天模型）
================================================================
【对应知识点】文档第 3 周「LangChain 核心抽象」第 2 项：ChatModel

【周次学习要点】
  - ChatModel 封装 LLM 调用，抹平各家请求/响应差异：换模型只换构造参数。
  - LangChain 1.x 用 init_chat_model 统一初始化；国内厂商走 OpenAI 兼容端点。
  - 本周直接复用第 2 周写好的 get_provider()：框架负责编排，适配器仍是你自己的。

【易忽略细节】
  1. 国内厂商 base_url 必须带 /v1 后缀，否则 404；DeepSeek 是裸域名例外。
  2. 消息要用 Message 对象（SystemMessage / HumanMessage），不是裸 dict。
  3. FakeListChatModel 是本地假模型，按序返回预设 responses，无 Key 也能跑通全链路。

【示例用途】可运行：`python week03/core_abstractions/02_chat_model.py`
             测试见 tests/week03/test_core_abstractions.py
"""
from __future__ import annotations

from langchain.chat_models import init_chat_model
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import HumanMessage, SystemMessage


def build_fake_model() -> FakeListChatModel:
    """本地假模型：验证编排逻辑时不需要任何 API Key。"""
    return FakeListChatModel(responses=["cyclone 网关负责统一模型接入与成本控制。"])


def describe_real_model() -> None:
    """真实客户端的写法（本例不发起请求）：配置来自第 2 周的环境变量约定。"""
    # qwen = init_chat_model(
    #     "qwen-plus",
    #     model_provider="openai",
    #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 必须带 /v1
    #     api_key=os.getenv("DASHSCOPE_API_KEY"),
    # )
    print("真实模型入口：init_chat_model(...)，环境变量沿用第 2 周 DASHSCOPE_API_KEY")
    print("init_chat_model 可调用：", callable(init_chat_model))


def demo() -> None:
    """用 Message 对象拼消息，调用本地假模型。"""
    model = build_fake_model()
    messages = [
        SystemMessage(content="你是运维助手，回答要一句话。"),
        HumanMessage(content="cyclone 网关是干什么的？"),
    ]
    response = model.invoke(messages)
    print("模型回答：", response.content)
    print("消息角色：", [m.type for m in messages])


if __name__ == "__main__":
    demo()
    describe_real_model()
