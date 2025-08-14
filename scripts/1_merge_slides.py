import os
import fitz
import re

def strip_bookmarks(pdf_path):
    """Open a PDF, remove bookmarks by creating a new doc with all pages."""
    try:
        original = fitz.open(pdf_path)
        cleaned = fitz.open()
        cleaned.insert_pdf(original)
        original.close()
        return cleaned
    except Exception as e:
        print(f"Failed to process '{pdf_path}': {e}")
        return None

def main():
    root_folder = os.getcwd()
    slides_folder = os.path.join(root_folder, "slides")

    if not os.path.isdir(slides_folder):
        print("'slides/' folder not found. No PDFs to process.")
        return

    pdf_files = sorted([
        f for f in os.listdir(slides_folder)
        if f.lower().endswith('.pdf')
    ])

    if not pdf_files:
        print("'slides/' folder is empty. No PDFs to merge.")
        return

    merged_doc = fitz.open()
    toc = []
    page_counter = 0

    for pdf_file in pdf_files:
        pdf_path = os.path.join(slides_folder, pdf_file)
        cleaned_doc = strip_bookmarks(pdf_path)

        if cleaned_doc is None or cleaned_doc.page_count == 0:
            continue

        merged_doc.insert_pdf(cleaned_doc)

        # Remove leading zeros from the title

        bookmark_title = os.path.splitext(pdf_file)[0]
        match = re.match(r'^(\d+)(.*)', bookmark_title)
        if match:
            raw_number, rest = match.groups()
            rest = rest.lstrip()

            # Always strip leading zeros if the number has more than one digit and starts with zero
            if len(raw_number) > 1 and raw_number.startswith("0"):
                number_part = str(int(raw_number))
            else:
                number_part = raw_number

            if not rest.startswith('.'):
                bookmark_title = f"{number_part}. {rest}"
            else:
                bookmark_title = number_part + rest

        toc.append([1, bookmark_title, page_counter + 1])
        page_counter += cleaned_doc.page_count

        cleaned_doc.close()

    if page_counter == 0:
        print("No valid PDF content found to merge. Output not created.")
        return

    merged_doc.set_toc(toc)
    output_path = os.path.join(root_folder, "Lectures.pdf")

    try:
        merged_doc.save(output_path)
        print(f"Merged PDF saved as: {os.path.relpath(output_path)}")
    except Exception as e:
        print(f"Failed to save merged PDF: {e}")
    finally:
        merged_doc.close()

if __name__ == "__main__":
    main()
