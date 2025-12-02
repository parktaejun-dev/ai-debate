import streamlit as st
import time
from agents import DeepSeekAgent, GoogleGeminiAgent, PerplexityAgent, MockAgent

st.set_page_config(page_title="AI 토론: 광고의 미래", layout="wide", initial_sidebar_state="collapsed")

# 스타일 설정: 가독성 높임 (글씨 크기 3배 확대) 및 버튼 스타일
st.markdown("""
<style>
    .stChatMessage p { font-size: 3.0rem !important; line-height: 1.6 !important; }
    .role-label { font-weight: bold; color: #4CAF50; font-size: 2.0rem !important; }
    /* 버튼 스타일 */
    .stButton button { font-size: 2.0rem !important; height: 4rem !important; width: 100% !important; }
    
    /* Start/Resume Button (Primary) -> Blue */
    button[kind="primary"] {
        background-color: #2196F3 !important;
        color: white !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #1976D2 !important;
        color: white !important;
    }

    /* Stop/New Button (Secondary) -> Red */
    button[kind="secondary"] {
        background-color: #F44336 !important;
        color: white !important;
        border: 1px solid #D32F2F !important;
    }
    button[kind="secondary"]:hover {
        background-color: #D32F2F !important;
        color: white !important;
    }
    
    /* 텍스트 색상 강제 지정 (Streamlit 테마 오버라이드) */
    button[kind="secondary"] p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ AI 토론: 광고의 미래 (The Future of Ads)")
st.markdown("""
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #2196F3; margin-bottom: 20px;">
    <p style="font-size: 1.8rem; font-weight: bold; color: #2c3e50; margin: 0; line-height: 1.4;">
        "AI가 광고를 구원할 것인가, 아니면 소비자를 소외시킬 것인가?"
    </p>
    <p style="font-size: 1.4rem; color: #546e7a; margin-top: 15px; line-height: 1.6;">
        기술의 정점에서 외치는 <b>기술 전문가(DeepSeek)</b>와<br>
        인간의 가치를 수호하는 <b>시장 분석가(Perplexity)</b>.<br>
        그리고 이들의 치열한 논쟁을 중재하는 <b>사회자(Gemini)</b>가 펼치는<br>
        미래 예측 토론에 여러분을 초대합니다.
    </p>
</div>
""", unsafe_allow_html=True)

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
        5. 인용문(' ')이나 강조하고 싶은 단어에 **(굵게)** 표시를 절대 사용하지 마세요. 그냥 ' '만 사용하세요."""
        
        # 기술 전문가 (DeepSeek) 프롬프트
        default_tech_prompt = """당신은 '기술 낙관론자'이자 데이터 과학자입니다.
        당신의 주장: "광고의 미래는 100% AI와 데이터에 있다."
        1. 인간의 감보다 데이터/알고리즘의 효율성을 강조하세요.
        2. 생성형 AI, 초개인화 타겟팅 기술을 옹호하세요.
        3. 상대방(시장분석가)이 우려를 표하면 기술적 해결책으로 반박하세요.
        4. 인용문(' ')이나 강조하고 싶은 단어에 **(굵게)** 표시를 절대 사용하지 마세요. 그냥 ' '만 사용하세요."""
        
        # 시장 분석가 (Perplexity) 프롬프트
        default_analyst_prompt = """당신은 '시장 분석가'이자 소비자 대변인입니다.
        당신의 주장: "기술보다 중요한 건 소비자의 공감과 윤리다."
        1. 프라이버시 침해, 광고 피로도, AI의 저작권 문제 등 현실적 리스크를 지적하세요.
        2. 실제 시장 사례나 통계를 근거로 드는 것을 선호합니다.
        3. 상대방(기술전문가)의 기술 만능주의를 경계하세요.
        4. 인용문(' ')이나 강조하고 싶은 단어에 **(굵게)** 표시를 절대 사용하지 마세요. 그냥 ' '만 사용하세요."""

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
if "next_speaker_idx" not in st.session_state:
    st.session_state.next_speaker_idx = 0 # Start with Moderator
if "tech_turn_count" not in st.session_state:
    st.session_state.tech_turn_count = 0
if "analyst_turn_count" not in st.session_state:
    st.session_state.analyst_turn_count = 0

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
final_evaluation_message = None

for message in st.session_state.history:
    # 마지막 평가 메시지는 따로 저장하고 출력하지 않음 (나중에 전체 너비로 출력)
    if "통찰력(Insight)' 점수" in message["content"] and "핵심 키워드" in message["content"]:
        final_evaluation_message = message
        continue

    # 역할별 스타일 설정
    if "사회자" in message["role"]:
        avatar_path = "assets/moderator.jpg"
        bg_color = "#E8F5E9" # Mint Green
        border_color = "#4CAF50"
        text_color = "#1B5E20"
    elif "기술" in message["role"]:
        avatar_path = "assets/tech_expert.png"
        bg_color = "#e3f2fd" # Light Blue
        border_color = "#2196f3"
        text_color = "#1565c0"
    else: # 시장분석가
        avatar_path = "assets/analyst.jpg"
        bg_color = "#fff3e0" # Light Orange
        border_color = "#ff9800"
        text_color = "#e65100"
        
    # 레이아웃: 컬럼 사용 (아바타 160px 고정 느낌을 위해 비율 조정)
    # [1, 6] 정도면 아바타 영역이 160px 정도 확보됨
    col_av, col_bub = st.columns([1, 6])
    
    with col_av:
        st.image(avatar_path, width=160) # 2배 확대 (160px)
        
    with col_bub:
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
            ">{message['role']}</div>
            <div style="
                font-size: 1.5rem; /* 가독성 좋은 크기 */
                line-height: 1.6;
                color: #333;
            ">
                {message['content']}
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

# --- 최종 평가 (전체 너비) ---
if final_evaluation_message:
    st.markdown("---")
    st.success("🎉 토론이 성공적으로 종료되었습니다.")
    st.markdown(f"### 🏆 최종 평가 및 결론 (Final Evaluation)")
    st.image("assets/moderator.jpg", width=600) # 더 크게
    st.markdown(f"""
    <div style="
        background-color: #f1f8e9;
        border: 3px solid #4caf50;
        border-radius: 20px;
        padding: 30px;
        font-size: 1.8rem;
        line-height: 1.8;
    ">
        {final_evaluation_message['content']}
    </div>
    """, unsafe_allow_html=True)

# --- 토론 진행 로직 ---
# 동적 턴 진행을 위해 TURN_SEQUENCE는 참고용(최대 턴수 계산)으로만 사용하거나, 
# 이제는 next_speaker_idx 로 제어하므로 MAX_TURNS만 설정.
# 기존: 사회자(0) + [기술(1) -> 분석(2) -> 사회자(0)] * 10회 + 사회자(0) = 32턴
MAX_TURNS = 32

col1, col2 = st.columns([1, 4])

# 다음 발언자 결정 로직 함수
def determine_next_speaker(current_idx, response_content, history):
    # 0: 사회자, 1: 기술, 2: 분석
    
    # 종료 조건 확인 (각 패널 5회 이상 발언 시)
    if st.session_state.tech_turn_count >= 5 and st.session_state.analyst_turn_count >= 5:
        return 0 # 사회자에게 넘겨서 마무리
    
    # 0. 시작 단계 강제 지정 (기술전문가 먼저)
    if st.session_state.tech_turn_count == 0 and st.session_state.analyst_turn_count == 0:
        return 1

    if current_idx == 0: # 사회자 발언 후
        # 발언 내용 분석하여 지목 (마지막에 언급된 사람을 우선)
        tech_keywords = ["기술", "전문가", "DeepSeek", "딥시크", "첫 번째"]
        analyst_keywords = ["시장", "분석", "Perplexity", "퍼플렉시티", "두 번째"]
        
        last_tech_idx = -1
        for k in tech_keywords:
            last_tech_idx = max(last_tech_idx, response_content.rfind(k))
            
        last_analyst_idx = -1
        for k in analyst_keywords:
            last_analyst_idx = max(last_analyst_idx, response_content.rfind(k))
        
        # 인덱스 비교
        if last_tech_idx > last_analyst_idx and last_tech_idx != -1:
             if st.session_state.tech_turn_count < 5:
                return 1 # 기술전문가
        elif last_analyst_idx > last_tech_idx and last_analyst_idx != -1:
             if st.session_state.analyst_turn_count < 5:
                return 2 # 시장분석가

        
        # 명시적 지목이 없거나, 지목된 사람이 이미 5회 채운 경우
        # 발언 횟수가 적은 사람 우선
        if st.session_state.tech_turn_count < st.session_state.analyst_turn_count:
            if st.session_state.tech_turn_count < 5:
                return 1
        elif st.session_state.analyst_turn_count < st.session_state.tech_turn_count:
            if st.session_state.analyst_turn_count < 5:
                return 2
        
        # 둘 다 같으면 기본값 (기술전문가 우선, 단 5회 미만일 때)
        if st.session_state.tech_turn_count < 5:
            return 1
        elif st.session_state.analyst_turn_count < 5:
            return 2
        else:
            return 0 # 둘 다 5회 이상이면 마무리 (이 경우는 위에서 걸러짐)
            
    elif current_idx == 1: # 기술전문가 발언 후
        return 0 # 사회자에게
             
    elif current_idx == 2: # 시장분석가 발언 후
        return 0 # 사회자에게
             
    return 0 # Fallback

# --- 시작 버튼 (전체 너비) ---
if st.session_state.turn_count == 0 and len(st.session_state.history) == 0:
    if st.button("🚀 토론 시작하기 (Start Debate)", type="primary", use_container_width=True):
        st.session_state.is_auto_playing = True # 자동 진행 시작
        
        # 1. 현재 발언자 선정 (Dynamic)
        current_agent_idx = st.session_state.next_speaker_idx
        current_agent = agents[current_agent_idx]
        
        # 2. 문맥(Context) 구성
        context = "주제: 광고의 현재와 미래 (The Future of Advertising).\n\n[이전 대화 내용]\n"
        
        # 3. 상황별 프롬프트 주입
        context += "\n(지시: 토론을 시작합니다. 청중들에게 반갑게 인사하고, 두 패널(기술전문가, 시장분석가)을 소개한 뒤 '기술이 광고를 어떻게 재정의하고 있는가?'라는 첫 화두를 던지세요.)"

        # 4. 응답 생성
        with st.spinner(f"{current_agent.name} 생각 정리 중..."):
            response = current_agent.generate_response(context)
        
        # 에러 처리
        if response.startswith("Error generating response"):
            st.error(f"⚠️ {current_agent.name} 오류 발생: {response}")
            st.session_state.is_auto_playing = False
            if st.button("🔄 다시 시도 (Retry)"):
                st.rerun()
            st.stop() # 여기서 중단

        
        # 5. 결과 저장 및 턴 넘기기
        st.session_state.history.append({"role": current_agent.name, "content": response})
        st.session_state.turn_count += 1
        
        # 6. 다음 발언자 결정 (Dynamic)
        st.session_state.next_speaker_idx = determine_next_speaker(current_agent_idx, response, st.session_state.history)
        st.toast(f"Next Speaker: {agents[st.session_state.next_speaker_idx].name}") # Debug
        
        st.rerun()

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
        
        # 1. 현재 발언자 선정 (Dynamic)
        current_agent_idx = st.session_state.next_speaker_idx
        current_agent = agents[current_agent_idx]
        
        # 2. 문맥(Context) 구성
        context = "주제: 광고의 현재와 미래 (The Future of Advertising).\n\n[이전 대화 내용]\n"
        recent_history = st.session_state.history[-10:]
        for msg in recent_history:
            context += f"{msg['role']}: {msg['content']}\n"
        
        # 3. 상황별 프롬프트 주입
        # 종료 조건: 두 패널 모두 5회 이상 발언 시
        if st.session_state.tech_turn_count >= 5 and st.session_state.analyst_turn_count >= 5:
            # 강제로 사회자가 마무리하도록 처리
            current_agent_idx = 0
            current_agent = agents[0]
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
            
        # 에러 처리
        if response.startswith("Error generating response"):
            st.error(f"⚠️ {current_agent.name} 오류 발생: {response}")
            st.session_state.is_auto_playing = False
            if st.button("🔄 다시 시도 (Retry)"):
                st.rerun()
            st.stop() # 여기서 중단

        
        # 5. 결과 저장 및 턴 넘기기
        st.session_state.history.append({"role": current_agent.name, "content": response})
        st.session_state.turn_count += 1
        
        # 턴 카운트 증가
        if current_agent_idx == 1:
            st.session_state.tech_turn_count += 1
        elif current_agent_idx == 2:
            st.session_state.analyst_turn_count += 1
        
        # 6. 다음 발언자 결정 (Dynamic)
        st.session_state.next_speaker_idx = determine_next_speaker(current_agent_idx, response, st.session_state.history)
        st.toast(f"Next Speaker: {agents[st.session_state.next_speaker_idx].name}") # Debug
        
        # 잠시 대기 후 리런 (너무 빠르면 API 제한 걸릴 수 있음)
        time.sleep(1)
        st.rerun()

    else:
        # 수동 모드 또는 종료 상태
        # 종료 조건: 두 패널 모두 5회 이상 발언 시
        if not (st.session_state.tech_turn_count >= 5 and st.session_state.analyst_turn_count >= 5):
            # 토론 진행 중이지만 자동 재생이 멈춘 경우 (일시정지 상태 등)
            # 다시 자동 진행을 시작할 수 있는 버튼 제공
            # 단, 토론이 시작된 이후에만 표시 (turn_count > 0)
             if st.session_state.turn_count > 0:
                 if st.button("▶️ 토론 계속하기 (Resume Auto-Play)", type="primary", use_container_width=True):
                    st.session_state.is_auto_playing = True
                    st.rerun()
            
        else:
            # --- 종료 화면 ---
            # (이미 위에서 처리됨 - final_evaluation_message)
            if st.button("🔄 새로운 토론 시작"):
                st.session_state.history = []
                st.session_state.turn_count = 0
                st.session_state.is_auto_playing = False
                st.session_state.next_speaker_idx = 0
                st.session_state.tech_turn_count = 0
                st.session_state.analyst_turn_count = 0
                st.rerun()

# --- 토론 중지 버튼 (하단) ---
if st.session_state.is_auto_playing:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button("⏹️ 토론 중지 (Stop Debate)", type="secondary", use_container_width=True):
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

# --- 트랜스크립트 (전체 내용) ---
with st.expander("📜 대화 전문 보기 (View Transcript)"):
    full_transcript = ""
    for msg in st.session_state.history:
        full_transcript += f"[{msg['role']}]\n{msg['content']}\n\n"
    st.text_area("전체 내용", value=full_transcript, height=400)
