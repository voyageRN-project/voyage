import { Component } from "react";
import "./NavBarStyles.css";
import {Link} from "react-router-dom";
import { MenuItems } from "./MenuItems";
import logo from "../photos/‏‏logowithoutline.jpg"


class NavBar extends Component {
    state = {clicked : false};
    handleClicked = () =>{
        this.setState({clicked: !this.state.clicked})
    }
    render() {
        return(
            <nav className="NavBarItems">
                 <Link to="/" className="navbar-logo">
                    <img src={logo}/>
                </Link>
                <div className="menu-icon" onClick={this.handleClicked}>
                    <i className={this.state.clicked ? "fas fa-times" : "fas fa-bars"}></i>
                </div>


                <ul className={this.state.clicked ? "nav-menu active" : "nav-menu"} >
                    {MenuItems.map((item, index) => {
                        return(
                             <li key={index}>
                        <Link className= {item.cName} to= {item.url}>
                        <i className={item.icon}></i>{item.title}
                        </Link>
                    </li>
                        )
                    })}
                   
                </ul>
            </nav>
        )
    }
} 


export default NavBar;