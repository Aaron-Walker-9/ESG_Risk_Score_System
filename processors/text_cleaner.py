
import pymupdf as fitz
import re

def pdf_to_clean_sentences(pdf_path):
    doc = fitz.open(pdf_path)
    cleaned_sentences = []

    for page in doc:
        #get text coordinates
        blocks = page.get_text("blocks")
        page_width = page.rect.width

        #left and right columns
        left_col = [b for b in blocks if b[0] < page_width/2]
        right_col = [b for b in blocks if b[0] >= page_width/2]

        #sort within each column by y (top to bottom)
        left_col = sorted(left_col, key=lambda b: b[1])
        right_col = sorted(right_col, key=lambda b: b[1])

        #join per-column text in reading order (left first, then right)
        column_text = []
        for col in [left_col, right_col]:
            text = " ".join(b[4] for b in col)
            column_text.append(text)

        #split sentences using regex
        for text in column_text:
            
            sentences = text.replace("\n"," ") # convert newline into space
            sentences= re.sub(r'\s+', ' ', sentences) #converts multuple spaces into single space 
            sentences  = re.sub(r'[•*]','', sentences) # removes symbols • and *
            sentences = re.split(r'(?<=[.!?])\s+', sentences.strip())#seperates sentences by grammar and spaces
            cleaned_sentences.extend(sentences)

    return cleaned_sentences
