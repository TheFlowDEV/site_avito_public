import "../add_adv/add_adv.scss"
import axios from 'axios'
import { Ripple, initMDB,Tab,Input,Dropdown } from 'mdb-ui-kit/js/mdb.es.min.js'; // Import needed modules
import { related,register,search,get_notifications,notify_connect } from '../headers_file.js';
window.register_type=false;
window.register=register
window.search=search
window.related = related
var category = null;

document.onreadystatechange = function()
{
    if (document.readyState=='interactive'){
        const imgInputHelper = document.getElementById("image-input");
        var imgContainer = document.getElementById("custom__image-container");
        var imgFiles = [];
        const addImgHandler = () => {
            const file = imgInputHelper.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
              const div_with_img = document.createElement("div");
              const newImg = document.createElement("img");
              newImg.src = reader.result;
              div_with_img.appendChild(newImg);
              imgContainer.appendChild(div_with_img);
             
            };
            // Store img file
            imgFiles.push(file);
            // Reset image input
            imgInputHelper.value = "";
            return;
          };
          imgInputHelper.addEventListener("change", addImgHandler);
    notify_connect('studentmarket.site')
    document.getElementById("notify_get").addEventListener("click",get_notifications)
    window.Ripple = Ripple;
    initMDB({ Ripple,Tab,Input,Dropdown })
document.getElementById("wrapper").addEventListener("click",(ev)=>{
    ev.preventDefault()
    if (ev.target.nodeName=="BUTTON")
    {
        category=ev.target.innerHTML;
        document.getElementById('main_category').placeholder=category
        document.getElementById("wrapper").hidden=true;
        document.getElementById("next_page").hidden=false;
        document.getElementById("back_row").hidden=false;
    }
})
document.getElementById("back_button").addEventListener("click",()=>{
    document.getElementById("next_page").hidden=true;
    category=null;
    imgFiles=[];
    imgContainer.innerHTML='';
    console.log(imgFiles)
    console.log(imgContainer.innerHTML)
    document.getElementById("wrapper").hidden=false;
    document.getElementById("back_row").hidden=true;
    document.getElementById('main_category').placeholder=''
})
document.getElementById("add_adv_button").addEventListener("click",(e)=>{
    e.preventDefault()
    let form = new FormData();
    form.append('main_name',document.getElementById("main_name").value)
    if (document.getElementById("main_name").value=="")
    {
        alert("Заполните имя объявления")
        return null;
    }
    form.append('text',document.getElementById("description").value)
    if (document.getElementById("description").value=="")
    {
        alert("Заполните описание объявления")
        return null;
    }
    form.append('category',category)
    if (document.getElementById("cost").value=="")
    {
        alert("Заполните цену объявления")
        return null;
    }
    form.append('cost',document.getElementById("cost").value)
    for (const file of imgFiles)
    {
        form.append("photos",file)
    }
    axios.post("api/add_adv",form,{
        headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value,"Content-Type":'multipart/form-data'}
    }).then((response)=>{
        if (response.data.status="Success")
            {
                window.location = response.data.url
            }
        else
        {
            alert("Возникла ошибка при добавлении объявления");
        }
    })
})

    }
}