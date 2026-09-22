package com.example.demo;

import org.springframework.data.jpa.repository.JpaRepository;
import java.time.LocalDateTime;

public interface SearchHistoryRepository extends JpaRepository<SearchHistory, Long> {
    void deleteBySearchedAtBefore(LocalDateTime cutoff);
}