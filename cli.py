"""Simple CLI for .mat files."""

import argparse
from loader import MatFile
from plotter import plot_variable, list_styles


def main():
    parser = argparse.ArgumentParser(description="Plot and inspect MATLAB .mat files")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # info command
    info_parser = subparsers.add_parser("info", help="Show information about a .mat file")
    info_parser.add_argument("file", help="Path to .mat file")

    # list command
    list_parser = subparsers.add_parser("list", help="List variables in a .mat file")
    list_parser.add_argument("file", help="Path to .mat file")

    # plot command
    plot_parser = subparsers.add_parser("plot", help="Plot a variable")
    plot_parser.add_argument("file", help="Path to .mat file")
    plot_parser.add_argument("variable", help="Name of the variable to plot")
    plot_parser.add_argument("--style", default="dark", help="Plot style (dark, seaborn, ggplot, ...)")
    plot_parser.add_argument("--type", default="auto", help="Plot type: auto, line, image, hist")
    plot_parser.add_argument("--save", help="Save plot to a file (e.g. plot.png)")

    # styles command
    subparsers.add_parser("styles", help="List all available plot styles")

    args = parser.parse_args()

    if args.command == "info":
        m = MatFile(args.file)
        info = m.info()
        print(f"File   : {info['path']}")
        print(f"Format : {info['format']}")
        print(f"Size   : {info['size_bytes']} bytes")
        print(f"Variables: {info['n_variables']}")
        for v in info["variables"]:
            print(f"  - {v['name']}: shape={v['shape']}, dtype={v['dtype']}")

    elif args.command == "list":
        m = MatFile(args.file)
        for v in m.list_variables():
            print(f"{v['name']:20} shape={str(v['shape']):15} dtype={v['dtype']}")

    elif args.command == "plot":
        m = MatFile(args.file)
        data = m.get(args.variable)
        plot_variable(
            data,
            title=args.variable,
            plot_type=args.type,
            style=args.style,
            save=args.save,
            show=True
        )

    elif args.command == "styles":
        styles = list_styles()
        print("Available styles:")
        for s in sorted(set(styles)):
            print(f"  {s}")


if __name__ == "__main__":
    main()