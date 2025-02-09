import requests
from bs4 import BeautifulSoup
import re
import csv

def format_drug_name(name):
    """Format drug name for URL (convert to lowercase and replace spaces with dashes)"""
    return name.lower().replace(" ", "-")

def extract_drug2(drug1):
    """Extract only the text inside the brackets from 'More about {Drug2}'"""
    url = f"https://www.drugs.com/{format_drug_name(drug1)}.html"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find "More about {Drug2}" heading
        more_about_header = soup.find(lambda tag: tag.name == "h2" and "More about" in tag.get_text())
        if more_about_header:
            match = re.search(r'\((.*?)\)', more_about_header.get_text().strip())  # Extract text inside brackets
            return match.group(1) if match else None
    return None


def clean_review(review_text):
    """Extract only the main review content, removing metadata, ratings, and unnecessary text."""
    
    # Extract all quoted text
    quoted_texts = re.findall(r'"(.*?)"', review_text)
    
    if quoted_texts:
        return quoted_texts[0]  # Keep only the first quoted content (actual review)

    return None 

def extract_reviews(drug1, drug2):
    """Extract clean reviews from the correct 'Reviews for {Drug1}' section"""
    
    # Construct the correct review URL
    if drug2:
        url = f"https://www.drugs.com/comments/{format_drug_name(drug2)}/{format_drug_name(drug1)}.html"
    else:
        url = f"https://www.drugs.com/comments//{format_drug_name(drug1)}.html"

    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all review sections
        review_section = soup.find_all("div", class_="ddc-comment")
        raw_reviews = [review.get_text(strip=True) for review in review_section]

        # Clean reviews
        cleaned_reviews = [clean_review(review) for review in raw_reviews]
        cleaned_reviews = list(filter(None, cleaned_reviews))  # Remove None values

        return cleaned_reviews if cleaned_reviews else ["No reviews found."]
    
    return [f"Failed to retrieve reviews page. Status Code: {response.status_code}"]

# User input for drug name
drug1 = input("Enter the drug name (e.g., 'Ativan'): ").strip()

# Extract Drug2 from 'More about {Drug2}' section
drug2 = extract_drug2(drug1)

# Extract reviews for the input drug (Drug1)
reviews_list = extract_reviews(drug1, drug2)

# Save reviews to a CSV file with serial numbers
filename = f"{format_drug_name(drug1)}_reviews.csv"
with open(filename, "w", encoding="utf-8", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Serial No.", "Review"])  # Column headers
    for i, review in enumerate(reviews_list, start=1):
        writer.writerow([i, review])  # Store serial number and review

print(f"✅ Reviews extracted and saved to {filename}")
