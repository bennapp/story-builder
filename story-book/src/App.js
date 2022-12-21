import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import storyJson from './story/story.json'
import cover from './story/cover.png'

function importAll(r) {
  let images = {};
  r.keys().forEach((item, index) => { images[item.replace('./', '')] = r(item); });
  return images
}

const images = importAll(require.context('./story', false, /\.(png|jpe?g|svg)$/));

function App() {
  const [pageIndex, setPageIndex] = useState(-1);
  const isEnd = pageIndex === Object.keys(images).length - 1;

  const handleUserKeyPress = useCallback(event => {
    const { keyCode } = event;
    if (keyCode === 37 && pageIndex !== -1) {
      setPageIndex(pageIndex - 1);
    } else if (keyCode === 39) {
      isEnd ? setPageIndex(-1) : setPageIndex(pageIndex + 1);
    }
  }, [pageIndex, isEnd]);

  useEffect(() => {
    window.addEventListener("keydown", handleUserKeyPress);
    return () => {
      window.removeEventListener("keydown", handleUserKeyPress);
    };
  }, [handleUserKeyPress]);

  return (
    <div className='wrapper'>
      <h1>{pageIndex === -1 ? storyJson.title : isEnd ? 'End' : '' }</h1>
      <img className='story-image' src={pageIndex === -1 ? cover : images[`${pageIndex}.png`]}></img>
      <div style={{ marginTop: '8px' }}>
        { pageIndex !== -1 && (<button onClick={() => { setPageIndex(pageIndex - 1) }}>⬅️</button>) }
        <button onClick={() => { isEnd ? setPageIndex(-1) : setPageIndex(pageIndex + 1) }}>➡️</button>
      </div>
      <p className='story-text'>{storyJson.pages[pageIndex]}</p>
    </div>
  );
}

export default App;
