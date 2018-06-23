import React, { Component } from 'react';
import {authGET,logout} from '../apis/auth';
import { Redirect } from 'react-router';
import '../css/UserDetails.css';

export default class UserDetails extends React.Component{
    constructor(props) {
      super(props);
      this.state = {
        userdetails:{
          username:"",
          email:"",
          first_name:"",
          last_name:"",
          date_joined:""
        },
        loggedIn:true
      };

      authGET("http://localhost:8000/userdetail/",this, function(response,obj){
        obj.setState({ userdetails : response});
      });

      this.handleLogout = this.handleLogout.bind(this);
    }
  
    async handleLogout(event) {
      logout();
      this.setState({ loggedIn : false });
      event.preventDefault()
    }
  
    render() {
      if (!this.state.loggedIn) {
        return <Redirect to='/' />
      }
      return (
        <div className="UserDetails">
          <div className="card">
            <header>Profile</header>
            <label>Username: <span>{this.state.userdetails.username}</span></label>
            <hr className="divider"/>
            <label>Email: <span>{this.state.userdetails.email}</span></label>
            <hr className="divider"/>
            <label>First Name: <span>{this.state.userdetails.first_name}</span></label>
            <hr className="divider"/>
            <label>Last Name: <span>{this.state.userdetails.last_name}</span></label>
            <hr className="divider"/>
            <label>Date Joined: <span>{this.state.userdetails.date_joined}</span></label>
            <button onClick={this.handleLogout} className="logout-button">Logout</button>
          </div>
        </div>
      );
    }
  }