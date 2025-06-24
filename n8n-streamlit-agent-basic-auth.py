import streamlit as st
import requests
import uuid

# Hàm đọc nội dung từ file văn bản
def rfile(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File {name_file} không tồn tại.")

# Constants
BEARER_TOKEN = st.secrets.get("BEARER_TOKEN")
WEBHOOK_URL = st.secrets.get("WEBHOOK_URL")

def generate_session_id():
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "sessionId": session_id,
        "chatInput": message
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print('Response hỏi đáp:', response_data)
        # Trích xuất contract
        contract = response_data[0].get('output', "No output")
        
        # Trả về object theo định dạng N8nOutputItems
        return [{"json": {"contract": contract}}]
    
    except requests.exceptions.RequestException as e:
        return [{"json": {"contract": f"Error: Failed to connect to the LLM - {str(e)}"}}]

def display_output(output):
    """Hiển thị nội dung hợp đồng"""
    contract = output.get('json', {}).get('contract', "No contract received")
    st.markdown(contract, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Trợ lý AI", page_icon="🤖", layout="centered")

    st.markdown(
        """
        <style>
            .assistant {
                padding: 10px;
                border-radius: 10px;
                max-width: 75%;
                background: none; /* Màu trong suốt */
                text-align: left;
            }
            .user {
                padding: 10px;
                border-radius: 10px;
                max-width: 75%;
                background: none; /* Màu trong suốt */
                text-align: right;
                margin-left: auto;
            }
            .assistant::before { content: "🤖 "; font-weight: bold; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Hiển thị logo (nếu có)
    try:
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            st.image("logo.png")
    except:
        pass
    
    # Đọc nội dung tiêu đề từ file
    try:
        with open("00.xinchao.txt", "r", encoding="utf-8") as file:
            title_content = file.read()
    except Exception as e:
        title_content = "Trợ lý AI"

    st.markdown(
        f"""<h1 style="text-align: center; font-size: 24px;">{title_content}</h1>""",
        unsafe_allow_html=True
    )

    # Khởi tạo session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    # Hiển thị lịch sử tin nhắn
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user">{message["content"]}</div>', unsafe_allow_html=True)
        elif message["role"] == "assistant":
            display_output(message["content"])

    # Ô nhập liệu cho người dùng
    if prompt := st.chat_input("Nhập nội dung cần trao đổi ở đây nhé?"):
        # Lưu tin nhắn của user vào session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Hiển thị tin nhắn user vừa gửi
        st.markdown(f'<div class="user">{prompt}</div>', unsafe_allow_html=True)

        # Gửi yêu cầu đến LLM và nhận phản hồi
        with st.spinner("Đang chờ phản hồi từ AI..."):
            llm_response = send_message_to_llm(st.session_state.session_id, prompt)

        # Lưu phản hồi của AI vào session state
        st.session_state.messages.append({"role": "assistant", "content": llm_response[0]})
        
        # Hiển thị phản hồi của AI
        display_output(llm_response[0])

        # Rerun để cập nhật giao diện
        st.rerun()

if __name__ == "__main__":
    main()
