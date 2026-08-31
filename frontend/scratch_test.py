import streamlit as st
import pandas as pd

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

@st.dialog("My Modal")
def show_modal(val):
    st.write("You selected:", val)
    if st.button("Delete"):
        st.write("Deleted!")
        st.session_state["my_df"]["selection"]["rows"] = []
        st.rerun()

st.write("Click a row:")
event = st.dataframe(
    st.session_state.df,
    selection_mode="single-row",
    on_select="rerun",
    key="my_df"
)

if event.selection.rows:
    row_idx = event.selection.rows[0]
    val = st.session_state.df.iloc[row_idx]["A"]
    show_modal(val)
    # Clear the selection so the checkbox unchecks
    st.session_state["my_df"]["selection"]["rows"] = []
