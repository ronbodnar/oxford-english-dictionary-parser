# OED Word Parser

**OED Word Parser** is a Python-based tool designed to scrape and parse English word data from the Oxford English Dictionary (OED) website. This project provides a robust solution for extracting and managing word-related information, including definitions, snippets, and parts of speech. It’s particularly useful for linguists, language enthusiasts, and developers working with English language datasets.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Contributing](#contributing)
5. [License](#license)
6. [Disclaimer](#disclaimer)

## Features

- **Efficient Data Extraction**: Scrape words, snippets, and parts of speech from OED search pages.
- **Customizable Request Delay**: Set a delay between requests to avoid server overload.
- **Flexible Pagination**: Specify starting page and maximum number of pages to parse.
- **Output Control**: Save parsed data to a specified output file.

## Installation

To run the script, you need to have Python 3 and the required packages installed. Follow these steps:

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/ronbodnar/oed-word-parser.git
    cd oed-word-parser
    ```

2. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Up the Environment:**

    Ensure you have Python 3.6 or higher installed. You may also want to set up a virtual environment.

## Usage

Run the script using the following command:

```bash
python oed-word-parser.py --request-delay 2 --max-pages 100 --starting-page 1 --output-file results.txt
```

**Arguments:**

- `--request-delay` (int): Delay between requests in seconds (default: 1).
- `--max-pages` (int): Maximum number of pages to parse (default: infinity).
- `--starting-page` (int): The page number to start parsing from (default: 1).
- `--output-file` (str): Path to the output file (default: `output/oed-word-parser.txt`).

**Example:**

To start parsing from page 1, with a delay of 2 seconds between requests, and save results to `parsed_data.txt`, use:

```bash
python oed-word-parser.py --request-delay 2 --max-pages 50 --starting-page 1 --output-file parsed_data.txt
```

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please follow these steps:

1. **Fork the Repository**
2. **Create a New Branch**: `git checkout -b feature/your-feature`
3. **Commit Your Changes**: `git commit -am 'Add new feature'`
4. **Push to the Branch**: `git push origin feature/your-feature`
5. **Create a Pull Request**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is intended for educational purposes and personal use. The script is not affiliated with or endorsed by the Oxford English Dictionary (OED). Users are responsible for ensuring compliance with OED's terms of service and legal restrictions on data usage.