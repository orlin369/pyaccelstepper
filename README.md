# pyaccelstepper

## Review

This library is dedicated to controll stepper motors via python language.
This source is originaly inspired and up to the high degree copied from [here](https://github.com/waspinator/AccelStepper).
Original software is arduino based.

This library is designet to work with several software platforms.
 - Windows
 - Linux
 - OSx
 - Micro Python
 
The hardware platforms that mycro python is tested on:
 - ESP8266
 - ESP32

If you have abilities to test the library on othe hardware platforms, please feel free to contact us and tell us the results.

# Installation Windows/Linux/macOS

## Environment

 - For better experience is good to have git client. This will will alow you to install easy from github this library. The link to the [git client](https://git-scm.com/download/win).

 - This script is written in Python 3.8.5. To [download](https://www.python.org/downloads/) it please visit official site of the Python and download [3.8.5](https://www.python.org/ftp/python/3.8.5/python-3.8.5.exe)


## Create a virtual environment (Optional)
 - Make virtual environment
```sh
python -m venv venv
```

 - For Windows machines
```sh
venv/bin/activate.ps1
```
 - For Linux or macOS machines:
```sh
source venv/bin/activate
```

## Update the environment
 - Update the pip system
```bash
python -m pip install --upgrade pip 
```

## Install the library
 - Install the repository from link
```sh
python -m pip install --upgrade git+https://github.com/orlin369/pyaccelstepper.git#egg=pyaccelstepper
```
 - You are ready for the first run.

## Install the library manually (optional)
 - Download the repository from [link](git+https://github.com/orlin369/pyaccelstepper)

 - Install setuptools
```sh
python -m pip install setuptools
```

 - Unzip the downloaded repo.
 - Navigate to the unziped folder in terminal.
 - Install the package
```sh
python setup.py install
```
 - You are ready for the first run.

# Installation Micro Python

## Environment

 - For better experience is good to have git client. This will will alow you to install easy from github this library. The link to the [git client](https://git-scm.com/download/win).

 - The official IDE of this library is [Thony](https://thonny.org/), so consider to downlod it and install it for your OS platform.

## Install the firmware to the target

From version 4 of the Thony you can install firmare directly from the Thony IDE.
This is very handy. Otherways ples consider to install it by yourself depending on yor target board.

## Connecting to the target

Thony supports various target including local interpreter of the workstation OS.
 
 - Go to: Run -> Configure Interpreter...
 - Click on tab: Interpreter
 - From the first dropdown select your interpreter.
 - From the second dropdown menu select targrt connection type.
 In case you use ESP32 plese selec the COM port of the target connected to your workstation.
 - Close the dialog configuration window and go to man window.
 - Click RUN button (it looks like play button).

Now it is time to upload the main library and examples.

 - Open the file tree of the target device and create new library called affter the name of the main foleder of the library:
 ```
 pyaccelstepper
 ```
 - Create new file inside pyaccelstepper folder named:
 ```
 accel_stepper.py
 ```
 - Copy the content of the original file in to the target file.
 
 If you read this text this mean that this tutorial is no so bad after all and you have +100 stregth to continue and achieve the goal.
 Anyway, it is time to create the examplle file.
 - In the main directory of the target device please create file named whatever you want.
 - Then copy the content form some example file provided in examples directory in this library.

10 Check your wiering otherways you can blow things.

20 If you feel confidant enough please consider and click the RUN button.

30 If it spins then you did a great job.

40 Else GOTO 10

50 EEEND

# Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository on GitHub.
2. Clone your forked repository to your local machine.
3. Create a new branch for your changes: `git checkout -b my-new-feature`.
4. Make your modifications and write tests if applicable.
5. Commit your changes: `git commit -am 'Add some feature'`.
6. Push the branch to your forked repository: `git push origin my-new-feature`.
7. Create a pull request on the main repository.

We appreciate your contributions!

# License

This project is licensed under the MIT License. See the [MIT](https://choosealicense.com/licenses/mit/) file for more details.
