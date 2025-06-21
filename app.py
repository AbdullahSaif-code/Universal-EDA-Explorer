import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(
    page_title="Universal EDA Explorer",
    layout="centered",
    initial_sidebar_state="expanded"  # This makes the sidebar shown by default
)

# Performance: cache file reading
@st.cache_data
def load_csv(file):
    try:
        return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

# File uploader for custom dataset
uploaded_file = st.file_uploader("Upload your CSV dataset", type=["csv"])
if uploaded_file is not None:
    df = load_csv(uploaded_file)
    if df is not None:
        st.success("Custom dataset loaded!")
    else:
        st.stop()
else:
    st.info("Please upload a CSV file to begin exploring your data.")
    st.stop()

st.title("🔎 Universal EDA Explorer")

columns = df.columns.tolist()

# Dynamically build sidebar filters based on available columns
st.sidebar.header("Filter Data")
filter_values = {}
for col in columns:
    unique_vals = sorted(df[col].dropna().unique())
    if 1 < len(unique_vals) < 100:  # Only show filter if not too many unique values and not constant
        selected = st.sidebar.selectbox(f"{col}", options=["All"] + [str(v) for v in unique_vals])
        filter_values[col] = selected

# Filter DataFrame based on sidebar selections
filtered_df = df.copy()
for col, selected in filter_values.items():
    if selected != "All":
        try:
            dtype = df[col].dtype
            if pd.api.types.is_numeric_dtype(dtype):
                selected = pd.to_numeric(selected)
        except Exception:
            pass
        filtered_df = filtered_df[filtered_df[col] == selected]

# Handle empty DataFrame
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your filters.")
    st.stop()

# Add help/documentation
with st.expander("ℹ️ How to use this dashboard", expanded=False):
    st.markdown("""
    - **Filter** the data using the sidebar.
    - **Select X and Y columns** to visualize relationships.
    - **Choose a relationship type** for different graph styles.
    - **Summary statistics** for any column are shown on the right.
    - If no graph appears, check your selections or filters.
    """)

st.markdown("### Custom Graph Generator")

relationship_type = st.radio(
    "Select Relationship Type",
    options=["Auto", "One-to-One", "One-to-Many", "Many-to-Many"],
    horizontal=True
)

# Column type filtering for graph selection
numeric_columns = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
categorical_columns = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() < 100]

col1, col2, col3 = st.columns(3)
with col1:
    if relationship_type == "Many-to-Many":
        x_options = ["Select..."] + categorical_columns
    elif relationship_type in ["Auto", "One-to-One", "One-to-Many"]:
        x_options = ["Select..."] + columns
    selected_x = st.selectbox("X Column", options=x_options)
with col2:
    if relationship_type == "Many-to-Many":
        y_options = ["Select..."] + categorical_columns
    elif relationship_type in ["Auto", "One-to-One"]:
        y_options = ["Select..."] + numeric_columns
    elif relationship_type == "One-to-Many":
        y_options = ["Select..."] + numeric_columns
    else:
        y_options = ["Select..."] + columns
    selected_y = st.selectbox("Y Column", options=y_options)
with col3:
    selected_col = st.selectbox("Summary Column", options=columns)

# Show summary statistics
if selected_col:
    st.markdown(f"#### Summary Statistics for `{selected_col}`")
    if pd.api.types.is_numeric_dtype(df[selected_col]):
        st.dataframe(filtered_df[selected_col].describe().to_frame())
    else:
        st.dataframe(filtered_df[selected_col].value_counts().to_frame("count"))

# Input validation and user guidance
if (selected_x == "Select..." or selected_y == "Select..."):
    st.info("Please select both X and Y columns to generate a graph.")
