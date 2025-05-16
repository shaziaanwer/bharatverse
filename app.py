import streamlit as st
import pandas as pd
from utils import get_best_months, load_art_data_snowflake, load_seasonal_data_snowflake, load_tourism_data_snowflake
import matplotlib.pyplot as plt

# App config
st.set_page_config(page_title="BharatVerse", layout="wide")

# Load Data from Snowflake
art_df = load_art_data_snowflake()
tourism_df = load_tourism_data_snowflake()
seasonal_df = load_seasonal_data_snowflake()

# Styling (unchanged)
st.markdown("""
<style>
@keyframes fadeSlideUp {
    0% {opacity: 0; transform: translateY(50px);}
    100% {opacity: 1; transform: translateY(0);}
}
.hero {
    position: relative;
    background-size: cover;
    background-position: center;
    padding: 180px 20px;
    border-radius: 20px;
    color: white;
    text-align: center;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin-bottom: 40px;
    animation: fadeSlideUp 1.2s ease-out forwards;
    opacity: 0;
    animation-delay: 0.3s;
}
.hero::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.45);
    z-index: 1;
    border-radius: 20px;
}
.hero-content {
    position: relative;
    z-index: 2;
}
.hero h1 {font-size: 2.8em; margin-bottom: 20px;}
.hero p {font-size: 1.4em; font-weight: 300;}
@media (max-width: 768px) {
    .hero {padding: 100px 20px;}
    .hero h1 {font-size: 2em;}
    .hero p {font-size: 1em;}
}
</style>
<div class="hero">
    <div class="hero-content">
        <h1>Welcome to BharatVerse: Explore India's Art & Culture</h1>
        <p>Discover the rich traditions and art of India. Your journey starts here.</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Filters
# st.header("Explore Indian Art by Filters")
# categories = art_df["category"].unique()
# states = art_df["state"].unique()
# selected_category = st.selectbox("Filter by Art Category", options=["All"] + list(categories))
# selected_state = st.selectbox("Filter by State", options=["All"] + list(states))

# filtered_df = art_df.copy()
# if selected_category != "All":
#     filtered_df = filtered_df[filtered_df["category"] == selected_category]
# if selected_state != "All":
#     filtered_df = filtered_df[filtered_df["state"] == selected_state]

# merged = pd.merge(filtered_df, tourism_df, on="state", how='left')

# Header
st.markdown("<h2 style='text-align:center;'>Explore Indian Art by Filters</h2>", unsafe_allow_html=True)

# Dropdowns
categories = art_df["category"].unique()
states = art_df["state"].unique()
selected_category = st.selectbox("Filter by Art Category", options=["Select Category"] + list(categories))
selected_state = st.selectbox("Filter by State", options=["Select State"] + list(states))

# Check if any filter is selected
apply_filter = False
filtered_df = art_df.copy()

if selected_category != "Select Category":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]
    apply_filter = True
if selected_state != "Select State":
    filtered_df = filtered_df[filtered_df["state"] == selected_state]
    apply_filter = True

# Merge tourism data
merged = pd.merge(filtered_df, tourism_df, on="state", how='left')

# Display results
if apply_filter:
    st.markdown("Results")

    if merged.empty:
        st.info("No matching art forms found for the selected filters.")
    else:
        cols = st.columns(3)
        for idx, row in merged.iterrows():
            col = cols[idx % 3]
            with col:
                with st.container():
                    image_url = row['image_url'] if pd.notnull(row['image_url']) else ""

                    st.markdown(f"""
                        <div style='
                            background-image: url("{image_url}");
                            background-size: cover;
                            background-position: center;
                            border-radius: 15px;
                            padding: 20px;
                            margin: 10px 0;
                            min-height: 250px;
                            color: white;
                            position: relative;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                        '>
                            <div style='
                                background: rgba(0,0,0,0.5);
                                border-radius: 15px;
                                padding: 15px;
                            '>
                                <h4 style='margin-bottom:10px'>{row['artform']}</h4>
                                <p><b>State:</b> {row['state']}</p>
                                <p><b>Category:</b> {row['category']}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Learn More Expander
                    with st.expander("Learn More"):
                        if 'description' in row and pd.notnull(row['description']):
                            st.markdown(row['description'])
                        else:
                            st.markdown("_No description available._")
else:
    st.warning("Please select at least one filter to view results.")
st.markdown("---")


# Tourism Dashboard
st.header("Tourism Insights Dashboard")
top_states = tourism_df.sort_values(by="domesticvisitors", ascending=False)
st.subheader("Top States by Domestic & Foreign Visitors")
st.bar_chart(top_states.set_index("state")[["domesticvisitors", "foreignvisitors"]])
st.markdown("---")

# Plan My Visit - Enhanced
st.markdown("<h2 style='text-align:center;'>🗺️ Plan My Visit</h2>", unsafe_allow_html=True)
st.markdown("Craft your perfect trip based on culture, crowd, and climate.")

# State Selection with Placeholder
state_options = ["Select a state to view results"] + sorted(art_df["state"].unique())
state_choice = st.selectbox("✨ Choose a State", state_options)

if state_choice != "Select a state to view results":
    # Fetch Data
    state_artforms = art_df[art_df["state"] == state_choice]["artform"].unique()
    best_months = get_best_months(state_choice, seasonal_df)
    merged_all = pd.merge(art_df, tourism_df, on="state")
    gem_states = merged_all[
        (merged_all["domesticvisitors"] < 1_000_000) & 
        (merged_all["foreignvisitors"] < 100_000)
    ]["state"].unique()

    # Display Card
    st.markdown(f"""
    <div style='
        background-color: black;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.07);
        border: 1px solid #e0e0e0;
        margin-top: 20px;
    '>
        <h3 style='margin-bottom: 10px;'>{state_choice}</h3>
        <p><strong>🎨 Featured Art Forms:</strong> {', '.join(state_artforms)}</p>
        <p><strong>📅 Best Months to Visit:</strong> {', '.join(best_months)}</p>
        {"<p style='color:green; font-weight:bold;'>💎 This state is a Hidden Gem: Less crowded, deeply cultural!</p>" if state_choice in gem_states else ""}
    </div>
    """, unsafe_allow_html=True)

    # Extra Suggestions Section
    st.markdown("#### 🌟 Recommended Cultural Experiences:")
    state_rows = art_df[art_df["state"] == state_choice]
    for i, row in state_rows.iterrows():
        # Remove raw links from description if any
        import re
        clean_desc = re.sub(r'http\S+', '', row['description']).strip() if pd.notnull(row['description']) else "_No description available._"
        st.markdown(f"""
        - **{row['artform']}** ({row['category']}): *{clean_desc}*
        """)

    # CTA
    st.info("Tip: Plan your trip during local festivals or art fairs for an unforgettable vibe ✨")

st.markdown("---")



with st.container():
    st.markdown("""
    <style>
    @keyframes fadeSlideUp {
        0% {opacity: 0; transform: translateY(50px);}
        100% {opacity: 1; transform: translateY(0);}
    }
    .hero-box {
        position: relative;
        background: linear-gradient(135deg, #1a1a1a, #3a3a3a);
        background-size: cover;
        background-position: center;
        padding: 60px 30px;
        border-radius: 20px;
        color: white;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: fadeSlideUp 1.2s ease-out forwards;
        opacity: 0;
        animation-delay: 0.2s;
        margin-bottom: 40px;
    }
    .hero-box h1 {font-size: 2.8em; margin-bottom: 10px; text-align: center;}
    .hero-box p {font-size: 1.2em; font-weight: 300; text-align: center;}
    </style>
    <div class="hero-box">
        <h1>Deep Dive: Cultural Tourism by State</h1>
        <p>Discover the rich traditions and art of India. Your journey starts here.</p>
    """, unsafe_allow_html=True)

    # Dropdown with placeholder
    state_options = ["Choose a state to explore"] + sorted(tourism_df["state"].unique())
    state_choice_deep = st.selectbox(
        "Choose a state to explore in depth",
        options=state_options,
        key="deep_dive_state"
    )

    # Only run if a valid state is selected
    if state_choice_deep != "Choose a state to explore":
        state_tourism = tourism_df[tourism_df["state"] == state_choice_deep]
        state_art = art_df[art_df["state"] == state_choice_deep]
        state_season = seasonal_df[seasonal_df["state"] == state_choice_deep]

        st.markdown(f"### {state_choice_deep} Snapshot", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Domestic Visitors", f"{int(state_tourism['domesticvisitors'].values[0]):,}")
        with col2:
            st.metric("Foreign Visitors", f"{int(state_tourism['foreignvisitors'].values[0]):,}")
        with col3:
            total = state_season["visitors"].sum()
            st.metric("Seasonal Visitors Tracked", f"{int(total):,}")

        st.markdown("### Monthly Visitor Trend", unsafe_allow_html=True)
        monthly = state_season.groupby("month")["visitors"].sum().reindex([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]).fillna(0)
        st.line_chart(monthly)

        st.markdown("### Traditional Art Forms in this State", unsafe_allow_html=True)
        if state_art.empty:
            st.warning("No art forms found for this state.")
        else:
            for _, row in state_art.iterrows():
                st.info(f"*{row['artform']}* ({row['category']})")

        # Tip section
        state_experiences = {
            "Odisha": "Don't miss the Puri Jagannath Temple and the Ratha Yatra Festival!",
            "Kolkata": "Enjoy the famous Durga Puja festival and the traditional sweets like Rosogolla."
        }
        st.markdown(f"**Local Tip for {state_choice_deep}:** {state_experiences.get(state_choice_deep, 'Explore its rich art and culture!')}")

    # Close the hero div
    st.markdown("</div>", unsafe_allow_html=True)
