fetch(`./grinch/story.json`);
document.getElementById('title').textContent = story_json.title;
