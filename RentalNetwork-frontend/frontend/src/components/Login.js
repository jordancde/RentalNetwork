import React, { Component } from 'react';
import {signin} from '../apis/auth';
import '../css/Login.css';
import { Redirect } from 'react-router'

export default class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {
          username: "", 
          password: "", 
          error: "", 
          loggedIn: localStorage.getItem("token")!=null
        };
        
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);
      }

      handleSubmit(event) {
        var credentials = { username: this.state.username, password: this.state.password };
        if(!this.state.username||!this.state.password){
          this.setState({ error : "One or more fields left blank."});
        }else{
          signin(credentials,this, function(obj,error){

            if(error==""){
              obj.setState({ loggedIn : true});
            } else if(error.indexOf("401")>=0){
              obj.setState({ error: "Invalid username/password."});
            }else if(error.indexOf("Network Error")>=0){
              obj.setState({ error: "Server is offine or unreachable."});
            }else{
              obj.setState({ error: "Error." });
            }

          });
        }
        event.preventDefault();
      }

      handleChange(event) {
        const target = event.target;
        const value = target.value
        const name = target.name;
        this.setState({
          [name] : value
        });
      }
    
      render() {
        if (this.state.loggedIn) {
          return <Redirect to='/user' />
        }
        return (
          <form className="login" onSubmit={this.handleSubmit} >
            <h1 className="login-title">Login</h1>
            <input type="text" value={this.state.username} name="username" onChange={this.handleChange} className="login-input" placeholder="Email" autoFocus/>
            <input type="password" value={this.state.password} name="password" onChange={this.handleChange} className="login-input last-field" placeholder="Password" autoFocus/>
            <p className="error" hidden={!this.state.error}>{this.state.error}</p>
            <input type="submit" value="Lets Go" className="login-button" onClick={this.handleSubmit}/>
          </form>
        );
      }
}
