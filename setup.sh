mkdir -p ~/.streamlit/
echo "[general]
email = \"ltddan82@googlemail.com\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml