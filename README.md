# Wikipedia Sports Articles Search
This project is a web application that allows users to search for Wikipedia articles related to various American sports leagues such as NFL, NBA, MLB, and NHL. The application scrapes Wikipedia pages, preprocesses the text data, builds an index using the BM25 algorithm, and provides a user-friendly interface for searching through the articles. It aims to assist users in quickly finding relevant information on their favorite sports topics.

## Features
### 1. Web Scraping
   - Scrapes Wikipedia articles related to American sports leagues.
   - Extracts article titles, text content, categories, links, references, and other relevant metadata.

### 2. Text Preprocessing
   - Tokenizes the text data.
   - Removes stopwords (common words like "the", "and", "is") to focus on meaningful keywords.
   - Stems words to reduce them to their base form (e.g., "running" becomes "run").

### 3. BM25 Indexing
   - Builds an index using the BM25Okapi algorithm.
   - Ranks the articles based on their relevance to user queries.
   - Provides efficient retrieval of relevant articles based on search queries.

### 4. User Interface
   - Provides a user-friendly web interface for searching articles.
   - Accepts user queries and displays relevant articles with titles and links.
   - Allows users to input search queries and get instant results.

## Usage:
### Installation
   - Clone the repository to your local machine.
   - Make sure you have Python installed.
   - Install the required Python packages using `pip install -r requirements.txt`.

### Running the Application
   - Execute the Python script `main.py`.
   - The Flask application will start running locally.
   - Access the application through your web browser by navigating to `http://127.0.0.1:5000/`.

### Searching for Articles
   - Enter your search query in the provided input box.
   - Press Enter or click the Search button.
   - Relevant articles matching your query will be displayed with titles and links.

## Dependencies
- `requests`: For making HTTP requests to fetch Wikipedia pages.
- `BeautifulSoup`: For parsing HTML content obtained from Wikipedia.
- `nltk`: For natural language processing tasks such as tokenization, stopword removal, and stemming.
- `rank_bm25`: For implementing the BM25 algorithm for information retrieval.
- `Flask`: For building and running the web application.

## License
- This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- The project utilizes various open-source libraries and frameworks. Special thanks to the developers of these tools for their contributions.