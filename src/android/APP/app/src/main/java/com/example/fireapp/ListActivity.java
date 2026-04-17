package com.example.fireapp;

import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;

public class ListActivity extends AppCompatActivity {

    RecyclerView recyclerView;
    FireDetectionAdapter adapter;
    ArrayList<FireDetection> detectionList = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_listview);

        recyclerView = findViewById(R.id.recyclerView); // XML에 RecyclerView 존재해야 함
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new FireDetectionAdapter(this, detectionList);
        recyclerView.setAdapter(adapter);

        fetchFireData();
    }

    private void fetchFireData() {
        String url = "http://220.69.208.113:8000/fires";

        new Thread(() -> {
            try {
                URL u = new URL(url);
                HttpURLConnection conn = (HttpURLConnection) u.openConnection();
                conn.setRequestMethod("GET");

                BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) sb.append(line);
                reader.close();

                JSONArray arr = new JSONArray(sb.toString());
                detectionList.clear();

                for (int i = 0; i < arr.length(); i++) {
                    JSONObject o = arr.getJSONObject(i);
                    FireDetection d = new FireDetection(
                            o.getString("timestamp"),
                            o.getString("camera_id"),
                            o.getDouble("latitude"),
                            o.getDouble("longitude"),
                            o.getString("image")
                    );
                    detectionList.add(d);
                }

                runOnUiThread(() -> adapter.notifyDataSetChanged());

            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }
}

