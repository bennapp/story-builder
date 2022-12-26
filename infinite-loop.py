import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def create_text_repsone(input_text):
  response = openai.Completion.create(model="text-davinci-003", prompt=input_text, temperature=0.5, max_tokens=40)
  print(response)
  text = response["choices"][0]["text"]
  text = text.replace("\n", "")
  print(text)
  return text


create_text_repsone('My favorite horses name is Biscuit. Could you tell me a funny joke about Biscuit')
create_text_repsone('What is my favorite horses name?')
