RUN THE FOLLOWING COMMAND FOR INITIALIZATION

pip install -r requirement.txt

flask db init

flask db migrate -m "initial mirate"

flask db upgrade