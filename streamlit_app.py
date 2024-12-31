import streamlit as st
from langgraph.graph import Graph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import json
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 로드

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

class ChatBot:
    def __init__(self):
        self.model = ChatOpenAI()
        self.graph = self._create_graph()
    
    def _create_graph(self):
        # 메시지 처리
        def process_message(state):
            messages = state["messages"]
            response = self.model.invoke(messages)
            return {"messages": messages + [response]}
        
        # 컨텍스트 분석
        def analyze_context(state):
            messages = state["messages"]
            # 간단한 감정 분석 등 추가 가능
            return {"context": {"timestamp": datetime.now().isoformat()}}
        
        # 대화 저장
        def save_conversation(state):
            st.session_state.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "messages": [msg.content for msg in state["messages"]]
            })
            return state
        
        # 그래프 생성
        workflow = Graph()
        workflow.add_node("process_message", process_message)
        workflow.add_node("analyze_context", analyze_context)
        workflow.add_node("save_conversation", save_conversation)
        
        # 엣지 연결
        workflow.add_edge("process_message", "analyze_context")
        workflow.add_edge("analyze_context", "save_conversation")
        
        return workflow.compile()
    
    def get_response(self, messages):
        state = {
            "messages": messages,
            "current_step": "start",
            "context": {}
        }
        return self.graph.invoke(state)

def main():
    st.title("고급 LangGraph 챗봇")
    
    # 사이드바 설정
    with st.sidebar:
        st.subheader("대화 기록")
        if st.button("대화 내보내기"):
            # JSON 형식으로 대화 내보내기
            st.download_button(
                label="Download JSON",
                data=json.dumps(st.session_state.conversation_history, indent=2),
                file_name="chat_history.json",
                mime="application/json"
            )
        
        # 대화 초기화 버튼
        if st.button("대화 초기화"):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
    
    # 챗봇 초기화
    chatbot = ChatBot()
    
    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
            st.write(message.content)
    
    # 사용자 입력 처리
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 메시지 추가
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        try:
            # 챗봇 응답 생성
            result = chatbot.get_response(st.session_state.messages)
            
            # 응답 저장 및 표시
            st.session_state.messages.append(result["messages"][-1])
            with st.chat_message("assistant"):
                st.write(result["messages"][-1].content)
        
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()