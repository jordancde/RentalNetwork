import React from 'react';
import ReactDOM from 'react-dom';
import './css/index.css';
import { BrowserRouter, Switch, Route } from 'react-router-dom';
import registerServiceWorker from './utils/registerServiceWorker';
import Login from './components/Login';
import UserDetails from './components/UserDetails';

//<Route exact path='/' component={Home}/>
ReactDOM.render((
    <BrowserRouter>
        <Switch>
            <Route exact path='/' component={Login}/>
            <Route path='/user' component={UserDetails}/>
        </Switch>
    </BrowserRouter>
), document.getElementById('root'))

registerServiceWorker();
