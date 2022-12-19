import React, { useState } from 'react';
import './App.css';
import storyJson from './story/story.json'
import cover from './story/cover.jpg'

function importAll(r) {
  let images = {};
  r.keys().forEach((item, index) => { images[item.replace('./', '')] = r(item); });
  return images
}

const images = importAll(require.context('./story', false, /\.(png|jpe?g|svg)$/));

console.log(images)

function App() {
  const [pageIndex, setPageIndex] = useState(-1);
  const isEnd = pageIndex === Object.keys(images).length - 1;

  return (
    <div className='wrapper'>
      <h1>{pageIndex === -1 ? storyJson.title : isEnd ? 'End' : '' }</h1>
      <img className='story-image' src={pageIndex === -1 ? cover : images[`${pageIndex}.jpg`]}></img>
      <div style={{ marginTop: '8px' }}>
        { pageIndex !== -1 && (<button onClick={() => { setPageIndex(pageIndex - 1) }}>⬅️</button>) }
        { !isEnd && (<button onClick={() => { setPageIndex(pageIndex + 1) }}>➡️</button>) }
      </div>
      <p className='story-text'>{storyJson.pages[pageIndex]}</p>
    </div>
  );
}

export default App;