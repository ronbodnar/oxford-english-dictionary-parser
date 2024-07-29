import os
import time
import argparse
import requests
from bs4 import BeautifulSoup

# The script file's directory on the file system.
script_directory = os.path.dirname(os.path.abspath(__file__))

# The output file path
output_file = os.path.join(script_directory, 'output', 'oed-word-parser.txt')

# Set up a requests Session to keep the connection to the server open while making requests.
session = requests.Session()
            
def main():
    '''
    Main function that initiates the content parsing process.

    This function serves as the entry point of the script. It prints the command-line arguments provided
    to the script for debugging purposes. The function expects the following optional arguments:

    - `request-delay` (int): Delay between requests in seconds. Default is 1.
    - `max-pages` (int): Maximum number of pages to parse. Default is infinity (no limit).
    - `starting-page` (int): The page number to start parsing from. Default is 1.

    If any arguments are not provided, the function uses the default values.

    After printing the arguments, it calls the `start_parsing` function to begin the process of fetching,
    parsing, and saving content.

    Command-line Arguments:
    - `request-delay` (int, optional): Delay between requests in seconds (default is 1).
    - `max-pages` (int, optional): Maximum number of pages to process (default is infinity).
    - `starting-page` (int, optional): The page number to start parsing from (default is 1).

    Returns:
    None
    '''
    
    # Create the argument parser 
    parser = argparse.ArgumentParser(description='Start the content parsing process.')

    # Add optional arguments
    parser.add_argument('--request-delay', type=int, default=1, 
                        help='Delay between requests in seconds (default: 1)')
    parser.add_argument('--max-pages', type=int, default=float('inf'), 
                        help='Maximum number of pages to parse (default: infinity)')
    parser.add_argument('--starting-page', type=int, default=1, 
                        help='The page number to start parsing from (default: 1)')
    parser.add_argument('--output-file', type=str, default=output_file, 
                        help='The full path of the output file (default: $script_dir/output/oed-word-parser.txt)')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Begin parsing with the command-line arguments (or their default values)
    start_parsing(args.starting_page, args.max_pages, args.request_delay, args.output_file)

def fetch_content(page):
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
        
        # Output the elapsed time and the page number.
        print(f'Received content for page {page} in {elapsed_secs:.3f} seconds')
        
        # Handle cases where the response is not OK.
        if response.status_code != 200:
            print(f"Error occurred: Failed to retrieve content. Status code: {response.status_code}")
            return None
        
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
    tuple: A tuple containing three lists:
        - all_words (list of str): List of extracted words.
        - all_snippets (list of str): List of extracted snippets.
        - all_parts_of_speech (list of str): List of extracted parts of speech.
    '''
    
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
            all_snippets.append(snippet_div.get_text().strip())
        
        # Extract the part of speech
        ps_span = item.find('span', class_='ps')
        if ps_span:
            all_parts_of_speech.append(ps_span.get_text().strip())

    # Check if there is any mismatch in the lengths of all_words, all_snippets, and all_parts_of_speech
    if len(all_words) != len(all_snippets) and len(all_snippets) != len(all_parts_of_speech):
        print('List Length Mismatch')
    
    # Outputting the number of words, snippets, and parts of speech found.
    print(f'Words: {len(all_words)}\tSnippets: {len(all_snippets)}\tParts of Speech: {len(all_parts_of_speech)}')
    
    return all_words, all_snippets, all_parts_of_speech

def start_parsing(starting_page, max_pages, request_delay, output_file):
    '''
    Begin parsing content from a starting page and continue through subsequent pages.

    This function fetches content starting from the specified page, parses it, and appends the parsed
    data to an output file. The process continues until the maximum number of pages is reached or no more
    content is available. The function pauses for response_delay second(s) between requests to avoid overwhelming the server.

    Parameters:
    starting_page (int): The page number from which to start fetching and parsing content.

    Returns:
    None
    '''
    
    # Fetch the content for the current page.
    content = fetch_content(starting_page)
    
    # Set the current page to the starting page.
    current_page = starting_page
    
    # Continue processing the content from pages until there are no more pages, or an error exists
    while content is not None:
        # Stop after we reach the maximum number of pages to parse.
        if current_page == max_pages:
            break
        
        # Parse the content that was fetched from the webpage.
        parsed_content = get_parsed_content(content)
        
        # Append the parsed content to the output file.
        save_parsed_content(output_file, parsed_content, current_page)
            
        # Increase the current page by one.
        current_page = current_page + 1
        
        # Delay the fetching of the next page by 1 second.
        time.sleep(request_delay)
    
        # Fetch the content for the next page.
        content = fetch_content(current_page)
        
def save_parsed_content(output_file, parsed_content, current_page):
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
        # Append t current page and word data, separated by '~~' delimiter to avoid interference with characters in snippets.
        lines.append(f'{current_page}~~{parsed_words[i]}~~{parsed_snippets[i]}~~{parsed_parts_of_speech[i]}\n')
    
    # Output the list of lines to the output file.
    with open(output_file, 'a', encoding='utf-8') as f:
        f.writelines(lines)

# Only run the parser if the script is ran directly (which it has to be).
if __name__ == '__main__':
    main()