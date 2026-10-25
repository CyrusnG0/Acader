import { APP_TITLE } from './title';
import { renderGallery } from './receipt/gallery';
import type { GoldenGallery } from './receipt/types';

document.title = APP_TITLE;
const app=document.querySelector<HTMLElement>('#app');
if(app){fetch('/review/golden-receipts.json').then(response=>{if(!response.ok)throw new Error('Review data unavailable');return response.json() as Promise<GoldenGallery>}).then(data=>renderGallery(data,app)).catch(()=>{const title=document.createElement('h1');title.textContent='The Writing Room';const message=document.createElement('p');message.textContent='Review data is not ready. Run npm run review:receipts from prototype/web to prepare the synthetic gallery.';app.replaceChildren(title,message)})}
