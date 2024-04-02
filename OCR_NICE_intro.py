
import pandas as pd
import re

NICE_ocr=pd.read_csv('sections_tmp.csv',sep='\t')
clean_text=NICE_ocr.iloc[0]['Intro']
subsections = re.split(r'\bB\.\d+\.\d*\s+', clean_text)[1:]



def split_text_on_capitalization(text):
    # Regular expression to find words followed by a space and a capital letter
    pattern = re.compile(r'(?<=\w) (?=[A-Z])')

    # Split the text based on the pattern
    split_points = pattern.split(text)

    # Initialize two lists to hold the split results
    list1 = []
    list2 = []

    # Loop through the split points
    for i, segment in enumerate(split_points):
        # Add to list1 if it's the title or first segment
        if i == 0:
            list1.append(segment)
        # Otherwise, add to list2
        else:
            list2.append(segment)

    # Join list2 items into a single string as they are part of the continuous sentence
    final_list2 = ', '.join(list2)

    return list1, [final_list2]


for subsection in subsections:
    header, subsection_text = split_text_on_capitalization(subsection)


title='Dapagliflozin for treating chronic heart failure with reduced ejection fraction'