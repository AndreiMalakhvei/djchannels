import React from "react";

const Invitations = (props) => {


   return (<div>
                    {props.invitationsList.map((invitation, index) =>
                        <div key={index}>
                            <h4>Invitation to chat {invitation.chat} recieved from user {invitation.author}</h4>
                            <button onClick={((e) => props.accepted(e, invitation))}>ACCEPT</button>
                            <button onClick={((e) => props.declined(e, invitation))}>DECLINE</button>
                        </div>
                    )
                    }
                </div>);
}

export default Invitations