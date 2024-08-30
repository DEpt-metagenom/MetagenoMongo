## 1. Clone https://github.com/DEpt-metagenom/MetagenoMongo.git

## 2.Download python libraries. Run the command in the app root directory
pip install -r requirements.txt

## 3.Set environment variables.
https://github.com/DEpt-metagenom/intern_tasks/issues/8#issuecomment-2307166696

## (Optional) please comment out the following part in app.py if you run the app on your labtop--
if os.getenv('META_REMOTE_PATH') is None or os.getenv('META_KEY_PATH') is None:
     current_app.logger.error("META_REMOTE_PATH or META_KEY_PATH is missing.")
     raise EnvironmentError("Required environment variables are not set.")

## 4.Run the application in the app root directory
python flask-version/metagenomongo/app.py

## 5.Access http://localhost:5000/


## (Optional) Save files to the remote server function
1. Login to the GPU server 2 (gpu2)
2. Run the application at the app root directory
3. Import or input valid data
4. Click the button "Save as csv"
5. Login to the GPU server 3 (gpu3)
6. Follow the instructions at: https://github.com/DEpt-metagenom/intern_tasks/issues/8#issuecomment-2307166696
