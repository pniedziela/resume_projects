import streamlit as st 
from st_social_media_links import SocialMediaIcons
social_media_links = [
    "https://www.linkedin.com/in/pniedziela96/"
]

social_media_icons = SocialMediaIcons(social_media_links)



def main():
    st.set_page_config(page_title="Main")
    
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>

    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: white;'>Przemysław Niedziela</h1>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color: gray;'>Software Engineer | ML Engineer | AI Enthusiast | PhD Candidate</h5>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<sub>If you wish to contact me: pniedziela96@gmail.com / LD</sub>",  unsafe_allow_html=True)
    
    st.divider()

    st.write(
        """:blue[Hi!] This page serves as a container and repository for my hobby software projects :blue[(you can find
        them all on the left side of the screen on the separate menu)]. I use them as a practical intro to all new algorithms/software/technologies 
        I wish to learn/get comfortable with. Feel free to try them, just keep in mind these are not commercial and :rainbow[usually] I don't try to beat Google with them! :)"""
    )
    st.divider()
    social_media_icons.render()
    
if __name__ == "__main__":
    main()
