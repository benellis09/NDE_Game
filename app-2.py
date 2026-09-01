import streamlit as st
from game_engine import get_ndt_question

# ==========================================
# 0. INJECT RETRO SUPER MARIO BROS CSS CODES
# ==========================================
st.set_page_config(layout="wide")

st.markdown("""
<style>
    /* Import retro arcade font */
    @import url('https://googleapis.com');

    /* Global Typography & Theme Colors */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #5c94fc !important; /* Classic Mario sky blue */
        font-family: 'Press Start 2P', monospace !important;
        color: #ffffff !important;
    }

    /* Target headers and force text styling */
    h1, h2, h3, h4, p, span, label {
        font-family: 'Press Start 2P', monospace !important;
        color: #ffffff !important;
        text-shadow: 2px 2px 0px #000000 !important; /* 3D black outline text */
    }

    /* Style the main dashboard metric containers */
    [data-testid="stMetricValue"] div {
        font-family: 'Press Start 2P', monospace !important;
        font-size: 1.25rem !important;
        color: #fce4a0 !important; /* Retro gold text */
        text-shadow: 2px 2px 0px #000000 !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 0.65rem !important;
        color: #ffcccc !important;
    }

    /* Style Streamlit Buttons into Retro UI Panels */
    div.stButton > button {
        background-color: #b84418 !important; /* Brick red */
        color: #ffffff !important;
        border: 4px solid #000000 !important;
        border-radius: 0px !important; /* Pixel perfect sharp corners */
        font-family: 'Press Start 2P', monospace !important;
        font-size: 0.75rem !important;
        padding: 12px 10px !important;
        text-shadow: 1px 1px 0px #000000 !important;
        box-shadow: 4px 4px 0px #000000 !important; /* Hard 3D shadow */
        transition: transform 0.1s, box-shadow 0.1s;
    }

    /* Button Hover & Active States */
    div.stButton > button:hover {
        background-color: #fcd8a8 !important; /* Golden block hover */
        color: #b84418 !important;
        text-shadow: none !important;
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        transform: translateY(2px);
        box-shadow: 1px 1px 0px #000000 !important;
    }

    /* Style Alert Boxes (Success, Error, Info) to fit Retro Theme */
    [data-testid="stAlert"] {
        background-color: #000000 !important;
        border: 4px solid #ffffff !important;
        border-radius: 0px !important;
    }
    [data-testid="stAlert"] p {
        font-size: 0.7rem !important;
        line-height: 1.5 !important;
    }
    
    /* Clean up lines */
    hr {
        border-top: 4px dashed #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# 1. Define the Map Stages & NDT Topics
MAP_STAGES = [
    {"world": "World 1-1: ASNT Admin", "topic": "SNT-TC-1A personnel qualification guidelines"},
    {"world": "World 1-2: Surface Methods", "topic": "Liquid Penetrant capillary action and developer types"},
    {"world": "World 2-1: Magnetic Fields", "topic": "Magnetic Particle continuous vs residual magnetization"},
    {"world": "World 2-2: Subsurface Flaws", "topic": "Ultrasonic wave propagation and acoustic impedance"},
    {"world": "World 3-1: Radiation Safety", "topic": "Radiographic film density and geometric unsharpness"}
]
TOTAL_STAGES = len(MAP_STAGES)

# 2. Initialize Game Session State
if "player_pos" not in st.session_state:
    st.session_state.player_pos = 0  # Start at Space 0
if "coins" not in st.session_state:
    st.session_state.coins = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None

# Function to fetch a brand-new live question using our game_engine
def load_next_stage_question():
    if st.session_state.player_pos < TOTAL_STAGES:
        stage_info = MAP_STAGES[st.session_state.player_pos]
        with st.spinner(f"🍄 Hitting the Question Block for {stage_info['world']}..."):
            question_data = get_ndt_question(stage_info["topic"], stage_info["world"])
            st.session_state.current_question = question_data
    else:
        st.session_state.current_question = None

# Initialize the very first question if it doesn't exist yet
if st.session_state.current_question is None and st.session_state.player_pos < TOTAL_STAGES:
    load_next_stage_question()

# 3. Render Top Game HUD (Status Dashboard)
st.title("🍄 SUPER NDT CHALLENGE")
hud_col1, hud_col2, hud_col3 = st.columns(3)

with hud_col1:
    if st.session_state.current_question and not st.session_state.current_question.get("error"):
        st.metric(label="CURRENT WORLD", value=st.session_state.current_question["world"].upper())
    else:
        st.metric(label="CURRENT WORLD", value="GAME OVER")
with hud_col2:
    st.metric(label="COINS COLLECTED", value=f"x {st.session_state.coins:02d}") # Padded numbers look retro
with hud_col3:
    st.metric(label="BOARD POSITION", value=f"TILE {st.session_state.player_pos}/{TOTAL_STAGES}")

st.markdown("---")

# 4. Render the Visual Game Track (Horizontal Map)
st.write("### 🗺️ LEVEL SELECTION TRACK")
board_cols = st.columns(TOTAL_STAGES + 1)

for idx in range(TOTAL_STAGES + 1):
    with board_cols[idx]:
        if idx == TOTAL_STAGES:
            st.markdown("## 🏰")
            st.caption("**CASTLE**")
        elif idx == st.session_state.player_pos:
            st.markdown("## 🔴")
            st.caption("**MARIO**")
        else:
            st.markdown("## 📦")
            st.caption(f"STAGE {idx+1}")

st.markdown("---")

# 5. Display Feedback from Previous Turn
if st.session_state.last_feedback:
    if st.session_state.last_feedback["correct"]:
        st.success(st.session_state.last_feedback["text"])
    else:
        st.error(st.session_state.last_feedback["text"])
    st.info(f"💡 **STUDY TIP:** {st.session_state.last_feedback['tip']}")
    st.markdown("---")

# 6. Check Win Condition or Render Current Quiz Item
if st.session_state.player_pos >= TOTAL_STAGES:
    st.balloons()
    st.success("🎉 CONGRATULATIONS! YOU CLEARED ALL WORLDS AND MASTERED YOUR LEVEL III NDT MATERIAL!")
    if st.button("PLAY AGAIN / RESET GAME", use_container_width=True):
        st.session_state.player_pos = 0
        st.session_state.coins = 0
        st.session_state.last_feedback = None
        st.session_state.current_question = None
        st.rerun()
else:
    q = st.session_state.current_question
    if q and q.get("error"):
        st.error(q["message"])
        if st.button("RETRY QUESTION BLOCK GENERATION"):
            load_next_stage_question()
            st.rerun()
    elif q:
        st.write(f"### ❓ CHALLENGE: HIT THE QUESTION BLOCK!")
        st.info(q["question"])
        
        # Display the multiple-choice buttons safely
        for choice_idx, option_text in enumerate(q["options"]):
            if st.button(option_text.upper(), key=f"btn_{choice_idx}", use_container_width=True):
                if choice_idx == q["correct_option_index"]:
                    st.session_state.coins += 10
                    st.session_state.last_feedback = {
                        "correct": True,
                        "text": f"🌟 BRILLIANT! YOU COLLECTED A {q.get('item_reward', 'MUSHROOM').upper()} AND ADVANCED!",
                        "tip": q.get("study_tip", "EXCELLENT WORK TRACKING ASNT METHODOLOGIES.")
                    }
                    st.session_state.player_pos += 1
                else:
                    st.session_state.last_feedback = {
                        "correct": False,
                        "text": "💥 OUCH! HIT BY A GOOMBA! THAT OPTION WAS INCORRECT.",
                        "tip": q.get("study_tip", "REVIEW YOUR CODE GUIDELINES FOR THIS SECTION.")
                    }
                load_next_stage_question()
                st.rerun()
