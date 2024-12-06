import streamlit as st
import pandas as pd
import plotly.express as px
import tabula
import base64
import numpy as np
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Smart Finance Dashboard", layout="wide")

# Function to process PDF to DataFrame
def process_pdf(file):
    try:
        df_list = tabula.read_pdf(file, pages="all", multiple_tables=True, stream=True)
        if df_list:
            return pd.concat(df_list, ignore_index=True)
        else:
            st.error("No tables found in the PDF.")
            return None
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Function to load data from CSV or PDF
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".pdf"):
        return process_pdf(file)
    else:
        st.error("Unsupported file format. Please upload a CSV or PDF file.")
        return None

# Function to add centered background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as img:
        encoded_string = base64.b64encode(img.read()).decode()  # Convert to base64 string
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Function to display recommendations page
def display_recommendations(data):
    st.title("Smart Finance Recommendations 💵💰")
    st.markdown("### Based on Your Selected Priority")

    if data is None:
        st.warning("Please upload a CSV or PDF file first!⚠️")
        return

    # Dynamic category detection
    if 'category' in data.columns.str.lower():
        categories = data[data.columns[data.columns.str.lower() == 'category'][0]].unique()
    else:
        # Try to identify category column
        categorical_columns = data.select_dtypes(include=['object']).columns
        if categorical_columns.empty:
            categories = ["Essential Bills", "Savings", "Investment", "Entertainment", "Shopping"]
        else:
            categories = data[categorical_columns[0]].unique()

    st.subheader("Set Your Financial Priorities 💰💸")
    savings_goal = st.slider("Monthly Savings Goal ($)", 0, 5000, 1000)
    priority_categories = st.multiselect(
        "Select Priority Categories",
        categories.tolist() if isinstance(categories, np.ndarray) else categories
    )

    st.subheader("Personalized Recommendations 📶")

    # Generate recommendations based on selected categories
    for category in priority_categories:
        st.write(f"📊 {category} Recommendations:")
        if "saving" in category.lower():
            st.write(f"- Set up automatic transfers to savings account")
            st.write(f"- To reach your ${savings_goal} monthly goal, save ${savings_goal/30:.2f} daily")
        elif "invest" in category.lower():
            st.write("- Consider low-cost index funds")
            st.write("- Diversify your investment portfolio")
        elif "bill" in category.lower():
            st.write("- Set up automatic bill payments")
            st.write("- Review subscriptions monthly")
        else:
            st.write(f"- Create a budget for {category}")
            st.write(f"- Track {category.lower()} expenses regularly")

    # Dynamic budget allocation
    st.subheader("Recommended Budget Allocation 💸")
    num_categories = len(priority_categories)
    if num_categories > 0:
        allocation = {}
        remaining = 1.0

        # Allocate budget based on priorities
        for i, category in enumerate(priority_categories):
            if i == num_categories - 1:
                allocation[category] = remaining
            else:
                share = remaining / (num_categories - i)
                allocation[category] = share
                remaining -= share

        fig = px.pie(
            values=list(allocation.values()),
            names=list(allocation.keys()),
            title="Recommended Monthly Budget Distribution"
        )
        st.plotly_chart(fig)

# Dynamic Dashboard Creation
def create_dashboard(data):
    st.sidebar.header("Visualization Options")
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "3D Scatter Plot", "Area Chart"])
    numeric_columns = data.select_dtypes(include=["float", "int"]).columns.tolist()

    if not numeric_columns:
        st.error("No numeric columns found for visualization.")
        return

    x_axis = st.sidebar.selectbox("X-Axis", options=numeric_columns)
    y_axis = st.sidebar.selectbox("Y-Axis", options=numeric_columns)

    if chart_type == "Bar Chart":
        fig = px.bar(data, x=x_axis, y=y_axis, color_discrete_sequence=px.colors.qualitative.Bold)
    elif chart_type == "Line Chart":
        fig = px.line(data, x=x_axis, y=y_axis, color_discrete_sequence=px.colors.qualitative.Pastel)
    elif chart_type == "Pie Chart":
        category = st.sidebar.selectbox("Category Column", options=data.columns)
        fig = px.pie(data, names=category, values=y_axis, color_discrete_sequence=px.colors.qualitative.Safe)
    elif chart_type == "3D Scatter Plot":
        z_axis = st.sidebar.selectbox("Z-Axis", options=numeric_columns)
        fig = px.scatter_3d(data, x=x_axis, y=y_axis, z=z_axis, color=data.columns[0], color_discrete_sequence=px.colors.qualitative.Prism)
    elif chart_type == "Area Chart":
        fig = px.area(data, x=x_axis, y=y_axis, color_discrete_sequence=px.colors.qualitative.Vivid)

    st.plotly_chart(fig, use_container_width=True)

# Main Application
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Data Analytics", "Recommendations"])

    if page == "Data Analytics":
        st.title("Smart Finance Dashboard 📊📈")
        st.markdown("Upload your CSV or PDF file to generate dynamic visualizations📉.")
        uploaded_file = st.file_uploader("Upload CSV or PDF File", type=["csv", "pdf"])

        if uploaded_file is not None:
            with st.spinner("Loading data..."):
                data = load_data(uploaded_file)
            if data is not None:
                st.success("Data loaded successfully!🥳🙌🏻")
                st.write("### Uploaded Data Preview")
                st.dataframe(data)
                create_dashboard(data)

    elif page == "Recommendations":
        st.title("Smart Finance Recommendations")
        st.markdown("Get personalized suggestions based on your financial priorities.")
        uploaded_file = st.file_uploader("Upload CSV or PDF File", type=["csv", "pdf"])

        if uploaded_file is not None:
            with st.spinner("Loading data..."):
                data = load_data(uploaded_file)
            if data is not None:
                display_recommendations(data)

if __name__ == "__main__":
    main()
