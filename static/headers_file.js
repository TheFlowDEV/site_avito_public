import axios from "axios";
import {Input} from 'mdb-ui-kit'
import "material-symbols/outlined.scss"
import Autocomplete from 'bootstrap5-autocomplete'
import * as VKID from '@vkid/sdk';
export {
  init_switch,
  register,
  get_notifications,
  related,
  click_adv_handler,
  search,
  notify_connect,
  init_search,
  draw_vk
};
VKID.Config.set({app: 51916233, redirectUrl: "https://studentmarket.site/authorize_VK"});
function draw_vk(){
if (document.getElementById('ddown'))
  {
    const oneTap = new VKID.OneTap();
    const container = document.getElementById('VkIdSdkOneTap');
    if (container.getAttribute('rendered')!="true"){
    container.setAttribute('rendered',"true");
    if (container) {
    oneTap.render({ container: container, scheme: VKID.Scheme.LIGHT, lang: VKID.Languages.RUS });
    

    }
  }
  }
}
function notify_connect(ip)
{
  
  let socket = new WebSocket(`wss://${ip}/ws/notify`);
  const element = document.getElementById('notifications_container')
  const counter = document.getElementById('notif_count')
  socket.onmessage= function (event){
    let msg = JSON.parse(event.data)
    if (msg['type']=='notify'){
      if (counter.innerHTML=='')
      {
        counter.innerHTML=1;
        element.innerHTML=''
      }
      else
      {
        counter.innerHTML=parseInt(counter.innerHTML)+1;
      }
    element.innerHTML+='<li><div class="row container border"><span>' +
    msg.head +
    "</span><span>" +
    msg.body +
    "  " +
    msg.timestamp +
    "</span></div></li>";
    if (element.className.indexOf('show')>-1){
       counter.innerHTML='';
       axios.post('/api/notifications',{'read_id':msg.id},{headers:{
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
       }})
    }
    }
  }
  socket.onclose = function(e) {
    console.log('СЛУЧИЛАСЬ ОШИБКА! '+e.reason)
    setTimeout(notify_connect, 1000, ip);
};
}
function init_switch() {
  if (document.getElementById("switch_button")) {
    document.getElementById("switch_button").addEventListener("click", () => {
      document.getElementById('type_email').classList.remove('is-invalid')
      document.getElementById('type_password').classList.remove('is-invalid')
      document.getElementById('VALIDATOR-5000').hidden=true;
      if  (document.getElementById('type_nickname'))document.getElementById('type_nickname').classList.remove('is-invalid')

      window.register_type = !window.register_type;
      if (window.register_type) {
        document.getElementById("container_of_form").innerHTML =
          '<div data-mdb-input-init  id="nickname-div" class="form-outline mb-4"><input type="text" class="form-control" id="type_nickname"><label class="form-label" for="type_nickname">Имя пользователя</label></div>' +
          document.getElementById("container_of_form").innerHTML;
        document.querySelectorAll(".form-outline").forEach((formOutline) => {
          new Input(formOutline).init();
        });
        document.getElementById("switch_button").innerHTML =
          "Вы уже зарегистрированы?";
        document.getElementById("login_button").innerHTML =
          "Зарегистрироваться";
        document.getElementById('VALIDATOR-5000').innerHTML='Пользователь с такой почтой или никнеймом уже существует'
        document.getElementById('VkIdSdkOneTap').hidden=true;
      } else {
        document.getElementById('VALIDATOR-5000').innerHTML='Неверный email или пароль'
        document.getElementById("nickname-div").remove();
        document.getElementById("switch_button").innerHTML =
          "Вы здесь впервые? Зарегистрируйтесь";
          document.getElementById('VkIdSdkOneTap').hidden=false;

        document.getElementById("login_button").innerHTML = "Войти";
      }
    });
  }
}
function search() {
  let text = document.getElementById("search_textbox").value==""?document.getElementById("search_textbox_small").value:document.getElementById("search_textbox").value;
  let url = new URL(window.location);
  url.pathname = "/";
  url.searchParams.set("text", text);
  window.location = url;
}
function register(type) {
  //type: logout- выход,register-регистрация,login-вход
  var data = { type: "logout" };
  
  if (type != "logout") {
    document.getElementById('type_email').classList.remove('is-invalid')
    document.getElementById('type_password').classList.remove('is-invalid')
    if (document.getElementById('type_nickname')) document.getElementById('type_nickname').classList.remove('is-invalid')
    if (type) {
      if (
        document.getElementById("type_nickname").value == "" ||
        document.getElementById("type_email").value == "" ||
        document.getElementById("type_password").value == ""
      ) {
        alert("Вводите НЕПУСТЫЕ ЗНАЧЕНИЯ в поля для ввода!");
        return false;
      }
      data = {
        type: "register",
        username: document.getElementById("type_nickname").value,
        email: document.getElementById("type_email").value,
        password: document.getElementById("type_password").value,
      };
    } else {
      if (
        document.getElementById("type_email").value == "" ||
        document.getElementById("type_password").value == ""
      ) {
        alert("Вводите НЕПУСТЫЕ ЗНАЧЕНИЯ в поля для ввода!");
        return false;
      }
      data = {
        type: "login",
        email: document.getElementById("type_email").value,
        password: document.getElementById("type_password").value,
      };
    }
  }
  axios.post("/api/login_register", data, {
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
    }).then((data) => {
      if (data.data.status == "Success") window.location.reload();
      else
      {
        document.getElementById('type_email').classList.add('is-invalid')
        document.getElementById('type_password').classList.add('is-invalid')
        document.getElementById('VALIDATOR-5000').hidden=false
        if (document.getElementById('type_nickname')) document.getElementById('type_nickname').classList.add('is-invalid')

      }
    });
}
function init_search()
{
  
  const ac=new Autocomplete(document.getElementById('search_textbox'),{
    data:[],
    onSelectItem:({label,value})=>
        {
            window.location.href=`/adverstiment?adv_id=${value}`;
        },
        fullWidth:true
})
const ac_small = new Autocomplete(document.getElementById('search_textbox_small'),{
    data:[],
    onSelectItem:({label,value})=>
        {
            window.location.href=`/adverstiment?adv_id=${value}`;
        },
    fullWidth:true
})
let timeoutId=null;
document.getElementById('search_textbox').addEventListener('input',()=>
{
    let text=document.getElementById('search_textbox').value
    if (!text) text=''
    if (timeoutId) clearTimeout(timeoutId)
    timeoutId= setTimeout(()=>
    {
        let data = {'destination':'search','text':text}
        axios.post('/api/get_adv',data,{headers:{'X-CSRFToken':document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((response)=>
          {
            ac.setData(response.data.advs)
          })
    },100)
})
document.getElementById('search_textbox_small').addEventListener('input',()=>
    {
      let text=document.getElementById('search_textbox_small').value
      if (!text) text=''
      if (timeoutId) clearTimeout(timeoutId)
      timeoutId= setTimeout(()=>
      {
        let data = {'destination':'search','text':text}
        axios.post('/api/get_adv',data,{headers:{'X-CSRFToken':document.querySelector('[name=csrfmiddlewaretoken]').value}}).then((response)=>
          {
            ac_small.setData(response.data.advs)
          })
      },100)
    })
document.addEventListener('keydown',(e)=>
{
    if (e.code=='Enter')
        {
            search();
        }
})
}
function get_notifications() {
  axios.get("/api/notifications").then((response) => {
    let data = response.data
    console.log(data)
    data.notifications.forEach(msg =>{
    document.getElementById('notifications_container').innerHTML='<li onclick=window.location=`'+msg.Url+'`><div class="row container border"><span>' +
    msg.Head +
    "</span><span>" +
    msg.Body +
    "  " +
    msg.Timestamp +
    "</span></div></li>";
  });
  document.getElementById("notif_count").innerHTML = "";
})
}
function related() {
  let url = new URL(window.location);
  url.pathname = "/profile";
  url.searchParams.set("use_favorite", true);
  window.location = url;
}
function click_adv_handler(ev) {
  ev.preventDefault();
  if (ev.target.className.indexOf("icon") > -1) {
    axios
      .post(
        "/api/adv_status_set",
        {
          status: "favorite",
          id: ev.target.parentElement.getAttribute("id_adv"),
        },
        {
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
              .value,
          },
        }
      )
      .then(() => {
        console.log(ev.target.className.indexOf("checked"))
        if (ev.target.className.indexOf("checked") > -1 ||ev.target.className.indexOf("checked_also") > -1) {
          if (ev.target.className.indexOf("checked_also") > -1)
            ev.target.classList.remove("checked_also");
          else ev.target.classList.remove("checked");
        } 
        else {

          ev.target.classList.add("checked");
        }
      });
  } else if (ev.target.id == "product_name" || ev.target.nodeName == "IMG") {
    let id = ev.target.parentElement.getAttribute("id_adv");
    let url = new URL(window.location);
    url.searchParams.set("adv_id", id);
    url.pathname = "/adverstiment";
    axios.post("/api/click_adv",{ id: id },
        {
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,},}).then(() => {
        window.location = url;
      });
  }
}
