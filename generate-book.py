import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import urllib.request
import json
import shutil
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-v1-5",
)

def create_openai_image(prompt, file_name):
  response = openai.Image.create(
    prompt=prompt,
    n=1,
    size="1024x1024"
  )
  image_url = response['data'][0]['url']
  urllib.request.urlretrieve(image_url, file_name)

def create_stability_image(prompt, file_name):
  answers = stability_api.generate(
    prompt=prompt,
    cfg_scale=9.0,
    sampler=generation.SAMPLER_K_DPMPP_2M
  )

  for resp in answers:
    for artifact in resp.artifacts:
      if artifact.finish_reason == generation.FILTER:
        warnings.warn("prompt has saftey violation")
      if artifact.type == generation.ARTIFACT_IMAGE:
          global img
          img = Image.open(io.BytesIO(artifact.binary))
          img.save(file_name)

def create_image(prompt, file_name, api):
  if api == 'openai':
    create_openai_image(prompt, file_name)
  else:
    create_stability_image(prompt, file_name)

def create_story_text(pages, story_prompt):
  story_prompt_command = f"Tell me a {pages} paragraph short story about: {story_prompt}"
  response = openai.Completion.create(model="text-davinci-003", prompt=story_prompt_command, temperature=0.7, max_tokens=400)
  text = response["choices"][0]["text"]
  print(text)
  return text

def create_story_title(story_full_text):
  story_title_command = f"create an exciting, creative, clever, and short title for the following story: ${story_full_text}"
  response = openai.Completion.create(model="text-davinci-003", prompt=story_title_command, temperature=0.9, max_tokens=40)
  text = response["choices"][0]["text"]
  text = text.replace("\n", "")
  print(text)
  return text

def get_story_parts_from(story):
  story_parts = story.split("\n\n")
  if not len(story_parts[0]):
    story_parts.pop(0)
  
  return story_parts

def create_page_summary(page_text, character_summary):
  for name, description in character_summary.items():
    page_text = page_text.replace(name, description)
  summary_command = f"describe an image of: {page_text}"
  print(summary_command)
  response = openai.Completion.create(model="text-davinci-003", prompt=summary_command, temperature=0.00, max_tokens=80)
  text = response["choices"][0]["text"]
  print(text)
  return text

def character_dict_from(text):
  character_summary = {}
  for description_string_with_newline in text.split('.'):
    description_string = description_string_with_newline.replace('\n', '')
    if len(description_string):
      character_and_description = description_string.split(': ')
      name = character_and_description[0]
      description = character_and_description[1]
      character_summary[name] = description

  return character_summary

def create_character_summary(story_prompt):
  summary_command = f"describe each character visually, what kind of creature they are, and do not include their names in the description. Return the answer in the following format, name: <description> for this prompt: ${story_prompt}?"
  response = openai.Completion.create(model="text-davinci-003", prompt=summary_command, temperature=0.2, max_tokens=120)
  text = response["choices"][0]["text"]
  print(text)
  charact_dict = character_dict_from(text)
  print(charact_dict)
  return charact_dict

def generate_images_from(run_name, story_parts, character_summary, art_style, api):
  for i, page_text in enumerate(story_parts):
    summary = create_page_summary(page_text, character_summary)
    prompt = f'as {art_style} style, {summary}'
    file_name = f'{run_name}/{i}.png'
    create_image(prompt, file_name, api)

def generate_cover_image(run_name, story_title, character_summary, art_style, api):
  summary = create_page_summary(story_title, character_summary)
  prompt = f'as {art_style} style, {summary}'
  file_name = f"{run_name}/cover.png"
  create_image(prompt, file_name, api)

def write_story_to_file(run_name, story_title, story_parts, art_style):
  if not os.path.exists(run_name):
    os.makedirs(run_name)
  
  story_dict = { "title": story_title, "pages": story_parts, "art_style": art_style, "run_name": run_name }
  jsonString = json.dumps(story_dict)
  jsonFile = open(f"{run_name}/story.json", "w")
  jsonFile.write(jsonString)
  jsonFile.close()

