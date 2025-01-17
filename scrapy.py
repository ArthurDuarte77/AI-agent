from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from parse import parse_with_gemini

def scrape_website(website, parse_description):
    print("Starting local browser...")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless (sem interface gráfica)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  # Para rodar em alguns ambientes Linux
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    try:
      driver.get(website)
      print("Navigated! Scraping page content...")
      html = driver.page_source
      dom_chunks = split_dom_content(clean_body_content(extract_body_content(html_content=html)))
      parsed_result = parse_with_gemini(dom_chunks, parse_description)
      return parsed_result
    finally:
      driver.quit()


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]


if __name__ == "__main__":
    website = "https://ai.google.dev/gemini-api/docs/structured-output"
    parse_description = "Como o modelo recebe a especificação de formato do texto no comando?"
    result = scrape_website(website, parse_description)
    print(result)
