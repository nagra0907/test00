import streamlit as st
import openai
import tempfile
import os
import time

st.set_page_config(page_title="PDF 대화 도우미", page_icon="📑")
st.header("📑 PDF Assistant")
st.info("PDF 파일을 올리고 파일 내용을 바탕으로 질문해 보세요.")

api_token = st.text_input("🔐 OpenAI API Key를 입력하세요", type="password")

if api_token:
    oai_client = openai.Client(api_key=api_token)

    session = st.session_state
    session.setdefault("pdf_file_id", None)
    session.setdefault("assistant_ref", None)
    session.setdefault("thread_ref", None)

    uploaded_pdf = st.file_uploader("📥 PDF 파일을 선택하세요", type=["pdf"])

    def store_pdf(file_obj):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(file_obj.read())
            temp_path = temp_pdf.name

        file_upload = oai_client.files.create(
            file=open(temp_path, "rb"),
            purpose="assistants"
        )
        os.remove(temp_path)
        return file_upload.id

    if st.button("🔄 세션 초기화"):
        session.pdf_file_id = None
        session.assistant_ref = None
        session.thread_ref = None
        st.success("세션이 초기화되었습니다.")

    if uploaded_pdf and not session.pdf_file_id:
        st.info("파일을 서버로 전송 중...")
        session.pdf_file_id = store_pdf(uploaded_pdf)
        st.success("파일 업로드 성공 ✅")

        assistant_cfg = oai_client.beta.assistants.create(
            name="PDF Assistant",
            instructions="첨부된 PDF 파일을 바탕으로 사용자 질문에 응답하세요.",
            model="gpt-4o",
            tools=[{"type": "file_search"}]
        )
        session.assistant_ref = assistant_cfg.id

        thread_cfg = oai_client.beta.threads.create()
        session.thread_ref = thread_cfg.id

    if all([session.pdf_file_id, session.assistant_ref, session.thread_ref]):
        query = st.text_input("💬 문서와 관련된 질문을 입력하세요")

        if query:
            oai_client.beta.threads.messages.create(
                thread_id=session.thread_ref,
                role="user",
                content=query,
                attachments=[{"file_id": session.pdf_file_id, "tools": [{"type": "file_search"}]}]
            )

            task = oai_client.beta.threads.runs.create(
                thread_id=session.thread_ref,
                assistant_id=session.assistant_ref
            )

            with st.spinner("AI가 답변을 준비 중입니다..."):
                while task.status not in ["completed", "failed", "cancelled"]:
                    time.sleep(1)
                    task = oai_client.beta.threads.runs.retrieve(
                        thread_id=session.thread_ref,
                        run_id=task.id
                    )

                if task.status == "completed":
                    msgs = oai_client.beta.threads.messages.list(
                        thread_id=session.thread_ref
                    )
                    reply = msgs.data[0].content[0].text.value
                    st.success("🤖 AI 답변:")
                    st.markdown(reply)
                else:
                    st.error(f"❌ 작업 실패: {task.status}")
else:
    st.warning("🔑 먼저 OpenAI API Key를 입력해주세요.")
