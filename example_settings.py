OPENAI_API_KEY = 'sk-1234567890abcdefghijklmnopqrstuvwxyz'  # Replace with your OpenAI API key
PATH_TO_PDF = 'path_to_your_pdf.pdf'  # Replace with the path to your PDF file

PAGES_PER_CHUNK = 10
INITIAL_PAGES_TO_SKIP = 3
LAST_PAGES_TO_SKIP = 7

MODEL_ID = 'gpt-4o-mini'

OUTPUT_DIR = 'output'
MAX_WORKERS = 10  # Don't set this too large as you might run into rate limits

SYSTEM_PROMPT = """Bitte extrahiere aus der angegebenen PDF-Datei alle wesentlichen Definitionen, Formeln, Lemmas und Sätze. Das Output-Format soll Rich Markdown sein und die Formeln sollen in LaTeX eingefügt werden. Die Extraktion soll kompakt und präzise erfolgen, unter der Annahme, dass der Nutzer bereits mit dem Stoff vertraut ist. Ziel ist es, eine klare und prägnante Zusammenfassung zu bieten, die als schnelles Nachschlagewerk für jemanden dienen kann, der mit den Konzepten bereits vertraut ist. Dementsprechend sollte die Zusammenfassung auf das Wesentliche reduziert sein und unnötige Details vermeiden. Beispiele und Übungen sind nicht erforderlich.

Das Format soll eine Auflistung von Einträgen im folgenden Format sein, jeweils getrennt durch '\n\n---\n\n':

{Identifikationsnummer} **{Name}**
{Intuituv verständliche, kurze Beschreibung}
Formal: {Formel oder Definition in LaTeX}
 
Als Beispiel für das gewünschte Format sieh dir die folgenden Einträge an:

1.1.6 **Epigraph**  
Der Epigraph besteht aus dem Graphen von f auf X sowie allen darüberliegenden Punkten.  
Formal: $\\text{epi}(f, X) = \\{(x, \\alpha) \\in X \\times \\mathbb{R} \\mid f(x) \\leq \\alpha\\}$

---

1.2.3 **Lösbarkeit**  
Ein Minimierungsproblem ist lösbar, wenn das Infimum der Zielfunktion auf der zulässigen Menge tatsächlich angenommen wird.  
Formal: Ein Problem ist lösbar, wenn ein $\\bar{x} \\in M$ existiert, sodass $\\inf_{x \\in M} f(x) = f(\\bar{x})$.

Bitte achte darauf, dass alle Einträge in diesem Stil präsentiert werden und die wesentlichen mathematischen Aspekte klar hervorgehoben werden."""
USER_PROMPT = """Ich möchte, dass du aus der beigefügten PDF-Datei alle wichtigen mathematischen Inhalte extrahierst, einschließlich Definitionen, Formeln, Lemmas und Sätze. Verwende Rich Markdown für die Formatierung und LaTeX für die mathematischen Formeln. Bitte orientiere dich am Format der Beispiele für Epigraph und Lösbarkeit, die ich dir gegeben habe. Die Informationen sollen so aufbereitet werden, dass sie für jemanden, der mit dem Thema bereits vertraut ist, als effiziente Zusammenfassung dienen können."""
