# mat-cli

Simple command-line tool to inspect and plot MATLAB `.mat` files **without MATLAB**.

## How to use

```bash
# Show file info
py cli.py info yourfile.mat

# List variables
py cli.py list yourfile.mat

# Plot a variable
py cli.py plot yourfile.mat signal --style dark
py cli.py plot yourfile.mat data --style seaborn --type image

# Show all available styles
py cli.py styles