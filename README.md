# Recommendations Engine - Staging

## Setup
1. Start the MongoDB and flask containers in detached mode: `docker-compose up -d`
2. Test the app by visiting http://localhost:5000 and executing an endpoint, i.e http://localhost:5000/users


__Important__: *The app will hot reload whenever you save a file in your local workplace. This means you will be able to modify files in your IDE and the flask app will automatically reload without having to rebuild the docker container/app.*
