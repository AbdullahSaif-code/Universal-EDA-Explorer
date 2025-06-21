# Universal EDA Explorer

Universal EDA Explorer is a flexible, interactive Streamlit dashboard for **exploratory data analysis (EDA)** on any CSV dataset.  
Upload your own CSV file and instantly filter, visualize, and summarize your data—no coding required!

---

## 🚀 Features

- **Upload any CSV dataset** (no hardcoded columns)
- **Dynamic sidebar filters** for all columns (skips columns with too many unique values)
- **Data preview** of the uploaded file
- **Custom graph generator**:  
  - Select X and Y columns  
  - Choose relationship type: Auto, One-to-One, One-to-Many, Many-to-Many  
  - Advanced options: aggregation, color, axis labels, plot size
- **Summary statistics** for any column (numeric or categorical)
- **Download filtered data** as CSV
- **Download generated plot** as HTML
- **User guidance** and warnings for unsuitable graph/column combinations
- **Handles empty DataFrames** and bad file uploads gracefully

---

## 📦 Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/AbdullahSaif-code/Universal-EDA-Explorer.git
    cd Netflix_EDA_Flask_app
    ```

2. **Install requirements**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🏃 Usage

1. **Run the app**
    ```bash
    streamlit run app.py
    ```

2. **Upload your CSV file** using the uploader at the top.

3. **Preview your data** and use the sidebar to filter columns.

4. **Generate custom graphs** by selecting X and Y columns and relationship type.

5. **Customize your plot** with aggregation, color, axis labels, and size.

6. **Download** the filtered data or your plot as needed.

---

## 📊 Visualization Types

- **Auto:** Smartly chooses the best plot based on column types.
- **One-to-One:** Scatter plot for two numeric columns.
- **One-to-Many:** Bar plot for categorical X and numeric Y.
- **Many-to-Many:** Heatmap for two categorical columns.

---

## 🛡️ Error Handling & Tips

- If your CSV is invalid or empty, you’ll see a clear error message.
- Columns with too many unique values are skipped for filtering and plotting to keep the UI usable.
- If your filtered data is empty, you’ll be prompted to adjust your filters.
- Only appropriate columns are shown for each graph type (e.g., only numeric for Y in bar/scatter).

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Credits

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)

---

## 💡 Inspiration

Universal EDA Explorer was created to make data exploration accessible to everyone—no coding required. Whether you’re a data scientist, analyst, or just curious about your data, this tool helps you gain insights quickly