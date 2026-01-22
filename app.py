import streamlit as st
import pandas as pd
import re
import hashlib

# ---------------- Functions ----------------
def normalize_sl_phone(number):
    """
    Normalize Sri Lankan phone numbers to 947XXXXXXXX format
    Accepts formats like:
    - 701234567
    - 0712345678
    - 94712345678
    - +94712345678
    """
    if pd.isna(number):
        return None

    # Convert to string and remove all non-numeric characters
    num = str(number).strip()
    num = re.sub(r'\D', '', num)

    # Add leading 0 if it's 9 digits starting with 7
    if len(num) == 9 and num.startswith('7'):
        num = '0' + num

    # Normalize to 947XXXXXXXX
    if num.startswith('0') and len(num) == 10:
        num = '94' + num[1:]
    elif num.startswith('94') and len(num) == 11:
        num = num
    elif num.startswith('947') and len(num) == 11:
        num = num
    else:
        return None  # invalid number

    return num

def sha256_hash(value):
    """Apply SHA-256 hashing"""
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="SL Phone Hasher", page_icon="🔒", layout="centered")
st.title("Sri Lanka Phone Hasher for FB/Meta Custom Audiences")
st.write("Upload a CSV with a column named `phone`. The app will normalize and hash the numbers.")

# File upload
uploaded_file = st.file_uploader("Choose CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Check column
    if 'phone' not in df.columns:
        st.error("CSV must contain a column named 'phone'.")
    else:
        # Normalize
        df['normalized_phone'] = df['phone'].apply(normalize_sl_phone)

        # Show first 20 rows to debug
        # st.write("Sample of normalized numbers:")
        # st.dataframe(df[['phone', 'normalized_phone']].head(20))

        # Drop invalid numbers
        df = df.dropna(subset=['normalized_phone'])

        # Hash
        df['hashed_phone'] = df['normalized_phone'].apply(sha256_hash)

        # Prepare download
        upload_df = df[['hashed_phone']]
        st.success(f"Processed {len(upload_df)} phone numbers successfully!")

        # Show first few hashed numbers
        st.write("Sample of hashed numbers:")
        st.dataframe(upload_df.head(20))

        # Convert to CSV for download
        csv = upload_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Hashed CSV",
            data=csv,
            file_name='fb_custom_audience_hashed.csv',
            mime='text/csv'
        )
