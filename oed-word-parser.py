import os
import time
import argparse
import requests
from bs4 import BeautifulSoup

# The script file's directory on the file system.
script_directory = os.path.dirname(os.path.abspath(__file__))

# The output file path
output_file = os.path.join(script_directory, 'output.txt')

# Set up a requests Session to keep the connection to the server open while making requests.
session = requests.Session()
            
def main():
    '''
    Main function that initiates the content parsing process.

    This function serves as the entry point of the script. It prints the command-line arguments provided
    to the script for debugging purposes. The function expects the following optional arguments:

    - `request-delay` (int, optional): Delay between requests in seconds (default is 1).
    - `error-delay` (int, optional): Delay between retrying after an error (default is 60).
    - `max-retries` (int, optional): Maximum number of retries when encountering an error (default: 1).
    - `max-pages` (int, optional): Maximum number of pages to process (default is infinity).
    - `starting-page` (int, optional): The page number to start parsing from (default is 1).
    - `output-file` (string, optional): The path of the output file to write to (default is output.txt).
    - `delimiter` (string, optional): The delimiter for the output file (default: `,`)

    If any arguments are not provided, the function uses the default values.

    It checks to ensure the output-file directory exists, and creates it if it does not.
    Then, it calls the `start_parsing` function to begin the process of fetching, parsing, and saving content.

    Returns:
    None
    '''
    
    # Create the argument parser 
    parser = argparse.ArgumentParser(description='Start the content parsing process.')

    # Add optional arguments
    parser.add_argument('--request-delay', type=int, default=2, 
                        help='Delay between requests in seconds (default: 2)')
    parser.add_argument('--error-delay', type=int, default=60, 
                        help='Delay between an error and re-attempt. (default: 60)')
    parser.add_argument('--max-retries', type=int, default=1, 
                        help='The maximum number of retries after an error. (default: 1')
    parser.add_argument('--max-pages', type=int, default=int(1e5),  
                        help='Maximum number of pages to parse (default: 100,000)')
    parser.add_argument('--starting-page', type=int, default=1, 
                        help='The page number to start parsing from (default: 1)')
    parser.add_argument('--output-file', type=str, default=output_file, 
                        help='The full path of the output file (default: output.txt)')
    parser.add_argument('--delimiter', type=str, default=',', 
                        help='The delimiter for the output file. (default: `,`')

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # The output directory for the output file
    output_directory = os.path.dirname(args.output_file)
    
    # If the output directory doesn't exist, create it.
    if not os.path.exists(output_directory):
        print(f"Creating output directory at: {output_directory}")
        os.makedirs(output_directory)

    # Begin parsing with the command-line arguments (or their default values)
    start_parsing(args.starting_page, args.max_pages, args.max_retries, args.request_delay,
                args.error_delay, args.output_file, args.delimiter)

def fetch_content(page, error_delay, max_retries, retry = False):
    '''
    Fetch HTML content from the OED search page for a specific page number.

    This function sends an HTTP GET request to the OED search page, including query parameters for page number
    and other search options. It handles potential errors, logs the time taken for the request, and returns
    the HTML content of the response if successful. If the request fails or an error occurs, it returns None.

    Parameters:
    session (requests.Session): An instance of a requests session used to make the HTTP request.
    page (int): The page number to retrieve content for.

    Returns:
    str: The HTML content of the response if the request is successful; None if an error occurs.
    '''
    
    # The base URL of the OED web page search entries.
    url = "https://www.oed.com/search/advanced/Entries"

    # Headers to be sent with the request.
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
    }
    
    # The query parameters to send with the request. Can be improved to find-tune and search by subject, region, usage, and origin.
    params = {
        'textTermOpt0': 'WordPhrase',
        'dateOfUseFirstUse': 'false',
        'sortOption': 'AZ',
        'page': page,
        'obsolescence': 'inCurrentUse',
    }
    try:
        # The start time of the request for logging purposes.
        start = time.time()
        
        # Fetch the response from the webpage.
        response = session.get(url, params=params, headers=headers)
        
        # Set the encoding of the response to UTF-8 before reading the text.
        response.encoding = 'UTF-8'
        
        # Calculate the elapsed response time in seconds.
        elapsed_secs = time.time() - start
        
        # Store the number of time we have retried a request.
        num_retries = 0
        
        # Handle cases where the response is not 200 (OK).
        if response.status_code != 200:
            print(f"Failed to retrieve content for page {page} after {elapsed_secs:.3f} seconds. Status code: {response.status_code}", end="")
            if not retry and num_retries <= max_retries:
                print(f" | Retrying after {error_delay} seconds...")
                time.sleep(error_delay)
                num_retries += 1
                return fetch_content(page, error_delay, max_retries, True)
            else:
                print(" | Retrying to fetch content failed.")
                return None
        
        # Output the elapsed time and the page number.
        print(f'Received content for page {page} in {elapsed_secs:.3f} seconds')
        
        # Return the text from the response.
        return response.text
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return None
    
