'''

Web Scraping Language Processer
by Devin Taylor
Spring 2023
'''

# Python Standard Libaries
import requests                         # Python Standard Library for url requests
import re                               # Python regular expression library
import os
from nltk import pos_tag, word_tokenize
from prettytable import PrettyTable
import sys
# Python 3rd Party Libraries
import nltk     # Import the Natural Language Toolkit
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.corpus import PlaintextCorpusReader   #Import the PlainTextCorpusReader Module
from nltk.corpus import stopwords
nltk.download('gutenberg')
from nltk.corpus import gutenberg
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from bs4 import BeautifulSoup           # 3rd Party BeautifulSoup Library - pip install Beautifulsoup4
from collections import Counter

IMG_SAVE = "./IMAGES/"  # Directory to store images
# PARTS of SPEECH Lookup
POSTAGS = {
        'CC':   'conjunction',
        'CD':   'CardinalNumber',
        'DT':   'Determiner',
        'EX':   'ExistentialThere',
        'FW':   'ForeignWord',
        'IN':   'Preposition',
        'JJ':   'Adjective',
        'JJR':  'AdjectiveComparative',
        'JJS':  'AdjectiveSuperlative',
        'LS':   'ListItem',
        'MD':   'Modal',
        'NN':   'Noun',
        'NNS':  'NounPlural',
        'NNP':  'ProperNounSingular',
        'NNPS': 'ProperNounPlural',
        'PDT':  'Predeterminer',
        'POS':  'PossessiveEnding',
        'PRP':  'PersonalPronoun',
        'PRP$': 'PossessivePronoun',
        'RB':   'Adverb',
        'RBR':  'AdverbComparative',
        'RBS':  'AdverbSuperlative',
        'RP':   'Particle',
        'SYM':  'Symbol',
        'TO':   'to',
        'UH':   'Interjection',
        'VB':   'Verb',
        'VBD':  'VerbPastTense',
        'VBG':  'VerbPresentParticiple',
        'VBN':  'VerbPastParticiple',
        'VBP':  'VerbNon3rdPersonSingularPresent',
        'VBZ':  'Verb3rdPersonSingularPresent',
        'WDT':  'WhDeterminer',
        'WP':   'WhPronoun',
        'WP$':  'PossessiveWhPronoun',
        'WRB':  'WhAdverb'
        }

# Create the directory if necessary
if not os.path.exists(IMG_SAVE):
    os.makedirs(IMG_SAVE)
    
pageLinks = set()
imgDict   = {}



def RecurseURL(newURL, base, local):
    try:
        if base not in newURL:
            return
        print('\n\n----------------Scanning----------------\n\n', newURL)
        page = requests.get(newURL)   # retrieve a page from your favorite website
        pageText = page.text
        pageText = re.sub("[^a-zA-Z]", ' ', pageText)
        
        engText = word_tokenize(pageText)
        # Tag each word with it's part of speech using the NLTK pos_tagger
        tags = pos_tag(engText)
        
        soup = BeautifulSoup(page.text, 'html.parser')      # convert the page into soup
        allText = soup.text
        #for numbers in soup.find_all('footer'):
         #   print(element.text)         
       
        tokens = nltk.word_tokenize(allText)
        pos_tags = pos_tag(tokens)                
        table = PrettyTable()
        table.field_names = ["Word", "Part of Speech"]
        
        for word, pos in pos_tags:
            if pos.startswith("N") or pos.startswith("V"):
                table.add_row([word, pos])
        
        print(table)                
  
           
        #Zipcode Regex
        zipCodeRegex = b'\d{5}(?:-\d{4})?'
        
        #for words in allText:
         #   print        
        
        #Convert text into byte string
        textBytes = allText.encode()
        zipCodes = re.findall(zipCodeRegex, textBytes)
        
        
        
        #convert the byte strings to regular strings
        zipCodes = [num.decode() for num in zipCodes]
        print("\n\nZip Code(s)", zipCodes)
        
        
        #Phone Numbers Regex
        #phoneNumberRegex = b'\(?\d{3}\)?-?*\d{3}-?*-?\d{4}'
        phoneNumberRegex = b'\+[\d]{2}\s*\([0-9]{3}\)\s*[0-9]{3}\s*[0-9]{4}'
        
        phoneNumbers = re.findall(phoneNumberRegex, textBytes)
        
        #convert the byte strings to regular strings
        phoneNumbers = [num.decode() for num in phoneNumbers]
        print("Phone Number(s)", phoneNumbers)                
        
        print ("\n\nCompiling Vocabulary Frequencies")
              
        tbl = PrettyTable(["Vocabulary", "Occurs"])
        # download required NLTK data
        nltk.download('punkt')
        nltk.download('stopwords')
        
        # read in the text file
        #userSpecifiedFile = input("What is the path to the file and its extension? ")
        #with open(userSpecifiedFile, 'r') as f:
        #text = soup.read()
        
        # tokenize the text and remove stop words
        tokens = nltk.word_tokenize(pageText)
        stopWords = set(nltk.corpus.stopwords.words('english'))
        words = [token.lower() 
        for token in tokens 
            if token.lower() not in stopWords and len(token) >= 4]
        
        # count the occurrences of each word
        wordCounts = Counter(words)
        
        # create a pretty table to display the results
        table = PrettyTable(['Word', 'Count'])
        for word, count in wordCounts.most_common():
            table.add_row([word, count])
        
        # print the table
        print(table)                
        links= soup.findAll('a')   # Find all the possible links
        if links:
            for eachLink in links:
                
                newLink = eachLink.get('href') 
                if not newLink:
                    continue
                
                if 'http' not in newLink:
                    newLink = base+newLink
                    
                if not local in newLink:
                    continue   
                
                if newLink not in pageLinks: 
                    # verify this is a true new link
                    
                    # Process any images found
                    images = soup.findAll('img')  # Find the image tags
                    for eachImage in images:      # Process and display each image
                        try:
                            imgURL = eachImage['src']
                            print("Processing Image:", imgURL, end="")
                            if imgURL[0:4] != 'http':       # If URL path is relative
                                imgURL = base+imgURL         # try prepending the base url
                            
                            imageName = os.path.basename(imgURL)  # Get the basename 
                            imgOutputPath = IMG_SAVE+imageName    # Prepare the output path
                            
                            response = requests.get(imgURL)       # Get the image from the URL

                            imgContent = response.content
                            with open(imgOutputPath, 'wb') as outFile:
                                outFile.write(imgContent)
                                
                            # Save the image
                            print("  >> Saved Image:", imgOutputPath)
                        except Exception as err:
                            print(imgURL, err)
                            continue    
                    
                    pageLinks.add(newLink)              # add the link to our set of unique links 
                    RecurseURL(newLink, base, local)           # Process this link
                else:
                    continue
                    
    except Exception as err:
        # display any errors that we encounter
        print(err)

if __name__ == '__main__':
    
    ''' Main Program Entry Point ''' 
    baseURL     = 'https://website/'  #Input your target site. Ensure you have permission to scrape the site. The domain owner can detect this activity and take action.
    baseDomain  = 'https://website/'  #Input your target site. Ensure you have permission to scrape the site. The domain owner can detect this activity and take action.
    mustInclude  ='websitekeyword'                   #Change to a word that should be in the URL to prevent scanning other sites.

    pageLinks.add(baseURL)
    
    print("\nScanning: ", baseURL, '\n')
    RecurseURL(baseURL, baseDomain, mustInclude)
    
    print("\nScanning Complete\n")
    print("Unique URLs Discovered\n")
    
    for eachEntry in pageLinks:
        print(eachEntry)
    
print('\n\nScript Complete')
