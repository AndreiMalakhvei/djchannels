import styled from "./PopupModal.module.css";
import React from "react";
import ReactDom from "react-dom";

const Backdrop = (props) => {
  return <div className={styled.backdrop} onClick={props.onCloseModal}></div>;
};

const Modal = (props) => {
  return (
    <div className={styled.modal}>
      <header className={styled.header}>
        <h2>{props.title}</h2>
      </header>
      <div className={styled.content}>
        <p>{props.message}</p>
      </div>
      <footer className={styled.actions}>
        <button className={styled.modalbutton} onClick={props.onCloseModal}>Закрыть</button>
      </footer>
    </div>
  );
};

const PopupModal = (props) => {


    return (
           <React.Fragment>
      {ReactDom.createPortal(
        <Backdrop onCloseModal={props.onCloseModal} />,
        document.getElementById("backdrop")
      )}
      {ReactDom.createPortal(
        <Modal
          title={props.title}
          message={props.message}
          onCloseModal={props.onCloseModal}
        />,
        document.getElementById("modal")
      )}
    </React.Fragment>
    )
}

export default PopupModal