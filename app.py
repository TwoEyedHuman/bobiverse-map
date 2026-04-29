import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math

# 1. COORDINATE MAPPING
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
st.set_page_config(page_title="Bobiverse Tactical Tracker", layout="wide")
st.title("🌌 Bobiverse Tactical Movement Map")

# 3. DATA LOADING
try:
    df = pd.read_csv("Bobiverse PITs - PITs.csv")
    df['Assumed Date'] = pd.to_datetime(df['Assumed Date'])
    df = df.sort_values(['Bob', 'Assumed Date'])

    min_date = df['Assumed Date'].min()
    max_date = df['Assumed Date'].max()
    
    selected_date = st.sidebar.slider(
        "Timeline Date",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=min_date.to_pydatetime(),
        format="MMM YYYY"
    )
    selected_date = pd.Timestamp(selected_date)

    # 4. PLOTTING LOGIC
    fig = go.Figure()

    # A. Star Systems
    for sys, coords in SYSTEM_COORDS.items():
        fig.add_trace(go.Scatter(
            x=[coords[0]], y=[coords[1]],
            mode='markers+text',
            marker=dict(size=12, color='white', opacity=0.3),
            text=[sys], textposition="bottom center",
            showlegend=False, hoverinfo='text'
        ))

    # B. Calculate Bob Positions & Angles
    bobs = df['Bob'].unique()
    processed_positions = []

    for bob in bobs:
        bob_data = df[df['Bob'] == bob].sort_values('Assumed Date')
        past_data = bob_data[bob_data['Assumed Date'] <= selected_date]
        future_data = bob_data[bob_data['Assumed Date'] > selected_date]

        if not past_data.empty:
            last_entry = past_data.iloc[-1]
            prev_coords = get_coords(last_entry['System'])
            angle = 0  
            is_traveling = False
            travel_path = None

            if not future_data.empty:
                next_entry = future_data.iloc[0]
                next_coords = get_coords(next_entry['System'])
                
                if next_entry['System'] != last_entry['System']:
                    is_traveling = True
                    time_diff = (next_entry['Assumed Date'] - last_entry['Assumed Date']).total_seconds()
                    elapsed = (selected_date - last_entry['Assumed Date']).total_seconds()
                    fraction = elapsed / time_diff if time_diff > 0 else 0
                    
                    curr_x = prev_coords[0] + (next_coords[0] - prev_coords[0]) * fraction
                    curr_y = prev_coords[1] + (next_coords[1] - prev_coords[1]) * fraction
                    
                    # Calculate Heading
                    dx = next_coords[0] - prev_coords[0]
                    dy = next_coords[1] - prev_coords[1]
                    angle = 90 - (math.atan2(dy, dx) * 180 / math.pi)
                    
                    # Store path data to draw later so we can match auto-colors
                    travel_path = ([prev_coords[0], next_coords[0]], [prev_coords[1], next_coords[1]])
                    status = f"Traveling to {next_entry['System']}"
                else:
                    curr_x, curr_y = prev_coords
                    status = f"Stationary at {last_entry['System']}"
            else:
                curr_x, curr_y = prev_coords
                status = f"Stationary at {last_entry['System']}"

            processed_positions.append({
                "name": bob, "x": curr_x, "y": curr_y, 
                "angle": angle, "status": status,
                "is_traveling": is_traveling, "last_date": last_entry['Assumed Date'].date(),
                "path": travel_path
            })

    # C. Jitter Logic (Anti-Stacking)
    pos_counts = {}
    for p in processed_positions:
        coord_key = (round(p['x'], 2), round(p['y'], 2))
        pos_counts[coord_key] = pos_counts.get(coord_key, []) + [p]

    final_status_list = []
    for coord, cluster in pos_counts.items():
        n = len(cluster)
        for idx, p in enumerate(cluster):
            display_x, display_y = p['x'], p['y']
            
            # Tiny orbit for Bobs at the same station
            if n > 1 and not p['is_traveling']:
                offset_radius = 0.7  
                theta = (2 * math.pi * idx) / n
                display_x += offset_radius * math.cos(theta)
                display_y += offset_radius * math.sin(theta)

            # Draw Path First (matches Bob's auto-generated color via legendgroup)
            if p['path']:
                fig.add_trace(go.Scatter(
                    x=p['path'][0], y=p['path'][1],
                    mode='lines',
                    line=dict(width=1, dash='dot'),
                    legendgroup=p['name'],
                    showlegend=False,
                    hoverinfo='none'
                ))

            # Draw Bob Icon
            fig.add_trace(go.Scatter(
                x=[display_x], y=[display_y],
                mode='markers+text',
                marker=dict(size=14, symbol='triangle-up', angle=p['angle']),
                text=[p['name']], textposition="top center",
                name=p['name'],
                legendgroup=p['name'] # Ensures same auto-color as path
            ))
            
            final_status_list.append({"Bob": p['name'], "Status": p['status'], "Last Log": p['last_date']})

    # D. Layout
    fig.update_layout(
        template="plotly_dark",
        height=800,
        xaxis=dict(title="LY (X)", gridcolor="#333", zeroline=False),
        yaxis=dict(title="LY (Y)", gridcolor="#333", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.subheader(f"Tactical Status: {selected_date.date()}")
    st.table(pd.DataFrame(final_status_list))

except Exception as e:
    st.error(f"Error: {e}")