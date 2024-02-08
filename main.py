import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi
from flask import Flask, render_template, request

# Initialize Flask
app = Flask(__name__)

# Initialize NLTK components
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

# Set the search terms and define number of articles
search_terms = ["NFL", "NBA", "MLB", "NHL"]
article_number = 25

# Declare the search word(s) that comes after the search terms
search_suffix = "information" 

# Scrape through Wikipedia articles related to American sports
def scrape_sports_articles():
    global search_bm25

    # Generate dataset for the search terms
    articles = []
    
    for term in search_terms:        
        url = f"https://en.wikipedia.org/w/index.php?search={term} {search_suffix}"
        
        # Get a list of 25 urls relevant to the search term
        urls = get_urls(url)

        for url in urls: 
            soup = get_data(url)

            # Find the Author, Title, and Article ID
            cite_page = soup.find('li', {'id': 't-cite'}).find('a')

            if cite_page:
                link = f"https://en.wikipedia.org{cite_page.get('href')}"
                cite_data = get_data(link) 

                if cite_data:              
                    cite_data = cite_data.find('div', {'class': 'plainlinks'}).findAll('li')

                    # Get the relevent data
                    for data in cite_data:
                        data = data.get_text()

                        # Get the title
                        if 'Page name' in data:
                            title = data.split(': ')[1]
                        
                        # Get the title
                        if 'Author' in data:
                            author_editor = data.split(': ')[1]
                        
                        # Get the retrival date
                        if 'Date retrieved' in data:
                            date_retrived = data.split(': ')[1]
                        
                        # Get the creation/last modification date
                        if 'Date of last revision' in data:
                            modification_date = data.split(': ')[1]

                        # Get the title
                        if 'Page Version ID' in data:
                            article_id = data.split(': ')[1]          
            
            # Get the text content
            text_list = []
            text_soup = soup.find('div', {'class': 'mw-content-ltr mw-parser-output'})
            texts = text_soup.findAll('p')

            for text in texts:
                text_list.append(text.get_text())

            text = " ".join(text_list)

            # Get the word count
            words = text.split()
            word_count = len(words)
            
            # Get the categories from the vector-toc-contents
            vectors = soup.find('ul', {'class': 'vector-toc-contents'})
            vectors = vectors.findAll('a', {'class': 'vector-toc-link'})
            
            # Get the categories while ignoring the first blank output
            categories = []

            for vector in vectors[1:]:
                category = vector.get('href').replace('#', '')
                categories.append(category)

            # Get the links in the page
            links = [a['href'] for a in soup.find_all('a', href=True)]

            # Get the references in the page
            references = [a['href'] for a in soup.find_all('a', {'class': 'external text'}, href=True)]
           
            # Revision History
            revision_history = soup.find('li', {'id': 'ca-history'}).find('a')
            link = f"https://en.wikipedia.org{revision_history.get('href')}" 

            soup_history = get_data(link)

            # Find all revision dates in the revision history table
            revision_data = soup_history.select(".mw-changeslist-date")

            revision_dates = []

            # Extract and print the revision dates
            for date in revision_data:
                revision_dates.append(date.get_text())            
                        
            articles.append({"url": url, "title": title, "text": text, "categories": categories, "links":links,
                             "references": references, "last_modification_date": modification_date,
                             "revision_history": revision_dates, "author_editor": author_editor,
                             "article_id": article_id, "date_retrieved": date_retrived, "word_count": word_count})
        
    return articles

# Get HTML data
def get_data(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Get URLs from search pages
def get_urls(url):   
    global article_number     
    soup = get_data(url)

    # Find all relevant links in the page
    results = soup.findAll("div", {"class": "mw-search-result-heading"})  
    urls = [] 

    for result in results:
            link = result.find("a")

            # Add the necessary https text
            link = f"https://en.wikipedia.org{link.get('href')}"  
            urls.append(link)
    
    # Each page displays 20 links so we go to next page and add more links
    next_page = soup.find("div", {"class": "mw-pager-navigation-bar"})
    next_page_url = next_page.find("a")
    next_page_url = f"https://en.wikipedia.org{next_page_url.get('href')}" 
    
    soup = get_data(next_page_url)

    # Find all relevant links in the page
    results = soup.findAll("div", {"class": "mw-search-result-heading"}) 

    # Add more links. Limit the extra links to 20.
    if article_number > 40:
        article_number = 40

    for i in range (article_number - 20):
            link = results[i].find("a")

            # Add the necessary https text
            link = f"https://en.wikipedia.org{link.get('href')}"  
            urls.append(link)

    return urls

# Preprocess text: tokenize, remove stopwords, and stem
def preprocess_text(text):
    # split the text into individual words
    tokens = word_tokenize(text.lower())

    # Remove punctuation from each word
    tokens = [word for word in tokens if word.isalnum()]

    filtered_tokens = []

    # Filter out tokens that are stopwords like "the" "and" "an"
    for token in tokens:
        if token not in stop_words:
            # Reduces words to their base form
            stemmed_token = stemmer.stem(token)
            filtered_tokens.append(stemmed_token)

    # Return the final preprocessed text
    return " ".join(filtered_tokens)

# Build BM25 index
def build_bm25_index(articles):
    # Preprocess text and tokenize for each article
    tokenized_corpus = []

    for article in articles:
        # Process the text in the articles
        tokenized_text = preprocess_text(article["text"]).split(" ")
        tokenized_corpus.append(tokenized_text)
        
    # Create BM25 index
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25

# Search function using BM25
def search_bm25(query, bm25, articles):  
    # Process the user query
    tokenized_query = preprocess_text(query).split(" ")

    # Get the ranking scores
    scores = sorted(bm25.get_scores(tokenized_query), reverse=True)

    # Get the count of scores greater that 40% of the highest score
    threshold = 0.4  # 40%

    highest_score = scores[0]
    n = sum(1 for score in scores if score > threshold * highest_score)

    # Get the relevant articles from the search
    relevant_articles = bm25.get_top_n(tokenized_query, articles, n=n)

    return relevant_articles

# Define a route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():    
    global sports_articles
    global bm25 

    if request.method == 'POST':
        user_query = request.form['query']
        relevant_articles = search_bm25(user_query, bm25, sports_articles)

        results = []
        for i in range(len(relevant_articles)):
            result = {"title": relevant_articles[i]['title'], "url": relevant_articles[i]['url']}
            results.append(result)
        
        return render_template('index.html', query=user_query, results=results)
    else:
        return render_template('index.html', message="No relevant articles found.")
       
if __name__ == "__main__":
    # Get the articles and index them using bm25
    sports_articles = scrape_sports_articles()
    bm25 = build_bm25_index(sports_articles)

    # Run the Flask app
    app.run()
