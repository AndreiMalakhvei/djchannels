import React, {useState, useEffect, useContext, useRef} from "react";
import ContextStorage from "./context/contextStorage";
import styled from "./Chat.module.css"
import {useParams} from "react-router-dom";
import axios from "axios";
import Participants from "./components/buildblocks/Participants";
import MyRooms from "./components/buildblocks/MyRooms";
import MessagesDisplay from "./components/buildblocks/MessagesDisplay";
import PopupInvite from "./components/buildblocks/PopupInvite";
import Invitations from "./components/buildblocks/Invitations";

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
        setChatID(id)
    }

    useEffect(() => {
        console.log(`connecting to new room ${chatID}`)
        const newSocket = new WebSocket(`ws://localhost:8000/ws/chat/${chatID}/?user=${user.user_id}`);
        setSocket(newSocket);
        window.history.replaceState("", "", `http://localhost:3000/chat/${chatID}/`)

        // axios
        //     .get('http://127.0.0.1:8000/chatapi/roomslist/', {params: {user: user.user_id}})
        //     .then(response => {
        //
        //         setMyRooms(response.data)
        //     })

        newSocket.onopen = () => console.log("WebSocket connected");
        newSocket.onclose = () => console.log("WebSocket disconnected");
        return () => {
            newSocket.close();
        };
    }, [chatID]);


    useEffect(() => {
        axios
            .get('http://127.0.0.1:8000/chatapi/roomslist/', {params: {user: user.user_id}})
            .then(response => {

                setMyRooms(response.data)
            })
    }, [chatID]);


    useEffect(() => {
        axios
            .get('http://127.0.0.1:8000/chatapi/getinvitations/', {params: {user: user.user_id}})
            .then(response => {
                console.log(response.data)
                setInvitations(response.data)
            })
    }, [chatID]);



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
            .get(`http://127.0.0.1:8000/chatapi/chathistory/`, {params: {name: chatID}})
            .then(response => {
                setMessages(response.data)
            })
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
        const mess = {
            "mark": "invite",
            "data": data
        }
        socket.send(JSON.stringify(mess))
        setInvite(false)
    }

    const inviteAccept = (e, data) => {
        const mess = {
            "mark": "invite_accept",
            "data": data
        }
        socket.send(JSON.stringify(mess))
        setInvitations( (current) =>
            current.filter( (item) => item.chat !== data.chat && item.author !== data.author)
        )

        setChatID(data.chat)


    }

    const leaveChat = (e) => {
        const mess = {
            "mark": "leave_chat",
            "chat": chatID
        }
        socket.send(JSON.stringify(mess))
        roomSwitch(myRooms[0].name)
    }


    const inviteDecline = (e, data) => {
        const mess = {
            "mark": "invite_decline",
            "data": data
        }
        socket.send(JSON.stringify(mess))
        setInvitations( (current) =>
            current.filter( (item) => item.chat !== data.chat && item.author !== data.author)
        )
    }


    return (
        <div className={styled.dashboardwrappper}>

            {invite && <PopupInvite onCloseModal={onCloseInvite} sendInvitations={sendInvitations}
            room={chatID}/>}


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


            {invitations.length > 0 &&
                <Invitations invitationsList={invitations} accepted={inviteAccept} declined={inviteDecline}/>
            }

            <div className={styled.userslistwrapper}>
                <Participants/>
            </div>


            <div>
                <button type="submit" onClick={leaveChat}>LEAVE CURRENT CHAT</button>
            </div>

        </div>
                    );
                    }

export default Chat;
