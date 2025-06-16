import streamlit as st

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏌️")

st.title("🏌️ 12-Hole Handicap Calculator")

gross = st.number_input("Your gross score (12 holes):", value=63)
rating = st.number_input("Course Rating (12 holes):", value=31.4)
slope = st.number_input("Slope Rating:", value=109)

if st.button("Calculate"):
    diff = ((gross - rating) * 113) / slope
    st.success(f"🎯 Handicap Differential: {diff:.2f}")
