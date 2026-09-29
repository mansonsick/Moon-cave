// Percent-based coordinates share one uncropped canvas in portrait and landscape.
// Decorative layers never intercept a story's touch targets.
export function sceneLayers({background, layers = [], baseURL, label = ''}) {
  const stage = document.createElement('div');
  stage.className = 'scene-stage'; stage.setAttribute('aria-label', label);
  const add = ({id, src, box = [0,0,100,100], z = 0, className = ''}) => {
    const image = document.createElement('img');
    image.src = new URL(src, baseURL); image.alt = ''; image.draggable = false;
    image.className = `scene-layer ${className}`; image.dataset.layer = id;
    const [x,y,w,h] = box;
    Object.assign(image.style,{left:`${x}%`,top:`${y}%`,width:`${w}%`,height:`${h}%`,zIndex:z});
    stage.append(image); return image;
  };
  add({id:'background',src:background,className:'scene-background'});
  for (const layer of layers) add(layer);
  return stage;
}
