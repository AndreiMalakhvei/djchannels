import {useContext} from "react";
import ContextStorage from "../context/contextStorage";

const Login= () => {

    const {handleLogin} = useContext(ContextStorage)


    return (
            <div>
                <form onSubmit={handleLogin}>
                <label htmlFor="username">USERNAME</label>
                <input type="text" id="username"/>
                <label htmlFor="password">PASSWORD</label>
                <input type="password" id="password"/>
                <button type="submit">LOGIN</button>
            </form>
            </div>
    )
}

export default Login