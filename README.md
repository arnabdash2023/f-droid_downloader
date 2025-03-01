# F-Droid Downloader

F-Droid Downloader is a Python script that automates the process of downloading APKs from the F-Droid repository. It fetches the F-Droid index, extracts package names, and downloads the APKs using the `apkeep` tool.

## Features

- Downloads the F-Droid index JAR file.
- Extracts package names from the index JSON file.
- Downloads APKs for the extracted package names.
- Tracks download progress and resumes from where it left off.

## Requirements

- Python 3.x
- `requests` library
- `apkeep` tool (requires Rust)

## Installation

1. Install Python 3.x if you haven't already.
2. Install the required Python library:

    ```sh
    pip install requests
    ```

3. Install `apkeep` using Rust:

    ```sh
    cargo install apkeep
    ```

## Usage

To run the script, use the following command:

```sh
python fdown.py
```

## Options

- ```--refresh``` or ```-r```: Refresh the F-Droid package list by downloading the latest index.

#### Example

```python
python fdown.py --refresh
```

## How It Works

1. **Download the JAR file**: The script downloads the F-Droid index JAR file from the specified URL.
2. **Extract the JAR file**: The script extracts the contents of the JAR file to a specified directory.
3. **Extract package names**: The script processes the extracted JSON file to extract package names and saves them to ```packages.txt```.
4. **Download APKs**: The script reads the package names from ```packages.txt``` and downloads the APKs using ```apkeep```. It tracks the download progress and saves it to ```download_tracker.json```.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
