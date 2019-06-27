# BSE Equities
App is designed to demonstrate use of redis as database. To run this application locally. 

##Run locally

####Install Redis Server
```
sudo apt update
sudo apt install redis-server
```
check the redis server status with
```
sudo systemctl status redis
```
####Setup the code
Clone git repository using 
```
git clone git@github.com:akashshah610/bse_equities.git
```

Go to the `bse_equities` directory and create virtual enviorment and install python requirements. 
Make sure you are creating virtual env with python `2.7.15`.
```
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
#### Configure redis url (Optional)
Create enviorment in file in root folder with name `.env` and below details.
```
REDIS_URL=redis://localhost:6379/0
```
or by setting env variable using command.
```
export REDIS_URL=redis://localhost:6379/0
```
#### Upload Data
Upload BSE equity price data to redis server
```
python -m scripts.refresh_equity_price
```

#### Run server
Run Cherrypy Server using
```
python -m web.app
```
Open browser by clicking this link http://0.0.0.0:8080/.