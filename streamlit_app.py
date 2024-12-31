import streamlit as st
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드

# 기본 설정
if "messages" not in st.session_state:
    st.session_state.messages = []

def create_chatbot():
    # LangGraph 설정
    model = ChatOpenAI()
    
    def process_message(state):
        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages": messages + [response]}
    
    # StateGraph 사용 (Graph 대신)
    workflow = StateGraph(initial_state={"messages": [], "current_step": "start"})
    
    # 노드 추가
    workflow.add_node("process_message", process_message)
    
    # 시작점 정의 (이 부분이 중요합니다)
    workflow.set_entry_point("process_message")
    
    # 조건부 엣지 추가
    def should_continue(state):
        return "process_message"
    
    # 엣지 추가
    workflow.add_edge("process_message", should_continue)
    
    return workflow.compile()

def main():
    st.title("LangGraph 챗봇")
    
    # 챗봇 초기화
    chatbot = create_chatbot()
    
    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
            st.write(message.content)
    
    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 추가
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # 챗봇 응답 생성
        state = {
            "messages": st.session_state.messages,
            "current_step": "start"
        }
        
        result = chatbot.invoke(state)
        
        # 응답 저장 및 표시
        st.session_state.messages.append(result["messages"][-1])
        with st.chat_message("assistant"):
            st.write(result["messages"][-1].content)

if __name__ == "__main__":
    main()