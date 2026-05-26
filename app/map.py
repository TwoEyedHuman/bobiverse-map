import math

import plotly.graph_objects as go

from app.data import SYSTEM_COORDS


def build_map(processed_positions):
    """Build plotly figure from pre-computed Bob positions.

    Returns:
        fig: plotly Figure
        status_list: list of dicts [{Bob, Status, Last Log}, ...]
    """
    fig = go.Figure()

    # Star systems
    for sys_name, coords in SYSTEM_COORDS.items():
        fig.add_trace(
            go.Scatter(
                x=[coords[0]],
                y=[coords[1]],
                mode="markers+text",
                marker=dict(size=12, color="white", opacity=0.3),
                text=[sys_name],
                textposition="bottom center",
                showlegend=False,
                hoverinfo="text",
            )
        )

    # Anti-stacking: cluster Bobs at same coords
    pos_counts = {}
    for p in processed_positions:
        coord_key = (round(p["x"], 2), round(p["y"], 2))
        pos_counts[coord_key] = pos_counts.get(coord_key, []) + [p]

    status_list = []
    for _coord, cluster in pos_counts.items():
        n = len(cluster)
        for idx, p in enumerate(cluster):
            display_x, display_y = p["x"], p["y"]

            # Orbit offset for stationary Bobs sharing a system
            if n > 1 and not p["is_traveling"]:
                offset_radius = 0.7
                theta = (2 * math.pi * idx) / n
                display_x += offset_radius * math.cos(theta)
                display_y += offset_radius * math.sin(theta)

            # Travel path (dotted line, shares legend color via legendgroup)
            if p["path"]:
                fig.add_trace(
                    go.Scatter(
                        x=p["path"][0],
                        y=p["path"][1],
                        mode="lines",
                        line=dict(width=1, dash="dot"),
                        legendgroup=p["name"],
                        showlegend=False,
                        hoverinfo="none",
                    )
                )

            # Bob icon
            fig.add_trace(
                go.Scatter(
                    x=[display_x],
                    y=[display_y],
                    mode="markers+text",
                    marker=dict(size=14, symbol="triangle-up", angle=p["angle"]),
                    text=[p["name"]],
                    textposition="top center",
                    name=p["name"],
                    legendgroup=p["name"],
                )
            )

            status_list.append(
                {"Bob": p["name"], "Status": p["status"], "Last Log": p["last_date"]}
            )

    fig.update_layout(
        template="plotly_dark",
        height=800,
        xaxis=dict(title="LY (X)", gridcolor="#333", zeroline=False),
        yaxis=dict(title="LY (Y)", gridcolor="#333", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig, status_list
