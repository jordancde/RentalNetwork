
import axios from 'axios';
import Querystring from 'querystring';

var CLIENT_ID = "44ZjkxFgtKsGTcrRzTY5xb7d3MhrVuuvtPLrV0vN";
var CLIENT_SECRET = "PyQTNe7VDtDMtaxmw83XDubbwNRPz6MBXvPXsZlhsQDRc7OjQPRwoZg17rAO1KC7cCSqUH43NInoEswzX3r7rIbmvDFaOOwn9DNpwPeqijcBRT2ZVIuQU28c0hfTt8w8";

var TOKEN_URL_BASE = "http://localhost:8000/";

export function signin(credentials,obj,_callback){
    
    var TOKEN_URL=TOKEN_URL_BASE+"o/token/";

    const tokendata = {
        grant_type: "password",
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        scope: 'user',
        username: credentials.username,
        password: credentials.password
    };

    axios.post(TOKEN_URL, Querystring.stringify(tokendata))   
    .then(response => {
        var token = response.data.access_token;
        var refresh_token = response.data.refresh_token;
        localStorage.setItem("token", token);
        localStorage.setItem("refresh_token", refresh_token);
        _callback(obj,"");
    })   
    .catch((error) => {
        console.log('error ' + error.toString());  
        _callback(obj,error.toString()); 
    });
}

export function refresh(){

    var TOKEN_URL=TOKEN_URL_BASE+"o/token/";

    const tokendata = {
        grant_type: "refresh_token",
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
        refresh_token: localStorage.getItem("refresh_token")
    };
    axios.post(TOKEN_URL, Querystring.stringify(tokendata))   
    .then(response => {
        var token = response.data.access_token;
        var refresh_token = response.data.refresh_token;
        localStorage.setItem("token", token);
        localStorage.setItem("refresh_token", refresh_token);
    })   
    .catch((error) => {
        console.log('error ' + error.toString());  
    });
}

export function logout(){
    var TOKEN_URL=TOKEN_URL_BASE+"o/revoke_token/";

    const tokendata = {
        token: localStorage.getItem("token"),
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
    };
    
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    axios.post(TOKEN_URL, Querystring.stringify(tokendata))   
    .then(response => {
        console.log(response);
    })   
    .catch((error) => {
        console.log('error ' + error.toString());  
    });
}

export function authGET(URL,obj,_callback){
    var USER_TOKEN = localStorage.getItem("token");
    const AuthStr = 'Bearer '.concat(USER_TOKEN); 
    axios.get(URL, { headers: { Authorization: AuthStr } })
    .then(response => {
        _callback(response.data,obj);
    })
    .catch((error) => {
        console.log('error ' + error.toString());
    });
}

export function authPOST(URL,data,obj,_callback){
    var USER_TOKEN = localStorage.getItem("token");
    const AuthStr = 'Bearer '.concat(USER_TOKEN); 
    axios.post(URL,data, { headers: { Authorization: AuthStr } })
    .then(response => {
        _callback(response.data,obj);
    })
    .catch((error) => {
        console.log('error ' + error.toString());
    });

}




