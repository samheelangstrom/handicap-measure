import streamlit as st
import requests

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏌️")

# --- API Key & Base ---
API_KEY = "FKU4CCHVZDLQ5PDTN7YLVCCIDE"
BASE_URL = "https://api.golfcourseapi.com/v1"
HEADERS = {"x-api-key": API_KEY}

# --- Header ---
st.title("🏌️ UK Golf Handicap Calculator")

# --- Cached course search ---
@st.cache_data(show_spinner=False)
def search_courses(query):
    params = {"q": query, "country": "GB", "limit": 50}
    response = requests.get(f"{BASE_URL}/courses", params=params, headers=HEADERS)
    if response.status_code == 200:
        courses = response.json().get("courses", [])
        courses_sorted = sorted(courses, key=lambda c: c["name"])
        return courses_sorted
    return []

# --- Search and Dropdown ---
query = st.text_input("Search for a UK golf course:")

course_data = {}
if query:
    courses = search_courses(query)
    course_names = [f"{c['name']} ({c.get('city', '')})" for c in courses]
    selected = st.selectbox("Select a course:", options=["-- Select --"] + course_names)

    if selected != "-- Select --":
        course_data = next(c for c in courses if f"{c['name']} ({c.get('city', '')})" == selected)
        course_id = course_data["id"]

        # Get detailed course info
        detail_url = f"{BASE_URL}/courses/{course_id}"
        detail_resp = requests.get(detail_url, headers=HEADERS)

        if detail_resp.status_code == 200:
            tee_data = detail_resp.json().get("tees", [])
            if tee_data:
                tee = tee_data[0]  # Use first tee box
                rating = tee.get("rating", 0.0)
                slope = tee.get("slope", 0)
                par = tee.get("par", 0)
            else:
                rating, slope, par = 0.0, 0, 0
        else:
            st.error("Could not fetch detailed course info.")
            rating, slope, par = 0.0, 0, 0
else:
    rating, slope, par = 0.0, 0, 0

# --- Hole Count & Gross Input ---
num_holes = st.selectbox("How many holes did you play?", [6, 9, 12, 18])
gross = st.number_input(f"Your gross score over {num_holes} holes:", min_value=1, value=63)

# --- Safe defaults if no API result ---
rating = rating if rating >= 1.0 else 66.0
slope = slope if slope >= 55 else 113
par = par if par >= 1 else 72

# --- Manual override options ---
rating = st.number_input(f"Course Rating for {num_holes} holes:", min_value=1.0, value=rating, format="%.1f")
slope = st.number_input("Slope Rating:", min_value=55, max_value=155, value=slope)
par = st.number_input(f"Par for {num_holes} holes:", min_value=1, max_value=100, value=par)

# --- Handicap Differential Calculation ---
if st.button("Calculate Handicap Differential"):
    diff = ((gross - rating) * 113) / slope
    st.success(f"🎯 Handicap Differential: **{diff:.2f}**")
