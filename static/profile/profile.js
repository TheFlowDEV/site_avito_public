import '../profile/profile.scss'
import axios from 'axios'
import { Ripple,Input, initMDB,Tab,Dropdown,Modal } from 'mdb-ui-kit/js/mdb.es.min.js'; // Import needed modules
import { init_search,init_switch,get_notifications,register,search,click_adv_handler,notify_connect, draw_vk} from '../headers_file';
const set_stars = (rating) => {
    if (!rating) rating=0
if (rating>4.5)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'  alt=''><img src='/static/star.svg' alt=''>"
else if (rating>4)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'  alt=''><img src='/static/half_star.svg' alt=''>"
else if (rating>3.5)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>3)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/half_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>2.5)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>2)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/half_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>1.5)return "<img src='/static/star.svg'  alt=''><img src='/static/star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>1)return "<img src='/static/star.svg'  alt=''><img src='/static/half_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>0.5)return "<img src='/static/star.svg'  alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else if (rating>0) return "<img src='/static/half_star.svg'  alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
else return "<img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'alt=''><img src='/static/empty_star.svg'  alt=''><img src='/static/empty_star.svg' alt=''>"
}
window.register_type=false;
window.register=register
var array_of_adv_ids =[];
var count = 0;
let srch_params = new URLSearchParams(window.location.search)
var user_id = srch_params.get('id',null)
var type_adv = srch_params.get('use_favorite',null)?'favorite':'active';
window.search=search

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
function checkPosition() {
    const height = document.body.offsetHeight
    const screenHeight = window.innerHeight
  
    const scrolled = window.scrollY
  
    const threshold = height - screenHeight / 4
  
    const position = scrolled + screenHeight
    if (position >= threshold) {
        window.removeEventListener('scroll',checkPosition)
        let data;
        count++;
        if (type_adv =='history'){
            axios.post("/api/history_get",{'count':count},{
                headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
            }).then((response)=>
            {
                let data = response.data
                if (data.status=="OK"){
                    data.history.forEach(i=>{
                        if (!(array_of_adv_ids.includes((i.id).toString()))){
                        adv_cards.innerHTML=adv_cards.innerHTML+`<div class="position-relative d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6 show_up"><div id_adv="${i.id}" class="product_card container card mb-5 border border-0"  ><img src=${i.photo} class="img-fluid" style="height: 200px;"alt="...">${(i.is_favorite!=null)?`<img class='icon' src=${i.is_favorite?'/static/heart.svg':'/static/empty_heart.svg'}>`:""}<h5 id="product_name" class="product-text__nobootstrap">${i.main_name}</h5><h5>${i.cost} ₽</h5><h6>${i.datetime}</h6></div></div>`
                        array_of_adv_ids.push((i.id).toString())
                        }
                    })
                    count = Math.floor(array_of_adv_ids.length/20)
                    setTimeout(function(){
                        window.addEventListener('scroll',checkPosition)
                     },1000);
                }
    
            })
            return null;
        }
        else if (type_adv=='favorite')
        {
            data={"destination":"profile","type":type_adv,"count":count}
        }
        else
        {
            data = {'destination':'profile',"type":type_adv,'count':count}
            if (user_id) data['user_id']=user_id
            
        }
        axios.post("/api/get_adv",data,{
            headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
        }).then((response)=>
        {
            let data = response.data
            if (data.status=="OK"){
                data.advs.forEach(i=>{
                    if (!(array_of_adv_ids.includes((i.id).toString()))){
                    adv_cards.innerHTML=adv_cards.innerHTML+`<div class="position-relative d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6 show_up"><div id_adv="${i.id}" class="product_card container card mb-5 border border-0"  ><img src=${i.photo} class="img-fluid" style="height: 200px;"alt="...">${(i.is_favorite!=null)?`<img class='icon ${i.is_favorite?'checked_also':''}'>`:""}<h5 id="product_name" class="product-text__nobootstrap">${i.main_name}</h5><h5>${i.cost} ₽</h5><h6>${i.datetime}</h6></div></div>`
                    array_of_adv_ids.push((i.id).toString())
                    }
                })
                count = Math.floor(array_of_adv_ids.length/20)
                setTimeout(function(){
                    window.addEventListener('scroll',checkPosition)
                 },1000);
            }

        })
    }
  }


