# Local Development Notes



## Running the Application

To run the application locally using the provided virtual environment:

1.  **Activate the virtual environment (optional but recommended):**
    ```bash
    source .venv/bin/activate
    ```

2.  **Run the application:**
    ```bash
    .venv/bin/python -m abogen.main
    ```
    *Note: Using the full path to the python executable ensures you are using the virtual environment's python even if you haven't activated it.*

## Prerequisites

-   **espeak-ng**: Ensure `espeak-ng` is installed on your system (e.g., `brew install espeak-ng` on macOS).

## Running the CLI

To run the command-line interface (headless mode):

```bash
.venv/bin/python -m abogen.cli --input <path_to_input_file> --output <path_to_output_dir>
```

### Arguments

-   `--input`, `-i`: Path to the input file (epub, pdf, md, txt). **Required**.
-   `--output`, `-o`: Path to the output directory. **Required**.
-   `--voice`, `-v`: Voice code (default: `af_heart`).
-   `--lang`, `-l`: Language code (default: `a` for American English).
-   `--speed`, `-s`: Speed factor (default: `1.0`).

### Example

```bash
.venv/bin/python -m abogen.cli --input my_book.epub --output ./audiobook --voice af_heart --speed 1.2
```


## Testing

### Unit Tests

```bash
.venv/bin/python -m unittest discover
```


## Notes

### Hugging face cache for models 
The models are dynamically loaded and cached in the following location:

MacOs : ~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots


## Setup for local development

```bash
rm -rf .venv
python3.10 -m venv .venv
source .venv/bin/activate
python --version
pip3 install -e . --break-system-packages
```

Additional step for macOS:
```bash
pip3 install git+https://github.com/hexgrad/kokoro.git

```

Additional step for Fedora & AMD:
```bash
sudo dnf install -y espeak-ng
pip3 uninstall torch 
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.4

#required for Radeom 860m
export HSA_OVERRIDE_GFX_VERSION=11.0.0

```