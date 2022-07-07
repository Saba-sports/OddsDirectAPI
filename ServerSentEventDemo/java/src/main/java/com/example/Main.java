package com.example;

import com.google.gson.Gson;
import com.launchdarkly.eventsource.EventSource;
import okhttp3.*;
import org.jetbrains.annotations.NotNull;

import java.io.IOException;
import java.net.URI;
import java.time.Duration;
import java.util.Objects;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

public class Main {
    public static void main(String[] args) {
        var program = new Main();
        program.connect();
    }

    public void connect() {
        var loginUrl = "https://apistaging.wx7777.com/login";
        var vendorId = "YOUR_VENDOR_ID";
        var memberId = "YOUR_MEMBER_ID";

        var requestBody = RequestBody.create(
                String.format("{\"vendor_id\":\"%1$s\",\"vendor_member_id\":\"%2$s\"}", vendorId, memberId),
                MediaType.parse("application/json; charset=utf-8"));

        var client = new OkHttpClient().newBuilder().build();
        var req = new Request.Builder()
                .url(loginUrl)
                .addHeader("Accept-Encoding", "gzip")
                .addHeader("Accept", "*/*")
                .addHeader("Content-Encoding", "application/json")
                .post(requestBody)
                .build();

        var call = client.newCall(req);

        call.enqueue(new Callback() {
            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                var result = Objects.requireNonNull(response.body()).string();
                var gson = new Gson();
                var resBody = gson.fromJson(result, Properties.class);
                var token = resBody.getProperty("access_token");

                connectSSE(token);
            }

            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
            }
        });
    }

    private void connectSSE(String token) {
        var headerBuilder = new Headers.Builder();
        headerBuilder.add("Accept", "text/event-stream");
        // Do not add "Content-Encoding" here, okhttp add it automatic
        headerBuilder.add("Authorization", "Bearer " + token); // add "Authorization" here better than QueryString

        var url = "https://apistaging.wx7777.com/sports/stream/beta/getsports?language=en";
        var eventSourceBuilder = new EventSource.Builder(new SimpleEventHandler(), URI.create(url))
                .headers(headerBuilder.build())
                .connectTimeout(Duration.ofSeconds(10));

        try (var eventSource = eventSourceBuilder.build()) {
            eventSource.start();

            TimeUnit.MINUTES.sleep(10);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}