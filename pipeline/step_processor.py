import cadquery as cq
from cadquery import exporters
import os
import math


VIEW_CONFIGS = {
    "isometric": {
        "description": "Isometric view (standard 3/4 technical view)",
        "camera_dir": (-1, -1, -1),
        "up_dir": (0, 0, 1),
    },
    "front": {
        "description": "Front view",
        "camera_dir": (0, -1, 0),
        "up_dir": (0, 0, 1),
    },
    "top": {
        "description": "Top / Plan view",
        "camera_dir": (0, 0, -1),
        "up_dir": (0, 1, 0),
    },
    "side": {
        "description": "Side / Right view",
        "camera_dir": (-1, 0, 0),
        "up_dir": (0, 0, 1),
    },
    "back": {
        "description": "Back view",
        "camera_dir": (0, 1, 0),
        "up_dir": (0, 0, 1),
    },
}


def load_step(filepath: str):
    """Load a STEP file into a CadQuery Workplane."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"STEP file not found: {filepath}")
    shape = cq.importers.importStep(filepath)
    return shape


def export_svg_view(shape, output_svg_path: str, view: str = "isometric") -> str:
    """
    Export a CadQuery shape to SVG from the specified view angle.
    Returns the path to the written SVG file.
    """
    cfg = VIEW_CONFIGS.get(view, VIEW_CONFIGS["isometric"])

    # Build projection options
    opt = {
        "projectionDir": cfg["camera_dir"],
        "showAxes": False,
        "showHidden": True,
        "strokeWidth": -1,            # auto line width
        "hiddenColor": (0.5, 0.5, 0.5),
        "strokeColor": (0, 0, 0),
        "focus": None,
    }

    exporters.export(shape, output_svg_path, exporters.ExportTypes.SVG, opt=opt)
    return output_svg_path


def get_view_configs():
    """Return the available view config names and descriptions."""
    return {k: v["description"] for k, v in VIEW_CONFIGS.items()}
