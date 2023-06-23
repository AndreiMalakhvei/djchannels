import styled from "./PopupInvite.module.css";
import React, {useContext, useEffect, useState} from "react";
import ReactDom from "react-dom";
import axios from "axios";
import Select from 'react-select'
import makeAnimated from 'react-select/animated';
import ContextStorage from "../../context/contextStorage";


const Backdrop = (props) => {
  return <div className={styled.backdrop} onClick={props.onCloseModal}></div>;
};

const Modal = (props) => {

    const options = []
    props.usersList.map(item => {
        options.push({"value": item.id, "label": item.username})
    })

    const animatedComponents = makeAnimated();
    const [chosen, setChosen] = useState([])

    const handleOnChange = (selected) => {
        setChosen(selected)
    }

    const sendInvitations = () => {
        props.sendInvitations(chosen)
    }

  return (
    <div className={styled.modal}>
      <header className={styled.header}>
        <h2>{props.title}</h2>
      </header>

         <Select
      closeMenuOnSelect={false}
      components={animatedComponents}
      // defaultValue={}
      isMulti
      options={options}
      onChange={handleOnChange}
    />

      <footer className={styled.actions}>
        <button className={styled.modalbutton} onClick={props.onCloseModal}>Close</button>
        <button className={chosen.length > 0 ? styled.modalbutton: styled.dis} onClick={sendInvitations}
        disabled={!chosen} >Invite</button>
      </footer>
    </div>
  );
};

const PopupInvite = (props) => {
    let {user} = useContext(ContextStorage)
    const [users, setUsers] = useState([])
    useEffect(() => {
        axios
            .get('http://127.0.0.1:8000/chatapi/userslist/', {params: {room:props.room}})
            .then(response => {
                setUsers(response.data)
            })
    }, []);




    return (
           <React.Fragment>
      {ReactDom.createPortal(
        <Backdrop onCloseModal={props.onCloseModal} />,
        document.getElementById("backdrop")
      )}
      {ReactDom.createPortal(
        <Modal usersList={users} onCloseModal={props.onCloseModal} sendInvitations={props.sendInvitations}/>,
        document.getElementById("modal")
      )}
    </React.Fragment>
    )
}

export default PopupInvite