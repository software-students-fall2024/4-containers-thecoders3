![Lint-free](https://github.com/software-students-fall2024/4-containers-thecoders3/actions/workflows/lint.yml/badge.svg)
![ML-Client build & test](https://github.com/software-students-fall2024/4-containers-thecoders3/actions/workflows/build.yaml/badge.svg)
![Web-App build & test](https://github.com/software-students-fall2024/4-containers-thecoders3/actions/workflows/web-app.yaml/badge.svg)

## Team members

* Wilson Xu [Profile](https://github.com/wilsonxu101)
* Hanna Han [Profile](https://github.com/HannaHan2)
* Sewon Kim [Profile](https://github.com/SewonKim0)
* Rhan Chen [Profile](https://github.com/xc528)

## Description

This project is a web-based application that converts user speech into text. Users can speak into their device's microphone, and the application processes the audio to display the corresponding text on the web interface. Additionally, users can edit the text and copy it elsewhere if desired.

## Steps to run the software

1. Clone this repository to the editor in your computer

2. Install and run the ```Docker Desktop```

3. Run the app: 
```
docker-compose up --build
```

4. View the app in your browser: 

open a web browser and go to [link](http://127.0.0.1:5001)

## Steps to run the test for machine-learning-client

1. use ```cd``` navigate to the machine-learning-client directory, for example:
```
cd machine-learning-client
```

2. Set up a virtual environment and install dependencies: 
```
pip install pipenv
pipenv install
pipenv shell
```

3. Run tests: 
```
python3 -m pytest
```

4. If you want to check the code coverage of the code, run: 
```
coverage run -m pytest
coverage report -m
```

## Steps to run the test for web-app

1. Install ```FFmpeg```. For example, if you want to install ```FFmpeg``` on Mac, you can use ```Homebrew```:
```
brew install ffmpeg
```

2. use ```cd``` navigate to the web-app directory, for example:
```
cd web-app
```

3. Set up a virtual environment and install dependencies: 
```
pip install pipenv
pipenv install
pipenv shell
```

4. Run tests: 
```
python3 -m pytest
```

5. If you want to check the code coverage of the code, run: 
```
coverage run -m pytest
coverage report -m
```