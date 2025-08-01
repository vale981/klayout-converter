# QTCAD KLayout Converter

This project provides a simple script `klayout-converter` to extract
shapes from files supported by [KLayout](https://www.klayout.de/)
(`OASIS`, `gds`, etc) into a `json` file. The resulting file can then
be used with [QTCAD](https://nanoacademic.com/solutions/qtcad/).

The use of `OASIS` files is recommended, as they support named layers
and user properties.

## Usage
To run this script, simply use
[uv](https://docs.astral.sh/uv/getting-started/installation/). Alternatively,
make sure that the `klayout` python package is installed and invoke
the script in the `src/` subdirectory. Finally, if you're sporting nix simply invoke `nix run github:vale981/klayout-converter -- [args...]`.

```shell
  $ git clone htts://github.com/vale981/klayout-converter
  $ cd klayout-converter
  $ uv run klayout-converter --help

    Usage: klayout-converter [-h] [-t TOP_CELL] [-n NAME_PROPERTY] [-l LENGTH_UNIT] in_file out_file

    Positional Arguments:
      in_file               The file (OASIS, GDS, ...) to be converted.
      out_file              The json file into which the results are written.

    Options:
      -h, --help            show this help message and exit
      -t, --top-cell TOP_CELL
                            The name of the cell containing the shapes to be imported.
      -n, --name-property NAME_PROPERTY
                            The name of the user property containing the name of a shape.
      -l, --length-unit LENGTH_UNIT
                            The exponent of the power of ten of the length unit relative to meters.
```
