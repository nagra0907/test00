import streamlit as st
import openai

st.set_page_config(page_title="AI Q&A Helper", page_icon="🧠")
st.header("🧠 AI 질문 도우미")
st.info("GPT-4.1-mini를 활용해 궁금한 점을 물어보세요.")

if 'user_api_key' not in st.session_state:
    st.session_state['user_api_key'] = ''

st.session_state['user_api_key'] = st.text_input(
    label="🔑 OpenAI API Key를 입력해주세요",
    value=st.session_state['user_api_key'],
    type="password"
)

if st.session_state['user_api_key']:
    openai.api_key = st.session_state['user_api_key']

    query = st.text_input("💬 질문을 입력하세요")

    @st.cache_data(show_spinner="AI가 답변을 준비 중입니다...", experimental_allow_widgets=True)
    def fetch_ai_response(user_prompt, user_key):
        oai_client = openai.OpenAI(api_key=user_key)
        result = oai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "당신은 친절하고 유용한 AI 조수입니다."},
                {"role": "user", "content": user_prompt}
            ]
        )
        return result.choices[0].message.content.strip()

    if query:
        try:
            ai_reply = fetch_ai_response(query, st.session_state['user_api_key'])
            st.subheader("📢 AI 응답")
            st.write(ai_reply)
        except Exception as err:
            st.error(f"❗ 오류가 발생했습니다: {err}")
else:
    st.warning("🔐 먼저 OpenAI API Key를 입력해야 합니다.")

