from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os

# Configura a chave de API do Google
os.environ["GOOGLE_API_KEY"] = "AIzaSyBkz49oIDf4XYNfkDdbvXHvikatbRkY_WU"  # Substitua pela sua chave de API do Google


template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)


model = ChatGoogleGenerativeAI(model="gemini-pro")  # Use o modelo Gemini Pro

def parse_with_gemini(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        print(f"Parsed batch: {i} of {len(dom_chunks)}")
        parsed_results.append(response.content)  # Use response.content para obter o texto

    return "\n".join(parsed_results)


if __name__ == '__main__':
    dom_chunks = [
        "O preço do produto é R$100,00. A cor do produto é azul.",
        "O nome do produto é caneta. O material é plástico.",
        "O tipo de entrega é expresso. A data de entrega é 2024-08-15."
    ]
    parse_description = "Extraia apenas o preço do produto."

    parsed_text = parse_with_gemini(dom_chunks, parse_description)
    print(f"Resultado: {parsed_text}")