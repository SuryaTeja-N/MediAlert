from app import create_app, get_db

app = create_app()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

if __name__ == '__main__':
    init_db()  # This will recreate the database tables
    app.run(debug=True)
