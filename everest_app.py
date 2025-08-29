# everest_app.py
import os
from datetime import datetime
import streamlit as st
from google.oauth2 import service_account
import gspread
from everest_team_runner import run_team_sync  # <-- sync wrapper

# ------------------------------
# Streamlit page setup
# ------------------------------
st.set_page_config(page_title="Everest Builders CRM", layout="centered")
st.title("🏗️ Everest Builders Associates – Smart Quote Assistant")
st.image("everest_logo.png", width=200)
st.write("✨ Your dream home starts here — receive an instant rough estimate today.")

# ------------------------------
# Quick Estimate Section
# ------------------------------
st.header("🏡 Tell Us About Your Dream Home")
location = st.text_input("📍 Enter your location")
size = st.number_input("📐 Home Size (in sq.ft)", min_value=300, max_value=10000, step=50)
budget = st.number_input("💰 Your Budget (₹)", min_value=100000, step=50000)

if st.button("✨ Get My Estimate"):
    if location and size and budget:
        st.success(f"✅ Estimated cost for a {size} sq.ft home in {location} is around ₹{size*2000:,}*")
        st.caption("*Final quote after site inspection.")
    else:
        st.warning("⚠️ Please fill all fields to get your estimate.")

# ------------------------------
# Lead Capture Form
# ------------------------------
with st.form("lead_form", clear_on_submit=True):
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    location_input = st.text_input("Location")
    sqft = st.number_input("Sq.Ft.", min_value=500, max_value=10000, step=100)
    requirements = st.text_area("Special Requirements")
    submitted = st.form_submit_button("Submit")

if submitted:
    st.success("✅ Lead captured successfully!")
    # ------------------------------
# 🏡 Services Section (6 items) — Enhanced
# ------------------------------
st.markdown("## 🏡 Our Services")
st.write("We provide complete home building solutions for your dream projects. Choose from our wide range of expert services:")

# Two rows, three columns each
row1_cols = st.columns(3)
row2_cols = st.columns(3)

# Row 1
with row1_cols[0]:
    st.markdown("### 🛠️ House Construction")
    st.write(
        "Build your dream home from scratch with **quality materials** and **expert engineers**. "
        "We handle foundation, walls, roofing, and finishing, ensuring durability and style."
    )

with row1_cols[1]:
    st.markdown("### 🏢 Villas & Apartments")
    st.write(
        "Premium villas and modern apartments with **customized designs**, maximizing space, comfort, "
        "and aesthetic appeal. Tailored solutions for families and investors alike."
    )

with row1_cols[2]:
    st.markdown("### 🎨 Renovation & Interiors")
    st.write(
        "Upgrade your home with **modern interiors**, modular kitchens, and smart layouts. "
        "Enhance functionality, style, and **property value** with our expert renovation services."
    )

# Row 2
with row2_cols[0]:
    st.markdown("### 🌳 Landscaping & Outdoor Spaces")
    st.write(
        "Create stunning gardens, patios, and outdoor living spaces. "
        "From greenery to hardscaping, we design **peaceful, aesthetic, and functional exteriors**."
    )

with row2_cols[1]:
    st.markdown("### 🔌 Electrical & Smart Home Solutions")
    st.write(
        "Install **safe electrical systems** and smart home automation. "
        "Control lighting, temperature, security, and appliances for a **modern, energy-efficient home**."
    )

with row2_cols[2]:
    st.markdown("### 💧 Plumbing & Water Management")
    st.write(
        "High-quality plumbing solutions, rainwater harvesting, and water-saving systems. "
        "Ensure **reliable water supply**, eco-friendly designs, and **hassle-free maintenance**."
    )


# ------------------------------
# Detailed Quote Generation Form (GPT/Autogen)
# ------------------------------
with st.form("detailed_quote_form"):
    city = st.text_input("City", value="Salem")
    sqft = st.number_input("Built-up area (sq.ft)", min_value=200, max_value=10000, value=1200, step=50)
    floors = st.selectbox("Floors", ["Single", "Duplex", "G+2", "Other"], index=0)
    bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5], index=2)
    finish = st.selectbox("Finish level", ["basic", "standard", "premium"], index=1)
    plot = st.text_input("Plot size (e.g., 24x50 ft)", value="24x50 ft")
    special = st.text_area("Special requirements", value="Pooja room, Western kitchen")
    contact = st.text_input("Contact (phone/email) — optional", value="")
    submitted_quote = st.form_submit_button("Generate Rough Quote")

if submitted_quote:
    task = (
        f"Client message: Build a {sqft} sq.ft {floors} home in {city}. "
        f"{bedrooms} BHK, {finish} finish, plot {plot}. "
        f"Special: {special or 'None'}. "
        f"Contact: {contact or 'NA'}."
    )
    with st.spinner("Thinking…"):
        reply = run_team_sync(task)
    st.subheader("Reply to Client")
    st.write(reply)

# ------------------------------
# Contact Section
# ------------------------------
st.markdown("---")
st.markdown("📞 Contact us: +91 9962841572 | ✉️ everestbuildersassociates@gmail.com")
st.markdown("📱 Follow us on Instagram: [Everest Builders Associates](https://www.instagram.com/everestbuilders_92)")
st.markdown("💬 WhatsApp us: [Chat on WhatsApp](https://wa.me/919962841572)")