document.onreadystatechange = function()
{
    
    if (document.readyState=="interactive"){
        init_search()
        draw_vk()
        const imgInputHelper = document.getElementById("add-single-img");
        const imgInputHelperLabel = document.getElementById("add-img-label");
        const imgContainer = document.querySelector(".custom__image-container");
        var once_created = false
        const imgFiles = [];
        const addImgHandler = () => {
      const file = imgInputHelper.files[0];
      if (!file) return;
      // Generate img preview
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        if (!once_created){
        const newImg = document.createElement("img");
        newImg.src = reader.result;
        newImg.setAttribute('id','user-image')
        imgContainer.insertBefore(newImg, imgInputHelperLabel);
        imgInputHelperLabel.src=reader.result
        once_created=true;
        }
        else
        {
            document.getElementById('user-image').src=reader.result
        }
      };
      // Store img file
      imgFiles.push(file);
      // Reset image input
      imgInputHelper.value = "";
      return;
    };
    imgInputHelper.addEventListener("change", addImgHandler);
    notify_connect('studentmarket.site')
    const adv_cards = document.getElementById('adv_cards');
    window.Ripple = Ripple;
    initMDB({Dropdown,Tab,Input,Modal})
    init_switch()
    if (adv_cards){
        adv_cards.childNodes.forEach(element => {
            if (element.className=="position-relative d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6"){
            array_of_adv_ids.push(element.childNodes[1].getAttribute('id_adv'))
        }
        });
        }
        adv_cards.addEventListener('click',click_adv_handler)
        document.getElementById("notify_get").addEventListener("click",get_notifications)
    const buttons = document.querySelectorAll('.btn_list')
    if (document.getElementById('subscribe-button')){
    document.getElementById('subscribe-button').addEventListener('click',(ev)=>
    {
        if (ev.target.innerHTML.indexOf('Подписаться')>-1)
        {
            axios.post('/api/subscribe',{'subscribe':true,'to_user':document.getElementById('username').innerHTML},{
                headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
            }).then(()=>
            {
                ev.target.innerHTML='Отписаться'
            })
        }
        else
        {
            axios.post('/api/subscribe',{'to_user':document.getElementById('username').innerHTML},{
                headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
            }).then(()=>
            {
                ev.target.innerHTML='Подписаться'
            })
        }
    })
}
    buttons.forEach((button)=>
{   button.addEventListener('click',(e)=>{
    window.removeEventListener('scroll',checkPosition)
    count=0;
    array_of_adv_ids=[]
    buttons.forEach((b)=>{
        b.classList.remove('choosed')
    })
    if (e.target.id=="active_button") type_adv='active'
    else if (e.target.id=="unactive_button") type_adv='not active'
    else if(e.target.id=="favorite") type_adv='favorite'
    else 
    {
        e.target.classList.toggle('choosed')
        array_of_adv_ids=[];
        adv_cards.innerHTML='';
        type_adv='history'
        axios.post('api/history_get',{'count':count},{
            headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
        }).then((response)=>{
            
            let data = response.data
            data['history'].forEach((i)=>
        {
            if (!(array_of_adv_ids.includes((i.id).toString()))){
                adv_cards.innerHTML=adv_cards.innerHTML+`<div class="position-relative show_up d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6"><div id_adv="${i.id}" class="product_card container card mb-5 border border-0"  ><img src=${i.photo} class="img" alt="...">${(i.is_favorite!=null)?`<img class='icon ${i.is_favorite?'checked_also':''}'>`:""}<h5 id="product_name" class="product-text__nobootstrap">${i.main_name}</h5><h5>${i.cost} ₽</h5><h6>${i.datetime}</h6></div></div>`
                array_of_adv_ids.push((i.id).toString())
        }
        })
        })
        setTimeout(function(){
            window.addEventListener('scroll',checkPosition)
         },1000);
        return null
    }
    e.target.classList.toggle('choosed')
    array_of_adv_ids=[];
    adv_cards.innerHTML='';
    let data={"destination":'profile',"type":type_adv,'count':count}
    if (user_id) data['user_id']=user_id;
    axios.post("/api/get_adv",data,{
        headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
    }).then((response)=>
    {
        let data =response.data
        data['advs'].forEach((i)=>
        {
            if (!(array_of_adv_ids.includes((i.id).toString()))){
                adv_cards.innerHTML=adv_cards.innerHTML+`<div class="position-relative show_up d-flex col-6 col-lg-3 col-md-4 col-xl-2 col-sm-6"><div id_adv="${i.id}" class="product_card container card mb-5 border border-0"  ><img src=${i.photo} class="img" alt="...">${(i.is_favorite!=null)?`<img class='icon ${i.is_favorite?'checked_also':''}'>`:""}<h5 id="product_name" class="product-text__nobootstrap">${i.main_name}</h5><h5>${i.cost} ₽</h5><h6>${i.datetime}</h6></div></div>`
                array_of_adv_ids.push((i.id).toString())
        }
        }
        )
        setTimeout(function(){
                    window.addEventListener('scroll',checkPosition)
                 },1000);
    })
})
    
})
    window.addEventListener('scroll',checkPosition)
    document.getElementById('save_button').addEventListener('click',async ()=>
        {
            let data = new FormData()
            if (imgFiles.length==1) data.append('photo',imgFiles[0]);
            if (document.getElementById('type_email').value) data.append('email',document.getElementById('type_email').value)
            if (document.getElementById('type_phone').value) data.append('phone',document.getElementById('type_phone').value)
            if (document.getElementById('type_name').value) data.append('username',document.getElementById('type_name').value)
            axios.post('/api/changeusr',data,{
                headers:{'X-CSRFTOKEN':document.querySelector('[name=csrfmiddlewaretoken]').value}
            }).then(()=>
                {
                    window.location.reload()
                })

        })
    if (document.getElementById('block')){
    document.getElementById('block').addEventListener('click',(ev)=>
        {
                    let data = {'to_user':document.getElementById('username').innerHTML}
                    data['type']= document.getElementById('block').innerHTML=='Заблокировать'?'ban':'unban'
                    axios.post('/api/ban',data,{headers:{'X-CSRFTOKEN':document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((resp)=>
                        {
                            if (data['type']=='ban') document.getElementById('block').innerHTML='Разблокировать'
                            else document.getElementById('block').innerHTML='Заблокировать'
                        })
                
        })
}
    
    if (document.getElementById('reviews_init')){
        var count  = 0;
        var count_advs = 0;
        var unique_reviews = []
        var unique_advs = []
    let can_load = true;
    document.getElementById('reviews_body').addEventListener('scroll',(ev)=>
        {
            let scrollTop = ev.target.scrollTop;
            let clientHeight = ev.target.clientHeight;
            if (scrollTop>=clientHeight && can_load)
                {
                    can_load = false;
                    setTimeout(()=>{can_load=true;},1000);
                    let srch_params = new URLSearchParams(window.location.search)
                    axios.get('/api/review',{headers:{
                        'XCSRF-TOKEN':document.querySelector('[name=csrfmiddlewaretoken]').value
                    },params:{id:srch_params.get('id'),'count':count}}).then((response)=>
                        {
                            let data = response.data
                    document.getElementById('reviews_loader').hidden=true;
                    document.getElementById('reviews_modal_container').hidden=false;
                    let all_ratings_count = data['ratings']['5'] + data['ratings']['4'] +data['ratings']['3'] +data['ratings']['2'] +data['ratings']['1'];
                    document.getElementById('5-rating').innerHTML=data['ratings']['5'];
                    document.getElementById('4-rating').innerHTML=data['ratings']['4'];
                    document.getElementById('3-rating').innerHTML=data['ratings']['3'];
                    document.getElementById('2-rating').innerHTML=data['ratings']['2'];
                    document.getElementById('1-rating').innerHTML=data['ratings']['1'];
                    document.getElementById('5-pb').style.width=`${(data['ratings']['5']/all_ratings_count) *100}%`;
                    document.getElementById('4-pb').style.width=`${data['ratings']['4']*100/all_ratings_count}%`;
                    document.getElementById('3-pb').style.width=`${data['ratings']['3']*100/all_ratings_count}%`;
                    document.getElementById('2-pb').style.width=`${data['ratings']['2']*100/all_ratings_count}%`;
                    document.getElementById('1-pb').style.width=`${data['ratings']['1']*100/all_ratings_count}%`;
                    
                    let reviews_container = document.getElementById('reviews_container')
                    data.reviews.forEach((rev)=>
                        {
                            if (!unique_reviews.includes(rev.id.toString())){
                            unique_reviews.push(rev.id.toString())
                            reviews_container.innerHTML+=`<div class="container">
                            <div user_id=${rev.wrote_by} class="d-inline-flex"><img class='review_image me-2' src="${rev.user_photo}" alt=""><strong>${rev.user_username}</strong></div>
                            <div class="d-inline-flex">${set_stars(rev.rating)} <p adv_id=${rev.adverstiment} class="ms-2 my-auto">По объявлению «${rev.adverstiment_name}»</p></div>
                            <p>${rev.text}</p>
                          </div>`
                            }
                        })
                        })
                    count = Math.floor(unique_reviews.length/10)
                }
        })
    document.getElementById('reviews_init').addEventListener('click',()=>
        {
            let srch_params = new URLSearchParams(window.location.search)

            axios.get('/api/review',{headers:{
                'XCSRF-TOKEN':document.querySelector('[name=csrfmiddlewaretoken]').value
            },params:{id:srch_params.get('id')}}).then((response)=>
                {
                    let data = response.data
                    document.getElementById('reviews_loader').hidden=true;
                    document.getElementById('reviews_modal_container').hidden=false;
                    let all_ratings_count = data['ratings']['5'] + data['ratings']['4'] +data['ratings']['3'] +data['ratings']['2'] +data['ratings']['1'];
                    document.getElementById('5-rating').innerHTML=data['ratings']['5'];
                    document.getElementById('4-rating').innerHTML=data['ratings']['4'];
                    document.getElementById('3-rating').innerHTML=data['ratings']['3'];
                    document.getElementById('2-rating').innerHTML=data['ratings']['2'];
                    document.getElementById('1-rating').innerHTML=data['ratings']['1'];
                    document.getElementById('5-pb').style.width=`${(data['ratings']['5']/all_ratings_count) *100}%`;
                    document.getElementById('4-pb').style.width=`${data['ratings']['4']*100/all_ratings_count}%`;
                    document.getElementById('3-pb').style.width=`${data['ratings']['3']*100/all_ratings_count}%`;
                    document.getElementById('2-pb').style.width=`${data['ratings']['2']*100/all_ratings_count}%`;
                    document.getElementById('1-pb').style.width=`${data['ratings']['1']*100/all_ratings_count}%`;
                    let reviews_container = document.getElementById('reviews_container')
                    data.reviews.forEach((rev)=>
                        {
                            if (!unique_reviews.includes(rev.id.toString())){
                            unique_reviews.push(rev.id.toString())
                            reviews_container.innerHTML+=`<div class="container">
                            <div user_id=${rev.wrote_by} class="d-inline-flex"><img class='review_image me-2' src="${rev.user_photo}" alt=""><strong>${rev.user_username}</strong></div>
                            <div class="d-inline-flex">${set_stars(rev.rating)} <p adv_id=${rev.adverstiment} class="ms-2 my-auto">По объявлению «${rev.adverstiment_name}»</p></div>
                            <p>${rev.text}</p>
                          </div>`
                            }
                        })
                    count = 1;
                })
        })
    document.getElementById('review_modal_init_button').addEventListener('click',()=>{
        let srch_params=new URLSearchParams(window.location.search)
        let data  = {"destination":"profile","user_id":srch_params.get('id'),'type':'all','count':0}
        axios.post("/api/get_adv",data,{
            headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
        }).then((response)=>
            {
                if (response.data.status=="OK"){
                document.getElementById('reviews_input').hidden=false;
                document.getElementById('reviews_loading').hidden=true;
                let advs = response.data.advs
                console.log(advs)
                advs.forEach((item)=>
                    {
                        const elem = document.getElementById('reviews_advs_row')
                        if (!unique_advs.includes(item.id.toString()))
                            {
                                unique_advs.push(item.id.toString())
                                elem.innerHTML+=`<div adv_id='${item.id}' class="adv_modal d-inline-flex mt-3"><img class="adv_image me-2" src="${item.photo}" alt=""><div  adv_id='${item.id}'><h5>${item.main_name}</h5><strong>${item.cost} ₽</strong></div></div>`
                            }
                    })
                }
                count_advs = Math.floor(unique_advs.length/20);
            })
    })
    let last_time = 0;
    document.getElementById('my_review_modalbody').addEventListener('scroll',(ev)=>{
        let current_time = Date.now();
        if (current_time-last_time>500)
            {
                last_time = current_time;
                let srch_params = new URLSearchParams(window.location.search)
                let text = document.getElementById('adv_searcher').value==null?"":document.getElementById('adv_searcher').value;
                axios.post('/api/get_adv',{"destination":"profile","user_id":srch_params.get('id'),'type':'all','count':count_advs,'text':text},{headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((response)=>{
                    if (response.data.status=="OK"){

                    let advs = response.data.advs;
                    advs.forEach((item)=>
                        {
                            const elem = document.getElementById('reviews_advs_row')
                            if (!unique_advs.includes(item.id.toString()))
                                {
                                    unique_advs.push(item.id.toString())
                                    elem.innerHTML+=`<div adv_id='${item.id}' class="adv_modal d-inline-flex mt-3"><img class="adv_image me-2" src="${item.photo}" alt=""><div  adv_id='${item.id}'><h5>${item.main_name}</h5><strong>${item.cost} ₽</strong></div></div>`
                                }
                        })

                    }
                    count_advs = Math.floor(unique_advs.length/20);
                })
            }
    })
    let timeout;
    document.getElementById('adv_searcher').addEventListener('input',(ev)=>{
        let text = ev.target.value;
        let srch_params = new URLSearchParams(window.location.search)
        count_advs = 0;
        let data = {"destination":"profile","user_id":srch_params.get('id'),'type':'all','count':count_advs,'text':text}
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            axios.post("/api/get_adv",data,{
                headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}
            }).then((response)=>
                {
                    if (response.data.status=="OK"){
                    let advs = response.data.advs
                    document.getElementById('reviews_advs_row').innerHTML='';
                    unique_advs=[];

                    advs.forEach((item)=>{
                        if (!unique_advs.includes(item.id.toString())){
                            unique_advs.push(item.id.toString())
                            document.getElementById('reviews_advs_row').innerHTML+=`<div  class="adv_modal d-inline-flex mt-3" adv_id='${item.id}'><img class="adv_image me-2" src="${item.photo}" alt=""><div  adv_id='${item.id}'><h5>${item.main_name}</h5><strong>${item.cost} ₽</strong></div></div>`
                        }
                    })
                    count_advs = Math.floor(unique_advs.length/20);
                }
                })
        }, 800);
    })
    document.getElementById('reviews_advs_row').addEventListener('click',(ev)=>{
        let id = ev.target.getAttribute('adv_id')==null?ev.target.parentNode.getAttribute('adv_id'):ev.target.getAttribute('adv_id');
        if (id!=null)
            {
                let previous_modal = Modal.getInstance(document.getElementById('reviews_modal'))
                let modal = new Modal(document.getElementById('write_review_modal'))
                let srch_params = new URLSearchParams(window.location.search)
                axios.post('/api/get_adv',{"destination":"profile",'type':'get_one_adv','user_id':srch_params.get('id'),"adv_id":id},{headers:{"X-CSRFToken":document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((response)=>{
                    let adv = response.data.adv
                    if (response.data.my_review)
                        {
                            document.getElementById('write_review_input').value=response.data.my_review.text;
                            let value = response.data.my_review.rating;
                            document.getElementById('setstars-container').setAttribute('star_number',value);
                            const star1 = document.getElementById('1-star');
        const star2 = document.getElementById('2-star');
        const star3 = document.getElementById('3-star');
        const star4 = document.getElementById('4-star');
        const star5 = document.getElementById('5-star');
        const zero = '/static/empty_star.svg';
        const full = '/static/star.svg';
        if (value==1)
            {
                star1.src = full;
                star2.src = zero;
                star3.src = zero;
                star4.src = zero;
                star5.src = zero;
            }
          else if (value==2){
            star1.src = full;
            star2.src = full;
            star3.src = zero;
            star4.src = zero;
            star5.src = zero;
          }
          else if (value==3){
            star1.src = full;
            star2.src = full;
            star3.src = full;
            star4.src = zero;
            star5.src = zero;
          }
          else if (value==4){
            star1.src = full;
            star2.src = full;
            star3.src = full;
            star4.src = full;
            star5.src = zero;
          }
          else if (value==5){
            star1.src = full;
            star2.src = full;
            star3.src = full;
            star4.src = full;
            star5.src = full;
    
        }
        else
        {
            star1.src = zero;
            star2.src = zero;
            star3.src = zero;
            star4.src = zero;
            star5.src = zero;
        }
                        }
                    document.getElementById('adv_name').innerHTML=adv.main_name
                    document.getElementById('adv_photo').src=adv.photo
                    document.getElementById('adv_cost').innerHTML=adv.cost + " ₽"
                    localStorage.setItem('adv_id',adv.id)
                    previous_modal.hide()
                    
                    modal.show()
                })
                
            }
    })
    document.getElementById('setstars-container').addEventListener('click',(ev)=>{
        let value = ev.target.getAttribute("value")
        document.getElementById('setstars-container').setAttribute('star_number',value);
    })
    document.getElementById('setstars-container').addEventListener('mouseout',(ev)=>{
        let value =document.getElementById('setstars-container').getAttribute("star_number");
        const star1 = document.getElementById('1-star');
        const star2 = document.getElementById('2-star');
        const star3 = document.getElementById('3-star');
        const star4 = document.getElementById('4-star');
        const star5 = document.getElementById('5-star');
        const zero = '/static/empty_star.svg';
        const full = '/static/star.svg';
        if (value==1)
            {
                star1.src = full;
                star2.src = zero;
                star3.src = zero;
                star4.src = zero;
                star5.src = zero;
            }
          else if (value==2){
            star1.src = full;
            star2.src = full;
            star3.src = zero;
            star4.src = zero;
            star5.src = zero;
          }
          else if (value==3){
            star1.src = full;
            star2.src = full;
            star3.src = full;
            star4.src = zero;
            star5.src = zero;
          }
          else if (value==4){
            star1.src = full;
            star2.src = full;
            star3.src = full;
            star4.src = full;
            star5.src = zero;
          }
          else if (value==5){
            star1.src = full;
            star2.src = full;
            star3.src = full;
            star4.src = full;
            star5.src = full;
    
        }
        else
        {
            star1.src = zero;
            star2.src = zero;
            star3.src = zero;
            star4.src = zero;
            star5.src = zero;
        }
    })
    document.getElementById('setstars-container').addEventListener('mouseover',(ev)=>{
      let value = ev.target.getAttribute("value")
      const star1 = document.getElementById('1-star');
      const star2 = document.getElementById('2-star');
      const star3 = document.getElementById('3-star');
      const star4 = document.getElementById('4-star');
      const star5 = document.getElementById('5-star');
      const zero = '/static/empty_star.svg';
      const full = '/static/star.svg';
      if (value==1)
        {
            star1.src = full;
            star2.src = zero;
            star3.src = zero;
            star4.src = zero;
            star5.src = zero;
        }
      else if (value==2){
        star1.src = full;
        star2.src = full;
        star3.src = zero;
        star4.src = zero;
        star5.src = zero;
      }
      else if (value==3){
        star1.src = full;
        star2.src = full;
        star3.src = full;
        star4.src = zero;
        star5.src = zero;
      }
      else if (value==4){
        star1.src = full;
        star2.src = full;
        star3.src = full;
        star4.src = full;
        star5.src = zero;
      }
      else if (value==5){
        star1.src = full;
        star2.src = full;
        star3.src = full;
        star4.src = full;
        star5.src = full;

    }
    })
    document.getElementById('write_review_button').addEventListener('click',()=>{
        let star_value = document.getElementById('setstars-container').getAttribute("star_number")
        let review_text = document.getElementById('write_review_input')
        if (!star_value || !review_text) alert('Вы забыли ввести текст отзыва и поставить отзыв')
        let srch_params = new URLSearchParams(window.location.search)
        let data = {
            text:review_text.value,
        user_id:srch_params.get('id'),
    rating:star_value,
adv_id:localStorage.getItem('adv_id')}
        axios.post('/api/review',data,{headers:{'X-CSRFToken':document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((response)=>{
            if (response.data.status=="Success")
                {
                    window.location.reload()
                }
        })
    })

    document.getElementById("report_init_modal").addEventListener('click',(ev)=>{
        let modal = new Modal(document.getElementById("report_modal"));
        let message = document.getElementById("report_init_modal").getAttribute("data-mdb-message");
        document.getElementById("report_message_head").value=message;
        modal.show()
    })
    
}
document.getElementById("report_button").addEventListener('click',()=>{
    let data = {description:document.getElementById("report_message").value,head:document.getElementById("report_message_head").value}
    axios.post('/api/report',data,{headers:{'X-CSRFToken':document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((response)=>{
        alert("Ваше мнение будет учтено");
    })
})
    }
}
window.phone_revealer=phone_revealer

