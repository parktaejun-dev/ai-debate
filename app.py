import streamlit as st
import time
from agents import DeepSeekAgent, GoogleGeminiAgent, PerplexityAgent, MockAgent

st.set_page_config(page_title="AI Debate: Future of Ads", layout="wide")

st.title("🤖 AI 토론: 광고의 현재와 미래")

# Sidebar for Configuration
with st.sidebar:
    st.header("설정 (Configuration)")
    
    with st.expander("API 키 설정 (API Keys)", expanded=True):
        deepseek_key = st.text_input("DeepSeek API Key", type="password")
        google_key = st.text_input("Google Gemini API Key", type="password")
        perplexity_key = st.text_input("Perplexity API Key", type="password")
    
    st.divider()
    st.header("프롬프트 설정 (System Prompts)")
    
    # Default Prompts in Korean
    default_deepseek_prompt = "당신은 기술 분석가(Analyst)입니다. 광고 시장의 기술적 기반, 알고리즘, 데이터 처리 방식, 그리고 기술적 실현 가능성에 초점을 맞춥니다. 논리적이고 분석적인 태도로 토론에 참여하세요."
    default_google_prompt = "당신은 창의적인 비전가(Creative Visionary)입니다. 사용자 경험(UX), 스토리텔링, 그리고 새로운 광고 포맷의 창의적 잠재력에 초점을 맞춥니다. 감성적이고 미래지향적인 태도로 토론에 참여하세요."
    default_perplexity_prompt = "당신은 팩트 중심의 연구원(Researcher)입니다. 시장 통계, 실제 사례, 데이터, 그리고 검증된 사실에 초점을 맞춥니다. 객관적이고 근거 중심적인 태도로 토론에 참여하세요."

    deepseek_prompt = st.text_area("DeepSeek (딥씨크) 프롬프트", value=default_deepseek_prompt, height=150)
    google_prompt = st.text_area("Google Gemini (제미나이) 프롬프트", value=default_google_prompt, height=150)
    perplexity_prompt = st.text_area("Perplexity (퍼플렉시티) 프롬프트", value=default_perplexity_prompt, height=150)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# Initialize Agents
def get_agents():
    agents = []
    
    # DeepSeek Agent
    if deepseek_key:
        agents.append(DeepSeekAgent("Analyst (DeepSeek)", deepseek_prompt, deepseek_key))
    else:
        agents.append(MockAgent("Analyst (Mock)", deepseek_prompt))

    # Google Agent
    if google_key:
        agents.append(GoogleGeminiAgent("Creative (Google)", google_prompt, google_key))
    else:
        agents.append(MockAgent("Creative (Mock)", google_prompt))

    # Perplexity Agent
    if perplexity_key:
        agents.append(PerplexityAgent("Researcher (Perplexity)", perplexity_prompt, perplexity_key))
    else:
        agents.append(MockAgent("Researcher (Mock)", perplexity_prompt))
        
    return agents

agents = get_agents()

# Display Chat History
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Debate Controls
col1, col2 = st.columns(2)

with col1:
    if st.button("토론 시작 / 다음 발언 (Start/Next Turn)", type="primary"):
        # Determine whose turn it is
        current_agent_index = st.session_state.turn_count % len(agents)
        current_agent = agents[current_agent_index]
        
        # Construct context from recent history
        context = "주제: 광고의 현재와 미래 (The Present and Future of Advertising).\n\n"
        recent_history = st.session_state.history[-5:]
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
            
        if not st.session_state.history:
            context += "첫 발언을 시작해주세요."

        with st.spinner(f"{current_agent.name} 생각 중..."):
            response = current_agent.generate_response(context)
        
        # Update State
        st.session_state.history.append({"role": current_agent.name, "content": response})
        st.session_state.turn_count += 1
        st.rerun()

with col2:
    if st.button("토론 초기화 (Reset Debate)"):
        st.session_state.history = []
        st.session_state.turn_count = 0
        st.rerun()
