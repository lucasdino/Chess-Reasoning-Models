# Chess Reasoner
*Project for UCSD course CSE 291H (AI Agents) - taught by Prof. Raj Ammanabrolu*
---
## Setting up Repo
To set up this repo - we recommend creating a new venv (using Python's defualt `venv` creator, `conda`, or `uv`). Then download requirements.txt.

Additionally, to use the ollama chat features, you'll need to install ollama on your computer (downloads near top of README [here](https://github.com/ollama/ollama/blob/main/README.md#quickstart)). Then you'll need to download models from ollama to be able to interact with those -- namely make calls to `ollama run deepseek-r1:1.5b` (1.1GB download) and `ollama run deepseek-r1:7b` (4.7GB download - you'll need 8GB of RAM to run this ideally on an accelerator (GPU)).
