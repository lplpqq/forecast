#!/bin/sh

# * sourcing the environment provided by poetry
source $(poetry env info --path)/bin/activate

# * applying ruff
echo -e "Ruff results:"
ruff --fix ./
ruff format ./
echo ""

# * flake8
echo -e "Flake8 results:"
flake8 ./forecast
echo ""

# * Running pyright
echo -e "Pyright results:"
pyright -p forecast
echo ""

git add --all
