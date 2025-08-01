import os
import logging
import argparse
from pathlib import Path
import klayout.db
import math
import json


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
FORMAT = "%(message)s"
logging.basicConfig(
    level=LOGLEVEL,
    format=FORMAT,
)

log = logging.getLogger(__name__)


def parse_polygon(shape: klayout.db.Shape, name_property: str, scale_factor: float):
    """
    Parse the name, hull and hole points from a :any:`klayout` shape.

    Args:
        shape: The shape to parse.
        name_property: The user property that contains the name of the shape.
        scale_factor: The database scale factor.


    Returns:
        A dictionary containing details of the polygon.
    """

    poly: klayout.db.Polygon = shape.polygon

    # remove the line cut(s)
    parts = poly.split()
    regions = (klayout.db.Region(part) for part in parts)
    region = next(regions)
    for new_region in regions:
        region += new_region

    poly = next(region.merged().each())

    hull_points = [
        [p.x * scale_factor, p.y * scale_factor] for p in poly.each_point_hull()
    ]

    hole_points = [
        [[p.x * scale_factor, p.y * scale_factor] for p in poly.each_point_hole(hole)]
        for hole in range(poly.holes())
    ]

    name = shape.properties().get(name_property, None)
    log.info(f"Found polygon with name '{name}'")

    return dict(
        name=shape.properties().get(name_property, None),
        hull_points=hull_points,
        hole_points=hole_points,
    )


def load_klayout(
    file: Path,
    cell: str = "devicegen",
    name_property: str = "devicegen_name",
    length_unit_exponent: int = -9,
):
    """
    Read the cell named ``cell`` from any file format supperted by KLayout from
    ``file_path`` and parse its structure.

    Args:
        file_path: The path to the ``OASIS`` file.
        cell: The name of the cell that the device is specified in.
        name_property: The user property that contains the name of a shape.
        length_unit_exponent: The exponent of the power of ten of the length unit
                relative to meters.

    Returns:
        A list of dictionaries describing the layers.
    """

    layers = []
    layout = klayout.db.Layout()

    if not file.exists() or not file.is_file():
        raise ValueError(f"Invalid file: {str(file)}")

    layout.read(str(file))

    scale_factor = 10 ** (-6 + math.log10(layout.dbu) - length_unit_exponent)

    devicegen_cell = layout.cell(cell)
    if not devicegen_cell:
        raise KeyError(f"Cell {cell} not found.")

    for layer, info in zip(layout.layer_indexes(), layout.layer_infos()):
        shapes = []
        dg_layer = dict(name=info.name, shapes=shapes)
        layers.append(dg_layer)

        log.info(f"Adding layer '{dg_layer['name']}'")

        for _, shape in enumerate(devicegen_cell.each_shape(layer)):
            dg_layer["shapes"].append(parse_polygon(shape, name_property, scale_factor))

    return layers


def dump_layers(out_file: Path, length_unit: int, layers: list):
    """
    Dump the parsed ``layers`` and the ``length_unit`` into ``out_file``.
    """
    out_file.parent.mkdir(exist_ok=True, parents=True)
    if out_file.exists():
        answer = input("Output file exists. Override? [Yy/Nn]: ").strip().lower()

        if answer != "y":
            exit(0)

    with open(out_file, "w") as f:
        json.dump(dict(length_unit=length_unit, layers=layers), f, indent=2)

    log.info(f"Wrote parsed shapes to {out_file}")


def main():
    parser = argparse.ArgumentParser(prog="klayout-converter")

    parser.add_argument(
        "in_file",
        type=lambda val: Path(val).resolve(),
        help="The file (OASIS, GDS, ...) to be converted.",
    )
    parser.add_argument(
        "out_file",
        type=lambda val: Path(val).resolve(),
        help="The json file into which the results are written.",
    )

    parser.add_argument(
        "-t",
        "--top-cell",
        type=str,
        default="devicegen",
        help="The name of the cell containing the shapes to be imported.",
    )

    parser.add_argument(
        "-n",
        "--name-property",
        type=str,
        default="devicegen_name",
        help="The name of the user property containing the name of a shape.",
    )

    parser.add_argument(
        "-l",
        "--length-unit",
        type=int,
        default=-9,
        help="The exponent of the power of ten of the length unit relative to meters.",
    )

    args = parser.parse_args()
    layers = load_klayout(
        args.in_file, args.top_cell, args.name_property, args.length_unit
    )

    dump_layers(args.out_file, args.length_unit, layers)


if __name__ == "__main__":
    main()