else:
    x_dtype = df[selected_x].dtype
    y_dtype = df[selected_y].dtype

    # Warn if columns are not suitable for the selected relationship type
    warning = None
    if relationship_type in ["Auto", "One-to-One"]:
        if not (pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype)):
            warning = "Scatter plots work best with numeric columns for both X and Y."
    elif relationship_type == "One-to-Many":
        if not pd.api.types.is_numeric_dtype(y_dtype):
            warning = "Bar plots work best when Y is numeric."
    elif relationship_type == "Many-to-Many":
        if pd.api.types.is_numeric_dtype(x_dtype) or pd.api.types.is_numeric_dtype(y_dtype):
            warning = "Heatmaps work best when both X and Y are categorical."

    if warning:
        st.warning(warning)

    # Graph customization: color by (optional), aggregation, axis labels
    with st.expander("⚙️ Advanced Graph Options"):
        color_by = st.selectbox("Color By (optional)", options=["None"] + columns, index=0)
        agg_func = st.selectbox("Aggregation Function (for bar/heatmap)", options=["count", "sum", "mean"], index=0)
        x_label = st.text_input("X Axis Label", value=selected_x)
        y_label = st.text_input("Y Axis Label", value=selected_y)
        plot_height = st.slider("Plot Height (px)", min_value=300, max_value=1000, value=500)

    # Relationship-based graph selection
    fig = None
    if relationship_type == "Auto":
        if pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype):
            fig = px.scatter(filtered_df, x=selected_x, y=selected_y,
                             color=None if color_by == "None" else color_by,
                             title=f"{selected_y} vs {selected_x} (Scatter)",
                             height=plot_height,
                             labels={selected_x: x_label, selected_y: y_label})
        elif pd.api.types.is_numeric_dtype(y_dtype):
            if agg_func == "count":
                fig = px.bar(filtered_df, x=selected_x, color=None if color_by == "None" else color_by,
                             title=f"{selected_y} by {selected_x} (Bar)",
                             height=plot_height,
                             labels={selected_x: x_label, selected_y: y_label})
            else:
                grouped = filtered_df.groupby(selected_x)[selected_y].agg(agg_func).reset_index()
                fig = px.bar(grouped, x=selected_x, y=selected_y,
                             color=None if color_by == "None" else color_by,
                             title=f"{selected_y} by {selected_x} ({agg_func.title()})",
                             height=plot_height,
                             labels={selected_x: x_label, selected_y: y_label})
        else:
            fig = px.histogram(filtered_df, x=selected_x, color=None if color_by == "None" else color_by,
                               title=f"Distribution of {selected_x} (Histogram)",
                               height=plot_height,
                               labels={selected_x: x_label})
    elif relationship_type == "One-to-One":
        fig = px.scatter(filtered_df, x=selected_x, y=selected_y,
                         color=None if color_by == "None" else color_by,
                         title=f"One-to-One: {selected_y} vs {selected_x}",
                         height=plot_height,
                         labels={selected_x: x_label, selected_y: y_label})
    elif relationship_type == "One-to-Many":
        if agg_func == "count":
            fig = px.bar(filtered_df, x=selected_x, color=None if color_by == "None" else color_by,
                         title=f"One-to-Many: {selected_y} by {selected_x} (Count)",
                         height=plot_height,
                         labels={selected_x: x_label, selected_y: y_label})
        else:
            grouped = filtered_df.groupby(selected_x)[selected_y].agg(agg_func).reset_index()
            fig = px.bar(grouped, x=selected_x, y=selected_y,
                         color=None if color_by == "None" else color_by,
                         title=f"One-to-Many: {selected_y} by {selected_x} ({agg_func.title()})",
                         height=plot_height,
                         labels={selected_x: x_label, selected_y: y_label})
    elif relationship_type == "Many-to-Many":
        if not (pd.api.types.is_numeric_dtype(x_dtype) or pd.api.types.is_numeric_dtype(y_dtype)):
            if agg_func == "count":
                pivot = pd.pivot_table(filtered_df, index=selected_x, columns=selected_y, aggfunc='size', fill_value=0)
            else:
                pivot = pd.pivot_table(filtered_df, index=selected_x, columns=selected_y, values=filtered_df.columns[0], aggfunc=agg_func, fill_value=0)
            fig = px.imshow(pivot, title=f"Many-to-Many: {selected_x} vs {selected_y} (Heatmap)",
                            height=plot_height,
                            labels={"x": x_label, "y": y_label})
        else:
            st.warning("Many-to-Many heatmap requires both X and Y to be categorical columns.")

    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
        # Download plot as HTML
        plot_html = fig.to_html()
        st.download_button(
            label="⬇️ Download Plot as HTML",
            data=plot_html,
            file_name="plot.html",
            mime="text/html"
        )

# --- Move Preview Data and Download Filtered Data as CSV to the end ---

with st.expander("🔍 Preview Data"):
    st.dataframe(filtered_df.head(20))

csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv_buffer.getvalue(),
    file_name="filtered_data.csv",
    mime="text/csv"
)