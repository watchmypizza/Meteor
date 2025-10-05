document.querySelectorAll('.copy').forEach(btn=>{
  btn.addEventListener('click', async ()=>{
    const text = btn.getAttribute('data-copy') || btn.parentElement.innerText.trim();
    try{
      await navigator.clipboard.writeText(text);
      btn.textContent='Copied!';
      setTimeout(()=>btn.textContent='Copy', 1300);
    }catch(err){
      btn.textContent='Copy Failed';
      setTimeout(()=>btn.textContent='Copy', 1300);
    }
  });
});

document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click', e=>{
    const id=a.getAttribute('href');
    if(id && id !== '#' && document.querySelector(id)){
      e.preventDefault();
      document.querySelector(id).scrollIntoView({behavior:'smooth'});
    }
  });
});

document.querySelectorAll('.btn.primary').forEach(b=>{
  b.addEventListener('mousemove', (e)=>{
    const r=b.getBoundingClientRect();
    const x=e.clientX - r.left; const y=e.clientY - r.top;
    b.style.boxShadow = `0 10px 30px rgba(128,117,255,.35), 0 0 0 1px rgba(255,255,255,.08), inset 0 0 40px rgba(255,230,59,.12)`;
    b.style.background = `radial-gradient(240px 120px at ${x}px ${y}px, rgba(255,230,59,.28), transparent 60%), linear-gradient(135deg, var(--lav), var(--plum))`;
  });
  b.addEventListener('mouseleave', ()=>{
    b.style.boxShadow='var(--shadow)';
    b.style.background='linear-gradient(135deg,var(--lav),var(--plum))';
  });
});

const revealEls = [...document.querySelectorAll('.section, .hero .grid > div, .feature, .card')];
revealEls.forEach(el=>el.classList.add('reveal'));
const io = new IntersectionObserver((entries)=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      entry.target.classList.add('show');
      io.unobserve(entry.target);
    }
  });
},{threshold:.18});
revealEls.forEach(el=>io.observe(el));

document.querySelectorAll('details.acc').forEach(d=>{
  d.addEventListener('toggle', ()=>{
    const content = d.querySelector('div');
    if(!content) return;
    content.style.overflow='hidden';
    content.animate(
      [{opacity:0, transform:'translateY(-4px)'},{opacity:1, transform:'translateY(0)'}],
      {duration:250, easing:'ease-out'}
    );
    setTimeout(()=>{content.style.overflow=''},260);
  });
});

document.querySelectorAll('.logo').forEach(l=>{
  l.addEventListener('mouseenter',()=> l.style.filter='drop-shadow(0 6px 16px rgba(128,117,255,.45))');
  l.addEventListener('mouseleave',()=> l.style.filter='');
});
