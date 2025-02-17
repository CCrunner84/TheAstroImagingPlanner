import os
import pandas as pd
import plotly.figure_factory as ff

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from itertools import product

import numpy as np

import plotly.express as px
from astro_planner.stf import auto_stf
from astropy.io.fits import getdata

from image_grading.star_processing import get_gradient_data


# def show_fwhm_ellipticity_vs_r(df_radial, filename):
#     p = make_subplots(specs=[[{"secondary_y": True}]])

#     p.add_trace(
#         go.Scatter(
#             x=df_radial["chip_r_mean"],
#             y=df_radial["fwhm_50_pct"],
#             mode="markers",
#             name="fwhm",
#             error_y=dict(
#                 type="data",
#                 symmetric=False,
#                 array=df_radial["fwhm_75_pct"] - df_radial["fwhm_50_pct"],
#                 arrayminus=df_radial["fwhm_50_pct"] - df_radial["fwhm_25_pct"],
#             ),
#         ),
#         secondary_y=False,
#     )
#     p.add_trace(
#         go.Scatter(
#             x=df_radial["chip_r_mean"],
#             y=df_radial["ellipticity_50_pct"],
#             mode="markers",
#             name="ellipticity",
#             error_y=dict(
#                 type="data",
#                 symmetric=False,
#                 array=df_radial["ellipticity_75_pct"] - df_radial["ellipticity_50_pct"],
#                 arrayminus=df_radial["ellipticity_50_pct"]
#                 - df_radial["ellipticity_25_pct"],
#             ),
#         ),
#         secondary_y=True,
#     )
#     p.update_layout(
#         yaxis_range=[0, 5],
#         xaxis_title="Distance to chip center (pixels)",
#         yaxis=dict(titlefont=dict(color="blue"), tickfont=dict(color="blue")),
#         yaxis2=dict(titlefont=dict(color="red"), tickfont=dict(color="red")),
#         title=f"Radial analysis for<br>{os.path.basename(filename)}",
#     )
#     p.update_yaxes(title_text="FWHM (px)", secondary_y=False, range=[0, 5])
#     p.update_yaxes(title_text="Ellipticity", secondary_y=True, range=[0, 1])

#     return p


def show_frame_analysis(df_xy, filename, feature_col="fwhm"):

    df0 = df_xy.set_index(["x_bin", "y_bin"]).unstack(0).iloc[::-1]
    df1 = df0.stack()

    # Set text on hover
    df1["text"] = df1.apply(
        lambda row: f"fwhm: {row['fwhm']:.2f} px<br>\
radius: {row['chip_r']:.0f} px<br>\
ellipticity: {row['ellipticity']:.3f}<br>\
eccentricity: {row['eccentricity']:.3f}<br>\
major-axis: {row['a']:.3f}<br>\
minor-axis: {row['b']:.3f}<br>\
stars: {row['star_count']}<br>",
        axis=1,
    )
    df2 = df1["text"].unstack(1).iloc[::-1]

    # Add quiver for opposite direction
    df_quiver = df_xy[["x_bin", "y_bin", "vec_u", "vec_v"]]
    df_quiver["vec_u"] *= -1
    df_quiver["vec_v"] *= -1
    df_quiver = pd.concat([df_xy[["x_bin", "y_bin", "vec_u", "vec_v"]], df_quiver])

    p = ff.create_quiver(
        df_quiver["x_bin"],
        df_quiver["y_bin"],
        df_quiver["vec_u"],
        df_quiver["vec_v"],
        scale=200,
        scaleratio=1,
        name="quiver",
        line_width=1,
        line=dict(color="#000"),
    )
    zmax = df0[feature_col].values.max()
    if feature_col == "fwhm":
        zmin = 1
        zmax = max([5, zmax])
    elif feature_col == "ellipticity":
        zmin = 0
        zmax = max([0.5, zmax])
    elif feature_col == "eccentricity":
        zmin = 0
        zmax = max([1, zmax])

    p.add_trace(
        go.Heatmap(
            x=df0[feature_col].columns,
            y=df0.index,
            z=df0[feature_col].values,
            name="test",
            hovertext=df2,
            colorscale="balance",
            zmin=zmin,
            zmax=zmax,
            colorbar=dict(title=feature_col.upper()),
        )
    )
    p.update_layout(
        title=f"Frame analysis for<br>{os.path.basename(filename)}",
        font=dict(size=12, color="Black"),
    )

    # p.update_traces(showscale=False, selector=dict(type="heatmap"))

    # p.update_traces(colorbar_orientation="h", selector=dict(type="heatmap"))

    return p


