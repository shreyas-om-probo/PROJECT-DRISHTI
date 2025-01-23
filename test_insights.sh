cd INSIGHTS_API || { echo "INSIGHTS API directory not found! Exiting."; exit 1; }
uvicorn INSIGHTS_API:app --host 127.0.0.1 --port 8003 &

cd ../TWITTER_API || { echo "TWITTER API directory not found! Exiting."; exit 1; }
uvicorn TWITTER_API:app --host 127.0.0.1 --port 8002 &

cd ../|| { echo "Root directory not found! Exiting."; exit 1; }
FLASK_APP_PATH="TEST_UI_V3.py"
python "$FLASK_APP_PATH" --host=0.0.0.0 --port=8080 &
wait