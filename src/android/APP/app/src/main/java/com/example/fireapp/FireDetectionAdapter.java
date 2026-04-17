package com.example.fireapp;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Base64;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;

public class FireDetectionAdapter extends RecyclerView.Adapter<FireDetectionAdapter.ViewHolder> {

    private Context context;
    private ArrayList<FireDetection> detections;

    public FireDetectionAdapter(Context context, ArrayList<FireDetection> detections) {
        this.context = context;
        this.detections = detections;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.activity_item_notification, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        FireDetection item = detections.get(position);

        holder.idTextView.setText(String.valueOf(position + 1));
        holder.contentTextView.setText(item.getLocationString());
        holder.dateTextView.setText(item.getDate());
        holder.timeTextView.setText(item.getTime());

        // base64 → Bitmap
        byte[] imageBytes = Base64.decode(item.imageBase64, Base64.DEFAULT);
        Bitmap bmp = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.length);
        holder.imageView.setImageBitmap(bmp);

        holder.itemView.setOnClickListener(v -> {
            // 2. Bitmap을 임시 파일로 저장
            File cachePath = new File(context.getCacheDir(), "images");
            if (!cachePath.exists()) cachePath.mkdirs();
            File tempFile = new File(cachePath, "temp_" + System.currentTimeMillis() + ".jpg");
            try (FileOutputStream stream = new FileOutputStream(tempFile)) {
                bmp.compress(Bitmap.CompressFormat.JPEG, 100, stream);
            } catch (IOException e) {
                e.printStackTrace();
            }

            // 3. 파일 경로를 intent로 전달
            Intent intent = new Intent(context, DetailActivity.class);
            intent.putExtra("imagePath", tempFile.getAbsolutePath());
            intent.putExtra("timestamp", item.timestamp);
            intent.putExtra("cameraId", item.cameraId);
            intent.putExtra("latitude", item.latitude);
            intent.putExtra("longitude", item.longitude);
            context.startActivity(intent);
        });

    }

    @Override
    public int getItemCount() {
        return detections.size();
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView idTextView, contentTextView, dateTextView, timeTextView;
        ImageView imageView;

        public ViewHolder(View itemView) {
            super(itemView);
            idTextView = itemView.findViewById(R.id.idTextView);
            contentTextView = itemView.findViewById(R.id.contentTextView);
            dateTextView = itemView.findViewById(R.id.dateTextView);
            timeTextView = itemView.findViewById(R.id.timeTextView);
            imageView = itemView.findViewById(R.id.imageView);
        }
    }
}
