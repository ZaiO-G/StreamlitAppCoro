import streamlit as st

def check_password():
    if st.session_state.get("authenticated"):
        return
    st.title("Accès réservé")
    pwd = st.text_input("Mot de passe", type="password")
    if pwd == st.secrets["password"]:
        st.session_state.authenticated = True
        st.rerun()
    elif pwd:
        st.error("Mot de passe incorrect")
    st.stop()