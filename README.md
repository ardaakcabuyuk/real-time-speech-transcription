# real-time-speech-transcription-cli

This README provides a comprehensive guide to running and building the Real-Time Speech Transcription CLI application, either directly on your system or containerized using Docker.

## Prerequisites

Before running the CLI application on Docker, ensure you have `pulseaudio` installed on your system. If you're on MacOS, you can install `pulseaudio` using Homebrew:

```shell
brew install pulseaudio
```

After installing `pulseaudio`, run the daemon with the following command:

```shell
pulseaudio --load=module-native-protocol-tcp --exit-idle-time=-1 --daemon
```

This command starts the `pulseaudio` system-wide daemon with the TCP module loaded, which is necessary for the Docker container to communicate with the host's audio system.

## Running the Application Without Docker

To ensure a clean environment for running the application, it is recommended to use a Python virtual environment. Here's how to set up and activate a virtual environment:

1. **Navigate to your project directory:**

   ```shell
   cd path/to/real-time-speech-transcription-cli
   ```
2. **Create a virtual environment:**

   ```shell
   python3 -m venv .venv
   ```
3. **Activate the virtual environment:**

   * On macOS and Linux:
     ```shell
     source .venv/bin/activate
     ```
   * On Windows:
     ```powershell
     .\.venv\Scripts\activate
     ```
4. **Install dependencies:**

   ```shell
   pip install -r requirements.txt
   ```
5. **Run the application:**

   ```shell
   python3 main.py
   ```

This command will start the CLI application using your local Python environment configured within a virtual environment.

## Building the Docker Container

To build the Docker container for the CLI application, navigate to the directory containing the Dockerfile and run:

```shell
docker build -t app .
```

This command builds the Docker image and tags it as `app`.

## Running the Container

To run the CLI application using Docker, use the following command:

```shell
docker run -it \
  --env-file .env \
  -v ~/.config/pulse:/home/pulseaudio/.config/pulse \
  app
```

Here's what each argument means:

* `-it`: Allocates a pseudo-TTY and keeps STDIN open, allowing you to interact with the CLI within the Docker container.
* `--env-file .env`: Tells Docker to use an environment file named `.env`, which should contain environment variables required by the application.
* `-v ~/.config/pulse:/home/pulseaudio/.config/pulse`: Mounts the host's `pulseaudio` configuration directory to the container, enabling the application to use the host's audio system.

## Possible Issues

When running audio applications in Docker, especially on MacOS, you might encounter issues with ALSA and the Jack server, such as:

* ALSA not finding the sound card (`cannot find card '0'`).
* Jack server not running or starting.

These are known difficulties related to audio handling in Docker on MacOS, as there's no straightforward method to port host audio input/output devices to the container. Despite these warnings, audio recording and playback functionality has been confirmed to work.

If you encounter such errors, they are generally non-fatal and can be a result of ALSA's system-wide configuration not being applicable within the container. The application should still record and play audio as intended.
