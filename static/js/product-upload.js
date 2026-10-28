(() => {
  const form=document.getElementById('product-form');if(!form)return;
  const main=document.getElementById('main-image-input'), gallery=document.getElementById('gallery-file');
  const mainPreview=document.getElementById('main-preview'),galleryPreview=document.getElementById('gallery-preview');
  const errors=document.getElementById('upload-errors');
  const maxMb=Number(document.querySelector('[data-max-mb]').dataset.maxMb||5);
  const allowed=['image/jpeg','image/png','image/webp'];
  let galleryFiles=[];
  const showError=msg=>{errors.textContent=msg;errors.hidden=false;errors.scrollIntoView({behavior:'smooth',block:'nearest'});};
  const clearError=()=>{errors.textContent='';errors.hidden=true;};
  const validate=f=>{
    if(!allowed.includes(f.type))return `${f.name}: Choose JPEG, PNG or WebP.`;
    if(f.size>maxMb*1024*1024)return `${f.name}: Maximum ${maxMb} MB per image.`;
    if(!f.size)return `${f.name}: Empty file.`;
    return null;
  };
  const preview=(file,label,remove)=>{
    const tile=document.createElement('div');tile.className='preview-tile';
    const img=document.createElement('img');img.alt=label;const url=URL.createObjectURL(file);img.src=url;
    img.addEventListener('load',()=>URL.revokeObjectURL(url),{once:true});
    const tools=document.createElement('div');tools.className='preview-tools';
    const title=document.createElement('span');title.textContent=label;
    const btn=document.createElement('button');btn.type='button';btn.textContent='REMOVE ×';btn.addEventListener('click',remove);
    tools.append(title,btn);tile.append(img,tools);return tile;
  };
  function setMain(file){clearError();if(!file)return;let error=validate(file);if(error)return showError(error);
    const dt=new DataTransfer();dt.items.add(file);main.files=dt.files;mainPreview.replaceChildren(preview(file,'New main image',()=>{if(!confirm('Remove this selected replacement?'))return;main.value='';mainPreview.replaceChildren();}));
  }
  function drawGallery(){galleryPreview.querySelectorAll('.new-gallery').forEach(n=>n.remove());
    galleryFiles.forEach((file,i)=>{const tile=preview(file,file.name,()=>{if(!confirm('Remove this selected gallery image?'))return;galleryFiles.splice(i,1);syncGallery();});tile.classList.add('new-gallery');galleryPreview.append(tile);});
  }
  function syncGallery(){const dt=new DataTransfer();galleryFiles.forEach(f=>dt.items.add(f));gallery.files=dt.files;drawGallery();}
  function addGallery(files){clearError();for(const file of files){const error=validate(file);if(error){showError(error);return;}}
    const existing=document.querySelectorAll('.existing-gallery:not(.marked-remove)').length;
    if(existing+galleryFiles.length+files.length>12)return showError('Maximum 12 gallery images per product.');
    galleryFiles.push(...files);syncGallery();
  }
  function wireDrop(zone,input,handle){
    zone.addEventListener('click',()=>input.click());
    zone.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();input.click();}});
    ['dragenter','dragover'].forEach(evt=>zone.addEventListener(evt,e=>{e.preventDefault();zone.classList.add('drag-over');}));
    ['dragleave','drop'].forEach(evt=>zone.addEventListener(evt,e=>{e.preventDefault();zone.classList.remove('drag-over');}));
    zone.addEventListener('drop',e=>{if(e.dataTransfer.files.length)handle(Array.from(e.dataTransfer.files));});
    input.addEventListener('change',()=>{if(input.files.length)handle(Array.from(input.files));});
  }
  wireDrop(document.getElementById('main-drop'),main,files=>setMain(files[0]));
  wireDrop(document.getElementById('gallery-drop'),gallery,files=>addGallery(files));
  document.querySelector('[data-replace-main]')?.addEventListener('click',()=>main.click());
  const deleted=document.getElementById('gallery-delete-inputs');
  document.querySelectorAll('[data-remove-id]').forEach(btn=>btn.addEventListener('click',()=>{
    const tile=btn.closest('.preview-tile');if(!confirm('Remove this gallery image permanently when you save?'))return;
    tile.classList.add('marked-remove');tile.hidden=true;
    const hidden=document.createElement('input');hidden.type='hidden';hidden.name='remove_gallery';hidden.value=btn.dataset.removeId;deleted.append(hidden);
  }));
  const name=document.getElementById('id_name'),slug=document.getElementById('id_slug');
  if(name&&slug)name.addEventListener('input',()=>{if(!slug.dataset.manuallyEdited){slug.value=name.value.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');}});
  if(slug)slug.addEventListener('input',()=>slug.dataset.manuallyEdited='1');
  form.addEventListener('submit',e=>{clearError();if(galleryFiles.length>12){e.preventDefault();showError('Too many images.');}});
})();
