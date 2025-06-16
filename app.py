import streamlit as st
import requests

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏌️")

# --- Default values to prevent NameError ---
rating, slope, par = 66.0, 113, 72

# --- API Setup ---
API_KEY = "FKU4CCHVZDLQ5PDTN7YLVCCIDE"
BASE_URL = "https://api.golfcourseapi.com/v1"
HEADERS = {"x-api-key": API_KEY}

# --- Page Header ---
st.title("🏌️ UK Golf Handicap Calculator")

# --- Cached Course Search ---
@st.cache_data(show_spinner=False)
def search_courses(query):
    if not query or len(query) < 3:
        return []
    params = {"q": query, "country": "GB", "limit": 25}
    response = requests.get(f"{BASE_URL}/courses", params=params, headers=HEADERS)
    if response.status_code == 200:
        courses = response.json().get("courses", [])
        return sorted(courses, key=lambda c: c["name"])
    return []

# --- Course Search Interface ---
st.markdown("### Search for a UK Golf Course")
query = st.text_input("Start typing (min. 3 characters):")
course_data = {}

if len(query) >= 3:
    with st.spinner("Searching courses..."):
        courses = search_courses(query)
    course_names = [f"{c['name']} ({c.get('city', '')})" for c in courses]

    if course_names:
        selected = st.selectbox("Select from results:", course_names)
        course_data = next(c for c in courses if f"{c['name']} ({c.get('city', '')})" == selected)
        course_id = course_data["id"]

        # --- Fetch Detailed Course Info ---
        detail_url = f"{BASE_URL}/courses/{course_id}"
        detail_resp = requests.get(detail_url, headers=HEADERS)
        if detail_resp.status_code == 200:
            tee_data = detail_resp.json().get("tees", [])
            if tee_data:
                tee = tee_data[0]  # Use first tee box
                rating = tee.get("rating", rating)
                slope = tee.get("slope", slope)
                par = tee.get("par", par)
            else:
                st.warning("No tee data found for this course.")
        else:
            st.error("Failed to fetch course details.")
    else:
        st.info("No matching courses found.")
else:
    st.caption("Start typing at least 3 characters to search for courses...")

# --- Hole Count and Score Input ---
num_holes = st.selectbox("How many holes did you play?", [6, 9, 12, 18])
gross = st.number_input(f"Your gross score over {num_holes} holes:", min_value=1, value=63)

# --- Manual Override for Rating, Slope, Par ---
rating = rating if rating >= 1.0 else 66.0
slope = slope if slope >= 55 else 113
par = par if par >= 1 else 72

rating = st.number_input(f"Course Rating for {num_holes} holes:", min_value=1.0, value=rating, format="%.1f")
slope = st.number_input("Slope Rating:", min_value=55, max_value=155, value=slope)
par = st.number_input(f"Par for {num_holes} holes:", min_value=1, max_value=100, value=par)

# --- Handicap Differential Calculation ---
if st.button("Calculate Handicap Differential"):
    diff = ((gross - rating) * 113) / slope
    st.success(f"🎯 Handicap Differential: **{diff:.2f}**")
