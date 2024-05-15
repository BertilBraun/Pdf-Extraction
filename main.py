from datetime import datetime
import os
import re
import openai
import PyPDF2


from settings import (
    OPENAI_API_KEY,
    PATH_TO_PDF,
    PAGES_PER_CHUNK,
    INITIAL_PAGES_TO_SKIP,
    SYSTEM_PROMPT,
    USER_PROMPT,
    OUTPUT_DIR,
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
    print('Processing File...')
    # Upload the user provided file to OpenAI
    message_file = client.files.create(
        file=open(file_path, 'rb'),
        purpose='assistants',
    )

    print('Creating Thread...')

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

    print('Thread created. Starting assistant...')

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        tool_choice='required',
    )

    if run.status != 'completed':
        print('Run not completed.', run.status, run.last_error)
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
    print('Done splitting PDF into chunks. Now creating assistant...')

    assistant = client.beta.assistants.create(
        name='Extraction Assistant',
        instructions=SYSTEM_PROMPT,
        model='gpt-4-turbo',
        tools=[{'type': 'file_search'}],
    )

    print('Assistant created. Now uploading chunks...')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    with open(f'{OUTPUT_DIR}/{now}.md', 'w') as f:
        f.write(f'# Extraction from {PATH_TO_PDF}\n\n')

        for chunk in chunks:
            content = extract_from_file(assistant.id, chunk)
            print(content)
            f.write(content + '\n\n--- END OF EXTRACTION ---\n\n')
            f.flush()