def view_run(run_name):
  shutil.rmtree('./story-book/src/story')
  os.makedirs('./story-book/src/story')
  shutil.copytree(f'./{run_name}', './story-book/src/story', dirs_exist_ok=True)

## run_name let's you keep the files generated for previous runs, it just places them in a folder named by the `run_name` param
def create_story(run_name, story_prompt, pages, art_style, api='openai'):
  if not os.path.exists(run_name):
    os.makedirs(run_name)

  character_summary = create_character_summary(story_prompt)
  story_full_text = create_story_text(pages, story_prompt)
  story_parts = get_story_parts_from(story_full_text)

  story_title = create_story_title(story_full_text)
  write_story_to_file(run_name, story_title, story_parts, art_style)
  generate_cover_image(run_name, story_title, character_summary, art_style, api)
  generate_images_from(run_name, story_parts, character_summary, art_style, api)
  view_run(run_name)

run_name = 'fox-story'
pages = '6'
story_prompt = "a quick brown fox named Speedy that hops over a lazy boy named Ben. They become friends and the fox teaches the boy to be quick."
art_style = 'vintage illustration'

run_name = 'grinch'
story_prompt = 'the Grinch, who is a green fuzzy monster is back to steal Christmas again but this time with his red fuzzy monster sister, the Granch. They learn that its not worth it to steal Christmas becase what is important is family. They learn this from a little girl named Suzy.'
pages = '8',
art_style = 'Dr. Seuss'
pages = '6'

run_name = 'two-cats-pt2'
story_prompt = "two cats named Coco and Melon who live and are trapped in a girl named Emma's apartment. The two cats, also know as, The girls, break out of the apartment and travel all around the city. But after several crazy adventures they then decide to come home because they miss Emma. Emma is Blonde and beautiful. Coco is white, fluffy with green eyes, and is playful. Melon is siamese, has silver boots, and is lazy and cautious."
art_style = 'soft water color smooth air brushed'

run_name = 'simpsons'
story_prompt = "murder mystery episode of the simpsons. Everyone in the town thinks it was bart, but then because something you decide happens everyone thinks it was Mr. Burns. Homer is really mad a bart. Everyone eventually finds out it was Side show Bob"
art_style = 'blair witch project'

run_name = 'dota bros'
story_prompt = "There are four childhood friends, Hoagiez, Benjammin', Beezkneez, and QuailmanX, who play a computer game called Dota 2. Later in life, they still play Dota 2 together. now they are old boomers and their reaction times are slow; one day they have an epic 120 min game that they lose"
art_style = 'dota 2 fantasy anime'
pages = '8'

run_name = 'hpc-splay'
story_prompt = "Dobby, who is a greedy house elf, and his loyal sidekick Scabbers, who is a dirty rat, win a trip to Mar-a-Lago to meet former 45th President after buying Presidential Collection Digital Trading Cards and learn what really happened in the election through a School House Rock-style sing-along"
pages = '7'
art_style = "canon 35 mm at f / 5.6 lens color"

run_name ="blbsr"
story_prompt = "Lady Whistledown like story of Republican Senator man named Teddy, and Democrat speaker of the House Women named Nancy, secret romance in Bridgerton after they flee from Washington DC together in a romantic get away with lots of danger and other scary things"
pages = '5'
art_style = 'horror'

run_name = 'hpc-splay-2'
story_prompt = "Dobby and his loyal sidekick Scabbers win a trip to Mar-a-Lago to meet former 45th President after buying 45th Presedential themed NFTs and learn what really happened in the 2020 election through a School House Rock-style sing-along"
pages = '7'
art_style = "pixar"

run_name = 'bluetiful'
story_prompt = "a story about a crayon named Bluetiful who is not the sharpest crayon in the box. he grows up struggling to be like the other crayon kids. they make fun of him, and call him names. he is bullied by a crayon named Sea Green and a crayon named Tumbleweed. finally he learns he becomes the brightest crayon and learns to overcome the bullies"
pages = '5'
art_style = "crayon"

