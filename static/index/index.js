import '../index/index.scss'
import axios from 'axios'
import { register,get_notifications,related,search,click_adv_handler,init_switch,notify_connect,init_search, draw_vk} from '../headers_file';
import { Ripple, initMDB,Carousel,Input,Dropdown, Offcanvas } from 'mdb-ui-kit/js/mdb.es.min.js'; // Import needed modules
var delete_show_up = false;
const removeShowUpClass = async () => {
  const showUpElements = document.querySelectorAll('.show_up');
  for (const element of showUpElements) {
    await new Promise(resolve => {
      element.classList.remove('show_up');
      resolve()
    });
  }
};

removeShowUpClass();
document.onreadystatechange = function()
{
    if (document.readyState=="interactive"){   
    init_search()
    init_switch()
    var offcanvas = new Offcanvas(document.getElementById('offcanvas_categories_mobile'))
    if (document.getElementById("show_more")){
        document.getElementById("show_more").addEventListener('click',()=>{
            add_adv(true)
            delete_show_up=true; 
            document.getElementById("show_more").remove()
            setTimeout(()=>{
                window.addEventListener("scroll",checkPosition)
            },1000)
           
        })
    }
    document.getElementById('all_categories').addEventListener('click',()=>
        {
         offcanvas.show()
        })
    draw_vk();
    document.getElementById('offcanvas_close').addEventListener('click',()=>
        {
            offcanvas.hide()  
        })
    notify_connect('studentmarket.site')
    var count = 0;
    var product_row = document.getElementById("product_row")
    var array_of_adv_ids = [];
    if (product_row){
    product_row.childNodes.forEach(element => {
        if (element.className=="position-relative d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6"){
            array_of_adv_ids.push(element.childNodes[1].getAttribute('id_adv'))
}
        });
    }

var history_row = document.getElementById("history_row")
var history_array_of_adv_ids = [];
if (history_row){
history_row.childNodes.forEach(element => {
    if (element.className=="position-relative d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6"){
    history_array_of_adv_ids.push(element.childNodes[1].getAttribute('id_adv'))
        }
    });

}

const add_adv = (show_more_flag)=>{
        count++;
        let search_params = new URLSearchParams(window.location.search)
        let text=search_params.get('text')
        let category = search_params.get('category')
        if (!text) text=''
        if (!category) category=''
        let data={"destination":"main_page","count":count,'text':text,'category':category}
        axios.post("/api/get_adv",data,{
            headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
        }).then((response)=>
        {
            let data = response.data
            if (data.status=="OK"){
                data.advs.forEach(i=>{
                    if (!(array_of_adv_ids.includes((i.id).toString())) && !((history_array_of_adv_ids.includes((i.id).toString())))){
                    product_row.innerHTML=product_row.innerHTML+`<div class="position-relative d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6"><div id_adv="${i.id}" class="product_card container ${show_more_flag?"show_up":""} card mb-5 border border-0"  ><img src=${i.photo} class="img" alt="..." style="cursor:pointer;">${i.is_favorite!=null?`<img class="icon ${i.is_favorite?'checked_also':""}" alt="" style="cursor:pointer;">`:""}<h5 id="product_name" class="product-text__nobootstrap" style="cursor:pointer;">${i.main_name}</h5><h5>${i.cost} ₽</h5><h6>${i.datetime}</h6></div></div>`
                    array_of_adv_ids.push((i.id).toString())
                    }
                })
                count = Math.floor(array_of_adv_ids.length/20)
            }

        })
}
function checkPosition() {
    const height = document.body.offsetHeight
    const screenHeight = window.innerHeight
  
    const scrolled = window.scrollY
  
    const threshold = height - screenHeight *3
  
    const position = scrolled + screenHeight
    console.log(threshold,position)
    if (position >= threshold) {
        window.removeEventListener('scroll',checkPosition)
        if (delete_show_up) removeShowUpClass();
        add_adv(false)
        setTimeout(function(){
            window.addEventListener('scroll',checkPosition)
         },1000);
        }
        
    }
  

    window.Ripple = Ripple;
    initMDB({ Ripple,Carousel,Input,Dropdown,Offcanvas})
    if (document.getElementById("product_cards"))
    {
    document.getElementById("product_cards").addEventListener("click",click_adv_handler)
    }
if (document.getElementById("history_cards"))
    {
    document.getElementById("history_cards").addEventListener("click",click_adv_handler)
}
if (document.getElementById("notify_get")){
document.getElementById("notify_get").addEventListener("click",get_notifications)
}
}
}
function set_category(ev){
    ev.preventDefault();
    let url = new URL(window.location);
    let url_search_params = new URLSearchParams(url.search);

    url_search_params.set("category", ev.target.innerHTML.replace(/<i.*?<\/i>|<.*?>/g, "").trim()==""?ev.target.parentElement.innerHTML.replace(/<i.*?<\/i>|<.*?>/g, "").trim():ev.target.innerHTML.replace(/<i.*?<\/i>|<.*?>/g, "").trim()); // заменяет на пустую строку любой тег, включая тег <i> и все его содержимое, а также любой другой тег и его содержимое
    window.location.search=url_search_params;
}
function unset_category(){
    let url = new URL(window.location);
    let url_search_params = new URLSearchParams(url.search);
    url_search_params.delete("category");
    window.location.search= url_search_params;
}
window.register=register;
window.search=search;
window.unset_category=unset_category;
window.register_type=false;
window.set_category= set_category
window.related=related
