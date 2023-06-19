import React, {useEffect, useState} from "react";
import axios from "axios";
import {NavLink} from "react-router-dom";


const MyRooms = (props) => {
    const [myRooms, setMyRooms] = useState([])

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
                                    <button >{room.name}</button>
                                </div>
                        )}
                    </div>
                }
            </div>
        </React.Fragment>
);

}

export default MyRooms
