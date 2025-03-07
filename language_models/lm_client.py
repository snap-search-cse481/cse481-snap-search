import dspy
import google.generativeai as genai
import json
import re
import sys
from typing import Optional, List, Dict, Any

class GeminiClient:
    dummy_prompt: str = "You are a helpful assistant."
    filter_summarize_prompt: str = "You are an assistant specialized in extracting and summarizing factual information from provided text excerpts. Your task is to read the given excerpts from various websites and determine which individual is mentioned most frequently, assuming this is the person of interest. Then, using only the information provided in the texts, provide a concise, factual summary about this person. If some sources do not contain relevant details, simply ignore them and focus on those that do. It is critical that you strictly adhere to the provided excerpts, avoid making up any details, and clearly indicate any ambiguities if present. Focus on the basics of a person profile, like the persons's name, job, etc. Keep your summary concise and under 100 words."

    def __init__(self,
                 api_key: str = "AIzaSyBGmTP8OCrfNXydpQjZxI_OL2VX9XC_VfY",
                 model: str = 'gemini-1.5-pro',
                 system_prompt: Optional[str] = None,
                 custom_name: Optional[str] = None):
        try:
            # Configure Gemini API
            genai.configure(api_key=api_key)
            self.model_name = model
            self.system_prompt = system_prompt
            self.custom_name = custom_name

            # Create a generation config to use
            self.generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            # Initialize the Gemini model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=self.generation_config,
                system_instruction=system_prompt if system_prompt else self.dummy_prompt
            )
            
            # For DSPy, we'll use a generic LM interface instead of GeminiLM
            # We're skipping direct DSPy integration since there's no native GeminiLM
            # We'll use the Gemini API directly for our tasks
            
            print(f"Initialized GeminiClient with model: {self.model_name}")
            
        except Exception as e:
            raise ConnectionError(f"Could not initialize Gemini API: {e}")

    # Query method for interactive use
    def query_lm(self, query: str = 'Who are you?'):
        try:
            response = self.model.generate_content(query)
            if response:
                print(response.text)
            else:
                print("Empty response received")
        except Exception as e:
            print(f"Error querying Gemini: {e}")

    # Method for structured extraction using Gemini without relying on DSPy
    def extract_person_info(self, text: str) -> Dict[str, Any]:
        """Extract structured person information using Gemini"""
        
        # First, identify the person's name
        identify_prompt = f"""
        Based on the following text, identify the full name of the person who is mentioned most frequently or seems to be the main subject.
        
        Text: {text}
        
        Return ONLY the full name, nothing else.
        """
        
        try:
            name_response = self.model.generate_content(identify_prompt)
            person_name = name_response.text.strip() if name_response else "Unknown Person"
            
            # Then use Gemini for structured information extraction
            extract_prompt = f"""
            Based on the following text, extract structured information about {person_name}.
            Text: {text}
            
            Provide a JSON object with the following fields:
            - name: Full name
            - profession: Current job or profession
            - workplace: Current workplace or affiliation
            - email: Email address of person looking for
            - phone: Phone number of person looking for
            - fun_facts: A list of 3-5 interesting facts strictly about the person
            
            If any field is not available in the text, leave it blank or empty list for fun_facts.
            Format your response ONLY as valid JSON with these exact field names.
            """
            
            # Use Gemini directly for structured response
            response = self.model.generate_content(extract_prompt)
            response_text = response.text if response else ""
            
            # Extract JSON part from response
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no json code block, try to find anything that looks like a JSON object
                json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text
            
            # Try to parse the JSON
            person_data = json.loads(json_str)
            return person_data
            
        except Exception as e:
            # If extraction fails, return a structured dict with the error
            print(f"Error extracting person information: {e}")
            return {
                "name": person_name if 'person_name' in locals() else "Unknown",
                "profession": "",
                "workplace": "",
                "email": "",
                "phone": "",
                "fun_facts": ["Information extraction failed"],
                "error": str(e),
                "raw_response": response_text if 'response_text' in locals() else "No response received"
            }

    # Additional method for summarizing a person from text
    def summarize_person(self, text: str) -> str:
        """Summarize information about the most mentioned person in the text"""
        prompt = f"""
        {self.filter_summarize_prompt}
        
        Text: {text}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response else "No summary generated"
        except Exception as e:
            return f"Error generating summary: {e}"

if __name__ == '__main__':
    client = GeminiClient()
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        
        # Using improved extraction
        result = client.extract_person_info(input_text)
        
        # Formatting the output
        print(f"Name: {result.get('name', '')}")
        print(f"Profession: {result.get('profession', '')}")
        print(f"Workplace: {result.get('workplace', '')}")
        print(f"Email: {result.get('email', '')}")
        print(f"Phone: {result.get('phone', '')}")
        print(f"Fun Facts:")
        for fact in result.get('fun_facts', []):
            print(f"- {fact}")

    else:
        # Fallback to original query method
        client.query_lm()