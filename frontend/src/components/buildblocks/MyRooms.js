import React, {useEffect, useState} from "react";
import axios from "axios";
import {NavLink} from "react-router-dom";
import styled from "./MyRoom.module.css"


const MyRooms = (props) => {
    const [myRooms, setMyRooms] = useState([])

    const clickHandler = (e) => {
        e.preventDefault()
        props.switcher(e.target.value)
    }

    useEffect( () =>{
       axios
        .get('http://127.0.0.1:8000/chatapi/roomslist/')
        .then(response => {setMyRooms(response.data)
        console.log(response.data)})
    }, []);

    return (
        <React.Fragment>
            <div>
                <p>List of Rooms</p>
                {myRooms &&
                    <div>
                        {myRooms.map(
                            room =>
                                <div key={room.name}>
                                    <button onClick={clickHandler} className={styled.itemwrapper}
                                            value={room.name}>{room.name}</button>
                                    {props.currentChat === room.name && <p>CURRENT</p>}
                                </div>
                        )}
                    </div>
                }
            </div>
        </React.Fragment>
);

}

export default MyRooms
