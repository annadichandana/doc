import os
import json
import fitz  # PyMuPDF

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    title = doc.metadata.get("title", "") or doc[0].get_text("text").split('\n')[0].strip()

    headings = []
    font_sizes = {}

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = round(span["size"], 1)

                    if not text or len(text) < 3:
                        continue
                    
                    font_sizes[size] = font_sizes.get(size, 0) + 1
                    headings.append({
                        "text": text,
                        "size": size,
                        "page": page_num
                    })

    # Determine font size rankings
    sorted_sizes = sorted(font_sizes.keys(), reverse=True)
    size_to_level = {}
    if len(sorted_sizes) >= 1:
        size_to_level[sorted_sizes[0]] = "H1"
    if len(sorted_sizes) >= 2:
        size_to_level[sorted_sizes[1]] = "H2"
    if len(sorted_sizes) >= 3:
        size_to_level[sorted_sizes[2]] = "H3"

    outline = []
    for item in headings:
        level = size_to_level.get(item["size"])
        if level:
            outline.append({
                "level": level,
                "text": item["text"],
                "page": item["page"]
            })

    return {
        "title": title,
        "outline": outline
    }

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"

    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline(pdf_path)

            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            with open(output_path, "w",encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
