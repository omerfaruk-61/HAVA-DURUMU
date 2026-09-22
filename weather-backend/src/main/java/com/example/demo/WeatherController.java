package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/weather")
@CrossOrigin(origins = "*")
public class WeatherController {

    private String apiKey = "c27fcdf65f6a42fdd0f5618a922cb2b6";

    @Autowired
    private SearchHistoryRepository repository;

    private final RestTemplate restTemplate = new RestTemplate();

    @GetMapping("/current")
    public String getCurrentWeather(@RequestParam String city) {
        String url = String.format("https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s&units=metric&lang=tr", city, apiKey);
        String response = restTemplate.getForObject(url, String.class);

        SearchHistory history = new SearchHistory();
        history.setCity(city);
        repository.save(history);

        return response;
    }

    @GetMapping("/forecast")
    public String getForecast(@RequestParam String city) {
        String url = String.format("https://api.openweathermap.org/data/2.5/forecast?q=%s&appid=%s&units=metric&lang=tr", city, apiKey);
        return restTemplate.getForObject(url, String.class);
    }

    @GetMapping("/history")
    public List<SearchHistory> getHistory() {
        return repository.findAll();
    }

    @DeleteMapping("/history")
    public void clearHistory() {
        repository.deleteAll();
    }

    @Scheduled(cron = "0 0 */12 * * *")
    @Transactional
    public void cleanupOldHistory() {
        LocalDateTime cutoff = LocalDateTime.now().minusHours(12);
        repository.deleteBySearchedAtBefore(cutoff);
    }
}