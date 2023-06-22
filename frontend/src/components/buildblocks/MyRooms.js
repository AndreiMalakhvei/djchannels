import React, {useEffect, useState} from "react";
import axios from "axios";
import {NavLink} from "react-router-dom";
import styled from "./MyRoom.module.css"


const MyRooms = (props) => {
    // const [myRooms, setMyRooms] = useState([])

    const clickHandler = (e) => {
        e.preventDefault()
        props.switcher(e.target.value)
    }



    return (
        <React.Fragment>
            <div>
                <p>List of Rooms</p>
                {props.rooms &&
                    <div>
                        {props.rooms.map(
                            room =>
                                <div key={room.name}>
                                    <button onClick={clickHandler} className={styled.itemwrapper}
                                            value={room.name}>{room.name}</button>
                                    {room.name in props.missed && props.missed[room.name] > 0 &&
                                        room.name !== props.currentChat && <p>{props.missed[room.name]}</p>}
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
