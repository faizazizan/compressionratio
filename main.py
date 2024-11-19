import streamlit as st
import requests
from bs4 import BeautifulSoup
import gzip
import matplotlib.pyplot as plt
import numpy as np

# Streamlit app header
st.title("Webpage Compression Quality Checker")
st.subheader("Detect spammy web pages using compression ratios")

# Function to fetch and parse a webpage with headers
def fetch_and_parse(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with requests.Session() as session:
        response = session.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        soup = BeautifulSoup(response.content, 'html.parser')

    for tag in soup(['head', 'header', 'footer', 'script', 'style', 'meta']):
        tag.decompose()
    return soup

# Function to extract text selectively
def extract_text_selectively(soup):
    excluded_tags = {'style', 'script', 'meta', 'body', 'html', '[document]', 'button'}
    text_lines = []

    for element in soup.find_all(True, recursive=True):
        if element.name in excluded_tags:
            continue
        if element.name in {'p', 'li', 'h1', 'h2', 'h3', 'table'}:
            text_lines.append(element.get_text(strip=True))
    
    combined_text = ' '.join(text_lines)
    return combined_text

# Function to calculate compression ratio
def calculate_compression_ratio(text):
    original_size = len(text.encode('utf-8'))
    compressed_data = gzip.compress(text.encode('utf-8'))
    compressed_size = len(compressed_data)
    compression_ratio = original_size / compressed_size
    return compression_ratio

# Function to plot compression ratios
def plot_compression_ratios(compression_ratios):
    bins = np.arange(0.5, 7.5, 0.25)
    histogram, bin_edges = np.histogram(compression_ratios, bins=bins, density=True)
    probabilities = [min(1.0, cr / 4.0) * 100 for cr in bin_edges[:-1]]

    fig, ax1 = plt.subplots()

    ax1.bar(bin_edges[:-1], histogram, width=0.2, color='blue', alpha=0.6, label='Fraction of pages')
    ax1.set_xlabel('Compression Ratio')
    ax1.set_ylabel('Fraction of Pages', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(bin_edges[:-1], probabilities, color='magenta', label='Spam Probability (%)')
    ax2.set_ylabel('Probability of Spam (%)', color='magenta')
    ax2.tick_params(axis='y', labelcolor='magenta')

    plt.title('Compression Ratio vs Spam Probability')
    fig.tight_layout()
    return fig

# Automatically format URL to include 'https://'
def format_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url

# Streamlit input
url = st.text_input("Enter the URL to check:", "https://www.example.com")  # Default URL
url = format_url(url)

if url:
    try:
        # Process the webpage
        soup = fetch_and_parse(url)
        combined_text = extract_text_selectively(soup)

        # Calculate compression ratio
        compression_ratio = calculate_compression_ratio(combined_text)
        st.write(f"**Compression Ratio for {url}:** {compression_ratio:.2f}")

        # Classify the page
        spam_threshold = 3.5
        if compression_ratio > spam_threshold:
            st.error("⚠️ This page is likely spammy due to a high compression ratio.")
        else:
            st.success("✅ This page appears legitimate with a low compression ratio.")

        # Benchmark Explanation
        st.header("Benchmark Explanation")
        st.markdown("""
        ### **Low Compression Ratio (Good Quality)**  
        - **Range:** 1.0 - 2.5  
        - **Details:** Indicates rich, unique, and diverse content. Ideal for SEO and user engagement.  
        - **Examples:** Blog posts, research articles, or detailed product pages.

        ---

        ### **Moderate Compression Ratio (Acceptable Quality)**  
        - **Range:** 2.6 - 4.0  
        - **Details:** Some repetitive elements or templates. Content may still be useful but less diverse.  
        - **Suggestions:** Reduce redundancy and enhance content quality.

        ---

        ### **High Compression Ratio (Poor Quality)**  
        - **Range:** 4.1 and above  
        - **Details:** Indicates highly repetitive or boilerplate content. Risk of being flagged as spam.  
        - **Suggestions:** Rewrite content to add unique material and provide real value.
        """)

        # Recommendations based on ratio
        st.header("Recommendations")
        if compression_ratio <= 2.5:
            st.success("Your content is in excellent shape for SEO!")
        elif 2.6 <= compression_ratio <= 4.0:
            st.warning("Consider improving content diversity and reducing repetitive elements.")
        else:
            st.error("Your content quality is poor and at risk of being flagged as spam. Significant improvements are needed.")
    
    except Exception as e:
        st.error(f"An error occurred while processing the URL: {e}")
