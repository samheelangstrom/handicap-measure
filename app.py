import streamlit as st
import requests

st.set_page_config(page_title="Golf Handicap Calculator", page_icon="🏌️")

# --- Default fallback values ---
rating, slope, par = 66.0, 113, 72

# --- API Setup ---
API_KEY = "FKU4CCHVZDLQ5PDTN7YLVCCIDE"
BASE_URL = "https://api.golfcourseapi.com/v1"
HEADERS = {"x-api-key": API_KEY}

st.title("🏌️ UK Golf Handicap Calculator")

# --- Cache search ---
@st.cache_data(show_spinner=False)
def search_courses(query):
    if not query or len(query) < 3:
        return []
    params = {"search_query": query}
    resp = requests.get(f"{BASE_URL}/search", params=params, headers=HEADERS)
    if resp.status_code == 200:
        return sorted(resp.json().get("courses", []), key=lambda c: c.get("club_name", ""))
    return []

# --- Cache course detail ---
@st.cache_data(show_spinner=False)
def get_course_detail(course_id):
    resp = requests.get(f"{BASE_URL}/courses/{course_id}", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    return {}

# --- Search UI ---
st.markdown("### Search for a Golf Course (min. 3 characters)")
query = st.text_input("Type course or club name:")
course_data = {}

if len(query) >= 3:
    with st.spinner("Searching..."):
        courses = search_courses(query)

    course_display_names = [f"{c['club_name']} - {c['course_name']}" for c in courses]

    if course_display_names:
        selected = st.selectbox("Select a course:", course_display_names)
        selected_course = next(c for c in courses if f"{c['club_name']} - {c['course_name']}" == selected)
        course_id = selected_course["id"]

        with st.spinner("Fetching course details..."):
            course_detail = get_course_detail(course_id)

        st.markdown(f"**Selected Course:** {course_detail.get('club_name')} - {course_detail.get('course_name')}")
        location = course_detail.get("location", {})
        st.markdown(f"**Location:** {location.get('address', '')}, {location.get('city', '')}, {location.get('country', '')}")

        # Use first male tee data if available
        tees = course_detail.get("tees", {}).get("male", [])
        if not tees:
            st.warning("No male tees found — using default values.")
        else:
            tee = tees[0]
            rating = tee.get("rating", rating)
            slope = tee.get("slope", slope)
            par = tee.get("par", par)
    else:
        st.info("No courses found.")
else:
    st.caption("Search for a golf course above to get started.")

# --- Handicap Inputs ---
num_holes = st.selectbox("How many holes did you play?", [6, 9, 12, 18])
gross = st.number_input(f"Your gross score over {num_holes} holes:", min_value=1, value=63)

# --- Safe fallback ---
rating = rating if rating >= 1.0 else 66.0
slope = slope if slope >= 55 else 113
par = par if par >= 1 else 72

# --- Manual override for rating, slope, par ---
rating = st.number_input(f"Course Rating for {num_holes} holes:", min_value=1.0, value=rating, format="%.1f")
slope = st.number_input("Slope Rating:", min_value=55, max_value=155, value=slope)
par = st.number_input(f"Par for {num_holes} holes:", min_value=1, max_value=100, value=par)

# --- Handicap Calculation ---
if st.button("Calculate Handicap Differential"):
    diff = ((gross - rating) * 113) / slope
    st.success(f"🎯 Handicap Differential: **{diff:.2f}**")
