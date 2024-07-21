import axios from "axios";
import "../chat/chat.scss"
import {get_notifications,notify_connect} from '../headers_file';
import { Ripple,Input, initMDB,Dropdown } from 'mdb-ui-kit/js/mdb.es.min.js';
var set_user_from_el = (el)=>
    {
        var adv_id = el.id.match(/^user_\d+:adv_(\d+)$/);
        if (adv_id) {
            return {"el":el,"username":el.children[0].children[1].children[0].innerHTML,"adv":adv_id[1]};
        } else {
            return {"el":el,"username":el.children[0].children[1].children[0].innerHTML,"adv":null};
        }
    }
var selected_user = null;
document.onreadystatechange= function()
{
    if (document.readyState=="interactive")
        {
            document.getElementById("chat-users").addEventListener('click',(e)=>
                {
                    e.preventDefault()
                    console.log(e)
                    if (e.target.id !="chat-users")
                        {
                            let parent = e.target.closest(".list-group-item")
                            document.getElementById("chat-messages").innerHTML="";
                            selected_user = set_user_from_el(parent);
                            axios.post("/api/chat",{"type":"get_messages","to_user":selected_user.username,"adv_id":selected_user.adv},{headers:{"X-CSRFToken":document.getElementsByName("csrfmiddlewaretoken")[0].value}}).then((resp)=>
                                { 
                                    let message_container = document.getElementById("chat-messages")
                                    resp.data["messages"].forEach((msg)=>
                                        {
                                            message_container.innerHTML=`<div class="list-group-item ${msg.you?'text-end':''}"><div><span class="ellipse_message ${msg.you?'you':''}">${msg.you?"Вы":msg.username}:${msg.text}</span></div></div>` + message_container.innerHTML;
                                        })
                                })
                        }
                })
            let pres_users = document.getElementsByClassName("preselected_user");
            if (pres_users.length>0){
                selected_user = set_user_from_el(pres_users[0])
                selected_user.el.click()
                }
                axios.post("/api/chat",{type:"last_messages"},{headers:{"X-CSRFToken":document.getElementsByName('csrfmiddlewaretoken')[0].value}}).then((resp)=>{
                    setLastMessages(resp.data);
                })
            notify_connect('studentmarket.site')
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            sendMessage()
        }
    })
            var socket = new WebSocket("wss://studentmarket.site/ws/chat");
    install_socket()
    document.getElementById("notify_get").addEventListener("click",get_notifications)
    initMDB({Input,Ripple,Dropdown})
    function install_socket(){
        socket.onmessage=function(ev){
            let data = JSON.parse(ev.data); //ev.data
            if (data["type"]=="message"){ 
                if (selected_user){
                console.log(data)
                if (`user_${data["user-id"]}:adv_${data["adv_id"]}`==selected_user.el.id){
                document.getElementById("chat-messages").innerHTML=document.getElementById("chat-messages").innerHTML+`<div class="list-group-item ${data["you"]?'text-end':''}"><div><span class="ellipse_message ${data["you"]?'you':''}">${data["you"]?"Вы":data['username']}:${data['message']}</span></div></div>`
                }
            }
                if (document.getElementById(`user_${data["user-id"]}:adv_${data["adv_id"]}`))
                    {
                document.getElementById(`user_${data["user-id"]}:adv_${data["adv_id"]}`).children[0].children[1].children[2].innerHTML=data["username"]+":"+data["message"]
                }
            }
            
            
        }
        socket.onopen=function(ev){
           
        }
        socket.onclose = function(e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function() {
        socket = new WebSocket("ws://127.0.0.1:8000/ws/chat");
        install_socket();
        }, 1000);
    };
    }
    function sendMessage(){
        if (selected_user){
        socket.send(JSON.stringify({type:'text',request_type:"send",to_user:selected_user.username,message:document.getElementById("chat-input").value,adv_id:selected_user.adv}))
        }
    }
window.sendMessage=sendMessage
        }
}
function setLastMessages(data)
{
    const el = document.getElementById('chat-users').childNodes
                let i = 0;
                data['last_messages'].forEach(data => 
                    {

                        let user_li = document.getElementById(`user_${data.second_user.id}:adv_${data['adv_id']}`)
                        console.log(data)
                        if (user_li.className=="list-group-item border" || user_li.className=="preselected_user list-group-item border"){
                        user_li.children[0].children[1].children[2].innerHTML=`${data["author"]["username"]==data["second_user"]["username"]?data['author']['username']:"Вы"}:${data['text']}`
                        }
                    });
}
