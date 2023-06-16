import React, {useState, useEffect, useContext} from "react";
import ContextStorage from "./context/contextStorage";
import styled from "./Chat.module.css"

function Chat() {

  let {user} = useContext(ContextStorage)

  const [socket, setSocket] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {

    // Connect to the WebSocket server with the username as a query parameter
    const newSocket = new WebSocket(`ws://localhost:8000/ws/chat/11/`);
    setSocket(newSocket);

    newSocket.onopen = () => console.log("WebSocket connected");
    newSocket.onclose = () => console.log("WebSocket disconnected");

    // Clean up the WebSocket connection when the component unmounts
    return () => {
      newSocket.close();
    };
  }, []);

  useEffect(() => {
    if (socket) {
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data)
        setMessages((prevMessages) => [...prevMessages, data]);
        console.log(messages)

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
      <div className="chat-container">
        <div className={styled.postwrapper}>

          {messages.map((message, index) => (
              <div key={index} className={styled.post}>
                <div className={styled.postheader}>
                  <p>{message.username}</p>
                </div>
                <div className={styled.postmain}>
                  <div className={styled.postavatar}>
                    <div className={styled.avatarcircle}></div>
                  </div>
                  <div className={styled.postmessage}>
                    <p>{message.message}</p>
                  </div>
                </div>
                <div className={styled.postfooter}>
                  <p>{message.nowdate}, {message.nowtime}</p>
                </div>

              </div>
          ))}

        </div>


        <form onSubmit={handleSubmit}>
          <input
              type="text"
              placeholder="Type a message..."
              value={message}
              onChange={(event) => setMessage(event.target.value)}
          />
          <button type="submit">Send</button>
        </form>
      </div>
  );
}
export default Chat;