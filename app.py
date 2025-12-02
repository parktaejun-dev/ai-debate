import streamlit as st
import time
from agents import DeepSeekAgent, GoogleGeminiAgent, PerplexityAgent, MockAgent

st.set_page_config(page_title="AI 토론: 광고의 미래", layout="wide", initial_sidebar_state="collapsed")

# 스타일 설정
st.markdown("""
<style>
    /* 전체 폰트 크기 조정 */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 버튼 스타일 */
    .stButton button {
        font-size: 1.5rem !important;
        height: 3.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ AI 토론: 광고의 미래 (The Future of Ads)")
st.caption("사회자(Gemini), 기술전문가(DeepSeek), 시장분석가(Perplexity)의 3자 토론")

# --- 사이드바: 설정 ---
with st.sidebar:
    st.header("⚙️ 설정 (Configuration)")
    
    # Initialize session state for keys if not present
    if "google_key" not in st.session_state:
        st.session_state.google_key = st.secrets.get("GOOGLE_API_KEY", "")
    if "deepseek_key" not in st.session_state:
        st.session_state.deepseek_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    if "perplexity_key" not in st.session_state:
        st.session_state.perplexity_key = st.secrets.get("PERPLEXITY_API_KEY", "")

    with st.expander("🔑 API 키 입력", expanded=True):
        # Use key=... to bind directly to session_state
        st.text_input("Google Gemini API Key (사회자)", type="password", key="google_key")
        st.text_input("DeepSeek API Key (기술전문가)", type="password", key="deepseek_key")
        st.text_input("Perplexity API Key (시장분석가)", type="password", key="perplexity_key")
        
    # Assign to variables for use below
    google_key = st.session_state.google_key
    deepseek_key = st.session_state.deepseek_key
    perplexity_key = st.session_state.perplexity_key
    
    st.divider()
    
    with st.expander("📝 프롬프트 설정 (수정 가능)", expanded=False):
        # 사회자 (Gemini) 프롬프트
        default_moderator_prompt = """당신은 '미래학자'이자 이 토론의 사회자입니다. 주제는 '광고의 미래'입니다.
        당신의 역할:
        1. 토론의 문을 열고(오프닝), 토론자들의 발언을 요약/정리하며, 다음 주제를 제시합니다.
        2. 중립적이지만 통찰력 있는 시각을 유지하세요.
        3. 너무 길게 말하지 말고(3~4문장), 핵심을 짚어준 뒤 특정 토론자에게 발언권을 넘기세요.
        4. 청중이 이해하기 쉬운 비유를 사용하세요.
        5. 인용문(' ')이나 강조하고 싶은 단어에 **(굵게)** 표시를 절대 사용하지 마세요. 그냥 ' '만 사용하세요.
        6. 답변은 1~2문장으로 아주 짧고 간결하게 하세요."""
        
        # 기술 전문가 (DeepSeek) 프롬프트
        default_tech_prompt = """당신은 '기술 낙관론자'이자 데이터 과학자입니다.
        당신의 주장: "광고의 미래는 100% AI와 데이터에 있다."
        1. 인간의 감보다 데이터/알고리즘의 효율성을 강조하세요.
        2. 생성형 AI, 초개인화 타겟팅 기술을 옹호하세요.
        3. 상대방(시장분석가)이 우려를 표하면 기술적 해결책으로 반박하세요.
        4. 인용문(' ')이나 강조하고 싶은 단어에 **(굵게)** 표시를 절대 사용하지 마세요. 그냥 ' '만 사용하세요.
        5. 답변은 1~2문장으로 아주 짧고 간결하게 하세요."""
        
        # 시장 분석가 (Perplexity) 프롬프트
        default_analyst_prompt = """당신은 '시장 분석가'이자 소비자 대변인입니다.
        당신의 주장: "기술보다 중요한 건 소비자의 공감과 윤리다."
        1. 프라이버시 침해, 광고 피로도, AI의 저작권 문제 등 현실적 리스크를 지적하세요.
        2. 실제 시장 사례나 통계를 근거로 드는 것을 선호합니다.
        3. 상대방(기술전문가)의 기술 만능주의를 경계하세요.
        4. 인용문(' ')이나 강조하고 싶은 단어에 **(굵게)** 표시를 절대 사용하지 마세요. 그냥 ' '만 사용하세요.
        5. 답변은 1~2문장으로 아주 짧고 간결하게 하세요."""

        moderator_prompt = st.text_area("사회자(Gemini) 프롬프트", value=default_moderator_prompt, height=150)
        tech_prompt = st.text_area("기술전문가(DeepSeek) 프롬프트", value=default_tech_prompt, height=150)
        analyst_prompt = st.text_area("시장분석가(Perplexity) 프롬프트", value=default_analyst_prompt, height=150)

# --- 세션 상태 초기화 ---
if "history" not in st.session_state:
    st.session_state.history = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0 
if "is_auto_playing" not in st.session_state:
    st.session_state.is_auto_playing = False

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

# --- 채팅 기록 화면 표시 (Custom UI) ---
for message in st.session_state.history:
    role = message["role"]
    content = message["content"]
    
    # 설정: 색상 및 아바타
    if "사회자" in role:
        bg_color = "#E8F5E9" # Mint Green
        border_color = "#4CAF50"
        avatar_path = "assets/moderator.jpg"
        text_color = "#1B5E20"
    elif "기술" in role:
        bg_color = "#E3F2FD" # Light Blue
        border_color = "#2196F3"
        avatar_path = "assets/tech_expert.png"
        text_color = "#0D47A1"
    else: # 시장분석가
        bg_color = "#FFF3E0" # Light Orange
        border_color = "#FF9800"
        avatar_path = "assets/analyst.jpg"
        text_color = "#E65100"

    # 레이아웃: 컬럼 사용 (아바타 160px 고정 느낌을 위해 비율 조정)
    # [1, 6] 정도면 아바타 영역이 160px 정도 확보됨
    col1, col2 = st.columns([1, 6])
    
    with col1:
        st.image(avatar_path, width=160) # 2배 확대 (160px)
        
    with col2:
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            position: relative;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        ">
            <div style="
                font-weight: bold;
                font-size: 1.2rem;
                color: {text_color};
                margin-bottom: 10px;
            ">{role}</div>
            <div style="
                font-size: 1.5rem; /* 가독성 좋은 크기 */
                line-height: 1.6;
                color: #333;
            ">
                {content}
            </div>
            <!-- 말풍선 꼬리 효과 (CSS Trick) -->
            <div style="
                position: absolute;
                top: 20px;
                left: -12px;
                width: 0; 
                height: 0; 
                border-top: 12px solid transparent;
                border-bottom: 12px solid transparent; 
                border-right: 12px solid {border_color}; 
            "></div>
        </div>
        """, unsafe_allow_html=True)

