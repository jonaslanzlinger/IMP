#!/bin/bash


# Define IP addresses and ports
RPI01_IP="192.168.50.119"
RPI01_PORT=5001

RPI02_IP="192.168.50.56"
RPI02_PORT=5002

RPI03_IP="192.168.50.168"
RPI03_PORT=5003

RPI04_IP="192.168.50.51"
RPI04_PORT=5004

PROCESSING_MACHINE_IP="192.168.50.35"


# Cleanup function to release all resources gracefully
cleanup() {
    echo "!!! => Terminating..."

    # Stop the GStreamer pipeline on the Raspberry Pi
    sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI01_IP "pkill gst-launch-1.0"
    sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI02_IP "pkill gst-launch-1.0"
    sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI03_IP "pkill gst-launch-1.0"
    sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI04_IP "pkill gst-launch-1.0"

    # Stop the local GStreamer process
    pkill gst-launch-1.0

    echo "!!! => GStreamer pipelines stopped and resources released."
    exit 0
}


# Trap SIGINT
trap cleanup SIGINT


# Start the streams
echo "!!! => Starting audio stream from Raspberry Pi..."
sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI01_IP "gst-launch-1.0 alsasrc device=plughw:2,0 ! audioconvert ! audioresample ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! queue max-size-buffers=500 ! udpsink host=$PROCESSING_MACHINE_IP port=$RPI01_PORT" &
sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI02_IP "gst-launch-1.0 alsasrc device=plughw:2,0 ! audioconvert ! audioresample ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! queue max-size-buffers=500 ! udpsink host=$PROCESSING_MACHINE_IP port=$RPI02_PORT" &
sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI03_IP "gst-launch-1.0 alsasrc device=plughw:2,0 ! audioconvert ! audioresample ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! queue max-size-buffers=500 ! udpsink host=$PROCESSING_MACHINE_IP port=$RPI03_PORT" &
sshpass -p 'admin' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null admin@$RPI04_IP "gst-launch-1.0 alsasrc device=plughw:2,0 ! audioconvert ! audioresample ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! queue max-size-buffers=500 ! udpsink host=$PROCESSING_MACHINE_IP port=$RPI04_PORT" &


sleep 10


# Processing Machine - Collect and save the audio
echo "!!! => Starting audio collection on the processing machine..."
gst-launch-1.0 udpsrc port=$RPI01_PORT ! queue max-size-buffers=500 ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! audioconvert ! wavenc ! filesink location=pi1_audio.wav &
gst-launch-1.0 udpsrc port=$RPI02_PORT ! queue max-size-buffers=500 ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! audioconvert ! wavenc ! filesink location=pi2_audio.wav &
gst-launch-1.0 udpsrc port=$RPI03_PORT ! queue max-size-buffers=500 ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! audioconvert ! wavenc ! filesink location=pi3_audio.wav &
gst-launch-1.0 udpsrc port=$RPI04_PORT ! queue max-size-buffers=500 ! audio/x-raw,format=S16LE,channels=1,rate=44100,layout=interleaved ! audioconvert ! wavenc ! filesink location=pi4_audio.wav &


sleep 10


echo "!!! => Audio streaming and collection running..."


wait