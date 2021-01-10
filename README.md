# Recommendations Engine

## Setup
1. Start the MongoDB database in detached mode: `docker-compose up -d mongo`
2. Start the flask app (attached) in order to view console logs:
`docker-compose up pyapp
3. Test the app by visiting http://localhost:5000 and executing an endpoint, i.e http://localhost:5000/users


__Important__: *The app will hot reload whenever you save a file in your local workplace. This means you will be able to modify files in your IDE and the flask app will automatically reload without having to rebuild the docker container/app.*