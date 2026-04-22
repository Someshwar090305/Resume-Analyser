import fitz


def extract_text_from_pdf(file):
    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_text_from_txt(file):
    raw_bytes = file.read()
    return raw_bytes.decode("utf-8", errors="ignore")


def load_resume(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        text = extract_text_from_pdf(uploaded_file)
        if not text or len(text.strip()) < 50:
            return "", "PDF appears image-based or has no extractable text. Please paste the resume text manually."
        return text, None
    elif name.endswith(".txt"):
        text = extract_text_from_txt(uploaded_file)
        return text, None
    else:
        return "", "Unsupported file type. Please upload a .pdf or .txt file."
