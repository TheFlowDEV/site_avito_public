import '../register_oauth/register_oauth.scss'
import { Ripple,Input, initMDB } from 'mdb-ui-kit/js/mdb.es.min.js';
document.onreadystatechange = function()
{

    if (document.readyState=="interactive")
        {
            initMDB({Input,Ripple})
            document.getElementById("login").addEventListener("click",()=>{
                document.getElementById("buttons_container").hidden=true
                document.getElementById("login_form_container").hidden=false
            })
            document.getElementById("register").addEventListener("click",()=>{
                document.getElementById("buttons_container").hidden=true
                document.getElementById("registration_form_container").hidden=false
            })
        }
}