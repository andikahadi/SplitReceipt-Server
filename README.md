# SplitReceipt
SplitReceipt is a Web-App that connect GrabFood receipts from Gmail, assign items in receipts to your friend, and  create an expense in Splitwise app (http://splitwise.com).
This full-stack application also serves to fulfill the academic requirements of General Assembly's Software Engineering Immersive capstone project.

 - SplitReceipt Client Repo : https://github.com/andikahadi/SplitReceipt-Client
 - SplitReceipt Server Repo : https://github.com/andikahadi/SplitReceipt-Server
 - Database structure : https://drawsql.app/teams/splitreceipt/diagrams/split-receipt

# To run the server

- Install dependencies in venv
```pip install -r requirements.txt```

- Create .env file in same location as manage.py
1) Create database in pgAdmin 4, and add these database info in .env
``` 
NAME = "your_database_name"
USER = "your_pgAdmin4_username"
PASSWORD= "your_password"
```

2) Register app in https://secure.splitwise.com/apps, with homepage url as http://localhost:5173, and callback url as http://localhost:5173/authorize
Put Splitwise consumer key and consumer secret in .env:
```
consumer_key = your_consumer_key
consumer_secret = your_consumer_secret
```

3) Create google credentials https://console.cloud.google.com/apis/credentials.
Create OAuth2.0 Client IDs, to get Client ID and Client secret
Add in .env:
```
client_id = your_client_id
client_secret = your_client_secret
```

- Remove 000X_initial.py files from EmployeeApp/migrations and users/migrations folders. Then do migration to form the database
```
python manage.py makemigrations
python manage.py migrate
```

- Run server
```
python manage.py runserver
```

# Technologies Used
Front-end
 - React.js
 - Typescript

Back-end
 - Django
 - Python

Database
 - Postgresql

# How the app works
SplitReceipt app communicates with both Google API and Splitwise API. The app fetches GrabFood receipts from user's Gmail, display these receipts in SplitReceipt app for user to assign ownership, and send the assignment as expense in Splitwise.

1) Require user to have Gmail that's connected to Grab Apps, and Splitwise user with friends added.

2) To use SplitReceipt app, user first register and login to SplitReceipt app. At the 'Account' page there are 2 buttons, to connect to Gmail and to connect to Splitwise API. Do authorization for both.

3) 'Connect to Gmail' button give access token, which is then used for get_message API. It search through inbox messages from last_email_fetch time, or 4 weeks prior if user is newly created.

4) 'Connect to Splitwise' button give access token, which is then used for create_expense API, and get_friends API. Friends list is stored in React state.

5) At 'Receipts' page, assign receipt to either 'Split' or 'Mine'. 

6) After selecting 'Split', items of the receipt are displayed. Assign each item by filling up input box by Splitwise_friend name, and click set.  Click "Splitwise" button to send create_expense API, which create expense in Splitwise apps.`



# Client Pages

| Url           | Page          |
| ------------- | ------------- |
| '/'           | Receipts      |
| '/history'   | History      |
| '/account'   | Account      |
| '/login'   | Login      |
| '/register'   | Login      |

# Server Endpoints

| Endpoint      | Method        | Description   |
| ------------- | ------------- |------------- |
| 'api/token/'| POST      |to login|
| 'api/token/refresh/'| POST      |to get new access token|
| 'api/user/register'| POST      |to register new account|
| 'api/user-read/'| POST      |to get current user info|
| 'api/user-read/'| GET      |to get list of all user for admin|
| 'api/user-delete/'| POST      |to delete user for admin      |
| 'api/splitwise/'| GET      |to get authorization url      |
| 'api/splitwise/'   | POST      |to get splitwise access token      |
| 'api/splitwise-friend/'| POST      |to get user Splitwise friends list|
| 'api/post-expense/'| POST      |to call Splitwise API creating expense     |
| 'api/get-receipt/'   | POST      |to get receipt from database      |
| 'api/gmail-receipt/'| POST      |get receipt email from inbox based on last fetch time|
| 'api/receipt-update/'| PATCH      |update database to note that receipt is assigned     |


