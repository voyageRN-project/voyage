import "./FooterStyles.css"
import logo from "../photos/BB logo.jpg"

const Footer =() =>{
    return(
        <div className="footer">
            <div className="top">
                <div>
                <img src={logo}/>
                   
                    </div>
                    <div>
                    <a href="/">
                        <i className="fa-brands fa-facebook-square"></i>
                    </a>
                    <a href="/">
                        <i className="fa-brands fa-instagram-square"></i>
                    </a>
                    <a href="/">
                        <i className="fa-brands fa-behance-square"></i>
                    </a>
                    <a href="/">
                        <i className="fa-brands fa-twitter-square"></i>
                    </a>
                </div>
            </div>


            <div className="bottom">
                <div>
                    <h4>PROJECT</h4>
                    <a href="/">Afeka</a>
                    <a href="/">Final Project</a>
                    <a href="/">Neta & Roni</a>
                </div>
                <div>
                    <h4>COMMUNITY</h4>
                    <a href="/">GitHub</a>
                    <a href="/">Twitter</a>
                    <a href="/">Issues</a>
                </div>
                <div>
                    <h4>HELP</h4>
                    <a href="/">Support</a>
                    <a href="/">Contact Us</a>
                    <a href="/">Businesses Support</a>
                </div>
                <div>
                    <h4>OTHERS</h4>
                    <a href="/">Terms of Service</a>
                    <a href="/">Privacy Policy</a>
                    <a href="/">License</a>
                </div>
            </div>

        </div>
    )
}

export default Footer