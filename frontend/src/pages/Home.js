import React, {useState} from "react";
import PopupModal from "../components/UI/PopupModal";

const Home= () => {
    const [error, setError] = useState()

    const modalHandler = (e) => {
        setError({
        title: "Некорректный ввод",
        message: "Эти поля не могут быть пустыми",
      });
    }

    const errorHandler = () => {
    setError(false);
  };


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

        </div>
    )
}

export default Home