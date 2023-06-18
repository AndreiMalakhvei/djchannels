import React from 'react';
import Chat from './Chat';
import {Route, Switch, Redirect} from 'react-router-dom';
import Layout from "./components/layout/Layout";
import Home from "./pages/Home";
import './App.css';
import Login from "./pages/Login";

function App() {
    return (
        <Layout>
            <Switch>
                <React.Fragment>
                <div>
                    <Route path='/' exact>
                        <Redirect to='/home'/>
                    </Route>
                    <Route component={Home} path='/home/' />
                    <Route component={Chat} path='/chat/:chatId'/>
                    <Route component={Login} path='/login/' />
                </div>
                </React.Fragment>
            </Switch>
         </Layout>
    );
}

export default App;
