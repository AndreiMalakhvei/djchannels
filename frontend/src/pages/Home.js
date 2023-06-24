import React, {useContext, useState, useEffect} from "react";
import PopupModal from "../components/UI/PopupModal";
import ContextStorage from "../context/contextStorage";
import axios from "axios";
import {NavLink, useHistory} from 'react-router-dom';

const Home= () => {
    let {user} = useContext(ContextStorage)
    const [error, setError] = useState()
    const history = useHistory();
    const [totalMissed, setTotalMissed] = useState(0)
    const [roomsList, setRoomsList] = useState([])


    // useEffect(() => {
    //         axios
    //             .get(`http://127.0.0.1:8000/chatapi/unread/`, {params: {user: user.user_id}})
    //             .then(response => {
    //                 setTotalMissed(response.data.total_missed)
    //             })
    //     }, []);



     useEffect( () =>{
       axios
        .get('http://127.0.0.1:8000/chatapi/roomslist/')
        .then(response => {setRoomsList(response.data)
        })
    }, []);

    const modalHandler = (e) => {
        setError({
        title: "Некорректный ввод",
        message: "Эти поля не могут быть пустыми",
      });
    }

    const errorHandler = () => {
    setError(false);
  };

    const handleCreateRoom = (e) => {
        e.preventDefault()
        axios
            .post('http://127.0.0.1:8000/chatapi/createroom/', {
                name: e.target.newroom.value,
                owner: user.user_id
                })
            .then(response => {
                if (response.status === 201) {
                console.log('CREATED SUCCESSFULLY')
                history.push(`/chat/${e.target.newroom.value}`);
                }
            })
            .catch(function (error) {
                console.log(error.toString())
            })
    }


    return (
        <div>
            {error && (
                <PopupModal
                    onCloseModal={errorHandler}
                    title={error.title}
                    message={error.message}
                />
            )}
            <p>This is Home Page</p>
            <button onClick={modalHandler}>Send</button>

            <form onSubmit={handleCreateRoom}>
                <label htmlFor="newroom" >ENTER NEW ROOM NAME</label>
                <input id="newroom" type="text"/>
                <button type="submit">CREATE</button>
            </form>

            {roomsList &&
            <div>
                {roomsList.map(
                    room =>
                        <div key={room.name}>
                        <NavLink to={`chat/${room.name}`} >{room.name}</NavLink>
                        </div>
                )}
            </div> }

            { user &&
                    <li className="menu-element">
                        <p>Welcome, {user.username} !</p>
                        <p>You`ve got {totalMissed} unread messages</p>
                </li>
                }

        </div>
    )
}

export default Home