import streamlit as st
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import List
from pydantic import BaseModel, Field

# 환경 변수 로드
load_dotenv()

# 상태 클래스 정의
class ChatState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    current_step: str = Field(default="start")

# 기본 설정
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="안녕하세요! 저는 LangGraph 기반 챗봇입니다. 질문이 있다면 언제든 말씀해주세요!")
    ]

# 챗봇 생성 함수
def create_chatbot():
    # OpenAI 모델 설정
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    model = ChatOpenAI(api_key=api_key)
    
    # 상태 처리 함수
    def process_message(state: ChatState) -> ChatState:
        try:
            messages = state.messages
            response = model.invoke(messages)
            return ChatState(
                messages=messages + [response],
                current_step="processed"
            )
        except Exception as e:
            raise RuntimeError(f"모델 응답 처리 중 오류 발생: {str(e)}")
    
    # StateGraph 생성
    workflow = StateGraph(ChatState)
    
    # 노드 추가
    workflow.add_node("process_message", process_message)
    
    # 시작점 설정
    workflow.set_entry_point("process_message")
    
    # 엣지 정의
    workflow.add_edge("process_message", "process_message", None)
    
    return workflow.compile()



# 메인 함수
def main():
    st.title("LangGraph 챗봇")
    
    try:
        chatbot = create_chatbot()
    except Exception as e:
        st.error(f"챗봇 초기화 오류: {str(e)}")
        return
    
    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
            st.write(message.content)
    
    # 사용자 입력 처리
    if prompt := st.chat_input("메시지를 입력하세요"):
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # 초기 상태 설정
        state = ChatState(
            messages=st.session_state.messages,
            current_step="start"
        )
        
        try:
            result = chatbot.invoke(state)
            st.session_state.messages.append(result.messages[-1])
            with st.chat_message("assistant"):
                st.write(result.messages[-1].content)
        except Exception as e:
            st.error(f"메시지 처리 중 오류가 발생했습니다: {str(e)}")

# 실행
if __name__ == "__main__":
    main()
