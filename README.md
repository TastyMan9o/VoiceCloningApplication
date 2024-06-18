# Voice Cloning Tool

Voice Cloning Tool is a Python application for voice cloning, audio preprocessing, and video processing. This tool leverages various libraries including TTS, moviepy, and more.

## Project Structure

```plaintext
VoiceCloningTool/
├── Cloning_Output/
│   └── (here are the output audios you have cloned)
├── docs/
│   └── UserManual.pdf
├── icon/
│   └── (icon images)
├── Ultimate Vocal Remover/(optional)
│   └── UVR_Launcher.exe
├── main.py
├── audio_preprocessing.py
├── video_processing.py
├── recording_module.py
├── voice_cloning.py
├── README.md
└── requirements.txt


## Prerequisites:
    Python >= 3.9, < 3.11
    pip (Python package installer)

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/TastyMan9o/VoiceCloningApplication.git
    cd VoiceCloningTool
    ```

2. **Install required Python packages**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Install CUDA (Optional, but recommended for better performancem, if running on cpu would be very slow)**:
   Follow the steps below to install CUDA.

## CUDA Installation Guide

### Step 1: Determine Your GPU

Before installing CUDA, you need to determine your GPU model. You can find this information in your system settings or by using a tool like GPU-Z.

### Step 2: Find the Appropriate CUDA Version

Refer to the following table to determine the appropriate CUDA version for your GPU:

| NVIDIA GPU Model | CUDA Version |
|------------------|--------------|
| GeForce RTX 30xx | CUDA 11.x    |
| GeForce RTX 20xx | CUDA 10.x    |
| GeForce GTX 16xx | CUDA 10.x    |
| GeForce GTX 10xx | CUDA 9.x     |
| GeForce GTX 9xx  | CUDA 8.x     |
| Tesla V100       | CUDA 9.x     |
| Tesla P100       | CUDA 8.x     |

### Step 3: Download and Install CUDA Toolkit

1. **Download CUDA Toolkit**:
    - Visit the [NVIDIA CUDA Toolkit Download page](https://developer.nvidia.com/cuda-downloads).
    - Select your operating system and download the appropriate installer.

2. **Install CUDA Toolkit**:
    - Follow the installation instructions provided on the download page.

## Install Ultimate Vocal Remover (UVR5) (optional)
Ultimate Vocal Remover (UVR5) is a tool used for audio preprocessing. If your audio contains noise, other voices, or background music, you can use UVR5 to clean the audio before processing it with the Voice Cloning Tool. UVR5 is optional, and if your audio is already clean, you do not need to use it.

UVR5 Installation Guide
1. **Download UVR5**:  Visit the [Ultimate Vocal Remover download page](https://github.com/Anjok07/ultimatevocalremovergui?tab=readme-ov-file)

2. **Install UVR5**:  Click on 'UVR_5.X.X_setup.exe' and then choose the VoiceCloningTool folder as the installation directory.



## Running the Application
To run the Voice Cloning Tool, use the following command:
    py main.py



## User Manual
If you have specific operational issues, please refer to the User_Manual.pdf