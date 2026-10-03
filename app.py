import re

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)


MODEL_NAME = "gemini-3.5-flash"


st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗"
)


# Gemini API key
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TWILIO_ACCOUNT_SID = st.secrets.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = st.secrets.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = st.secrets.get("TWILIO_WHATSAPP_FROM")


# Create Gemini client
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


# Initialize the user's session state
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "whatsapp_number" not in st.session_state:
    st.session_state.whatsapp_number = ""
if "chat" not in st.session_state:
    st.session_state.chat = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "whatsapp_summary" not in st.session_state:
    st.session_state.whatsapp_summary = ""


st.title("🥗 MacroSnap")

if st.session_state.chat is None:
    st.subheader("Let's get started")
    st.write("Enter your name and WhatsApp number to start using MacroSnap.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name", value=st.session_state.user_name)
        whatsapp_number = st.text_input(
            "WhatsApp number",
            value=st.session_state.whatsapp_number,
            help="Include your country code, for example +14155552671.",
        )
        submitted = st.form_submit_button("Get started")

    if submitted:
        name = name.strip()
        whatsapp_number = whatsapp_number.strip()
        digits_only = "".join(character for character in whatsapp_number if character.isdigit())

        if not name:
            st.error("Please enter your name.")
        elif (
            not re.fullmatch(r"\+?[0-9\s().-]+", whatsapp_number)
            or len(digits_only) < 7
            or len(digits_only) > 15
        ):
            st.error("Please enter a valid WhatsApp number, including your country code.")
        else:
            st.session_state.user_name = name
            st.session_state.whatsapp_number = whatsapp_number
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": WELCOME_MESSAGE_TEMPLATE.format(name=name),
                }
            ]
            st.rerun()

    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if image_bytes := message.get("image"):
            st.image(image_bytes, caption="Meal photo", width=300)
        st.markdown(message["content"])

uploaded_image = st.file_uploader(
    "Upload a meal photo",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_image is not None:
    st.image(uploaded_image, caption="Meal photo preview", width=300)

if st.button("Analyze meal photo", disabled=uploaded_image is None):
    image_bytes = uploaded_image.getvalue()
    if len(image_bytes) > 15 * 1024 * 1024:
        st.error("Please choose an image smaller than 15 MB.")
    else:
        st.session_state.whatsapp_summary = ""
        st.session_state.messages.append(
            {"role": "user", "content": "Please analyze this meal photo.", "image": image_bytes}
        )
        with st.chat_message("user"):
            st.image(image_bytes, caption="Meal photo", width=300)
            st.markdown("Please analyze this meal photo.")

        with st.chat_message("assistant"):
            with st.spinner("MacroSnap is analyzing your photo..."):
                try:
                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=uploaded_image.type,
                    )
                    response = st.session_state.chat.send_message(
                        [
                            image_part,
                            "Identify the foods in this meal photo and estimate the calories, "
                            "protein, carbohydrates, and fat. Keep estimates rough and mention "
                            "when portion size or ingredients are uncertain.",
                        ]
                    )
                    answer = response.text or "I couldn't create a response. Please try again."
                    st.markdown(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception:
                    st.error("I couldn't analyze that photo with Gemini. Please try again.")

if prompt := st.chat_input("Ask MacroSnap about a meal..."):
    st.session_state.whatsapp_summary = ""
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("MacroSnap is thinking..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                answer = response.text or "I couldn't create a response. Please try again."
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception:
                st.error("I couldn't reach Gemini. Check your connection and try again.")

st.divider()
if st.button("Create WhatsApp summary"):
    if not any(message["role"] == "user" for message in st.session_state.messages):
        st.error("Discuss a meal with MacroSnap before creating a summary.")
    else:
        conversation = "\n\n".join(
            f"{message['role'].capitalize()}: {message['content']}"
            for message in st.session_state.messages
        )
        with st.spinner("Preparing your meal summary..."):
            try:
                summary_response = gemini_client.models.generate_content(
                    model=MODEL_NAME,
                    contents=f"{SUMMARY_REQUEST_PROMPT}\n\nConversation:\n{conversation}",
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                summary = (summary_response.text or "").strip()
                if summary:
                    st.session_state.whatsapp_summary = summary
                else:
                    st.error("MacroSnap couldn't prepare a summary. Please try again.")
            except Exception:
                st.error("MacroSnap couldn't prepare a summary. Please try again.")

if st.session_state.whatsapp_summary:
    st.subheader("WhatsApp summary preview")
    st.text_area(
        "Your summary",
        value=st.session_state.whatsapp_summary,
        height=180,
        disabled=True,
    )
    st.caption(
        "This preview is ready to copy. Your Twilio trial can't send this custom "
        "summary yet, so MacroSnap has not sent a WhatsApp message."
    )
