"""
Simple Streamlit app for the Used Car Pricer project.

This template:
- Loads sample_listings.csv from the repo root (or lets the user upload a CSV).
- Shows a table of listings and lets the user pick one.
- Attempts to call a predict_price(listing_dict) function in comp_pricer.py.
- If comp_pricer.predict_price is not available, shows instructions.

Adapt to match the actual API in comp_pricer.py (function name / expected input).
"""
from typing import Optional, Dict, Any
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Used Car Pricer", layout="wide")

st.title("Used Car Pricer")
st.write("Select a listing to price it, or upload your own CSV of listings.")

# Try to import comp_pricer and detect API
_comp_pricer = None
_predict_fn_name = None
try:
    import comp_pricer as _cp  # type: ignore
    _comp_pricer = _cp
    if hasattr(_cp, "predict_price"):
        _predict_fn_name = "predict_price"
    elif hasattr(_cp, "price"):
        _predict_fn_name = "price"
    elif hasattr(_cp, "get_price"):
        _predict_fn_name = "get_price"
    else:
        _predict_fn_name = None
except Exception as e:
    _comp_pricer = None
    _predict_fn_name = None

def load_sample_csv(path: str = "sample_listings.csv") -> Optional[pd.DataFrame]:
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            st.error(f"Failed to read {path}: {e}")
            return None
    return None

# Sidebar: choose source
source = st.sidebar.radio("Data source", ("Repo sample_listings.csv", "Upload CSV"))

df = None
if source == "Repo sample_listings.csv":
    df = load_sample_csv("sample_listings.csv")
    if df is None:
        st.warning("sample_listings.csv not found in the repo. Upload a CSV or push the file to your repo.")
else:
    uploaded = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")

if df is None:
    st.info("No data loaded. You can upload a CSV on the left or add sample_listings.csv to the repo root.")
    st.stop()

st.subheader("Listings preview")
st.dataframe(df.head(50))

# Selection
st.subheader("Pick a listing to price")
# Build a display column for selection (prefer id or first cols)
if "id" in df.columns:
    display_col = df["id"].astype(str)
else:
    # compose a small summary per row
    display_col = df.apply(lambda r: " | ".join([str(r[c]) for c in df.columns[:3]]), axis=1)

selection_index = st.selectbox("Select row", options=df.index.tolist(), format_func=lambda i: display_col.loc[i])

selected_row = df.loc[selection_index]
st.write("Selected listing")
st.json(selected_row.to_dict())

# Pricing action
st.subheader("Price this listing")
col1, col2 = st.columns([1, 2])

with col1:
    if _comp_pricer is None:
        st.error("comp_pricer.py not found or failed to import. Make sure comp_pricer.py is in the repo root and has a pricing function.")
    else:
        if _predict_fn_name is None:
            st.warning(
                "comp_pricer.py was imported but no known pricing function was detected.\n"
                "Expected one of: predict_price(listing_dict), price(listing_dict), get_price(listing_dict).\n"
                "Open comp_pricer.py and either implement predict_price(listing_dict) or tell the app the function name."
            )
        else:
            st.success(f"Detected comp_pricer.{_predict_fn_name}() — ready to price.")

with col2:
    # Optional parameter inputs could go here
    pass

if st.button("Compute price"):
    listing_dict: Dict[str, Any] = selected_row.to_dict()
    if _comp_pricer is None:
        st.error("Cannot compute price because comp_pricer module is not available.")
    elif _predict_fn_name is None:
        st.error(
            "comp_pricer is available but no supported pricing function was found. "
            "Please implement predict_price(listing_dict) (or rename your function) in comp_pricer.py."
        )
    else:
        try:
            predict_fn = getattr(_comp_pricer, _predict_fn_name)
            # Call the function. Accept either dict or pandas Series depending on user's implementation.
            result = predict_fn(listing_dict)
            st.success("Price computed")
            st.write("Result:")
            # If result is dict-like, pretty-print; otherwise just show it.
            if isinstance(result, dict):
                st.json(result)
            else:
                st.write(result)
        except TypeError:
            # Try calling with the Series if predict expects Series
            try:
                result = predict_fn(selected_row)
                st.success("Price computed (called with pandas Series)")
                if isinstance(result, dict):
                    st.json(result)
                else:
                    st.write(result)
            except Exception as e:
                st.exception(e)
        except Exception as e:
            st.exception(e)

st.markdown("---")
st.write(
    "Notes: If your comp_pricer has a different API, modify the detection logic at the top of this file "
    "or implement predict_price(listing_dict) in comp_pricer.py. For local testing run:\n\n"
)
st.code("streamlit run streamlit_app.py")