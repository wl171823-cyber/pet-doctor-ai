import streamlit as st
from openai import OpenAI

# --- 1. 配置区域 (开发者修改这里) ---
# 你可以在这里指定想让访客使用的模型
MODEL_CONFIG = {
    # 选项: "deepseek" 或 "aliyun" (通义千问) 或 "openai"
    "provider": "aliyun",

    # 模型参数配置
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat"
    },
    "aliyun": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus"  # 性价比高
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
}

# --- 页面配置 ---
st.set_page_config(page_title="AI 宠物健康助手", page_icon="🐾", layout="centered")

# --- 2. 获取 API Key (从 Secrets 安全读取) ---
try:
    # 尝试从 Streamlit Secrets 读取名为 "API_KEY" 的密钥
    api_key = st.secrets["sk-e6e07d9befb14961bfa38ae0d280a40a"]
except FileNotFoundError:
    st.error("❌ 未找到密钥配置！请在本地创建 .streamlit/secrets.toml 或在云端设置 Secrets。")
    st.stop()
except KeyError:
    st.error("❌ 配置文件中缺少 'API_KEY' 字段。")
    st.stop()

# 获取当前配置的模型信息
current_conf = MODEL_CONFIG[MODEL_CONFIG["provider"]]

# --- 侧边栏 ---
with st.sidebar:
    st.title("🐾 智能兽医助理")
    st.markdown(f"**当前状态**: 🟢 在线\n\n**接入模型**: `{current_conf['model']}`")
    st.info("本服务由 AI 驱动，提供免费咨询。建议仅供参考，急重症请务必线下就医！")

    st.divider()
    st.subheader("📝 宠物档案")
    pet_type = st.selectbox("宠物类型", ["猫咪 🐱", "狗狗 🐶", "异宠 🐰", "其他"])
    pet_age = st.slider("宠物年龄 (岁)", 0, 20, 2)
    pet_weight = st.number_input("宠物体重 (kg)", 0.1, 50.0, 5.0)

# --- 初始化聊天 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"""
        你是一位经验丰富、富有同情心的AI兽医专家。
        当前接诊对象：{pet_type}，{pet_age}岁，{pet_weight}kg。

        请遵循以下原则：
        1. **初步诊断**：给出3种最可能的疾病或原因。
        2. **风险预警**：如果是急症，必须加粗强调**立刻去医院**。
        3. **护理建议**：提供家庭护理措施。
        4. **好物推荐**：推荐1-2款通用用品（不推荐三无品牌）。
        5. **语气**：温柔、专业。
        """}
    ]

# --- 主界面 ---
st.title("🏥 AI 宠物在线问诊台")
st.caption("免费公益版 | 请详细描述症状")

# 初始化客户端
client = OpenAI(api_key=api_key, base_url=current_conf["base_url"])

# 显示历史
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 处理输入
if prompt := st.chat_input("我家猫咪今天早上吐了黄水..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=current_conf["model"],
                messages=st.session_state.messages,
                stream=True,
                temperature=0.7
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"连接繁忙，请稍后再试: {e}")
