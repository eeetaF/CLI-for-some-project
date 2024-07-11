import os
import sys
import time
import threading
from typing import List
import textwrap
import warnings
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# ANSI escape codes for colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"

warnings.filterwarnings("ignore")

class S_printer:
    def __init__(self):
        self.frames = []
        for i in range(7):
            with open(f'{script_dir}/cat_typing_{i}.txt', encoding="utf8") as file:
                self.frames.append(file.read())
        self.clear_console_os()
        self.print_static_cat(self.frames[0])
        self.stop_animations = threading.Event()
        self.threads_list = []
        self.current_line = 0
    
    def clear_console_os(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    # Function to print the static cat
    def print_static_cat(self, frame):
        sys.stdout.write('\033[H')  # Move cursor to the top
        for i, line in enumerate(frame.splitlines()):
            sys.stdout.write(f'\033[{i+1};1H{line}')  # Print each line of the frame at the correct position
        sys.stdout.flush()
    
    # question = sp.s_in(f'{RED}Question: {RESET}')
    def s_in(self, string="", height = 1, width = 54):
        self.s_out(string, height, width)
        user_input = input().strip()
        return user_input
    
    def s_out(self, string="", height = 1, width = 54):
        if string == "":
            self.current_line += 1
        else:
            wrapped_string = textwrap.wrap(string, width=90, drop_whitespace=False)  # Adjust width to fit the display
            for _, line in enumerate(wrapped_string):
                sys.stdout.write(f'\033[{self.current_line + height};{width}H{line}')
                self.current_line += 1
        sys.stdout.flush()
    
    def start_animations(self, string="", height = 1, width = 54):
        cat_animation_thread = threading.Thread(target=self.animate_cat, args=())
        cat_animation_thread.start()
        self.threads_list.append(cat_animation_thread)
        if string != "":
            string_animation_thread = threading.Thread(target=self.animate_string, args=(string, height + self.current_line, width))
            string_animation_thread.start()
            self.threads_list.append(string_animation_thread)
            self.current_line += 2
    
    def clear_right_side(self):
        self.current_line = 0
        for i in range(100):
            sys.stdout.write(f'\033[{1 + i};54H{" " * 100}')
        sys.stdout.flush()
    
    def clear_current_line(self):
        sys.stdout.write(f'\033[{1 + self.current_line};54H{" " * 100}')
        sys.stdout.flush()
            
    def stop_all_animations(self):
        self.stop_animations.set()
        for thread in self.threads_list:
            thread.join()
        self.threads_list.clear()
        self.stop_animations.clear()
        self.current_line = 0 if self.current_line < 2 else self.current_line - 2
        self.clear_current_line()

    # Function to animate the cat
    def animate_cat(self, delay=0.12):
        #end_time = time.time() + 5  # Run animation for 5 seconds
        while not self.stop_animations.is_set(): #time.time() < end_time:
            for frame in self.frames:
                sys.stdout.write('\033[H')  # Move cursor to the top
                for i, line in enumerate(frame.splitlines()):
                    sys.stdout.write(f'\033[{i+1};1H{line}')  # Print each line of the frame at the correct position
                sys.stdout.flush()
                time.sleep(delay)

    # Function to handle the string animation
    def animate_string(self, string, height, width):
        #end_time = time.time() + 5  # Run animation for 5 seconds
        animation_frames = [f"{string}   ", f"{string}.  ", f"{string}.. ", f"{string}..."]
        while not self.stop_animations.is_set(): # while time.time() < end_time:
            for frame in animation_frames:
                sys.stdout.write(f'\033[{height};{width}H{GREEN}{frame}{RESET}')
                sys.stdout.flush()
                time.sleep(0.5)
                
def embed_documents(doc, file_type, model_name="BAAI/bge-small-en-v1.5", cache_folder="ragnar/models"):
    if file_type == "md":
        docs = UnstructuredMarkdownLoader(doc).load()
    elif file_type == "pdf":
        docs = PyPDFLoader(doc).load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name=model_name, cache_folder=cache_folder)
    vector = FAISS.from_documents(documents=splits, embedding=embeddings)

    try:
        db = FAISS.load_local("ragnar/vector_db", embeddings, allow_dangerous_deserialization=True)
        db.merge_from(vector)
        db.save_local("ragnar/vector_db")
    except:
        vector.save_local("ragnar/vector_db")

def retrieve(query, chosen_docs, model_name="BAAI/bge-small-en-v1.5", cache_folder="ragnar/models"):
    embeddings = HuggingFaceEmbeddings(model_name=model_name, cache_folder=cache_folder)
    vector = FAISS.load_local("ragnar/vector_db", embeddings, allow_dangerous_deserialization=True)
    retriever = vector.as_retriever(
        search_kwargs={
            "k": 5,
            'fetch_k': 50,
            "filter": lambda doc: doc['source'] in chosen_docs
        }
    )
    return retriever.invoke(query)

def upload_file(sp, folder_path: str):
    embedded_docs = []
    sp.start_animations('loading')
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            try:
                if filename.endswith(".pdf"):
                    embed_documents(file_path, "pdf")
                else:
                    sp.s_out(f"{RED}Missed file:{RESET} {BLUE}{filename}{RESET} (unsupported type)")
                    continue
                sp.s_out(f"{GREEN}File uploaded successfully:{RESET} {BLUE}{filename}{RESET}")
                embedded_docs.append(filename)
            except Exception as e:
                sp.s_out(f"{RED}Error uploading file{RESET} {BLUE}{filename}{RESET}: {e}")
    return embedded_docs
        
