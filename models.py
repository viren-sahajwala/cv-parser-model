import nltk

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

import re
import pandas as pd

from pdfminer.high_level import extract_text
import docx2txt

def extract_text_from_file(file_path, file_name):
  ext = file_name.rsplit('.', 1)[1] # split to obtain file extension
  # to fetch text from pdf
  if ext == 'pdf':  
    return extract_text(file_path)
  else:
    # to extract text from document file
    txt = docx2txt.process(file_path)
    if txt:
        return txt.replace('\t', ' ')
    return txt



# Extracting name from the cv text
def extract_names(text):
  nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
  names = []
  for nltk_result in nltk_results:
    if type(nltk_result) == Tree:
      for nltk_result_leaf in nltk_result.leaves():
        names.append(nltk_result_leaf[0])
  return names[0]+ ' ' + names[1]



# Extracting phone number from the CV
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
def extract_phone_number(resume_text):
    phone = re.findall(PHONE_REG, resume_text)
    
    number = ''.join(phone[0])
    if resume_text.find(number) >= 0 and len(number) <20:
        return number
    return None



# Extracting email from the CV

EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')

def extract_emails(resume_text):
  emails = re.findall(EMAIL_REG, resume_text)
  return emails[0]


# Extracting Skills from the cv

SKILLS_DB = pd.read_excel('skills.xlsx')
SKILLS_DB = SKILLS_DB['Skill'].unique()

def extract_skills(input_text):
  stop_words = set(nltk.corpus.stopwords.words('english'))
  word_tokens = nltk.tokenize.word_tokenize(input_text)
 
  # remove the stop words
  filtered_tokens = [w for w in word_tokens if w not in stop_words]
 
  # remove the punctuation
  filtered_tokens = [w for w in word_tokens if w.isalpha()]
 
  # generate bigrams and trigrams (such as artificial intelligence
  bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
 
  # we create a set to keep the results in.
  found_skills = set()
 
  # we search for each token in our skills database
  for token in filtered_tokens:
    if token.lower() in SKILLS_DB:
      found_skills.add(token)
  
  # we search for each bigram and trigram in our skills database
  for ngram in bigrams_trigrams:
    if ngram.lower() in SKILLS_DB:
      found_skills.add(ngram)

  final_skills = ', '.join(map(str, found_skills))
  return final_skills



# Extracting education from the cv
major = pd.read_csv('majors-list.csv')
major = major['Major'].unique()

EDUCATION = [
    'BE','B.E.', 'B.E', 
    'BS', 'B.S', 'B', 'M', 'BMM', 'B.M.M.', 'B.M.S', 'BMS',
    'MSC.', 'BSC.', 'MSC', 'BSC',
    'ME', 'M.E', 'M.E.', 'MS', 'M.S', 'M.C.A.',
    'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
    'BA', 'B.A', 'BA.', 'B.A.', 'BCOM', 'B.COM.', 
    'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
    ]
      
def extract_education(resume_text):
  edn = []
  for sent in resume_text.split('\n'):
    for degree in EDUCATION:
      if degree in sent:
        edn.append(sent)
  names = [n.upper() for n in edn]
  
  new_edn = set()
  for n in names:
    for m in major:
      if m in n:
        new_edn.add(n)
  final_edn = ', '.join(map(str, new_edn))
  return final_edn 
