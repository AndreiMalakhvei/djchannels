import React, {useState, useEffect, useContext, useRef} from "react";
import ContextStorage from "./context/contextStorage";
import styled from "./Chat.module.css"
import {useParams} from "react-router-dom";
import axios from "axios";
import Participants from "./components/buildblocks/Participants";
import MyRooms from "./components/buildblocks/MyRooms";
import MessagesDisplay from "./components/buildblocks/MessagesDisplay";

function Chat() {
  const params = useParams()

  let {user} = useContext(ContextStorage)
  const [socket, setSocket] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [chatID, setChatID] = useState(params.chatId)


    const roomSwitch = (id) => {
    console.log(id)
    setChatID(id)
    }

   useEffect( () =>{
         axios
          .get(`http://127.0.0.1:8000/chatapi/chathistory/`, {params: {name: chatID}})
          .then(response => {setMessages(response.data)
          console.log(response.data)})
      }, [chatID]);


  useEffect(() => {
    // Connect to the WebSocket server with the username as a query parameter
    const newSocket = new WebSocket(`ws://localhost:8000/ws/chat/${params.chatId}/?user=${user.user_id}`);
    setSocket(newSocket);
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
        setMessages((prevMessages) => [...prevMessages, data]);
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


  return (
      <div className={styled.dashboardwrappper}>
       <div className={styled.channelslistwrapper}>
         <div className={styled.userslistwrapper}>
          <MyRooms switcher={roomSwitch} currentChat={chatID}/>
        </div>
       </div>

      <MessagesDisplay  messages={messages}  sendHandler={handleSubmit}   />

       <form onSubmit={handleSubmit}>
          <input type="text" placeholder="Type a message..." value={message}
              onChange={(event) => setMessage(event.target.value)}
          />
          <button type="submit">Send</button>
        </form>

        <div className={styled.userslistwrapper}>
          <Participants />
        </div>
  </div>
  );
}
export default Chat;
