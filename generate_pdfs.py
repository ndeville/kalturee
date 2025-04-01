from datetime import datetime
import os
import sys
import time
import shutil
from PyPDF2 import PdfReader, PdfWriter
import ollama
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO



def generate_title_with_ollama(theme):
    result = ollama.generate("llama3.3", f"""
Generate a creative and concise title for a research paper on the following theme: {theme}.
Only return the title, no other text.
This will be the main title of a PDF document.
    """)
    
    output = '\n'.join(line.strip() for line in result.response.splitlines())
    print(f"generate_title_with_ollama > {output}\n\n")
    return output

def generate_abstract_with_ollama(title):
    result = ollama.generate("llama3.3", f"""
Generate a brief academic abstract (150-200 words) for a research paper titled: '{title}'.
Only return the abstract text, no other text.
This will be the abstract section of the PDF document.
    """)
    
    output = '\n'.join(line.strip() for line in result.response.splitlines())
    print(f"generate_abstract_with_ollama > {output}\n\n")
    return output

def create_title_page(title, abstract):
    """Creates a new PDF page with title and abstract"""
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, title)
    
    # Add abstract
    c.setFont("Helvetica", 12)
    c.drawString(72, 700, "Abstract")
    
    # Write abstract text with word wrapping
    text_object = c.beginText(72, 680)
    text_object.setFont("Helvetica", 11)
    
    # Simple word wrap implementation
    words = abstract.split()
    line = ""
    for word in words:
        if len(line + " " + word) < 75:  # Approximate characters per line
            line = line + " " + word
        else:
            text_object.textLine(line)
            line = word
    if line:
        text_object.textLine(line)
        
    c.drawText(text_object)
    c.save()
    
    packet.seek(0)
    return PdfReader(packet)

def generate_pdfs(file_path, theme, num_documents=1):
    """
    Generates new PDF files with AI-generated title and abstract pages.
    
    Args:
        file_path (str): Path to the template PDF file
        theme (str): Theme to use for generating new content
        num_documents (int): Number of PDFs to generate
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    
    if not file_path.lower().endswith('.pdf'):
        print(f"Error: File '{file_path}' is not a PDF file.")
        return
    
    generated_files = []
    
    for i in range(num_documents):
        print(f"\n\n========= Creating PDF {i+1} of {num_documents}\n")
        
        # Create new file name
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(file_name)[0]
        new_file_name = f"{name_without_ext}_{i+1:02d}.pdf"
        new_file_path = os.path.join(file_dir, new_file_name)
        
        try:
            # Generate new content
            generated_title = generate_title_with_ollama(theme)
            generated_abstract = generate_abstract_with_ollama(generated_title)
            
            # Create new title page
            new_first_page = create_title_page(generated_title, generated_abstract)
            
            # Read the original PDF
            original_pdf = PdfReader(file_path)
            
            # Create PDF writer object
            pdf_writer = PdfWriter()
            
            # Add the new title page
            pdf_writer.add_page(new_first_page.pages[0])
            
            # Add all pages from original PDF
            for page in original_pdf.pages:
                pdf_writer.add_page(page)
            
            # Save the new PDF
            with open(new_file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            generated_files.append(new_file_path)
            print(f"✅ Saved new PDF > {new_file_path}")
            
        except Exception as e:
            print(f"Error generating PDF file: {e}")
    
    return generated_files

if __name__ == "__main__":
    start_time = time.time()
    
    pdf_path = "/Users/nic/demo/pharma/pharma-demo.pdf"
    theme = "Pharmaceutical Research Papers"
    num_documents = 5
    
    generate_pdfs(pdf_path, theme, num_documents)
    
    run_time = time.time() - start_time
    if run_time < 1:
        print(f"\nFinished creating {num_documents} PDFs in {round(run_time*1000)}ms at {datetime.now().strftime('%H:%M:%S')}.\n")
    elif run_time < 60:
        print(f"\nFinished creating {num_documents} PDFs in {round(run_time)}s at {datetime.now().strftime('%H:%M:%S')}.\n")
    else:
        print(f"\nFinished creating {num_documents} PDFs in {round(run_time/60)}mins at {datetime.now().strftime('%H:%M:%S')}.\n")
