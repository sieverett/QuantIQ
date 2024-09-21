from streamlit_quill import st_quill
import streamlit as st

st.markdown("""
<style>
.stElementContainer:has(> iframe) {
  height: 300px;
  overflow-y: scroll;
  overflow-x: hidden;
}
</style>
""", unsafe_allow_html=True)

# Spawn a new Quill editor
content = st_quill(key='fooar')

# Display editor's content as you type
content
