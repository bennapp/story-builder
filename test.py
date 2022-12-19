from cProfile import run
import os
import urllib.request
import json
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_story_text(pages, story_prompt):
  story_prompt_command = f"Tell me a {pages} paragraph short story about: {story_prompt}"
  response = openai.Completion.create(model="text-davinci-003", prompt=story_prompt_command, temperature=0.7, max_tokens=400)
  text = response["choices"][0]["text"]
  print(text)
  return text

def create_story_title(story_full_text):
  story_title_command = f"create a creative, clever, and short title for the following story: ${story_full_text}"
  response = openai.Completion.create(model="text-davinci-003", prompt=story_title_command, temperature=0.9, max_tokens=40)
  text = response["choices"][0]["text"]
  print(text)
  return text

def get_story_parts_from(story):
  story_parts = story.split("\n\n")
  if not len(story_parts[0]):
    story_parts.pop(0)
  
  return story_parts

def create_page_summary(page_text):
  summary_command = f"describe an image of: ${page_text}"
  response = openai.Completion.create(model="text-davinci-003", prompt=summary_command, temperature=0.05, max_tokens=80)
  text = response["choices"][0]["text"]
  print(text)
  return text

def create_character_summary(story_prompt):
  summary_command = f"in short full sentances, what are the names of the characters in: ${story_prompt}?"
  response = openai.Completion.create(model="text-davinci-003", prompt=summary_command, temperature=0.0, max_tokens=30)
  text = response["choices"][0]["text"]
  print(text)
  return text

def generate_images_from(run_name, story_parts, character_summary, art_style):
  for i, page_text in enumerate(story_parts):
    summary = create_page_summary(page_text)
    response = openai.Image.create(
      prompt=f'{art_style} style: {summary} where {character_summary}',
      n=1,
      size="1024x1024"
    )
    image_url = response['data'][0]['url']
    urllib.request.urlretrieve(image_url, f'{run_name}/{i}.jpg')

def generate_cover_image(run_name, story_title, character_summary, art_style):
  summary = create_page_summary(story_title)
  response = openai.Image.create(
    prompt=f'{art_style} style: {summary} where {character_summary}',
    n=1,
    size="1024x1024"
  )
  image_url = response['data'][0]['url']
  urllib.request.urlretrieve(image_url, f"{run_name}/cover.jpg")

def write_story_to_file(run_name, story_title, story_parts, art_style):
  if not os.path.exists(run_name):
    os.makedirs(run_name)
  
  story_dict = { "title": story_title, "pages": story_parts, "art_style": art_style, "run_name": run_name }
  jsonString = json.dumps(story_dict)
  jsonFile = open(f"{run_name}/story.json", "w")
  jsonFile.write(jsonString)
  jsonFile.close()

def create_story(run_name, story_prompt, pages, art_style):
  if not os.path.exists(run_name):
    os.makedirs(run_name)

  character_summary = create_character_summary(story_prompt)
  story_full_text = create_story_text(pages, story_prompt)
  story_parts = get_story_parts_from(story_full_text)

  story_title = create_story_title(story_full_text)
  write_story_to_file(run_name, story_title, story_parts, art_style)
  generate_cover_image(run_name, story_title, character_summary, art_style)
  generate_images_from(run_name, story_parts, character_summary, art_style)

run_name = 'fox-story'
pages = '6'
story_prompt = "a quick brown fox named Speedy that hops over a lazy boy named Ben. They become friends and the fox teaches the boy to be quick."
art_style = 'vintage illustration'

run_name = 'grinch'
story_prompt = 'the Grinch, who is a green fuzzy monster is back to steal Christmas again but this time with his red fuzzy monster sister, the Granch. They learn that its not worth it to steal Christmas becase what is important is family. They learn this from a little girl named Suzy.'
pages = '8',
art_style = 'Dr. Seuss'


create_story(run_name, story_prompt, pages, art_style)

# Testing:
# story_full_text = "\n\nOnce upon a time, there was a quick brown fox that lived in a nearby forest. Every day, the fox would go on a long journey to explore the world. One day, while on his travels, the fox stumbled upon a lazy boy who was lying in the grass. The fox was intrigued by the boy, and he decided to hop closer to take a better look.\n\nThe boy was surprised to see the fox, but he was also curious. He asked the fox why he was so quick and why he was hopping around. The fox smiled and told the boy that he was always on the move and that he enjoyed hopping to get around. The boy found this fascinating and asked the fox to teach him how to move quickly.\n\nThe fox was delighted to have a new friend, and he agreed to teach the boy. Every day, the fox would take the boy on a new adventure and teach him how to move quickly. The fox would demonstrate different techniques and show the boy how to move efficiently.\n\nThe boy was a quick learner and soon he was able to keep up with the fox. He was amazed at how much faster he could move and he was excited to explore the world with his new friend.\n\nThe fox and the boy became great friends and they would often go on adventures together. The boy was always eager to learn and he was grateful for the fox's guidance.\n\nThe fox and the boy continued to explore the world together for many years. The boy had learned how to be quick and he was no longer lazy. The fox was proud of his friend and he was happy to have someone to share his adventures with."
# story_title = "The Fox and the Speedy Boy: A Tale of Quickening Friendship"
# page_text = "Once upon a time, there lived a quick brown fox named Speedy. He was very fast and loved to run. One day, he was hopping through the forest when he came across a lazy boy named Ben. Ben was lying on the ground, taking a nap in the shade of a tree."
# create_page_summary(page_text)
# "In the image, Speedy is standing in front of Ben with his hands on his hips. He has a determined look on his face and is wearing a bright red tracksuit. Ben is standing a few feet away, looking up at Speedy with a look of admiration and concentration. He is wearing a blue t-shirt and shorts, and his feet are planted firmly on the ground."
# create_character_summary(story_prompt)
# write_story_to_file('test', 'just a test', ['1', '2'], 'dope')