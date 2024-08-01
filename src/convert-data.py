import csv
import json
import re
import argparse
from word import Word

# The dictionary to house Word objects.
words = {}

# The dictionary to map formats to their writer functions.
writer_functions = {
    'csv': lambda file, *args : write_csv(file),
    'txt': lambda file, *args : write_txt(file),
    'json': lambda file, *args: write_json(file, args[0])
}

def main():
    """
    Main function to handle command-line arguments and process files based on user input.
    
    This function:
    - Parses command-line arguments to get the input file path, output file path, output format, and JSON minification flag.
    - Calls the `populate_words` function to populate the words dictionary from the input file.
    - Calls the `write_to_file` function to write the processed data to the output file in the specified format.
    
    Command-line Arguments:
    - -i, --input-file: (str) The full path including the file name for the input CSV file to read data from.
    - -o, --output-file: (str) The full path including the file name for the output file to write data to.
    - -f, --format: (str) The format of the output file. Can be 'csv', 'txt', or 'json'.
    - -m, --minified: (flag) Optional flag to indicate if the JSON output should be minified (no extra whitespace).

    Example:
        python script.py -i input.csv -o output.json -f json -m

    Raises:
    SystemExit: If there is an issue with the command-line arguments or file processing.
    """
    
    # Create the argument parser 
    parser = argparse.ArgumentParser(description='Converts output from the oed-parser script into various formats for use in any application.')

    # Add arguments
    parser.add_argument('-i', '--input-file', type=str, required=True,
                        help='The full path including the file name for the input file.')
    parser.add_argument('-o', '--output-file', type=str, required=True,
                        help='The full path including the file name for the output file.')
    parser.add_argument('-f', '--format', type=str, required=True,
                        choices=['csv', 'txt', 'json'],
                        help='The format of the output. (json, txt, or csv)')
    parser.add_argument('-m', '--minified', action="store_true",
                        help='Flag for minifying the JSON response. (optional)')

    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Populate the words dictionary from data in the input file.
    populate_words(args.input_file)
    
    # Write the processed data to the output file using the format specified.
    write_to_file(args.output_file, args.format, args.minified)
    pass

def populate_words(input_file):
    """
    Populates the words dictionary from the given CSV input file.
    
    Each row in the input file should contain the following columns:
    1. Page number (ignored in this function)
    2. Text (the word itself)
    3. Snippet (a snippet or definition of the word)
    4. Parts of speech (a string of parts of speech, possibly separated by commas)
    
    The function performs the following tasks:
    - Reads the input CSV file.
    - Processes each row to extract the text, snippet, and parts of speech.
    - Cleans and formats the parts of speech.
    - Adds each word to the words dictionary, combining snippets if the word already exists.
    - Outputs statistics about the number of words processed and those missing snippets or parts of speech.
    
    Parameters:
    input_file (str): The path to the input CSV file.
    
    Example:
        populate_words('words.csv')
    
    Raises:
    IOError: If there is an issue with reading the input file.
    """
    
    with open(input_file, encoding="utf-8") as file:
        reader = csv.reader(file)
        
        # Iterate through the rows in the input file.
        for row in reader:
            # Skip bad rows for now.
            if len(row) != 4:
                print(f"Bad row length for row {row}")
                continue
            
            # Holds each part of speech found for the word
            speech_parts = []
            
            # Unpack the row data into the variables.
            page_num, text, snippet, parts_of_speech = row
            
            # If the word exists in the words dict, just append it to the existing word snippet.
            # The pipe act as a delimiter.
            if text in words:
                words[text].snippet += '|' + snippet
                continue
            
            # Break down the parts of speech into a list
            if parts_of_speech:
                # comb. form. is the only part that is two words, so target it directly
                individual_parts = re.findall(r'comb[.] form[.]|[A-Za-z]{1,}', parts_of_speech)
                
                # Iterate through the individual parts of speech
                for part in individual_parts:
                    # Clean the part
                    part = part.strip()
                    
                    # Replace superscripts
                    part = re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]', '', part)
                        
                    # Add the part to the list of speech parts for this word.
                    speech_parts.append(part)
                        
            # Instantiate a new Word object with the data and join the speech parts with a | delimiter.
            word = Word(text, snippet, "|".join(speech_parts))
            
            # And add it to the words dictionary.
            words[text] = word
        
    # Find all Words without a snippet.
    no_snippet = [word for word in words if words[word].snippet == '']
    
    # Find all Words without parts of speech.
    no_parts_of_speech = [word for word in words if words[word].parts_of_speech == '']
    
    # Output our findings.
    print(f"Found {len(words)} words, {len(no_snippet)} without snippets, {len(no_parts_of_speech)} without parts of speech")
    
def write_to_file(file_path, format, minified):
    """
    Writes data to a file in the specified format.
    
    Parameters:
    file_path (str): The path to the file where data will be written.
    format (str): The format in which to write the data. Supported formats are 'csv', 'json', and 'txt'.
    minified (bool): If True and format is 'json', the JSON output will be minified. Otherwise, it will be pretty-printed.
    """
    
    # The new line delimiter (required for CSV to eliminate empty lines)
    nl_delimiter = '' if format == 'csv' else None
    
    # Try to write to the file using the mapped writer function.
    try:
        with open(file_path, 'w', newline=nl_delimiter, encoding="utf-8") as file:
            # Find the writer function assigned to the format.
            writer_function = writer_functions.get(format)
            
            # Invoke the function or raise an error if the format is not supported.
            if writer_function:
                writer_function(file, minified)
            else:
                print(f"Invalid format: {format}")
                exit()
    except Exception as e:
        print(f"Error writing file: {e}")
            
def write_csv(file):
    """
    Writes the contents of the words dictionary to a CSV file.
    
    Each row in the CSV file represents a word with its text, snippet, and parts of speech.
    
    Parameters:
    file (TextIOWrapper): The file object to write the CSV data to.
    """
    
    # Create a CSV writer object associated with the given file
    writer = csv.writer(file)
            
    # Iterate over each word in the words dictionary
    for word in words:
        # Write a row in the CSV file with the word's text, snippet, and parts of speech
        writer.writerow([words[word].text, words[word].snippet, words[word].parts_of_speech])
                
def write_txt(file):
    """
    Writes the text of each word in the words dictionary to a text file.
    
    Each line in the text file represents the text attribute of a word.
    
    Parameters:
    file (TextIOWrapper): The file object to write the text data to.
    """
    
    # Write each word's text attribute to a new line in the text file
    file.writelines([words[word].text + '\n' for word in words])
        
def write_json(file, minified):
    """
    Writes the contents of the words dictionary to a JSON file.
    
    The JSON file will contain an array of JSON objects, each representing a word.
    
    Parameters:
    file (TextIOWrapper): The file object to write the JSON data to.
    minified (bool): If True, the JSON output will be minified. Otherwise, it will be pretty-printed with an indentation of 4 spaces.
    """
    
    # Convert each word in the words dictionary to a JSON object
    json_list = [json.loads(words[word].toJSON()) for word in words]
    
    # Write the list of JSON objects to the file with the appropriate formatting
    json.dump(json_list, file, indent=None if minified else 4)
    
if __name__ == "__main__":
    main()