import streamlit as st
from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict, Sequence, TypeVar, Annotated
from pydantic import BaseModel, Field

load_dotenv()

# 상태 클래스 정의
class ChatState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    current_step: str = Field(default="start")

# 기본 설정
if "messages" not in st.session_state:
    st.session_state.messages = []

def create_chatbot():
    model = ChatOpenAI()
    
    # 상태 처리 함수
    def process_message(state: ChatState) -> ChatState:
        messages = state.messages
        response = model.invoke(messages)
        return ChatState(
            messages=messages + [response],
            current_step="processed"
        )
    
    # StateGraph 생성
    workflow = StateGraph(ChatState)
    
    # 노드 추가
    workflow.add_node("process_message", process_message)
    
    # 시작점 설정
    workflow.set_entry_point("process_message")
    
    # 엣지 정의
    def router(state: ChatState) -> str:
        return "process_message"
    
    workflow.add_edge("process_message", router)
    
    return workflow.compile()

def main():
    st.title("LangGraph 챗봇")
    
    chatbot = create_chatbot()
    
    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
            st.write(message.content)
    
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
            st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()ok