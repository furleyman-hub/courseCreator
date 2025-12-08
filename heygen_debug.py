import streamlit as st
import heygen_client

st.set_page_config(page_title="HeyGen Debug", layout="centered")

st.title("HeyGen Assets Debug")

# Pull API key from the same secrets you already configured
heygen_client.HEYGEN_API_KEY = st.secrets.get("HEYGEN_API_KEY", None)

if not heygen_client.HEYGEN_API_KEY:
    st.error("HEYGEN_API_KEY is not set in Streamlit secrets.")
    st.stop()

st.write("Using HeyGen API key from secrets.")

if st.button("List avatars and voices"):
    try:
        with st.spinner("Fetching avatars..."):
            avatars = heygen_client.list_avatars()
        with st.spinner("Fetching voices..."):
            voices = heygen_client.list_voices()
    except Exception as e:
        st.error(f"Error calling HeyGen API: {e}")
    else:
        st.subheader("Avatars")
        st.caption("Look for avatar_id and name.")
        st.json(avatars)

        st.subheader("Voices")
        st.caption("Look for voice_id and name.")
        st.json(voices)
