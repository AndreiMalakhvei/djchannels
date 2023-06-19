import styled from "../../Chat.module.css";
import React from "react";

const MessagesDisplay= (props) => {


    return (
        <div className={styled.chatcontainer}>
        <div className={styled.postwrapper}>
          {props.messages.map((message, index) => (
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

      </div>
    );
}

export default MessagesDisplay