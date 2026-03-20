import streamlit as st
import pandas as pd
import random
import numpy as np

st.set_page_config(page_title="Artist Combo Randomizer", layout="wide")

st.title("🎨 Artist Combo Randomizer")
st.write("Targeting artists with overlap across western (Rule34) and eastern (Danbooru) image boards.")

# ────────────────────────────────────────
# Data Loading
# ────────────────────────────────────────
@st.cache_data
def load_data():
    # Updated to 'artist.csv' per your Github structure
    file_path = "artist.csv" 
    try:
        df = pd.read_csv(file_path)
        # Clean column names in case of trailing spaces
        df.columns = [c.strip() for c in df.columns]
        
        # Data Cleaning
        df['name'] = df['name'].astype(str).str.strip()
        df['rule34_posts'] = pd.to_numeric(df['rule34_posts'], errors='coerce').fillna(0).astype(int)
        df['danbooru_posts'] = pd.to_numeric(df['danbooru_posts'], errors='coerce').fillna(0).astype(int)
        
        # Filter out empty names
        df = df[df['name'].str.len() >= 2]
        return df
    except FileNotFoundError:
        st.error(f"File '{file_path}' not found in the current directory.")
        return pd.DataFrame(columns=['name', 'rule34_posts', 'danbooru_posts'])
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame(columns=['name', 'rule34_posts', 'danbooru_posts'])

df_overlap = load_data()

# ────────────────────────────────────────
# Sidebar: Advanced Filters
# ────────────────────────────────────────
with st.sidebar:
    st.header("📊 Dataset Stats")
    # Kept these stats as requested
    st.write("Total Artists: **20,374**")
    
    st.divider()
    st.subheader("Filter by Presence")
    
    # Dual Filters
    min_r34 = st.number_input("Min Rule34 Posts", 0, 15000, 10, help="Targets western popularity.")
    min_dan = st.number_input("Min Danbooru Posts", 0, 6000, 31)
    
    st.divider()
    st.subheader("Combo Settings")
    min_k = st.slider("Min artists per combo", 1, 10, 2)
    max_k = st.slider("Max artists per combo", min_k, 20, 6)
    num_combos = st.number_input("Number of combos", 1, 100, 10)
    
    st.divider()
    weight_mode = st.selectbox(
        "Weight Selection By:", 
        ["Rule34 Popularity", "Danbooru Popularity", "Combined", "Uniform (Random)"]
    )
    add_weights = st.checkbox("Add NovelAI Weights", value=False)

    # Filtering Logic
    filtered = df_overlap[
        (df_overlap['rule34_posts'] >= min_r34) & 
        (df_overlap['danbooru_posts'] >= min_dan)
    ]
    
    artists_list = filtered['name'].tolist()
    
    st.write("") # Spacer

    # ────────────────────────────────────────
    # THE SMALL STATUS BAR (Bottom of Sidebar)
    # ────────────────────────────────────────
    if not filtered.empty:
        st.markdown(
            f"""
            <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb; font-size: 14px; text-align: center;">
                ✅ <b>{len(filtered):,}</b> artists available
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb; font-size: 14px; text-align: center;">
                ❌ No artists match filters
            </div>
            """,
            unsafe_allow_html=True
        )

# ────────────────────────────────────────
# Generation Logic
# ────────────────────────────────────────
def generate_combo():
    k = min(random.randint(min_k, max_k), len(artists_list))
    
    if weight_mode != "Uniform (Random)":
        if weight_mode == "Rule34 Popularity":
            weights = filtered['rule34_posts'].values
        elif weight_mode == "Danbooru Popularity":
            weights = filtered['danbooru_posts'].values
        else: # Combined
            weights = filtered['rule34_posts'].values + filtered['danbooru_posts'].values
        
        # Safety for zero weights
        weights = weights + 0.1 
        prob = weights / weights.sum()
        chosen = np.random.choice(artists_list, size=k, replace=False, p=prob)
    else:
        chosen = random.sample(artists_list, k)

    if add_weights:
        return ", ".join([f"{round(random.uniform(0.5, 2.5), 1)}::{a}::" for a in chosen])
    return ", ".join(chosen)

# ────────────────────────────────────────
# Main Area Display
# ────────────────────────────────────────
if not filtered.empty:
    if st.button("🚀 Generate Artist Combos", type="primary", use_container_width=True):
        combos = [generate_combo() for _ in range(num_combos)]
        
        st.subheader("Your Results")
        for i, combo in enumerate(combos, 1):
            count = len(combo.split(", "))
            st.markdown(f"**Combo #{i}** ({count} artists)")
            st.code(combo, language="text")

        st.download_button(
            "💾 Download as .txt",
            data="\n".join(combos),
            file_name="artist_combos.txt",
            use_container_width=True
        )
else:
    st.warning("Adjust the filters in the sidebar to populate the artist pool.")

st.divider()
st.caption("Data: Correlated Rule34 & Danbooru Artist Overlap")