def show_inspector_image(
    filename,
    as_aberration_inspector=True,
    n_cols=3,
    n_rows=3,
    window_size=0,
    border=10,
    with_overlay=False,
    use_plotly=True,
):
    data = getdata(filename, header=False).astype(float)
    nx, ny = data.shape
    # Check if data is RGGB bayer array
    is_bayer = False
    if (nx % 2 == 0) and (ny % 2 == 0):
        g1 = data[1::2, ::2]
        g2 = data[::2, 1::2]
        r = data[::2, ::2]
        b = data[1::2, 1::2]

        g = (g1 + g2) / 2
        g_diff = g1 - g2
        g_med = np.median(np.abs(g_diff))
        # rg_med = np.median(np.abs(r - g))
        bg_med = np.median(np.abs(b - g))
        # rb_med = np.median(np.abs(r - b))

        if (g_med < (bg_med) / 2) or ("bayer" in filename.lower()):
            is_bayer = True
            data = np.array(
                [r / np.median(r) * np.median(g), g, b / np.median(b) * np.median(g)]
            )
            data = data.swapaxes(0, 2)
            data = data.swapaxes(0, 1)

    if is_bayer:
        nx, ny, nc = data.shape
    else:
        data = data.reshape(nx, ny, 1)
        nc = 1

    base_filename = os.path.basename(filename)
    title = f"Full Preview for<br>{base_filename}"

    if as_aberration_inspector:
        if window_size == 0:
            window_size = int(ny / (n_rows * 3))

        x_skip = int((nx - window_size) // (n_cols - 1))
        x_set = []
        for i_panel in range(n_cols):
            x_set.append(
                [i_panel, i_panel * x_skip, i_panel * x_skip + window_size - 1]
            )

        y_skip = int((ny - window_size) // (n_rows - 1))
        y_set = []
        for i_panel in range(n_cols):
            y_set.append(
                [i_panel, i_panel * y_skip, i_panel * y_skip + window_size - 1]
            )

        nx_canvas = n_cols * window_size + (n_cols - 1) * border
        ny_canvas = n_rows * window_size + (n_rows - 1) * border
        canvas = np.ones((nx_canvas, ny_canvas, nc)) * 2 ** 16

        for xlim, ylim in product(x_set, y_set):
            xlim_canvas = [
                xlim[0] * (border + window_size),
                xlim[0] * (border + window_size) + window_size - 1,
            ]
            ylim_canvas = [
                ylim[0] * (border + window_size),
                ylim[0] * (border + window_size) + window_size - 1,
            ]
            canvas[
                xlim_canvas[0] : xlim_canvas[1], ylim_canvas[0] : ylim_canvas[1], :
            ] = data[xlim[1] : xlim[2], ylim[1] : ylim[2], :]
        data = canvas
        title = f"Aberration Inspector for<br>{base_filename}"

    data = np.clip(auto_stf(data), 0, 1)
    if nc == 1:
        data = data[:, :, 0]

    p = px.imshow(
        data,
        color_continuous_scale="gray",
        binary_string=True,
        binary_compression_level=5,
        # binary_backend="pil",
        # binary_format="jpg",
    )
    p.update_layout(
        title=title,
        font=dict(size=12, color="Black"),
    )

    return p, data


def show_frame_gradient_analysis(filename, n_samples=32):

    data, header = getdata(filename, header=True)
    # record = dict(header)
    res, df_binned, df_pred, df_residual = get_gradient_data(
        data.astype(float), n_samples=n_samples
    )

    p = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=["Masked Raw Frame", "Background Fit", "Residual"],
    )
    median_value = df_binned.median().median()
    p1 = px.imshow(df_binned.iloc[::-1, :].values - median_value, aspect="auto")
    p2 = px.imshow(df_pred.iloc[::-1, :].values - median_value, aspect="auto")
    p3 = px.imshow(df_residual.iloc[::-1, :].values, aspect="auto")
    p.add_trace(p1["data"][0], row=1, col=1)
    p.add_trace(p2["data"][0], row=1, col=2)
    p.add_trace(p3["data"][0], row=1, col=3)
    p.update_layout(coloraxis=dict(colorscale="YlGnBu_r"))
    return p
