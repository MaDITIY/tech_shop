document.querySelector('.simple-checkbox__main').addEventListener('click', (main)=>{
    if(main.target.checked) {
        document.querySelectorAll('.simple-checkbox').forEach((e)=>{
            e.checked = !0;
        })
    }
    else {
        document.querySelectorAll('.simple-checkbox').forEach((e)=>{
            e.checked = !1;
        })
    }
})
