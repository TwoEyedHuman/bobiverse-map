import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. DATA STRUCTURE: Bob Movement History (X, Y, Z)
# Coordinates are approximate LY from Sol
bob_histories = {
    "Bob 1.0": [
        {"chapter": 1, "sys": "Sol", "x": 0, "y": 0, "z": 0},
        {"chapter": 10, "sys": "Epsilon Eridani", "x": 10.5, "y": -2.1, "z": 1.5},
        {"chapter": 17, "sys": "Delta Eridani", "x": 29.5, "y": 4.2, "z": -3.1}
    ],
    "Riker": [
        {"chapter": 1, "sys": "Sol", "x": 0, "y": 0, "z": 0},
        {"chapter": 20, "sys": "Sol", "x": 0.2, "y": 0.8, "z": 0.5} 
    ],
    "Bill": [
        {"chapter": 10, "sys": "Epsilon Eridani", "x": 10.5, "y": -2.1, "z": 1.5},
        {"chapter": 25, "sys": "Epsilon Eridani (High Orbit)", "x": 11.2, "y": -1.8, "z": 2.0}
    ],
    "Milo": [
        {"chapter": 1, "sys": "Sol", "x": 0, "y": 0, "z": 0},
        {"chapter": 15, "sys": "82 Eridani", "x": 19.7, "y": -5.0, "z": 1.1}
    ],
    "Mario": [
        {"chapter": 1, "sys": "Sol", "x": 0, "y": 0, "z": 0},
        {"chapter": 30, "sys": "Delta Pavonis", "x": 19.9, "y": -12.4, "z": -4.5}
    ]
}

# Star Systems (Static Reference Points)
star_systems = [
    {"name": "Sol", "x": 0, "y": 0, "z": 0},
    {"name": "Alpha Centauri", "x": 4.3, "y": 0.5, "z": -0.2},
    {"name": "Epsilon Eridani", "x": 10.5, "y": -2.1, "z": 1.5},
    {"name": "Delta Eridani", "x": 29.5, "y": 4.2, "z": -3.1},
    {"name": "82 Eridani", "x": 19.7, "y": -5.0, "z": 1.1},
    {"name": "Delta Pavonis", "x": 19.9, "y": -12.4, "z": -4.5}
]

# 2. UI SETUP
st.set_page_config(page_title="Bobiverse 3D Tactical", layout="wide")
st.title("🌌 Bobiverse 3D Spatial Path Tracker")

current_ch = st.sidebar.slider("Log Progress (Chapter)", 1, 40, 20)

# 3. 3D PLOT LOGIC
fig = go.Figure()

# A. Reference Stars (Small, non-colored circles)
sys_df = pd.DataFrame(star_systems)
fig.add_trace(go.Scatter3d(
    x=sys_df['x'], y=sys_df['y'], z=sys_df['z'],
    mode='markers+text',
    marker=dict(size=4, color='white', opacity=0.3),
    text=sys_df['name'],
    textposition="bottom center",
    name="Star Systems",
    hoverinfo='text'
))

# B. Bob Paths and Current Locations
colors = ['#00E5FF', '#FF3D00', '#76FF03', '#D4E157', '#F06292']

for i, (name, history) in enumerate(bob_histories.items()):
    # Filter by chapter
    active_path = [h for h in history if h['chapter'] <= current_ch]
    
    if active_path:
        path_df = pd.DataFrame(active_path)
        color = colors[i % len(colors)]
        
        # 1. The Path (Line)
        fig.add_trace(go.Scatter3d(
            x=path_df['x'], y=path_df['y'], z=path_df['z'],
            mode='lines',
            line=dict(color=color, width=4),
            name=f"{name} Path",
            showlegend=False
        ))
        
        # 2. The Bob (Current Position Marker)
        current = path_df.iloc[-1]
        fig.add_trace(go.Scatter3d(
            x=[current['x']], y=[current['y']], z=[current['z']],
            mode='markers+text',
            marker=dict(size=6, color=color, symbol='diamond'),
            text=[name],
            textposition="top center",
            name=name
        ))

# C. Camera and Environment
fig.update_layout(
    template="plotly_dark",
    margin=dict(l=0, r=0, b=0, t=0),
    scene=dict(
        xaxis=dict(title='X (LY)', range=[-5, 35], backgroundcolor="rgb(10, 10, 10)"),
        yaxis=dict(title='Y (LY)', range=[-15, 10], backgroundcolor="rgb(10, 10, 10)"),
        zaxis=dict(title='Z (LY)', range=[-10, 10], backgroundcolor="rgb(10, 10, 10)"),
        aspectmode='manual',
        aspectratio=dict(x=1.5, y=1, z=0.8)
    ),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

# 4. STATUS TABLE
status_data = []
for name, hist in bob_histories.items():
    current = [h for h in hist if h['chapter'] <= current_ch]
    if current:
        status_data.append({"Bob": name, "Status": f"At {current[-1]['sys']}"})

if status_data:
    st.table(pd.DataFrame(status_data))