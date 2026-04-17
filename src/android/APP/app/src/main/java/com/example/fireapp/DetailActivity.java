package com.example.fireapp;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.File;

public class DetailActivity extends AppCompatActivity {

    private String imagePath;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail);

        ImageView imageView = findViewById(R.id.detailImageView);
        TextView infoTextView = findViewById(R.id.detailInfoTextView);

        // 이미지 경로 받아오기
        imagePath = getIntent().getStringExtra("imagePath");
        Bitmap bmp = BitmapFactory.decodeFile(imagePath);
        imageView.setImageBitmap(bmp);

        // 텍스트 표시
        String timestamp = getIntent().getStringExtra("timestamp");
        String cameraId = getIntent().getStringExtra("cameraId");
        double lat = getIntent().getDoubleExtra("latitude", 0);
        double lon = getIntent().getDoubleExtra("longitude", 0);

        String info = "카메라: " + cameraId + "\n시간: " + timestamp + "\n위도: " + lat + "\n경도: " + lon;
        infoTextView.setText(info);
    }
    protected void onDestroy() {
        super.onDestroy();

        if (imagePath != null) {
            File file = new File(imagePath);
            if (file.exists()) {
                boolean deleted = file.delete();
                if (!deleted) {
                    Log.w("DetailActivity", "임시 이미지 파일 삭제 실패: " + imagePath);
                }
            }
        }
    }

}