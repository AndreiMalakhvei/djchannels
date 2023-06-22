import React, {useState, useEffect, useContext, useRef} from "react";
import ContextStorage from "./context/contextStorage";
import styled from "./Chat.module.css"
import {useParams} from "react-router-dom";
import axios from "axios";
import Participants from "./components/buildblocks/Participants";
import MyRooms from "./components/buildblocks/MyRooms";
import MessagesDisplay from "./components/buildblocks/MessagesDisplay";
import PopupInvite from "./components/buildblocks/PopupInvite";

function Chat() {
    const params = useParams()

    let {user} = useContext(ContextStorage)
    const [socket, setSocket] = useState(null);
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]);
    const [chatID, setChatID] = useState(params.chatId)
    const [missedMessages, setMissedMessages] = useState({})
    const [invite, setInvite] = useState(false)
    const [invitations, setInvitations] = useState([])

    const [myRooms, setMyRooms] = useState([])

    const roomSwitch = (id) => {
        console.log(id)
        setChatID(id)
    }


    const dispatchData = (data) => {
        if (data.mark === "chat message") {
            setMessages((prevMessages) => [...prevMessages, data])
        } else if (data.mark === "service") {
            setMissedMessages((prevState) => {
                return {...prevState, [data.chat]: data.quantity}
            })
        } else if (data.mark === "missed") {
            setMissedMessages(data.missed)
        } else if (data.mark === "invite") {
            setInvitations((prevMessages) => [...prevMessages, data.data])
        }
    }


    useEffect(() => {
        axios
            .get('http://127.0.0.1:8000/chatapi/roomslist/')
            .then(response => {
                setMyRooms(response.data)
            })
    }, []);

    useEffect(() => {
        axios
            .get(`http://127.0.0.1:8000/chatapi/chathistory/`, {params: {name: chatID}})
            .then(response => {
                setMessages(response.data)
            })
    }, [chatID]);

    useEffect(() => {
        console.log(`connecting to new room ${chatID}`)
        const newSocket = new WebSocket(`ws://localhost:8000/ws/chat/${chatID}/?user=${user.user_id}`);
        setSocket(newSocket);
        window.history.replaceState("", "", `http://localhost:3000/chat/${chatID}/`)
        newSocket.onopen = () => console.log("WebSocket connected");
        newSocket.onclose = () => console.log("WebSocket disconnected");
        return () => {
            newSocket.close();
        };
    }, [chatID]);

    useEffect(() => {
        if (socket) {
            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                dispatchData(data)
            };
        }
    }, [socket]);

    const handleSubmit = (event) => {
        event.preventDefault();
        if (message && socket) {
            let jetzt = new Date()
            const data = {
                message: message,
                username: user.username,
                jetzt: jetzt.getTime(),
                userid: user.user_id
            };
            socket.send(JSON.stringify(data));
            setMessage("");
        }
    };

    const modalSendHandler = (e) => {
        setInvite(true)
    }

     const onCloseInvite = (e) => {
        setInvite(false)
    }

    const sendInvitations = (data) => {
        console.log(data)
        const mess = {
            "mark": "invite",
            "data": data
        }
        socket.send(JSON.stringify(mess))
        setInvite(false)
    }


    return (
        <div className={styled.dashboardwrappper}>

            {invite && <PopupInvite onCloseModal={onCloseInvite} sendInvitations={sendInvitations}/>}


            <div className={styled.channelslistwrapper}>
                <div className={styled.userslistwrapper}>
                    <MyRooms switcher={roomSwitch} currentChat={chatID} rooms={myRooms} missed={missedMessages}/>
                </div>
            </div>

            <MessagesDisplay messages={messages} sendHandler={handleSubmit}/>

            <form onSubmit={handleSubmit}>
                <input type="text" placeholder="Type a message..." value={message}
                       onChange={(event) => setMessage(event.target.value)}
                />
                <button type="submit">Send</button>
            </form>


            <div>
                <button type="submit" onClick={modalSendHandler}>INVITE TO CHAT</button>
            </div>


            {invitations &&
                <div>
                    {invitations.map((invitation, index) =>
                        <div>
                            <h4>Invitation to {invitation.chat} recieved from {invitation.author}</h4>
                            <button value={index}>ACCEPT</button>
                            <button value={index}>DECLINE</button>
                        </div>
                    )
                    }
                </div>
            }

            <div className={styled.userslistwrapper}>
                <Participants/>
            </div>

        </div>
                    );
                    }

export default Chat;
