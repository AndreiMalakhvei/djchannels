import {NavLink} from "react-router-dom";
import {useContext, useEffect, useState} from "react";
import ContextStorage from "../../context/contextStorage";
import axios from "axios";

const Header = () => {

    let {user, logoutUser} = useContext(ContextStorage)

    return (
        <nav>
            <ul className="menu">
                <li className="menu-element">
                    <NavLink to='/home' className="navbar-text">Home</NavLink>
                </li>
                <li className="menu-element">
                    <NavLink to='/chat' className="navbar-text">Chat</NavLink>
                </li>

                { user &&
                    <li className="menu-element">
                        <p>Welcome, {user.username} !</p>

                </li>
                }


                { user?
                    (<li className="menu-element">
                     <NavLink to='/#' onClick={logoutUser} className="navbar-text">LogOut</NavLink>
                </li>) :

                    (<li className="menu-element">
                        <NavLink to='/login' className="navbar-text">LogIn</NavLink>
                    </li>)
                }
            </ul>
        </nav>
    );
};

export default Header;