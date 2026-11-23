const PRODUCTS={bijuterias:{id:'bijuterias',name:'Scoop de Bijuterias',price:59.90,icon:'💍'},skincare:{id:'skincare',name:'Scoop de Skincare',price:69.90,icon:'🧴'},misto:{id:'misto',name:'Scoop Misto',price:64.90,icon:'🎁'}};
const money=v=>v.toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const getCart=()=>JSON.parse(localStorage.getItem('gabora-cart')||'[]');
const saveCart=cart=>{localStorage.setItem('gabora-cart',JSON.stringify(cart));updateCount()};
function updateCount(){const el=document.querySelector('[data-cart-count]');if(el)el.textContent=getCart().reduce((a,b)=>a+b.quantity,0)}
function addToCart(id){const cart=getCart(),found=cart.find(x=>x.product_id===id);found?found.quantity++:cart.push({product_id:id,quantity:1});saveCart(cart);toast(`${PRODUCTS[id].name} adicionado ao carrinho`)}
function toast(msg){let t=document.createElement('div');t.textContent=msg;t.style='position:fixed;right:20px;bottom:20px;background:#2f1120;color:#fff;padding:14px 18px;border-radius:10px;z-index:99;box-shadow:0 8px 24px #0003';document.body.appendChild(t);setTimeout(()=>t.remove(),2600)}
document.addEventListener('DOMContentLoaded',()=>{updateCount();document.querySelectorAll('[data-add]').forEach(b=>b.onclick=()=>addToCart(b.dataset.add));});