api = 'stability'

run_name = 'hpc-splay-3'
story_prompt = "Dobby and his loyal sidekick Scabbers win a trip to Mar-a-Lago to meet former 45th President after buying 45th Presedential themed NFTs and learn what really happened in the 2020 election through a School House Rock-style sing-along"
pages = '6'
art_style = "pixar"

run_name = 'two-cats-pt3'
story_prompt = "two cats named Coco and Melon who live and are trapped in a girl named Emma's apartment. The two cats, also know as, The girls, break out of the apartment and travel all around the city. But after several crazy adventures they then decide to come home because they miss Emma. Emma is Blonde and beautiful. Coco is white, fluffy with green eyes, and is playful. Melon is siamese, has silver boots, and is lazy and cautious."
art_style = 'soft water color smooth air brushed'

run_name = 'hpc-splay-original-stability'
story_prompt = "Dobby, who is a greedy house elf, and his loyal sidekick Scabbers, who is a dirty rat, win a trip to Mar-a-Lago to meet former 45th President after buying Presidential Collection Digital Trading Cards and learn what really happened in the election through a School House Rock-style sing-along"
pages = '7'
art_style = "canon 35 mm at f / 5.6 lens color"

create_story(run_name, story_prompt, pages, art_style, api)

# create_character_summary(story_prompt)

# Testing:
# story_full_text = "\n\nOnce upon a time, there was a quick brown fox that lived in a nearby forest. Every day, the fox would go on a long journey to explore the world. One day, while on his travels, the fox stumbled upon a lazy boy who was lying in the grass. The fox was intrigued by the boy, and he decided to hop closer to take a better look.\n\nThe boy was surprised to see the fox, but he was also curious. He asked the fox why he was so quick and why he was hopping around. The fox smiled and told the boy that he was always on the move and that he enjoyed hopping to get around. The boy found this fascinating and asked the fox to teach him how to move quickly.\n\nThe fox was delighted to have a new friend, and he agreed to teach the boy. Every day, the fox would take the boy on a new adventure and teach him how to move quickly. The fox would demonstrate different techniques and show the boy how to move efficiently.\n\nThe boy was a quick learner and soon he was able to keep up with the fox. He was amazed at how much faster he could move and he was excited to explore the world with his new friend.\n\nThe fox and the boy became great friends and they would often go on adventures together. The boy was always eager to learn and he was grateful for the fox's guidance.\n\nThe fox and the boy continued to explore the world together for many years. The boy had learned how to be quick and he was no longer lazy. The fox was proud of his friend and he was happy to have someone to share his adventures with."
# story_title = "The Fox and the Speedy Boy: A Tale of Quickening Friendship"
# page_text = "Once upon a time, there lived a quick brown fox named Speedy. He was very fast and loved to run. One day, he was hopping through the forest when he came across a lazy boy named Ben. Ben was lying on the ground, taking a nap in the shade of a tree."
# create_page_summary(page_text)
# "In the image, Speedy is standing in front of Ben with his hands on his hips. He has a determined look on his face and is wearing a bright red tracksuit. Ben is standing a few feet away, looking up at Speedy with a look of admiration and concentration. He is wearing a blue t-shirt and shorts, and his feet are planted firmly on the ground."
# create_character_summary(story_prompt)
# write_story_to_file('test', 'just a test', ['1', '2'], 'dope')
# copy_and_overwrite('./grinch', './story-book/story')
# text = create_character_summary(story_prompt)
# character_summary = {'Bluetiful': 'A crayon with a bright blue color, but not the sharpest point.', 'Sea Green': 'A crayon with a light green color, with a sharp point.', 'Tumbleweed': 'A crayon with a light brown color, with a sharp point.'}
# page_text = 'Bluetiful was walking down the streen and ran into Sea Green, who said to him hey there look out for Tumbleweed'
# for name, description in character_summary.items():
#   page_text = page_text.replace(name, description)

# print(page_text)