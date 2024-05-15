import os
import re
import openai
import PyPDF2
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from settings import (
    OPENAI_API_KEY,
    PATH_TO_PDF,
    PAGES_PER_CHUNK,
    INITIAL_PAGES_TO_SKIP,
    SYSTEM_PROMPT,
    USER_PROMPT,
    OUTPUT_DIR,
    MAX_WORKERS,
)

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def split_pdf_into_chunks(
    pdf_path: str,
    pages_per_chunk: int = 10,
    initial_pages_to_skip: int = 0,
) -> list[str]:
    chunks = []
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        total_pages = len(reader.pages)

        for start in range(initial_pages_to_skip, total_pages, pages_per_chunk):
            writer = PyPDF2.PdfWriter()
            end = min(start + pages_per_chunk, total_pages)

            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            chunk_filename = f'{pdf_path[:-4]}_chunk_{start//pages_per_chunk + 1}.pdf'
            with open(chunk_filename, 'wb') as output_pdf:
                writer.write(output_pdf)

            chunks.append(chunk_filename)

    return chunks


def extract_from_file(assistant_id: str, file_path: str, retries: int = 1) -> str:
    # Upload the user provided file to OpenAI
    message_file = client.files.create(
        file=open(file_path, 'rb'),
        purpose='assistants',
    )

    # Create a thread and attach the file to the message
    thread = client.beta.threads.create(
        messages=[
            {
                'role': 'user',
                'content': USER_PROMPT,
                'attachments': [
                    {
                        'file_id': message_file.id,
                        'tools': [{'type': 'file_search'}],
                    }
                ],
            }
        ]
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        tool_choice='required',
    )

    if run.status != 'completed':
        print('Run not completed.', file_path, 'Status:', run.status, 'Error:', run.last_error)
        if retries > 0:
            print('Retrying...')
            return extract_from_file(assistant_id, file_path, retries - 1)
        else:
            print('Retries exhausted. Exiting...')
            exit(1)

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    message_content = messages[0].content[0].text.value  # type: ignore
    # delete citations of the style: "【SOURCE】"
    message_content = re.sub(r'【.*?】', '', message_content)
    return message_content


if __name__ == '__main__':
    print('Splitting PDF into chunks...')
    chunks = split_pdf_into_chunks(
        PATH_TO_PDF,
        pages_per_chunk=PAGES_PER_CHUNK,
        initial_pages_to_skip=INITIAL_PAGES_TO_SKIP,
    )
    print('Done splitting PDF into chunks.')
    print('Creating assistant...')

    assistant = client.beta.assistants.create(
        name='Extraction Assistant',
        instructions=SYSTEM_PROMPT,
        model='gpt-4-turbo',
        tools=[{'type': 'file_search'}],
    )

    print('Assistant created.')

    # Initialize list to hold content from each chunk
    results = [''] * len(chunks)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Map each chunk to a future object
        future_to_index = {executor.submit(extract_from_file, assistant.id, chunk): i for i, chunk in enumerate(chunks)}

        # As each future completes, place result at correct index
        for future in future_to_index:
            index = future_to_index[future]
            results[index] = future.result()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    # Write all results to file, maintaining original order
    with open(f'{OUTPUT_DIR}/{now}.md', 'w') as f:
        f.write(f'# Extraction from {PATH_TO_PDF}\n\n')
        for result in results:
            f.write(result + '\n\n--- END OF EXTRACTION ---\n\n')
            f.flush()

    print('All chunks processed and saved in order.')
