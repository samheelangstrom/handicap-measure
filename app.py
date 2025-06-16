import streamlit as st
import requests

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏉")

st.title("🏉 UK Golf Handicap Calculator")

API_KEY = "FKU4CCHVZDLQ5PDTN7YLVCCIDE"
API_URL = "https://api.golfcourseapi.com/api/v1/courses/search"
DETAILS_URL = "https://api.golfcourseapi.com/api/v1/courses"

# User selects number of holes played
num_holes = st.selectbox("How many holes did you play?", options=[6, 9, 12, 18], index=2)

# Search and select golf course
search_term = st.text_input("Search for a golf course in the UK:")
selected_course = None
course_data = None

if search_term:
    headers = {"x-api-key": API_KEY}
    params = {"query": search_term, "country": "GB"}
    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json().get("courses", [])
        if results:
            course_names = [f"{c['name']} ({c['city']})" for c in results]
            choice = st.selectbox("Select a course:", course_names)
            selected_course = next(c for c in results if f"{c['name']} ({c['city']})" == choice)

            # Fetch full details
            detail_resp = requests.get(f"{DETAILS_URL}/{selected_course['id']}", headers=headers)
            if detail_resp.status_code == 200:
                course_data = detail_resp.json()
        else:
            st.warning("No matching courses found.")
    else:
        st.error("Failed to fetch courses from API.")

rating = 0.0
slope = 109
par = 44

if course_data:
    st.markdown("### Course Details")
    info = {
        "Course Name": course_data.get("name"),
        "City": course_data.get("city"),
        "State/Region": course_data.get("state"),
        "Country": course_data.get("country"),
    }
    st.write(info)

    # Extract rating/slope from first available tee if present
    if course_data.get("tees"):
        tee = course_data["tees"][0]  # use first tee box as default
        rating = tee.get("rating", rating)
        slope = tee.get("slope", slope)
        par = tee.get("par", par)
        st.info(f"Using tee: {tee.get('name', 'N/A')}")

# User inputs
gross = st.number_input(f"Your gross score ({num_holes} holes):", min_value=1, value=63)
par = st.number_input(f"Total par for the {num_holes} holes:", min_value=1, value=par)
slope = st.number_input("Slope Rating:", min_value=55, max_value=155, value=slope)
rating = st.number_input(f"Course Rating for {num_holes} holes:", min_value=1.0, value=rating, format="%.1f")

# Calculate handicap
diff = None
if st.button("Calculate Handicap Differential"):
    try:
        differential = ((gross - rating) * 113) / slope
        st.success(f"🌟 Handicap Differential: {differential:.2f}")

        # Optional estimated 18-hole projection
        estimated_18_score = (gross / par) * 72
        st.info(f"📈 Estimated 18-hole gross score: {estimated_18_score:.1f}")
    except ZeroDivisionError:
        st.error("Slope Rating cannot be zero.")