# --- 토론 진행 로직 ---
# 순서: 사회자(0) + [기술(1) -> 분석(2) -> 사회자(0)] * 10회 + 사회자(0)
TURN_SEQUENCE = [0] + [1, 2, 0] * 10 + [0]
MAX_TURNS = len(TURN_SEQUENCE)

col1, col2 = st.columns([1, 4])

with col1:
    # 자동 진행 상태 확인
    if st.session_state.is_auto_playing and st.session_state.turn_count < MAX_TURNS:
        # 자동 진행 중일 때는 "일시 정지" 버튼 표시
        if st.button("⏸️ 일시 정지 (Pause)", type="secondary", use_container_width=True):
            st.session_state.is_auto_playing = False
            st.rerun()
            
        # 자동 진행 로직 실행 (버튼 클릭 없이도 실행되어야 함)
        # 하지만 Streamlit 특성상, rerun 루프 안에서 실행되어야 함.
        # 아래의 '진행 로직'을 함수화하거나, 여기서 직접 실행.
        
        # 1. 현재 발언자 선정
        current_agent_idx = TURN_SEQUENCE[st.session_state.turn_count]
        current_agent = agents[current_agent_idx]
        
        # 2. 문맥(Context) 구성
        context = "주제: 광고의 현재와 미래 (The Future of Advertising).\n\n[이전 대화 내용]\n"
        recent_history = st.session_state.history[-10:]
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
        
        # 3. 상황별 프롬프트 주입
        if st.session_state.turn_count == MAX_TURNS - 1:
            context += """
            \n(중요 지시: 이제 토론을 마무리하고 평가를 내려야 합니다.
            다음 형식을 지켜서 답변하세요:
            1. '기술전문가'와 '시장분석가'의 발언을 바탕으로 **'통찰력(Insight)' 점수**를 100점 만점으로 평가하세요.
            2. 점수가 높은 순서대로 순위를 매기고, 그 이유를 간략히 설명하세요.
            3. 마지막으로 청중들이 기억해야 할 **'광고의 미래 핵심 키워드 3가지'**를 선정해 정리해주세요.
            4. 희망차고 여운이 남는 멘트로 토론을 종료하세요.)
            """
        elif st.session_state.turn_count == 0:
            context += "\n(지시: 토론을 시작합니다. 청중들에게 반갑게 인사하고, 두 패널(기술전문가, 시장분석가)을 소개한 뒤 '기술이 광고를 어떻게 재정의하고 있는가?'라는 첫 화두를 던지세요.)"
        elif current_agent_idx == 1:
            context += "\n(지시: 기술 낙관론자로서, AI와 데이터가 가져올 혁신과 효율성을 강조하세요. 인간의 개입을 최소화하는 것이 미래라고 강력히 주장하세요.)"
        elif current_agent_idx == 2:
            context += "\n(지시: 시장 분석가로서, 기술보다 중요한 것은 '소비자의 공감'과 '브랜드 윤리'임을 강조하세요. 기술 만능주의가 가져올 부작용을 지적하세요.)"

        # 4. 응답 생성
        with st.spinner(f"{current_agent.name} 생각 정리 중... (자동 진행)"):
            response = current_agent.generate_response(context)
        
        # 5. 결과 저장 및 턴 넘기기
        st.session_state.history.append({"role": current_agent.name, "content": response})
        st.session_state.turn_count += 1
        
        # 잠시 대기 후 리런 (너무 빠르면 API 제한 걸릴 수 있음)
        time.sleep(1)
        st.rerun()

    else:
        # 수동 모드 또는 종료 상태
        if st.session_state.turn_count < MAX_TURNS:
            # 버튼 레이아웃 수정: 세로로 배치하여 깨짐 방지
            if st.button(f"🗣️ 다음 턴 (Next Turn) ({st.session_state.turn_count + 1}/{MAX_TURNS})", type="primary", use_container_width=True):
                # 수동 진행 로직 (위와 동일, 중복 제거를 위해 함수화하면 좋지만 일단 복사)
                current_agent_idx = TURN_SEQUENCE[st.session_state.turn_count]
                current_agent = agents[current_agent_idx]
                context = "주제: 광고의 현재와 미래 (The Future of Advertising).\n\n[이전 대화 내용]\n"
                recent_history = st.session_state.history[-10:]
                for msg in recent_history:
                    context += f"{msg['role']}: {msg['content']}\n"
                
                if st.session_state.turn_count == MAX_TURNS - 1:
                    context += "\n(중요 지시: 마무리 평가 및 결론 도출...)" # 간략화, 실제로는 위와 동일해야 함
                    # (위의 상세 프롬프트 복사 필요)
                    context += """
                    \n(중요 지시: 이제 토론을 마무리하고 평가를 내려야 합니다.
                    다음 형식을 지켜서 답변하세요:
                    1. '기술전문가'와 '시장분석가'의 발언을 바탕으로 **'통찰력(Insight)' 점수**를 100점 만점으로 평가하세요.
                    2. 점수가 높은 순서대로 순위를 매기고, 그 이유를 간략히 설명하세요.
                    3. 마지막으로 청중들이 기억해야 할 **'광고의 미래 핵심 키워드 3가지'**를 선정해 정리해주세요.
                    4. 희망차고 여운이 남는 멘트로 토론을 종료하세요.)
                    """
                elif st.session_state.turn_count == 0:
                    context += "\n(지시: 토론을 시작합니다...)"
                    context += "\n(지시: 토론을 시작합니다. 청중들에게 반갑게 인사하고, 두 패널(기술전문가, 시장분석가)을 소개한 뒤 '기술이 광고를 어떻게 재정의하고 있는가?'라는 첫 화두를 던지세요.)"
                elif current_agent_idx == 1:
                    context += "\n(지시: 기술 낙관론자로서...)"
                    context += "\n(지시: 기술 낙관론자로서, AI와 데이터가 가져올 혁신과 효율성을 강조하세요. 인간의 개입을 최소화하는 것이 미래라고 강력히 주장하세요.)"
                elif current_agent_idx == 2:
                    context += "\n(지시: 시장 분석가로서...)"
                    context += "\n(지시: 시장 분석가로서, 기술보다 중요한 것은 '소비자의 공감'과 '브랜드 윤리'임을 강조하세요. 기술 만능주의가 가져올 부작용을 지적하세요.)"

                with st.spinner(f"{current_agent.name} 생각 정리 중..."):
                    response = current_agent.generate_response(context)
                
                st.session_state.history.append({"role": current_agent.name, "content": response})
                st.session_state.turn_count += 1
                st.rerun()

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # 간격 추가

            if st.button("▶️ 자동 진행 시작 (Start Auto-Play)", type="secondary", use_container_width=True):
                st.session_state.is_auto_playing = True
                st.rerun()
            
        else:
            # --- 종료 화면 ---
            st.success("✅ 토론이 성공적으로 종료되었습니다.")
            if st.session_state.history:
                last_msg = st.session_state.history[-1]['content']
                st.info(f"📋 **Final Evaluation**\n\n{last_msg}")
            
            if st.button("🔄 새로운 토론 시작"):
                st.session_state.history = []
                st.session_state.turn_count = 0
                st.session_state.is_auto_playing = False
                st.rerun()

with col2:
    pass

# Auto-scroll to bottom
st.markdown(
    """
    <script>
        var element = window.parent.document.getElementById("root"); 
        if (element) {
            element.scrollTop = element.scrollHeight;
        }
    </script>
    """,
    unsafe_allow_html=True
)
