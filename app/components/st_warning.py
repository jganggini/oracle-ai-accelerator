import time
import streamlit as st

def get_warning(msg: str, icon: str = ":material/warning:"):
    """
    Displays a reusable success toast in Streamlit.

    Args:
        msg (str): The message to display in the toast.
        icon (str): The icon to display alongside the message (Streamlit format).
                    Default is ":material/warning:".
    """
    st.warning(msg, icon=icon)
    time.sleep(1)