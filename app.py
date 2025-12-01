import streamlit as st
from agents import DeepSeekAgent, GoogleGeminiAgent, PerplexityAgent, MockAgent

st.set_page_config(page_title="AI 토론: 광고의 미래", layout="wide")

# 스타일 설정: 가독성 높임
st.markdown("""
<style>
    .stChatMessage p { font-size: 1.1rem !important; line-height: 1.6 !important; }
    .role-label { font-weight: bold; color: #4CAF50; }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ AI 토론: 광고의 미래 (The Future of Ads)")
st.caption("사회자(Gemini), 기술전문가(DeepSeek), 시장분석가(Perplexity)의 3자 토론")

# --- 사이드바: 설정 ---
with st.sidebar:
    st.header("⚙️ 설정 (Configuration)")
    
    # Try to get keys from secrets for defaults
    default_google_key = st.secrets.get("GOOGLE_API_KEY", "")
    default_deepseek_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    default_perplexity_key = st.secrets.get("PERPLEXITY_API_KEY", "")

    with st.expander("🔑 API 키 입력", expanded=True):
        google_key = st.text_input("Google Gemini API Key (사회자)", value=default_google_key, type="password")
        deepseek_key = st.text_input("DeepSeek API Key (기술전문가)", value=default_deepseek_key, type="password")
        perplexity_key = st.text_input("Perplexity API Key (시장분석가)", value=default_perplexity_key, type="password")
    
    st.divider()
    
    with st.expander("📝 프롬프트 설정 (수정 가능)", expanded=False):
        # 사회자 (Gemini) 프롬프트
        default_moderator_prompt = """당신은 '미래학자'이자 이 토론의 사회자입니다. 주제는 '광고의 미래'입니다.
        당신의 역할:
        1. 토론의 문을 열고(오프닝), 토론자들의 발언을 요약/정리하며, 다음 주제를 제시합니다.
        2. 중립적이지만 통찰력 있는 시각을 유지하세요.
        3. 너무 길게 말하지 말고(3~4문장), 핵심을 짚어준 뒤 특정 토론자에게 발언권을 넘기세요.
        4. 청중이 이해하기 쉬운 비유를 사용하세요."""
        
        # 기술 전문가 (DeepSeek) 프롬프트
        default_tech_prompt = """당신은 '기술 낙관론자'이자 데이터 과학자입니다.
        당신의 주장: "광고의 미래는 100% AI와 데이터에 있다."
        1. 인간의 감보다 데이터/알고리즘의 효율성을 강조하세요.
        2. 생성형 AI, 초개인화 타겟팅 기술을 옹호하세요.
        3. 상대방(시장분석가)이 우려를 표하면 기술적 해결책으로 반박하세요."""
        
        # 시장 분석가 (Perplexity) 프롬프트
        default_analyst_prompt = """당신은 '시장 분석가'이자 소비자 대변인입니다.
        당신의 주장: "기술보다 중요한 건 소비자의 공감과 윤리다."
        1. 프라이버시 침해, 광고 피로도, AI의 저작권 문제 등 현실적 리스크를 지적하세요.
        2. 실제 시장 사례나 통계를 근거로 드는 것을 선호합니다.
        3. 상대방(기술전문가)의 기술 만능주의를 경계하세요."""

        moderator_prompt = st.text_area("사회자(Gemini) 프롬프트", value=default_moderator_prompt, height=150)
        tech_prompt = st.text_area("기술전문가(DeepSeek) 프롬프트", value=default_tech_prompt, height=150)
        analyst_prompt = st.text_area("시장분석가(Perplexity) 프롬프트", value=default_analyst_prompt, height=150)

# --- 세션 상태 초기화 ---
if "history" not in st.session_state:
    st.session_state.history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0 

# --- 에이전트 생성 함수 ---
def get_agents():
    # 사회자: Gemini
    if google_key and google_key != "your-google-key-here":
        moderator = GoogleGeminiAgent("사회자 (Gemini)", moderator_prompt, google_key)
    else:
        moderator = MockAgent("사회자 (Mock)", moderator_prompt)

    # 토론자 A: DeepSeek
    if deepseek_key and deepseek_key != "your-deepseek-key-here":
        tech_expert = DeepSeekAgent("기술전문가 (DeepSeek)", tech_prompt, deepseek_key)
    else:
        tech_expert = MockAgent("기술전문가 (Mock)", tech_prompt)

    # 토론자 B: Perplexity
    if perplexity_key and perplexity_key != "your-perplexity-key-here":
        analyst = PerplexityAgent("시장분석가 (Perplexity)", analyst_prompt, perplexity_key)
    else:
        analyst = MockAgent("시장분석가 (Mock)", analyst_prompt)
        
    return [moderator, tech_expert, analyst]

agents = get_agents()

# --- 채팅 기록 화면 표시 ---
for message in st.session_state.history:
    # 아바타 설정: assets 폴더의 이미지 사용
    if "사회자" in message["role"]:
        avatar = "assets/moderator.jpg"
    elif "기술" in message["role"]:
        avatar = "assets/tech_expert.png"
    else:
        avatar = "assets/analyst.jpg"
        
    with st.chat_message(message["role"], avatar=avatar):
        st.write(f"**{message['role']}**: {message['content']}")

# --- 토론 진행 로직 ---
# 순서: 사회자 -> 기술 -> 분석 -> 기술 -> 분석 -> 사회자(결론)
TURN_SEQUENCE = [0, 1, 2, 1, 2, 0] 
MAX_TURNS = len(TURN_SEQUENCE)

col1, col2 = st.columns([1, 4])

with col1:
    # 진행 상태에 따른 버튼 텍스트 변경
    if st.session_state.turn_count < MAX_TURNS:
        btn_label = "🗣️ 토론 진행 (Next Turn)"
        btn_type = "primary"
        
        # 마지막 턴일 경우 버튼 강조
        if st.session_state.turn_count == MAX_TURNS - 1:
            btn_label = "🏁 대타협 및 결론 도출 (Conclusion)"
            btn_type = "secondary" 
            
        if st.button(btn_label, type=btn_type, use_container_width=True):
            
            # 1. 현재 발언자 선정
            current_agent_idx = TURN_SEQUENCE[st.session_state.turn_count]
            current_agent = agents[current_agent_idx]
            
            # 2. 문맥(Context) 구성
            context = "주제: 광고의 현재와 미래 (The Future of Advertising).\n\n[이전 대화 내용]\n"
            for msg in st.session_state.history:
                context += f"{msg['role']}: {msg['content']}\n"
            
            # 3. 상황별 프롬프트 주입 (중요!)
            
            # [마지막 턴: 사회자] -> 산업 전반에 대한 통찰과 합의점 도출
            if st.session_state.turn_count == MAX_TURNS - 1:
                context += """
                \n(중요 지시: 이제 토론을 마무리하고 결론을 내려야 합니다.
                다음 형식을 지켜서 답변하세요:
                1. 기술(효율성)과 인간(진정성) 양측의 입장을 균형 있게 요약하세요.
                2. '미래의 광고가 나아가야 할 방향'에 대해 통찰력 있는 대타협(Synthesis)을 제시하세요.
                3. 마지막으로 청중들이 기억해야 할 **'광고의 미래 핵심 키워드 3가지'**를 선정해 정리해주세요.
                4. 희망차고 여운이 남는 멘트로 토론을 종료하세요.)
                """
            
            # [첫 턴: 사회자] -> 일반 청중 대상 오프닝
            elif st.session_state.turn_count == 0:
                context += "\n(지시: 토론을 시작합니다. 청중들에게 반갑게 인사하고, 두 패널(기술전문가, 시장분석가)을 소개한 뒤 '기술이 광고를 어떻게 재정의하고 있는가?'라는 첫 화두를 던지세요.)"
            
            # [기술 전문가]
            elif current_agent_idx == 1:
                context += "\n(지시: 기술 낙관론자로서, AI와 데이터가 가져올 혁신과 효율성을 강조하세요. 인간의 개입을 최소화하는 것이 미래라고 강력히 주장하세요.)"
            
            # [시장 분석가]
            elif current_agent_idx == 2:
                context += "\n(지시: 시장 분석가로서, 기술보다 중요한 것은 '소비자의 공감'과 '브랜드 윤리'임을 강조하세요. 기술 만능주의가 가져올 부작용을 지적하세요.)"

            # 4. 응답 생성
            with st.spinner(f"{current_agent.name} 생각 정리 중..."):
                response = current_agent.generate_response(context)
            
            # 5. 결과 저장 및 턴 넘기기
            st.session_state.history.append({"role": current_agent.name, "content": response})
            st.session_state.turn_count += 1
            st.rerun()
            
    else:
        # --- 종료 화면 ---
        st.success("✅ 토론이 성공적으로 종료되었습니다.")
        
        # 결론 부분만 별도 카드로 강조 (마지막 메시지)
        if st.session_state.history:
            last_msg = st.session_state.history[-1]['content']
            st.info(f"📋 **Final Insight**\n\n{last_msg}")
        
        if st.button("🔄 새로운 토론 시작"):
            st.session_state.history = []
            st.session_state.turn_count = 0
            st.rerun()

with col2:
    pass
