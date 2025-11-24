# Sample Data

This directory contains sample DJI telemetry data for testing purposes.

## Files

- `DJI_0001.SRT` - Sample SRT telemetry file from a DJI Mini 3 drone

## Using Sample Data

To test the application with sample data:

1. Use the `DJI_0001.SRT` file as the SRT input
2. For video testing, you'll need an actual MP4 file (not included due to size)
3. The SRT file demonstrates the typical DJI telemetry format

## SRT File Format

DJI SRT files contain the following information per second:
- **Timestamp**: Video timecode (HH:MM:SS,mmm)
- **FrameCnt**: Frame number
- **DateTime**: Recording date and time
- **GPS**: Latitude, Longitude, Altitude
- **Gimbal**: Pitch and Yaw angles
- **Camera**: ISO, Shutter speed, F-number, EV, Color mode

## Creating Your Own Test Data

To create test data from your DJI Mini 3:
1. Record a short video (10-30 seconds)
2. Copy both .MP4 and .SRT files from the drone
3. Use them with this application

## Example Data

The sample file simulates:
- **Location**: Buenos Aires, Argentina (-34.6°, -58.3°)
- **Flight Type**: Nadir mapping (gimbal ~-90°)
- **Duration**: 5 seconds
- **Altitude**: ~150m absolute, ~50m relative
- **Yaw**: Gradually increasing from 45° to 49°
