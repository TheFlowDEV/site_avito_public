import '../adverstiments/adverstiments.scss'
import { Ripple,Input, initMDB,Tab,Dropdown,Carousel, Modal } from 'mdb-ui-kit/js/mdb.es.min.js'; // Import needed modules
import { init_switch,related,register,search,get_notifications,notify_connect, init_search,draw_vk } from '../headers_file.js';
import axios from 'axios';
var deleted_images = [];
var added_images = [];
var added_images_id = [];
var backup_images = "";
function save(){
    let sh_param = new URLSearchParams(window.location.search)
    let name = document.getElementById("nameEdit").value;
    let cost = document.getElementById("priceEdit").value
    let is_active = document.getElementById("activeSwitch").checked
    let description = document.getElementById("descriptionEdit").value
    let reboot = false;
    if (deleted_images.length==0) reboot= true;
    if (added_images.length!=0)
        {
            let data = new FormData()
            data.append("id",sh_param.get("adv_id"))
            data.append("main_name",name);
            data.append("price",cost)
            data.append("is_active",is_active)
            data.append("text",description)
            data.append("change_photo","ADD")
            for (const file of added_images) data.append("file",file);
            {
                axios.post("/api/update_adv",data,{headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
                      .value,
                  }
                }).then(()=>
                    {
                        if (reboot) window.location.reload()
                    })
            }
        }
    if (deleted_images.length!=0){
        let data = new FormData()
        data.append("id",sh_param.get("adv_id"));
        data.append("main_name",name);
        data.append("price",cost);
        data.append("is_active",is_active);
        data.append("text",description);
        data.append("change_photo","DELETE");
        for (const id of deleted_images) data.append("photos",id);
        {
            axios.post("/api/update_adv",data,{headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
                  .value,
              }
            }).then(()=>
                {
                    if (!reboot) window.location.reload()
                })
        }
    }
   
    if (added_images.length==0 && deleted_images.length==0)
        {
            
            let data = new FormData()
            data.append("id",sh_param.get("adv_id"))
            data.append("main_name",name);
            data.append("price",cost)
            data.append("is_active",is_active)
            data.append("text",description)
            {
                axios.post("/api/update_adv",data,{headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
                      .value,
                  }
                }).then(()=>
                    {
                        window.location.reload()
                    })
            }
        
        }
}
function connect_to_chat()
{
    let search_params = new URLSearchParams(window.location.search);
    let adv_id = search_params.get("adv_id");
    let user_id = document.getElementById("user_adv_id").value
    axios.post("/api/chat",{"type":"create_chat",'adv_id':adv_id,'user_id':user_id},{
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
              .value,
        }
    }).then(()=>
        {
            window.location.href=`/chatTo${user_id}_${adv_id}`
        })
}
function clear_all()
{
    added_images=[];
    deleted_images=[];
    document.getElementById("photos_redact").innerHTML=backup_images;
}
function delete_image(e)
{
    e.preventDefault()
    if (added_images_id.indexOf(e.target.parentNode.id)>-1)
        {
            let id = added_images_id.indexOf(e.target.parentNode.id)
            added_images.splice(id,1)
            added_images_id.splice(id,1)

        }
    else
    {
        deleted_images.push(e.target.parentNode.id)
    }
    console.log(deleted_images)
    console.log(added_images)
    console.log(e.target.parentNode)
    e.target.parentNode.remove()
}

function toggle_heart()
{
    let search_params = new URLSearchParams(window.location.search);
    
    axios
      .post(
        "/api/adv_status_set",
        {
          status: "favorite",
          id: search_params.get("adv_id"),
        },
        {
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
              .value,
          },
        }
      ).then(() => {
        let heart =document.getElementById('heart')
        if (heart.className.indexOf("checked_also")>-1) heart.classList.remove('checked_also');
        else document.getElementById('heart').classList.toggle('checked')
      })
    
}
function phone_revealer()
{
    if (user_id){
        axios.post("/api/phone_reveal",{'id':user_id},{
    }).then((resp)=>
        {
            document.getElementById('phone_revealer').innerHTML=resp.data.phone
        })
}
}

window.register_type=false;
window.register=register
window.search=search
window.connect_to_chat=connect_to_chat
window.related = related
window.clear_all=clear_all
window.phone_revealer=phone_revealer
window.delete_image=delete_image
document.onreadystatechange= function()
{
    if (document.readyState=='interactive'){
        if (document.getElementById("photos_redact")) backup_images = document.getElementById("photos_redact").innerHTML;
        init_search()
    draw_vk()
    notify_connect('studentmarket.site')
    window.Ripple = Ripple;
    initMDB({Dropdown,Input,Tab,Carousel,Modal})
    init_switch()
    document.getElementById("notify_get").addEventListener("click",get_notifications)
    if (document.getElementById("editAdvModal")){
        document.getElementById("input_causer").addEventListener('click',()=>{
            document.getElementById("photoEdit").click()
        })
        document.getElementById("photoEdit").addEventListener("change",()=>{
            let reader = new FileReader()
            let last_file = document.getElementById("photoEdit").files[document.getElementById("photoEdit").files.length-1]
            reader.readAsDataURL(last_file)
            reader.onload = () => {
                let img = document.createElement('img')
                let div = document.createElement('div')
                let button = document.createElement('button')
                img.src = reader.result
                div.setAttribute('id','added_img_'+added_images.length)
                added_images_id.push('added_img_'+added_images.length);
                div.className="d-flex align-items-center gap-3"
                div.style.position="relative";
                img.style.width="100px";
                img.style.height="100px";
                button.type="button";
                button.className="btn-close position-absolute top-0 end-0";
                button.addEventListener('click',delete_image);
                button.style.backgroundColor="white";
                let el = document.getElementById("photos_redact")
                div.appendChild(img);
                div.appendChild(button);
                el.insertBefore(div,document.getElementById("input_causer"))
            }
            added_images.push(last_file)
        })
    }

    }

}
window.save=save
window.toggle_heart=toggle_heart