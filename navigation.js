/* Native navigation, with a consistent active state and reduced-motion support. */
(() => {
 const work=document.querySelector('[data-nav="work"]');
 const home=/\/(?:index\.html)?$/.test(location.pathname);
 if(!home || !work) return;
 const section=document.getElementById('work');
 const update=()=>{if(location.hash==='#work')work.setAttribute('aria-current','location');else work.removeAttribute('aria-current');};
 update();window.addEventListener('hashchange',update);
 if(section && 'IntersectionObserver' in window){new IntersectionObserver(entries=>{if(entries[0].isIntersecting)work.setAttribute('aria-current','location');else if(location.hash!=='#work')work.removeAttribute('aria-current');},{rootMargin:'-100px 0px -35% 0px'}).observe(section);}
})();
