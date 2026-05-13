from app import app

app.secret_key = "Inacap.2026"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
