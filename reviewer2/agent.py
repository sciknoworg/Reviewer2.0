from typing import Annotated
from langchain_core.tools import tool
import pandas as pd
import os
import json
import re

import os
import ssl
import certifi

# Point Python SSL to certifi's CA bundle
os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

import re
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import time

_ = load_dotenv(find_dotenv())

client = OpenAI(api_key=os.environ['OPENAI_KEY'])

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    

@tool
def paper_tool(
    file_bytes: Annotated[bytes, "Raw uploaded file bytes"],
    filename: Annotated[str, "Filename including extension"]
):
    """Load a PDF or JSON paper and return it in Markdown format."""
    try:
        # Detect file type
        is_pdf = filename.lower().endswith(".pdf")
        is_json = filename.lower().endswith(".json")

        if not (is_pdf or is_json):
            return "Unsupported file type. Only PDF or JSON allowed."

        # If PDF → extract text → convert to markdown
        if is_pdf:
            paper = ""

        # If JSON → load + convert to markdown
        if is_json:
            try:
                data = json.loads(file_bytes)
                paper = data['markdown']
            except Exception as e:
                return f"JSON processing error: {repr(e)}"

    except Exception as e:
        return f"Failed to execute. Error: {repr(e)}"

    return paper #f"Successfully executed:\nThe paper in markdown format: {paper}"

@tool
def paper_sectioning_tool(
    md: Annotated[str, "Paper in markdown format"]
):
    """ Parse the paper into sections"""
    try:
        heading_re = re.compile(
            r'(?ms)^(?P<level>#{1,6})\s*(?P<title>.+?)\s*$\n(?P<body>.*?)(?=(?:\n^#{1,6}\s)|\Z)',
            re.MULTILINE | re.DOTALL
        )        
        sections = []
        for m in heading_re.finditer(md):
            level = len(m.group('level'))
            title = m.group('title').strip()
            body = m.group('body').rstrip()
            sections.append({'level': level, 'title': title, 'body': body})

        headers = "\n"
        for idx, section in enumerate(sections):
            headers += f"""{idx+1} : {section['title']}
    """
    except Exception as e:
        return f"Failed to execute. Error: {repr(e)}"
    
    return {"headers": headers, "sections": sections}#f"Successfully executed:\nThe paper with headers: {headers}\nThe paper with sections: {sections}"
    

def call_openai(messages, model, function, temperature=0):
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                functions=function
            )
            return eval(response.choices[0].message.function_call.arguments)
        except:
            print("sleep for 5 seconds")
            time.sleep(5)
            
@tool
def extract_section_tool(
    sections: Annotated[list, "List of sections"],
    headers: Annotated[str, "Section headers"],
    section: Annotated[str, "Desired section"],
):
    """Extract desired section of a paper."""
    try:
        function = [
            {
                "name": "desired_section",
                "description": f"Identify which header corresponds to the '{section}' section.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "section": {
                            "type": "string",
                            "description": f"ID of the {section} section."
                        }
                    },
                    "required": ["section"]
                }
            }
        ]
        
        prompt = f"""
        You are given a list of headers from an academic paper:
        {headers}
    
        Identify which header corresponds to the "{section}" section. 
        Return the answer in this format: {{ "section": section-ID}}"""
        messages=[{"role": "user", "content": prompt}]
        section_idx =  call_openai(messages=messages, model="gpt-4.1-mini", function=function, temperature=0)['section']
        section_raw = sections[int(section_idx)-1] 
        
        prompt = f"""
        Identify the section {section} text from:

        {section_raw}
        
        Return the answer in this format: {{ "text": "section text..."}} 
        """
        
        function = [
            {
                "name": "desired_section",
                "description": f"Identify the '{section}' section text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": f"section {section} text."
                        }
                    },
                    "required": ["text"]
                }
            }
        ]
        messages=[{"role": "user", "content": prompt}]
        text =  call_openai(messages=messages, model="gpt-4.1-mini", function=function, temperature=0)['text']
        
    except Exception as e:
        return f"Failed to execute. Error: {repr(e)}"
    
    return text #f"Successfully executed:\nThe paper with {section} is: {text} "


    


    