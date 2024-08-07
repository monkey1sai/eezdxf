# Copyright (c) 2015-2022, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import math
import pathlib

import ezdxf
from ezdxf.layouts import Paperspace, Modelspace
from ezdxf.enums import TextEntityAlignment
from ezdxf.render import forms
from ezdxf.math import Vec2
from ezdxf import colors

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create VIEWPORT entities in paperspace layouts.
#
# VIEWPORT: https://ezdxf.mozman.at/docs/dxfentities/viewport.html
# ------------------------------------------------------------------------------

MESH_SIZE = 20


def build_cos_sin_mesh(mesh):
    height = 3.0
    dx = 30
    dy = 30

    delta = math.pi / MESH_SIZE
    for x in range(MESH_SIZE):
        sinx = math.sin(float(x) * delta)
        for y in range(MESH_SIZE):
            cosy = math.cos(float(y) * delta)
            z = sinx * cosy * height
            # set the m,n vertex to 3d point x,y,z
            mesh.set_mesh_vertex((x, y), (dx + x, dy + y, z))


def create_2d_modelspace_content(msp: Modelspace):
    rect = msp.add_polyline2d(
        [(5, 5), (10, 5), (10, 10), (5, 10)], dxfattribs={"color": colors.RED}
    )
    rect.close(True)

    msp.add_circle((10, 5), 2.5, dxfattribs={"color": colors.GREEN})

    triangle = msp.add_polyline2d(
        [(10, 7.5), (15, 5), (15, 10)], dxfattribs={"color": colors.CYAN}
    )
    triangle.close(True)


def create_3d_modelspace_content(msp: Modelspace):
    mesh = msp.add_polymesh(
        (MESH_SIZE, MESH_SIZE), dxfattribs={"color": colors.MAGENTA}
    )
    build_cos_sin_mesh(mesh)
size = (44.0, 46.5)
center = (27.0, 25.75)
def create_viewports(paperspace: Paperspace):
    # Define viewports in paper space:
    # center, size=(width, height) defines the viewport in paper space.
    # view_center_point and view_height defines the area in model space
    # which is displayed in the viewport.
    txt_attribs = dict(
        style="OpenSans-Bold",
        color=colors.BLUE,
    )
    paperspace.add_viewport(
        center=(2.5, 2.5),
        size=(5, 5),
        view_center_point=(7.5, 7.5),
        view_height=10,
        status=2,
    ) 
    # scale is calculated by:
    # height of model space (view_height=10) / height of viewport (height=5)
    paperspace.add_text(
        "View of Rectangle Scale=1:2", height=0.18, dxfattribs=txt_attribs
    ).set_placement((0, 5.2))

    paperspace.add_viewport(
        center=(8.5, 2.5),
        size=(5, 5),
        view_center_point=(10, 5),
        view_height=25,
        status=3,
    )
    paperspace.add_text(
        "View of Circle Scale=1:5", height=0.18, dxfattribs=txt_attribs
    ).set_placement((6, 5.2))

    paperspace.add_viewport(
        center=(14.5, 2.5),
        size=(5, 5),
        view_center_point=(12.5, 7.5),
        view_height=5,
        status=4,
    )
    paperspace.add_text(
        "View of Triangle Scale=1:1", height=0.18, dxfattribs=txt_attribs
    ).set_placement((12, 5.2))

    paperspace.add_viewport(
        center=(7.5, 10),
        size=(15, 7.5),
        view_center_point=(10, 6.25),
        view_height=7.5,
        status=5,
    )
    paperspace.add_text(
        "Overall View Scale=1:1", height=0.18, dxfattribs=txt_attribs
    ).set_placement((0, 14))

    paperspace.add_viewport(
        center=(16, 13.5),
        size=(0.3, 0.15),
        view_center_point=(10, 6.25),
        view_height=7.5,
        status=6,
    )
    # scale = 7.5/0.15 = 50
    paperspace.add_text(
        "Scale=1:50", height=0.18, dxfattribs=txt_attribs
    ).set_placement((16, 14), align=TextEntityAlignment.CENTER)

    vp = paperspace.add_viewport(
        center=(16, 10), size=(4, 4), view_center_point=(0, 0), view_height=30, status=7
    )
    vp.dxf.view_target_point = (40, 40, 0)
    vp.dxf.view_direction_vector = (-1, -1, 1)

    paperspace.add_text(
        "Viewport to 3D Mesh", height=0.18, dxfattribs=txt_attribs
    ).set_placement((16, 10), align=TextEntityAlignment.CENTER)


def draw_border_lines(psp: Paperspace, start: Vec2, size: Vec2):
    rect = forms.box(size.x, size.y)
    # DXF R12 does not support LWPOLYLINE
    psp.add_polyline2d(forms.translate(rect, start), close=True)


def make_dxf(dxfversion: str):
    doc = ezdxf.new(dxfversion, setup=True)
    # create/get the default layer for VIEWPORT entities:
    if "VIEWPORTS" not in doc.layers:
        vp_layer = doc.layers.add("VIEWPORTS")
    else:
        vp_layer = doc.layers.get("VIEWPORTS")
    # switch viewport layer off to hide the viewport borderlines
    vp_layer.off()
    # the VIEWPORT layer is not fixed:
    # Paperspace.add_viewport(..., dxfattribs={"layer": "MyViewportLayer"})

    create_2d_modelspace_content(doc.modelspace())
    create_3d_modelspace_content(doc.modelspace())
    # IMPORTANT: DXF R12 supports only one paper space aka layout, every
    # layout name returns the same layout

    layout: Paperspace = doc.layout("Layout1")  # type: ignore
    # Arch C = 18 x 24 in
    width, height = 24, 18
    m = 1
    if dxfversion == "R12":
        layout.page_setup_r12(size=(width, height), margins=(m, m, m, m), units="inch")
    else:
        layout.page_setup(size=(width, height), margins=(m, m, m, m), units="inch")
    # The canvas is defined by the page size minus the margins:
    canvas_width = width - 2 * m
    canvas_height = height - 2 * m
    # The lower left corner of the canvas has the coordinates: 0, 0
    # You can draw beyond that margins, but this content may not be printed
    # by the CAD application.
    draw_border_lines(
        layout,
        start=Vec2(-0.5, -0.5),
        size=Vec2(canvas_width + 1, canvas_height + 1),
    )
    create_viewports(layout)

    filename = f"viewports_in_paperspace_{dxfversion}.dxf"
    try:
        doc.saveas(CWD / filename)
    except IOError:
        print(f"Can't write: {filename}")


def main():
    make_dxf("R12")
    make_dxf("R2000")
    make_dxf("R2007")


if __name__ == "__main__":
    main()
