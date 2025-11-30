import streamlit as st
import time
from agents import OpenAIAgent, AnthropicAgent, GoogleGeminiAgent, MockAgent

st.set_page_config(page_title="AI Debate: Future of Ads", layout="wide")

st.title("🤖 AI Debate: The Present and Future of Advertising")

# Sidebar for Configuration
with st.sidebar:
    st.header("Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password")
    anthropic_key = st.text_input("Anthropic API Key", type="password")
    google_key = st.text_input("Google Gemini API Key", type="password")
    
    st.divider()
    st.markdown("### Roles")
    st.info("**OpenAI (Innovator)**: Optimistic about tech & AI.")
    st.info("**Anthropic (Skeptic)**: Cautious about privacy & ethics.")
    st.info("**Google (Strategist)**: Balanced, data-driven.")

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# Initialize Agents
def get_agents():
    agents = []
    
    # OpenAI Agent
    if openai_key:
        agents.append(OpenAIAgent("Innovator (OpenAI)", "You are an optimistic innovator. You believe AI and technology will revolutionize advertising for the better, making it more personalized and efficient. You are debating the future of advertising.", openai_key))
    else:
        agents.append(MockAgent("Innovator (Mock)", "Optimist"))

    # Anthropic Agent
    if anthropic_key:
        agents.append(AnthropicAgent("Skeptic (Anthropic)", "You are a skeptic. You are concerned about privacy, data ethics, and the intrusive nature of modern advertising. You advocate for consumer rights. You are debating the future of advertising.", anthropic_key))
    else:
        agents.append(MockAgent("Skeptic (Mock)", "Skeptic"))

    # Google Agent
    if google_key:
        agents.append(GoogleGeminiAgent("Strategist (Google)", "You are a strategist. You look at the market trends, data, and practical applications. You try to find a balance between innovation and user experience. You are debating the future of advertising.", google_key))
    else:
        agents.append(MockAgent("Strategist (Mock)", "Strategist"))
        
    return agents

agents = get_agents()

# Display Chat History
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Debate Controls
col1, col2 = st.columns(2)

with col1:
    if st.button("Start/Next Turn", type="primary"):
        # Determine whose turn it is
        current_agent_index = st.session_state.turn_count % len(agents)
        current_agent = agents[current_agent_index]
        
        # Construct context from recent history (last 5 messages to save tokens/keep context relevant)
        context = "Topic: The Present and Future of Advertising.\n\n"
        recent_history = st.session_state.history[-5:]
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
            
        if not st.session_state.history:
            context += "Start the debate with an opening statement."

        with st.spinner(f"{current_agent.name} is thinking..."):
            response = current_agent.generate_response(context)
        
        # Update State
        st.session_state.history.append({"role": current_agent.name, "content": response})
        st.session_state.turn_count += 1
        st.rerun()

with col2:
    if st.button("Reset Debate"):
        st.session_state.history = []
        st.session_state.turn_count = 0
        st.rerun()
