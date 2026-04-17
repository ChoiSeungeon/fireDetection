package com.example.fireapp;

public class FireDetection {
    public String timestamp;
    public String cameraId;
    public double latitude;
    public double longitude;
    public String imageBase64;

    public FireDetection(String timestamp, String cameraId, double latitude, double longitude, String imageBase64) {
        this.timestamp = timestamp;
        this.cameraId = cameraId;
        this.latitude = latitude;
        this.longitude = longitude;
        this.imageBase64 = imageBase64;
    }

    public String getDate() {
        return timestamp.split("T")[0];
    }

    public String getTime() {
        return timestamp.split("T")[1].substring(0, 5);
    }

    public String getLocationString() {
        return String.format("위도: %.5f\n경도: %.5f", latitude, longitude);
    }
}


