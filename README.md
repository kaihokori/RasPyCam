<p align="center"><img src="https://github.com/user-attachments/assets/d634bc77-e3c0-43f4-958c-3c3a0b03a2d6" height="100px" alt="RasPyCam Logo"></p>

<h1>Table of Contents</h1>

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
    - [Code Changes](#code-changes)
    - [Testing Changes](#testing-changes)
- [Acknowledgements](#acknowledgements)
- [License](#license)

<h1>Overview</h1>

RasPyCam is a python-based multi-stream camera system for the Raspberry Pi. This application has been designed as a replacement for the [RasPiCam](https://github.com/silvanmelchior/userland/tree/master/host_applications/linux/apps/raspicam) application developed by [Silvan Melchior](https://github.com/silvanmelchior) which is no longer maintained and has compatibility issues with the latest versions of the Raspberry Pi. 

There are two ways of using RasPyCam:
1. **As a standalone program**: The program can be run on a Raspberry Pi with a camera module connected to it. The program will respond to manual command calls and perform the necessary actions. This method will use the source code provided in this repository. 
2. **As a backend service**: The program can be run on a Raspberry Pi with a camera module connected to it alongside the [RPi Cam Web Interface](https://github.com/silvanmelchior/RPi_Cam_Web_Interface) system. The program will respond to the commands sent by the frontend and perform the necessary actions. This method will use the executable file created from the source code provided in this repository. As of version 1.0.0, the executable file is shipped with the [RPi Cam Web Interface](https://github.com/silvanmelchior/RPi_Cam_Web_Interface) system. Future updates to this repository will update the executable file in the frontend system. 

<h1>Features</h1>

- **Preview**: Retrieve the camera feed in real time. 
- **Image Capture**: Capture images from the connected camera. 
- **Video Recording**: Record videos from the connected camera. 
- **Motion Detection**: Detect motion in the camera feed. 
- **Multi-Stream Support**: Stream multiple camera feeds simultaneously from the connected camera.
- **Web Interface Support**: Interact with the program using the [RPi Cam Web Interface](https://github.com/silvanmelchior/RPi_Cam_Web_Interface) system. 

<h1>Requirements</h1>

Running the RasPyCam application requires installation of the picamera2, opencv-python, and Pillow libraries. You can install these dependencies using the following commands: 

```bash
pip install picamera2 opencv-python Pillow
```

<h1>Installation</h1>

If you intend to use RasPyCam as a standalone program, you can follow the following steps:

1. Clone the repository to your Raspberry Pi:
```bash
git clone https://github.com/kaihokori/raspycam.git
cd raspycam
```

2. Run the program:

> [!NOTE]
> Depending on your Pi's configuration, you may need to run the program with `sudo` privileges. This is because the program requires read/write access to the tmp and var directories which are restricted to root access. 

```bash
python main.py
```

<h1>Usage</h1>

RasPyCam is a continuously running program that observes the commands sent to the named pipe (by default this is `/var/FIFO`). 

To send commands to the program, you can use the following commands:
```bash
echo '{command} {parameter}' > /var/FIFO
```

Currently the program supports the following commands:
| Command | Parameter | Description |
|---------|-----------|-------------|
| ca | 1/0 | Starts (1) or stops (0) the video recording. Overwrites video if one already exists. |
| im |  | Takes a still image at full sensor resolution. |
| ru | 1/0 | Starts (1) or stops (0) the camera. The program will continue to run while the camera is stopped, but the only command that will be accepted is `ru 1` to restart the camera. |
| md | 1/0 | Starts (1) or stops (0) motion detection. |

If the program is initated without a specified configuration file, the program will utilise the following paths for inputs and outputs:
| Type | Path |
|------|------|
| Preview | /tmp/preview/cam_preview.jpg |
| Videos | /tmp/media/vi_%v_%Y%M%D_%h%m%s.mp4 |
| Stills | /tmp/media/im_%i_%Y%M%D_%h%m%s.jpg |
| Status File | /tmp/status_cam.txt |

> Command names and parameters have been named in accordance with the [RPi Cam Web Interface](https://github.com/silvanmelchior/RPi_Cam_Web_Interface) system to ensure compatibility.

To stop the program, you can either send SIGINT or SIGTERM signals to the program. This can be done by either pressing `Ctrl+C` in the terminal running the program or by using the `kill` command.

```bash
kill -15 $(pgrep -f main.py)
```

<h1>Contributing</h1>

Contributions to the RasPyCam project are welcome. If you would like to contribute to the project, please follow the steps below:

<h2>Code Changes</h2>

To make changes to the code, you can follow the steps below:

1. Fork the repository and clone it to your local machine
2. Make your changes, commit and push them to your forked repository

> [!IMPORTANT]
> When adding new features or modifying existing ones, please ensure that you have added the necessary tests to cover the changes. 

3. Create a pull request back to the main repository ([kaihokori/raspycam](https://github.com/kaihokori/raspycam))
4. Wait for the pull request to be reviewed and merged

<h2>Testing Changes</h2>

To test your changes and generage a coverage report, you can run the following command on a Raspberry Pi with a camera module connected to it: 

```bash
PYTHONPATH=./app pytest --import-mode=importlib --cov=app --cov-report=term --cov-report=html:coverage_html --cov-config=tests/.coveragerc
```

This command will run the testing suite and generate a coverage report. You can view this report by opening the `coverage_html/index.html` file in your browser. If you want to test a specific folder or file, just add the path to the end of the command. 

<h1>Acknowledgements</h1>

The development of this project was inspired by the [RasPiCam](https://github.com/silvanmelchior/userland/tree/master/host_applications/linux/apps/raspicam) application developed by [Silvan Melchior](https://github.com/silvanmelchior). 

Initially devleoped as part of a University project overseen by [Cian Byrne](https://github.com/wallarug), the development team consisted of: 
- [Kyle Graham](https://github.com/kaihokori)
- [Harry Le (Lê Thành Nhân)](https://github.com/NhanDotJS)
- [Chen-Don Loi](https://github.com/Chen-Loi)
- [Qiuda (Richard) Song](https://github.com/RichardQiudaSong)

<h1>License</h1>

The source code for the RasPyCam application is licensed under the MIT License. As an individual, you are free to use, modify, and distribute the source code for personal use. However, you must include the original license and copyright information in your modified version. 
