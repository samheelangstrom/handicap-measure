import streamlit as st

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏉")

st.title("🏉 Custom Hole Golf Handicap Calculator")

# User selects number of holes played
num_holes = st.selectbox("How many holes did you play?", options=[6, 9, 12, 18], index=2)

# User input for scores and course details
gross = st.number_input(f"Your gross score ({num_holes} holes):", min_value=1, value=63)
par = st.number_input(f"Total par for the {num_holes} holes:", min_value=1, value=44)
rating = st.number_input(f"Course Rating for {num_holes} holes:", min_value=1.0, value=31.4)
slope = st.number_input("Slope Rating:", min_value=55, max_value=155, value=109)

if st.button("Calculate Handicap Differential"):
    try:
        differential = ((gross - rating) * 113) / slope
        st.success(f"🌟 Handicap Differential: {differential:.2f}")

        # Optional estimated 18-hole projection
        estimated_18_score = (gross / par) * 72
        st.info(f"📈 Estimated 18-hole gross score: {estimated_18_score:.1f}")
    except ZeroDivisionError:
        st.error("Slope Rating cannot be zero.")
