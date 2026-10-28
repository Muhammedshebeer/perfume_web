(() => {
  const toggle=document.querySelector('[data-menu-toggle]'), nav=document.querySelector('[data-nav]');
  if(toggle && nav) toggle.addEventListener('click',()=>{const isOpen=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(isOpen));});
  const main=document.getElementById('detail-main-image');
  const lightbox=document.getElementById('lightbox');
  if(main){
    document.querySelectorAll('[data-gallery-src]').forEach(btn=>btn.addEventListener('click',()=>{
      main.src=btn.dataset.gallerySrc;main.alt=btn.dataset.galleryAlt||'Product image';
      document.querySelectorAll('[data-gallery-src]').forEach(b=>b.classList.remove('active'));btn.classList.add('active');
    }));
    const close=()=>{if(lightbox){lightbox.classList.remove('open');lightbox.setAttribute('aria-hidden','true');}};
    document.querySelector('[data-lightbox-open]')?.addEventListener('click',()=>{
      const img=document.getElementById('lightbox-image');img.src=main.src;img.alt=main.alt;
      lightbox.classList.add('open');lightbox.setAttribute('aria-hidden','false');
      lightbox.querySelector('[data-lightbox-close]').focus();
    });
    lightbox?.querySelector('[data-lightbox-close]')?.addEventListener('click',close);
    lightbox?.addEventListener('click',e=>{if(e.target===lightbox)close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape')close();});
  }
})();
