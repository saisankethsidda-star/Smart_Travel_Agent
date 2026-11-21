
import streamlit as st
import requests
import uuid
import json

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Naidu's WanderWays",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. N8N WEBHOOK CONFIGURATION
# =====================================================

N8N_WEBHOOK_URL = (
    "https://sai5319.app.n8n.cloud/webhook/"
    "63e2a58f-7709-4640-9b37-2a971c2174f5/chat"
)

# =====================================================
# 3. SESSION MANAGEMENT
# =====================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# =====================================================
# 4. PREMIUM CUSTOM CSS
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(
        135deg,
        #071526 0%,
        #102b46 55%,
        #081827 100%
    );
    color: white;
}

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0c2035,
        #071526
    );
}

section[data-testid="stSidebar"] * {
    color: white;
}

div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 12px;
}

.stButton button {
    border-radius: 12px;
    font-weight: 600;
    border: 1px solid rgba(85,220,255,0.3);
}

.hero-heading {
    color: #55dcff;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 5. MAIN BRANDING
# =====================================================

left, center, right = st.columns([1, 5, 1])

with center:
    st.title("✈️ Naidu's WanderWays")

    st.subheader(
        "Every Journey, An Adventure",
        text_alignment="center"
    )

    st.caption(
        "Discover More • Explore More • Travel Better",
        text_alignment="center"
    )

st.divider()

# =====================================================
# 6. SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🌍 Naidu's WanderWays")

    st.markdown("**Every Journey, An Adventure**")

    st.divider()

    st.subheader("⚙️ Connection Status")

    st.success("n8n Chat Trigger configured")

    st.caption("AI Travel Assistant")

    st.divider()

    st.subheader("💬 Your Conversation")

    st.caption("Session ID")

    st.code(st.session_state.session_id)

    if st.button(
        "➕ Start New Journey",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())

        st.rerun()

    st.divider()

    st.markdown("### ✨ Travel Made Easy")

    st.write(
        "Let our AI travel assistant help you "
        "plan unforgettable adventures."
    )

    st.divider()

    st.caption("Powered by Sai AI Workshop ❤️")

# =====================================================
# 7. EXTRACT N8N RESPONSE
# =====================================================

def extract_answer(data):

    if isinstance(data, list):

        answers = []

        for item in data:
            answer = extract_answer(item)

            if answer:
                answers.append(answer)

        return "\n\n".join(answers)

    if isinstance(data, dict):

        for key in [
            "output",
            "text",
            "response",
            "message",
            "content"
        ]:

            value = data.get(key)

            if isinstance(value, str) and value.strip():
                return value

            if isinstance(value, (dict, list)):
                return extract_answer(value)

        return json.dumps(data, indent=2, ensure_ascii=False)

    if isinstance(data, str):
        return data

    return str(data)

# =====================================================
# 8. CONNECT TO N8N CHAT TRIGGER
# =====================================================

def execute_n8n_workflow(user_message):

    payload = {
        "chatInput": user_message,
        "sessionId": st.session_state.session_id
    }

    try:

        response = requests.post(
            N8N_WEBHOOK_URL,
            params={
                "action": "sendMessage"
            },
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=180
        )

        response.raise_for_status()

        # Handle JSON or plain-text responses
        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "application/json" in content_type:
            data = response.json()
            return extract_answer(data)

        # Handle text responses
        response_text = response.text.strip()

        if not response_text:
            return "The AI agent returned an empty response."

        # Handle basic Server-Sent Event responses
        if response_text.startswith("data:"):

            result_lines = []

            for line in response_text.splitlines():

                if line.startswith("data:"):

                    event_data = line[5:].strip()

                    if event_data and event_data != "[DONE]":

                        try:
                            parsed = json.loads(event_data)
                            result_lines.append(
                                extract_answer(parsed)
                            )

                        except json.JSONDecodeError:
                            result_lines.append(event_data)

            if result_lines:
                return "\n".join(result_lines)

        return response_text

    except requests.exceptions.Timeout:

        return (
            "⏳ Your travel plan is taking longer "
            "than expected. Please try again."
        )

    except requests.exceptions.HTTPError:

        return (
            f"❌ n8n HTTP Error: {response.status_code}\n\n"
            f"Details: {response.text[:1500]}"
        )

    except requests.exceptions.ConnectionError:

        return (
            "❌ Unable to connect to n8n. "
            "Please check your internet connection."
        )

    except requests.exceptions.RequestException as error:

        return f"❌ Connection Error: {str(error)}"

    except ValueError:

        return (
            "❌ Invalid response received from n8n. "
            "Please check your workflow response settings."
        )

# =====================================================
# 9. HERO SECTION - NATIVE STREAMLIT COMPONENTS
# NO HTML RENDERING ISSUES
# =====================================================

if not st.session_state.messages:

    with st.container(border=True):

        st.markdown("")

        title_col1, title_col2, title_col3 = st.columns(
            [1, 5, 1]
        )

        with title_col2:

            st.markdown(
                "### 🌴 Your Next Adventure Starts Here!",
                text_alignment="center"
            )

        st.markdown("")

        st.markdown(
            "Welcome to **Naidu's WanderWays!**",
            text_alignment="center"
        )

        st.markdown(
            "Tell us your dream destination and travel preferences.",
            text_alignment="center"
        )

        st.markdown(
            "Our AI Travel Planner will help you create "
            "an unforgettable travel experience.",
            text_alignment="center"
        )

        st.divider()

        st.markdown(
            "### ✨ Explore Our Travel Services",
            text_alignment="center"
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown("## ✈️")
            st.caption("Destinations")

        with col2:
            st.markdown("## 🏨")
            st.caption("Accommodation")

        with col3:
            st.markdown("## 🍽️")
            st.caption("Food")

        with col4:
            st.markdown("## 🚗")
            st.caption("Transportation")

        with col5:
            st.markdown("## 💰")
            st.caption("Budget Planning")

    st.write("")

    # =================================================
    # 10. SUGGESTED TRAVEL REQUESTS
    # =================================================

    st.markdown("### 💡 Try Asking Your AI Travel Planner")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            "🌊 Plan a 5-day Goa trip for 15 people "
            "within ₹3 lakhs."
        )

        st.info(
            "🏔️ Suggest a 7-day Manali adventure "
            "with comfortable hotels."
        )

    with col2:

        st.info(
            "🏖️ Find the best beach destinations "
            "for a family vacation."
        )

        st.info(
            "🚗 Create a complete road trip itinerary "
            "with estimated expenses."
        )

# =====================================================
# 11. DISPLAY CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =====================================================
# 12. CHAT INPUT AND N8N EXECUTION
# =====================================================

user_input = st.chat_input(
    "✈️ Tell us about your dream trip..."
)

if user_input:

    # Display user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Execute AI Travel Planner

    with st.chat_message("assistant"):

        with st.spinner(
            "🌍 Planning your adventure... Please wait"
        ):

            answer = execute_n8n_workflow(user_input)

        st.markdown(answer)

    # Save AI response

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

# =====================================================
# 13. FOOTER - NATIVE STREAMLIT COMPONENTS
# NO HTML RENDERING ISSUES
# =====================================================

st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(
    [1, 4, 1]
)

with footer_col2:

    st.markdown(
        "### ✈️ Naidu's WanderWays",
        text_alignment="center"
    )

    st.markdown(
        "**Every Journey, An Adventure**",
        text_alignment="center"
    )

    st.caption(
        "Your Dreams. Our Plans. Unforgettable Journeys.",
        text_alignment="center"
    )

    st.caption(
        "Powered by Sai AI Workshop ❤️",
        text_alignment="center"
    )
