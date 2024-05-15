import openai
import PyPDF2

from settings import OPENAI_API_KEY, PATH_TO_PDF

openai.api_key = OPENAI_API_KEY


def split_pdf_into_chunks(pdf_path: str, pages_per_chunk: int = 10) -> list[str]:
    chunks = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)

        for start in range(0, total_pages, pages_per_chunk):
            writer = PyPDF2.PdfWriter()
            end = min(start + pages_per_chunk, total_pages)

            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            chunk_filename = f'{pdf_path[:-4]}_chunk_{start//pages_per_chunk + 1}.pdf'
            with open(chunk_filename, 'wb') as output_pdf:
                writer.write(output_pdf)

            chunks.append(chunk_filename)

    return chunks


if __name__ == '__main__':
    chunks = split_pdf_into_chunks(PATH_TO_PDF, pages_per_chunk=10)

    client = openai.OpenAI()

    assistant = client.beta.assistants.create(
        name='Extraction Assistant',
        instructions="""Bitte extrahiere aus der angegebenen PDF-Datei alle wesentlichen Definitionen, Formeln, Lemmas und Sätze. Das Output-Format soll Rich Markdown sein und die Formeln sollen in LaTeX eingefügt werden. Die Extraktion soll kompakt und präzise erfolgen, unter der Annahme, dass der Nutzer bereits mit dem Stoff vertraut ist. Ziel ist es, eine klare und prägnante Zusammenfassung zu bieten, die als schnelles Nachschlagewerk für jemanden dienen kann, der mit den Konzepten bereits vertraut ist. Als Beispiel für das gewünschte Format sieh dir die folgenden Einträge an:

**Epigraph**  
Der Epigraph besteht aus dem Graphen von f auf X sowie allen darüberliegenden Punkten.  
Formal: $\\text{epi}(f, X) = \\{(x, \\alpha) \\in X \\times \\mathbb{R} \\mid f(x) \\leq \\alpha\\}$

**Lösbarkeit**  
Ein Minimierungsproblem ist lösbar, wenn das Infimum der Zielfunktion auf der zulässigen Menge tatsächlich angenommen wird.  
Formal: Ein Problem ist lösbar, wenn ein $\\bar{x} \\in M$ existiert, sodass $\\inf_{x \\in M} f(x) = f(\\bar{x})$.

Bitte achte darauf, dass alle Einträge in ähnlichem Stil präsentiert werden und die wesentlichen mathematischen Aspekte klar hervorgehoben werden.""",
        model='gpt-4-turbo',
        tools=[{'type': 'file_search'}],
    )

    for chunk in chunks:
        # Upload the user provided file to OpenAI
        message_file = client.files.create(file=open(chunk, 'rb'), purpose='assistants')

        # Create a thread and attach the file to the message
        thread = client.beta.threads.create(
            messages=[
                {
                    'role': 'user',
                    'content': """Ich möchte, dass du aus der beigefügten PDF-Datei alle wichtigen mathematischen Inhalte extrahierst, einschließlich Definitionen, Formeln, Lemmas und Sätze. Verwende Rich Markdown für die Formatierung und LaTeX für die mathematischen Formeln. Bitte orientiere dich am Format der Beispiele für Epigraph und Lösbarkeit, die ich dir gegeben habe. Die Informationen sollen so aufbereitet werden, dass sie für jemanden, der mit dem Thema bereits vertraut ist, als effiziente Zusammenfassung dienen können.""",
                    # Attach the new file to the message.
                    'attachments': [
                        {
                            'file_id': message_file.id,
                            'tools': [{'type': 'file_search'}],
                        }
                    ],
                }
            ]
        )

        with client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            tool_choice='required',
        ) as stream:
            stream.until_done()
