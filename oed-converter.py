import os
import csv
from word import Word

# The list to house Word objects.
words = []

def read_file(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name), encoding="utf-8") as file:
        reader = csv.reader(file)
        
        for row in reader:
            if len(row) != 4: # Skip bad rows for now
                continue
            
            page_num, text, definition, parts_of_speech = row
            
            word = Word(text, definition, parts_of_speech)
            words.append(word)
        
    no_snippet = [word for word in words if word.snippet == '']
    no_parts_of_speech = [word for word in words if word.parts_of_speech == '']
    print(f"Found {len(words)} words, {len(no_snippet)} without snippets, {len(no_parts_of_speech)} without parts of speech")

read_file('parsed_words.txt')