def get_parsed_content(content):
    '''
    Parse HTML content to extract words, snippets, and parts of speech.

    This function uses BeautifulSoup to parse the given HTML content and extract lists of words,
    snippets, and parts of speech from `<div>` elements with the class 'resultsSetItemBody'. It checks
    for any mismatches in the lengths of the extracted lists and prints the counts of each type of data found.

    Parameters:
    content (str): The HTML content to parse.

    Returns:
    None: When None content is received.
    tuple: A tuple containing three lists:
        - all_words (list of str): List of extracted words.
        - all_snippets (list of str): List of extracted snippets.
        - all_parts_of_speech (list of str): List of extracted parts of speech.
    '''
    
    if content is None:
        return None
    
    # Parse the HTML content using BeautifulSoup with the 'lxml' parser
    soup = BeautifulSoup(content, 'lxml')

    # Find all <div> elements with the class 'resultsSetItemBody' in the parsed HTML
    results_set_items = soup.find_all('div', class_='resultsSetItemBody')

    # Initialize lists to store extracted data
    all_words = []
    all_snippets = []
    all_parts_of_speech = []

    # Extract data from each parent container
    for item in results_set_items:
        # Extract the word
        word_span = item.find('span', class_='hw')
        if word_span:
            all_words.append(word_span.get_text().strip())
        
        # Extract the snippet
        snippet_div = item.find('div', class_='snippet')
        if snippet_div:
            snippet = snippet_div.get_text().strip().replace('"', "'")
            all_snippets.append(f'"{snippet}"')
        
        # Extract the part of speech
        ps_span = item.find('span', class_='ps')
        if ps_span:
            all_parts_of_speech.append(ps_span.get_text().strip())

    # Check if there is any mismatch in the lengths of all_words, all_snippets, and all_parts_of_speech
    if len(all_words) != len(all_snippets) and len(all_snippets) != len(all_parts_of_speech):
        return None

    return all_words, all_snippets, all_parts_of_speech

def start_parsing(starting_page, max_pages, max_retries, request_delay, error_delay, output_file, delimiter):
    '''
    Begin parsing content from a starting page and continue through subsequent pages.

    This function fetches content starting from the specified page, parses it, and appends the parsed
    data to an output file. The process continues until the maximum number of pages is reached or no more
    content is available. The function pauses for response_delay second(s) between requests to avoid overwhelming the server.

    Parameters:
    starting_page (int): The page number from which to start fetching and parsing content.
    max_pages (int): The maximum number of pages to fetch before ending.
    request_delay (int): The delay in seconds between each request.
    error_delay (int): The delay in seconds to wait before retrying after encountering an error.
    output_file (str): The full path of the output file, including the file name.
    delimiter (str): The delimiter to use when saving the parsed content to the output file.

    Returns:
    None
    '''
    
    # Set the current page to the starting page.
    current_page = starting_page
    
    # Fetch the content for the current page.
    content = fetch_content(starting_page, error_delay, max_retries)
    
    if content is None:
        print(f'Failed to fetch content from initial page. Ending...')
        return
    
    # Parse pages until we reach the maximum number of pages, or a fatal error occurs.
    for i in range(max_pages):
        # Parse the content that was fetched from the webpage.
        parsed_content = get_parsed_content(content)
        
        # Check to see if the content was able to be parsed, if it was save it.
        if parsed_content is None:
            print(f'Failed to parse content from page {current_page}. Skipping and moving on...')
        else:
            # Append the parsed content to the output file.
            save_parsed_content(output_file, parsed_content, current_page, delimiter)
            
        # Increase the current page by one.
        current_page = current_page + 1
        
        # Delay the fetching of the next page by 1 second.
        time.sleep(request_delay)
    
        # Fetch the content for the next page.
        content = fetch_content(current_page, error_delay, max_retries)
        
def save_parsed_content(output_file, parsed_content, current_page, delimiter):
    '''
    Save parsed content to an output file.

    This function processes a list of parsed content, which includes words, snippets, and parts of speech,
    and appends this information to an output file. Each entry in the file consists of the current page number,
    the parsed word, the snippet, and the part of speech, separated by '~~' delimiters.

    Parameters:
    parsed_content (list): A list containing three elements:
        - parsed_words (list of str): List of words extracted from parsing.
        - parsed_snippets (list of str): List of snippets associated with the words.
        - parsed_parts_of_speech (list of str): List of parts of speech corresponding to the words.
    current_page (int or str): The current page number to be associated with each entry.

    Returns:
    None
    '''
    
    # Extract the parsed words, snippets, and parts_of_speech from the parsed_content list.
    parsed_words, parsed_snippets, parsed_parts_of_speech = parsed_content
    
    # The list to hold the lines we'll append to the output file.
    lines = []
    
    # Iterate the length of parsed words (and snippets + parts of speech, since they're all equal).
    for i in range(len(parsed_words)):
        # Append the current page and word data, separated by a delimiter.
        lines.append(f'{current_page}{delimiter}{parsed_words[i]}{delimiter}{parsed_snippets[i]}{delimiter}{parsed_parts_of_speech[i]}\n')
    
    # Output the list of lines to the output file.
    with open(output_file, 'a', encoding='utf-8') as f:
        f.writelines(lines)

# Only run the parser if the script is ran directly (which it has to be).
if __name__ == '__main__':
    main()