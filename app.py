import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="DataPilot | Data Analysis MVP", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS (KPI Cards, Clean Layout, & Footer)
# =====================================================
st.markdown("""
<style>
    /* Custom KPI Cards */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    .kpi-card h2 { margin: 0; color: #0284c7; font-size: 2rem; }
    .kpi-card p { margin: 0; font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Clean up the header */
    .main-header {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #0284c7;
        margin-bottom: 25px;
    }
    
    /* Ensure content isn't hidden behind the fixed footer */
    .block-container {
        padding-bottom: 80px;
    }
    
    /* Fixed Footer Styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f8fafc;
        color: #475569;
        text-align: center;
        padding: 12px 0;
        font-size: 14px;
        border-top: 1px solid #e2e8f0;
        z-index: 1000;
    }
    .footer a {
        color: #0284c7;
        text-decoration: none;
        font-weight: 600;
        margin: 0 5px;
    }
    .footer a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPER FUNCTIONS (Cached for Performance)
# =====================================================
@st.cache_data
def convert_df_to_csv(df):
    """Caches the converted CSV so we don't re-compute on every click."""
    return df.to_csv(index=False).encode('utf-8')

# =====================================================
# STATE MANAGEMENT
# =====================================================
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "df" not in st.session_state:
    st.session_state.df = None
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "visual_config" not in st.session_state:
    st.session_state.visual_config = []

# =====================================================
# HERO SECTION
# =====================================================
st.markdown("""
<div class='main-header'>
    <h1 style='margin:0; color:#0f172a;'>📊 DataPilot</h1>
    <p style='margin:0; color:#64748b;'>Upload → Clean → Visualize → Report</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR: NAVIGATION & UPLOAD
# =====================================================
st.sidebar.markdown("### 🧭 Navigation")
page = st.sidebar.radio("Go to:", ["1. Upload & Clean", "2. Visualize", "3. Final Report"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Data Source")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv","xls","xlsx"])

# Handle File Upload Safely
if uploaded_file:
    if st.session_state.current_file != uploaded_file.name:
        try:
            if uploaded_file.name.endswith(".csv"):
                try:
                    temp_df = pd.read_csv(uploaded_file, encoding="utf-8")
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    temp_df = pd.read_csv(uploaded_file, encoding="latin1")
            else:
                temp_df = pd.read_excel(uploaded_file)
            
            # Save both raw (for resets) and working copy
            st.session_state.raw_df = temp_df.copy()
            st.session_state.df = temp_df.copy()
            st.session_state.current_file = uploaded_file.name
            st.session_state.visual_config = [] # Reset visuals on new file
            st.sidebar.success("File loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

# Local reference for convenience
df = st.session_state.df

# =====================================================
# PAGE 1: UPLOAD & CLEAN
# =====================================================
if page == "1. Upload & Clean":
    st.header("🛠️ Dataset Control Room")

    if df is not None:
        
        # --- RESTORED KPI CARDS FOR LIVE CLEANING FEEDBACK ---
        st.subheader("Dataset Overview")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='kpi-card'><h2>{df.shape[0]:,}</h2><p>Total Rows</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card'><h2>{df.shape[1]:,}</h2><p>Total Columns</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='kpi-card'><h2>{df.duplicated().sum():,}</h2><p>Duplicate Rows</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='kpi-card'><h2>{df.isnull().sum().sum():,}</h2><p>Missing Values</p></div>", unsafe_allow_html=True)
        
        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        col_tools, col_preview = st.columns([1, 2])
        
        with col_tools:
            st.subheader("Data Cleaning")
            
            if st.button("Drop Duplicate Rows", use_container_width=True):
                st.session_state.df = df.drop_duplicates()
                st.rerun()

            numeric_cols = df.select_dtypes(include=["number"]).columns
            fill_strat = st.selectbox("Fill missing numeric values with:", ["Select Strategy", "Mean", "Median", "Zero"])
            
            if st.button("Apply Fill Strategy", use_container_width=True):
                if fill_strat == "Mean":
                    st.session_state.df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                elif fill_strat == "Median":
                    st.session_state.df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
                elif fill_strat == "Zero":
                    st.session_state.df[numeric_cols] = df[numeric_cols].fillna(0)
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("⚠️ Reset to Original Data", use_container_width=True):
                st.session_state.df = st.session_state.raw_df.copy()
                st.rerun()

        with col_preview:
            st.subheader("Live Data Preview")
            st.dataframe(df.head(15), use_container_width=True)
            
            csv_data = convert_df_to_csv(st.session_state.df)
            st.download_button(
                label="📥 Download Cleaned Dataset (CSV)",
                data=csv_data,
                file_name=f"cleaned_{st.session_state.current_file.split('.')[0]}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("👈 Please upload a dataset in the sidebar to begin.")

# =====================================================
# PAGE 2: VISUALIZE
# =====================================================
elif page == "2. Visualize":
    st.header("📈 Visual Builder")

    if df is not None:
        numeric_cols = df.select_dtypes(include=["number"]).columns
        all_cols = df.columns

        st.write("Configure your charts here. They will automatically be added to your Final Report.")
        num_visuals = st.slider("Number of visuals to build:", 1, 9, 3)
        chart_types = ["Histogram", "Bar", "Pie", "Line", "Scatter", "Boxplot"]

        st.session_state.visual_config = []

        for i in range(num_visuals):
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                chart = st.selectbox("Chart Type", chart_types, key=f"type_{i}")
            with col2:
                column = st.selectbox("Target Column", all_cols, key=f"col_{i}")
            
            st.session_state.visual_config.append((chart, column))

            with col3:
                fig, ax = plt.subplots(figsize=(5, 1.5))
                try:
                    if chart == "Histogram" and column in numeric_cols:
                        ax.hist(df[column].dropna(), bins=20, color='#0284c7', edgecolor='white')
                    elif chart == "Bar":
                        vc = df[column].value_counts().head(8)
                        ax.bar(vc.index.astype(str), vc.values, color='#0284c7')
                    elif chart == "Pie":
                        vc = df[column].value_counts().head(5)
                        ax.pie(vc.values, labels=vc.index.astype(str), autopct="%1.0f%%")
                    elif chart == "Line" and column in numeric_cols:
                        ax.plot(df[column].dropna(), color='#0284c7')
                    elif chart == "Scatter" and column in numeric_cols:
                        ax.scatter(range(len(df[column])), df[column].dropna(), color='#0284c7', alpha=0.5)
                    elif chart == "Boxplot" and column in numeric_cols:
                        ax.boxplot(df[column].dropna(), vert=False)
                    else:
                        st.write("⚠️ *Select a numeric column for this chart type.*")
                        
                    st.pyplot(fig)
                except Exception as e:
                    st.error("Cannot render preview.")
                finally:
                    plt.close(fig) 
            st.divider()
    else:
        st.info("👈 Please upload a dataset in the sidebar to begin.")

# =====================================================
# PAGE 3: FINAL REPORT
# =====================================================
elif page == "3. Final Report":
    st.header("📑 Executive Dashboard")

    if df is not None:
        
        # --- 1. KPI CARDS ---
        st.subheader("Key Performance Indicators")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='kpi-card'><h2>{df.shape[0]:,}</h2><p>Total Rows</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='kpi-card'><h2>{df.shape[1]:,}</h2><p>Total Columns</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='kpi-card'><h2>{df.duplicated().sum():,}</h2><p>Duplicate Rows</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='kpi-card'><h2>{df.isnull().sum().sum():,}</h2><p>Missing Values</p></div>", unsafe_allow_html=True)
        
        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        # --- 2. POWER BI STYLE VISUAL GRID (3 per row) ---
        st.subheader("Visual Analytics")
        numeric_cols = df.select_dtypes(include=["number"]).columns

        if st.session_state.visual_config:
            visuals = st.session_state.visual_config
            
            for i in range(0, len(visuals), 3):
                cols = st.columns(3)
                
                for idx, (chart, column) in enumerate(visuals[i:i+3]):
                    with cols[idx]:
                        st.markdown(f"<h5 style='text-align:center; color:#334155;'>{chart}: {column}</h5>", unsafe_allow_html=True)
                        
                        fig, ax = plt.subplots(figsize=(4, 3))
                        try:
                            if chart == "Histogram" and column in numeric_cols:
                                ax.hist(df[column].dropna(), bins=20, color='#10b981', edgecolor='white')
                            elif chart == "Bar":
                                vc = df[column].value_counts().head(8)
                                ax.bar(vc.index.astype(str), vc.values, color='#10b981')
                                plt.xticks(rotation=45)
                            elif chart == "Pie":
                                vc = df[column].value_counts().head(5)
                                ax.pie(vc.values, labels=vc.index.astype(str), autopct="%1.0f%%")
                            elif chart == "Line" and column in numeric_cols:
                                ax.plot(df[column].dropna(), color='#10b981')
                            elif chart == "Scatter" and column in numeric_cols:
                                ax.scatter(range(len(df[column])), df[column].dropna(), color='#10b981', alpha=0.5)
                            elif chart == "Boxplot" and column in numeric_cols:
                                ax.boxplot(df[column].dropna(), vert=False)
                            
                            plt.tight_layout()
                            st.pyplot(fig)
                        except Exception:
                            st.error(f"Cannot render {chart} for {column}.")
                        finally:
                            plt.close(fig)
                
                st.markdown("<br>", unsafe_allow_html=True) 
        else:
            st.info("Go to the 'Visualize' tab to build charts for your dashboard.")
            
        st.markdown("<hr><br>", unsafe_allow_html=True)
        
        # --- 3. STATISTICAL SUMMARY ---
        st.subheader("Statistical Summary")
        if len(numeric_cols) > 0:
            summary_df = df[numeric_cols].describe().T[['mean', 'min', 'max', 'std']]
            st.dataframe(summary_df.round(2), use_container_width=True)
        else:
            st.write("No numeric columns available for statistical summary.")

    else:
        st.info("👈 Please upload a dataset in the sidebar to begin.")

# =====================================================
# FIXED FOOTER
# =====================================================
st.markdown("""
<div class="footer">
    <strong>DataPilot</strong> | Contact Developer: 
    <a href="mailto:kavyanshverma8@gmail.com" target="_blank">Email</a> | 
    <a href="https://www.linkedin.com/in/kavyansh-verma/" target="_blank">LinkedIn</a> |
    <a href="https://vkavyansh.github.io/DataAnalyst-Portfolio/" target="_blank">GitHub</a> |
    <a href="https://vkavyansh.github.io/Portfolio/" target="_blank">Portfolio</a> 
</div>
""", unsafe_allow_html=True)