def choose_docs(sp, folder, embedded_docs):
    chosen_docs = []
    for i, doc in enumerate(embedded_docs):
        sp.s_out(f"{GREEN}{i+1}{RESET}: {doc}")
    while True:
        sp.s_out("")
        doc_index = sp.s_in(f"Enter the {GREEN}index{RESET} of the document you want to choose (or {CYAN}'all'{RESET}) (or {CYAN}'done'{RESET} to finish): ")
        if doc_index.lower() == "done":
            break
        elif doc_index.lower() == "all":
            chosen_docs = [folder + '/' + doc for doc in embedded_docs]
            sp.s_out(f"{BLUE}All documents{RESET} added to chosen documents.")
            break
        try:
            doc_index = int(doc_index) - 1
            if doc_index < 0 or doc_index >= len(embedded_docs):
                sp.s_out(f"{RED}Invalid index.{RESET} Please try again.")
                continue
            chosen_docs.append(folder + '/' + embedded_docs[doc_index])
            sp.s_out(f"Document {BLUE}{embedded_docs[doc_index]}{RESET} added to chosen documents.")
        except ValueError:
            sp.s_out(f"{RED}Invalid index.{RESET} Please try again.")
    return list(set(chosen_docs))

def ask(sp, query, chosen_docs):
    def format_docs(docs: List[Document]) -> str:
        formatted = [
            f"{BLUE}Article Title:{RESET} {doc.metadata['source'][23:]}\n{BLUE}Article Snippet:{RESET} {' '.join(doc.page_content.split()) + '...'}"
            for doc in docs
        ]
        return formatted

    prompt = PromptTemplate.from_template("""
    You will be provided the user's question and a context. 
    Your task is to answer the user's question based on the context. 
    The response should consist only of the answer to the user's question.
    If there is no answer to the user's question based on the context, you should respond with "I don't know."
    If the response is not relevant to the user's query or the context, you will lose points.

    User's Question: {query}
    Context: {context}
    """)

    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    llm = LlamaCpp(
        model_path="ragnar/models/capybarahermes-2.5-mistral-7b.Q4_K_M.gguf",
        callback_manager=callback_manager,
        n_ctx=2048,
        verbose=False
    )

    llm_chain = prompt | llm
    context = retrieve(query, chosen_docs)
    #formatted = format_docs(context)
    #for doc in formatted:
    #    sp.s_out(f"{doc}")
    #    sp.s_out("")
    sp.s_out("")
    sp.start_animations("Answering question")
    answer = llm_chain.invoke({"query": query, "context": context})
    return answer

def save_answer(sp, answer, folder_path):
    while True:
        filename = sp.s_in(f"Enter the {BLUE}name{RESET} to save the answer file (without extension): ")
        file_path = os.path.join(folder_path, f"{filename}.md")
        if os.path.exists(file_path):
            overwrite = sp.s_in(f"{RED}File already exists.{RESET} Do you want to overwrite it? ({CYAN}y{RESET}/{CYAN}n{RESET}): ")
            if overwrite.lower() == 'y':
                break
        else:
            break
    with open(file_path, "w") as f:
        f.write(f"{answer}\n")
    sp.s_out(f"{GREEN}Answer saved{RESET} as {BLUE}{filename}.md{RESET} in {MAGENTA}{folder_path}{RESET}")
    sp.s_out()
    sp.s_in(f"Press {CYAN}Enter{RESET} to continue... ")

def interact_with_llm(sp, chosen_docs):
    while True:
        sp.clear_right_side()
        query = sp.s_in(f"{MAGENTA}Enter your question{RESET} or {CYAN}'exit'{RESET} to quit or {CYAN}'choose'{RESET} to choose documents again: ")
        if query.lower() == "exit":
            return True
        elif query.lower() == "choose":
            return False
        else:
            sp.clear_right_side()
            sp.s_out(f"{MAGENTA}Question: {RESET}{query}")
            #sp.start_animations("looking in documents")
            answer = ask(sp, query, chosen_docs)
            sp.stop_all_animations()
            time.sleep(0.7)
            sp.s_out(f"{answer}")
            sp.s_out()
            save = sp.s_in(f"Do you want to {GREEN}save{RESET} this answer? ({CYAN}y{RESET}/{CYAN}n{RESET}): ")
            if save.lower() == 'y':
                save_answer(sp, answer, DOCUMENTS_FOLDER)

script_dir = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_FOLDER = os.path.join(script_dir, "documents")

def main():
    sp = S_printer()
    
    embedded_docs = upload_file(sp, DOCUMENTS_FOLDER)
    sp.s_out()
    sp.s_in(f"Press {CYAN}Enter{RESET} to continue... ")
    sp.stop_all_animations()
    while True:
        sp.clear_right_side()
        chosen_docs = choose_docs(sp, DOCUMENTS_FOLDER, embedded_docs)
        sp.s_out()
        sp.s_in(f"Press {CYAN}Enter{RESET} to continue... ")
        if interact_with_llm(sp, chosen_docs):
            sp.clear_console_os()
            return

if __name__ == "__main__":
    main()