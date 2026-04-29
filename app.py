import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# 1. COORDINATE MAPPING (Reference for 2D Plotting)
# Using approximate LY coordinates (X, Y) relative to Sol
SYSTEM_COORDS = {
    "Sol": (0, 0),
    "Alpha Centauri": (4.37, 0.2),
    "Epsilon Eridani": (10.5, -2.1),
    "Omicron Eridani": (16.2, -5.8),
    "Delta Eridani": (29.5, 4.2),
    "82 Eridani": (19.7, -5.0),
    "Beta Hydri": (24.3, -14.5),
    "Sigma Draconis": (18.8, 12.1),
    "Tau Ceti": (11.9, -1.5),
    "Epsilon Indi": (11.8, -2.5),
}

def get_coords(system_name):
    return SYSTEM_COORDS.get(system_name, (0, 0))

# 2. UI SETUP
st.set_page_config(page_title="Bobiverse PIT Tracker", layout="wide")
st.title("🌌 Bobiverse Point-in-Time (PIT) Tracker")

# 3. DATA LOADING
try:
    df = pd.read_csv("Bobiverse PITs - PITs.csv")
    # Convert dates to datetime objects
    df['Assumed Date'] = pd.to_datetime(df['Assumed Date'])
    df = df.sort_values(['Bob', 'Assumed Date'])

    # Sidebar: Time Selector
    min_date = df['Assumed Date'].min()
    max_date = df['Assumed Date'].max()
    
    selected_date = st.sidebar.slider(
        "Select Timeline Date",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=min_date.to_pydatetime(),
        format="MMM YYYY"
    )
    selected_date = pd.Timestamp(selected_date)

    # 4. PLOTTING LOGIC (2D)
    fig = go.Figure()

    # A. Draw Star Systems (Static Background)
    for sys, coords in SYSTEM_COORDS.items():
        fig.add_trace(go.Scatter(
            x=[coords[0]], y=[coords[1]],
            mode='markers+text',
            marker=dict(size=12, color='white', opacity=0.4),
            text=[sys], textposition="bottom center",
            showlegend=False, hoverinfo='text'
        ))

    # B. Calculate Bob Positions
    bobs = df['Bob'].unique()
    colors = ['#00E5FF', '#FF3D00', '#76FF03', '#D4E157', '#F06292', '#BA68C8']

    status_list = []

    for i, bob in enumerate(bobs):
        bob_data = df[df['Bob'] == bob].sort_values('Assumed Date')
        
        # Get history up to selected date
        past_data = bob_data[bob_data['Assumed Date'] <= selected_date]
        future_data = bob_data[bob_data['Assumed Date'] > selected_date]

        if not past_data.empty:
            last_entry = past_data.iloc[-1]
            prev_system = last_entry['System']
            prev_coords = get_coords(prev_system)
            color = colors[i % len(colors)]

            # Check if traveling (if there is a future destination)
            if not future_data.empty:
                next_entry = future_data.iloc[0]
                next_system = next_entry['System']
                
                if next_system != prev_system:
                    # CALCULATE INTERPOLATION (Movement)
                    next_coords = get_coords(next_system)
                    
                    time_diff = (next_entry['Assumed Date'] - last_entry['Assumed Date']).total_seconds()
                    elapsed = (selected_date - last_entry['Assumed Date']).total_seconds()
                    
                    # Fraction of journey completed (0.0 to 1.0)
                    fraction = elapsed / time_diff if time_diff > 0 else 0
                    
                    curr_x = prev_coords[0] + (next_coords[0] - prev_coords[0]) * fraction
                    curr_y = prev_coords[1] + (next_coords[1] - prev_coords[1]) * fraction
                    
                    # Draw Dotted Travel Line
                    fig.add_trace(go.Scatter(
                        x=[prev_coords[0], next_coords[0]],
                        y=[prev_coords[1], next_coords[1]],
                        mode='lines',
                        line=dict(color=color, width=1, dash='dot'),
                        showlegend=False, hoverinfo='none'
                    ))
                    
                    status = f"Traveling: {prev_system} ➔ {next_system}"
                else:
                    curr_x, curr_y = prev_coords
                    status = f"At {prev_system}"
            else:
                curr_x, curr_y = prev_coords
                status = f"At {prev_system}"

            # Draw the Bob
            fig.add_trace(go.Scatter(
                x=[curr_x], y=[curr_y],
                mode='markers+text',
                marker=dict(size=10, color=color, symbol='diamond'),
                text=[bob], textposition="top center",
                name=bob
            ))
            
            status_list.append({"Bob": bob, "Status": status, "Last Log": last_entry['Assumed Date'].date()})

    # C. Figure Layout (2D)
    fig.update_layout(
        template="plotly_dark",
        height=700,
        xaxis=dict(title="Light Years (X)", gridcolor="#333"),
        yaxis=dict(title="Light Years (Y)", gridcolor="#333"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 5. STATUS TABLE
    st.subheader(f"Status as of {selected_date.date()}")
    st.table(pd.DataFrame(status_list))

except FileNotFoundError:
    st.error("CSV file 'Bobiverse PITs - PITs.csv' not found. Please ensure it is in the same directory.")
except Exception as e:
    st.error(f"An error occurred: {e}")