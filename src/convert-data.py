import os
import csv
from word import Word

# Input file path.
input_file = os.path.join(os.path.dirname(__file__), 'parsed-data.txt')

# The list to house Word objects.
words = {}

# Read all records in the input file and create Word objects from the data.
def populate_words():
    with open(input_file, encoding="utf-8") as file:
        reader = csv.reader(file)
        
        # Iterate through the rows in the input file.
        for row in reader:
            # Skip bad rows for now.
            if len(row) != 4:
                continue
            
            page_num, text, snippet, parts_of_speech = row
            
            # Skips duplicate words (should probably merge snippets or handle them however you'd like).
            if text in words:
                continue
            
            # Instantiate a new Word object with the data.
            word = Word(text, snippet, parts_of_speech)
            
            # And add it to the words dictionary.
            words[text] = word
        
    # Find all Words without a snippet.
    no_snippet = [word for word in words if words[word].snippet == '']
    
    # Find all Words without parts of speech.
    no_parts_of_speech = [word for word in words if words[word].parts_of_speech == '']
    print(f"Found {len(words)} words, {len(no_snippet)} without snippets, {len(no_parts_of_speech)} without parts of speech")
    
def write_csv():
    with open(os.path.join(os.path.dirname(__file__), 'out.csv'), 'w', encoding="utf-8") as file:
        writer = csv.writer(file)
        
        for word in words:
            writer.writerow([words[word].text, words[word].snippet, words[word].parts_of_speech])
            
def write_words():
    with open(os.path.join(os.path.dirname(__file__), 'words.txt'), 'w', encoding="utf-8") as file:
        file.writelines([words[word].text + '\n' for word in words])

populate_words()
write_csv()
write_words()