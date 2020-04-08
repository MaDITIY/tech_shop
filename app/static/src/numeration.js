let num=document.querySelector('.page').innerHTML*8-7;
numeration(num);
function numeration(num) {
   document.querySelectorAll('.number').forEach((key)=> key.innerHTML=num++);
}