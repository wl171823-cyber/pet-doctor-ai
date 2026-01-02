import streamlit as st
from openai import OpenAI

# --- 页面配置 ---
st.set_page_config(
    page_title="AI 宠物健康助手",
    page_icon="🐾",
    layout="centered"
)

# --- 侧边栏设置 ---
with st.sidebar:
    st.title("🐾 智能兽医助理")
    st.write("我是您的全天候宠物健康顾问。请注意，AI建议仅供参考，急重症请务必线下就医！")

    # 获取 API Key (为了安全，建议用户在界面输入，或者部署时设为 Secret)
    api_key = st.text_input("请输入您的 API Key (OpenAI/DeepSeek等):", type="password")

    st.divider()
    st.subheader("📝 宠物档案")
    pet_type = st.selectbox("宠物类型", ["猫咪 🐱", "狗狗 🐶", "异宠 (仓鼠/鸟/爬宠) 🐰", "其他"])
    pet_age = st.slider("宠物年龄 (岁)", 0, 20, 2)
    pet_weight = st.number_input("宠物体重 (kg)", 0.1, 50.0, 5.0)

# --- 初始化聊天记录 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"""
        你是一位经验丰富、富有同情心的AI兽医专家。你的目标是辅助主人判断宠物状况。

        请遵循以下原则：
        1. **初步诊断**：根据用户描述的症状（结合宠物类型：{pet_type}，年龄：{pet_age}岁），给出3种最可能的疾病或原因，按概率排序。
        2. **风险预警**：如果是急症（如吞食异物、呼吸困难、严重脱水），必须第一时间建议立刻去医院，并用加粗字体强调。
        3. **护理建议**：提供家庭护理措施（如禁食禁水、物理降温等）。
        4. **好物推荐**：在诊断后，推荐1-2款相关的通用宠物用品（如：特定成分的益生菌、伊丽莎白圈、处方粮类型），但不要推荐具体的三无品牌。
        5. **语气**：温柔、专业、安抚焦虑的主人。
        """}
    ]

# --- 主界面 ---
st.title("🏥 AI 宠物在线问诊台")
st.caption("请详细描述宠物的症状（如：呕吐频率、精神状态、排便情况等）")

# 检查 API Key
if not api_key:
    st.info("💡 请在左侧侧边栏输入 API Key 以启动 AI 医生。")
    st.stop()

# 初始化 OpenAI 客户端 (兼容 OpenAI 格式的 API)
client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")  # 如果用其他模型，修改 base_url

# 显示历史消息
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("我家猫咪今天早上吐了黄水，精神不太好..."):
    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 生成 AI 回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",  # 或 gpt-4o, deepseek-chat
                messages=st.session_state.messages,
                stream=True,
                temperature=0.7
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

            # 3. 保存 AI 回复
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"发生错误: {e}")