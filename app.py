import streamlit as st
import requests
import json

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏌️")

# --- Default fallback values ---
DEFAULT_RATING = 66.0
DEFAULT_SLOPE = 113
DEFAULT_PAR = 72

# --- Initialize values ---
rating, slope, par = DEFAULT_RATING, DEFAULT_SLOPE, DEFAULT_PAR

# --- API or static file setup ---
API_KEY = "FKU4CCHVZDLQ5PDTN7YLVCCIDE"
BASE_URL = "https://api.golfcourseapi.com/v1"
HEADERS = {"x-api-key": API_KEY}

# --- Page Title ---
st.title("🏌️ Golf Handicap Calculator (By Club and City)")

# --- Option A: Load from API ---
@st.cache_data(show_spinner=False)
def get_all_courses_from_api():
    url = f"{BASE_URL}/courses?country=GB&limit=1000"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("courses", [])
    return []

# --- Option B: Load from local JSON (fallback or dev mode) ---
# @st.cache_data
# def get_all_courses_from_file():
#     with open("courses.json", "r") as f:
#         return json.load(f)["courses"]

# --- Load course data ---
courses = get_all_courses_from_api()  # or use get_all_courses_from_file()

# --- Dropdown options (club_name + city) ---
course_options = [
    f"{course['club_name']} ({course.get('location', {}).get('city', 'Unknown')})"
    for course in courses
]

# --- Course Selector ---
selected_course = st.selectbox("Select a Golf Course:", course_options)

# --- Find selected course data ---
course_data = next(
    (c for c in courses if f"{c['club_name']} ({c.get('location', {}).get('city', 'Unknown')})" == selected_course),
    None
)

# --- Extract tee data ---
if course_data:
    male_tees = course_data.get("tees", {}).get("male", [])
    if male_tees:
        tee = male_tees[0]  # Use first male tee box by default
        rating = tee.get("course_rating", DEFAULT_RATING)
        slope = tee.get("slope_rating", DEFAULT_SLOPE)
        par = tee.get("par_total", DEFAULT_PAR)
    else:
        st.warning("No male tee data available for this course. Using default values.")

# --- Hole Count and Gross Score ---
num_holes = st.selectbox("How many holes did you play?", [6, 9, 12, 18])
gross = st.number_input(f"Your gross score over {num_holes} holes:", min_value=1, value=63)

# --- Manual Override of Ratings ---
rating = st.number_input(f"Course Rating for {num_holes} holes:", min_value=1.0, value=rating, format="%.1f")
slope = st.number_input("Slope Rating:", min_value=55, max_value=155, value=slope)
par = st.number_input(f"Par for {num_holes} holes:", min_value=1, max_value=100, value=par)

# --- Calculate Handicap Differential ---
if st.button("Calculate Handicap Differential"):
    diff = ((gross - rating) * 113) / slope
    st.success(f"🎯 Handicap Differential: **{diff:.2f}**")
