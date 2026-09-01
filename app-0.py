import streamlit as st
from game_engine import get_ndt_question

# 1. Define the Map Stages & NDT Topics
# This array controls the order of your study topics on the game board
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
st.title("🍄 Super NDT Level III Challenge")

hud_col1, hud_col2, hud_col3 = st.columns(3)
with hud_col1:
    if st.session_state.current_question and not st.session_state.current_question.get("error"):
        st.metric(label="CURRENT WORLD", value=st.session_state.current_question["world"])
    else:
        st.metric(label="CURRENT WORLD", value="Game Over")
with hud_col2:
    st.metric(label="COINS COLLECTED", value=f"🪙 {st.session_state.coins}")
with hud_col3:
    st.metric(label="BOARD POSITION", value=f"Tile {st.session_state.player_pos} / {TOTAL_STAGES}")

st.markdown("---")

# 4. Render the Visual Game Track (Horizontal Map)
st.write("### 🗺️ Level Selection Track")
board_cols = st.columns(TOTAL_STAGES + 1)  # Stages + 1 Castle Finish Line

for idx in range(TOTAL_STAGES + 1):
    with board_cols[idx]:
        if idx == TOTAL_STAGES:
            st.markdown("### 🏰")
            st.caption("**CASTLE**")
        elif idx == st.session_state.player_pos:
            st.markdown("### 🔴")
            st.caption("**MARIO**")
        else:
            st.markdown("### 📦")
            st.caption(f"Stage {idx+1}")

st.markdown("---")

# 5. Display Feedback from Previous Turn
if st.session_state.last_feedback:
    if st.session_state.last_feedback["correct"]:
        st.success(st.session_state.last_feedback["text"])
    else:
        st.error(st.session_state.last_feedback["text"])
    
    st.info(f"💡 **Study Tip:** {st.session_state.last_feedback['tip']}")
    st.markdown("---")

# 6. Check Win Condition or Render Current Quiz Item
if st.session_state.player_pos >= TOTAL_STAGES:
    st.balloons()
    st.success("🎉 CONGRATULATIONS! You cleared all worlds and mastered your Level III NDT material!")
    if st.button("Play Again / Reset Game", use_container_width=True):
        st.session_state.player_pos = 0
        st.session_state.coins = 0
        st.session_state.last_feedback = None
        st.session_state.current_question = None
        st.rerun()
else:
    q = st.session_state.current_question
    
    if q and q.get("error"):
        st.error(q["message"])
        if st.button("Retry Question Block Generation"):
            load_next_stage_question()
            st.rerun()
    elif q:
        st.write(f"### ❓ Challenge: Hit the Question Block!")
        st.info(q["question"])
        
        # Display the multiple-choice buttons safely
        for choice_idx, option_text in enumerate(q["options"]):
            if st.button(option_text, key=f"btn_{choice_idx}", use_container_width=True):
                if choice_idx == q["correct_option_index"]:
                    # Correct Answer: Log rewards and increment state
                    st.session_state.coins += 10
                    st.session_state.last_feedback = {
                        "correct": True,
                        "text": f"🌟 Brilliant! You collected a {q.get('item_reward', 'Mushroom')} and advanced!",
                        "tip": q.get("study_tip", "Excellent work tracking ASNT methodologies.")
                    }
                    st.session_state.player_pos += 1
                else:
                    # Incorrect Answer: Log negative feedback, stay on current tile
                    st.session_state.last_feedback = {
                        "correct": False,
                        "text": "💥 Ouch! Hit by a Goomba! That option was incorrect.",
                        "tip": q.get("study_tip", "Review your code guidelines for this section.")
                    }
                
                # Fetch fresh AI question matching the new tile location before re-drawing
                load_next_stage_question()
                st.rerun()
