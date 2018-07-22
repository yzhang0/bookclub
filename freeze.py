from flask_frozen import Freezer
from application import app

# app.run(debug=True)
freezer = Freezer(app)
if __name__ == '__main__':
    freezer.freeze()
