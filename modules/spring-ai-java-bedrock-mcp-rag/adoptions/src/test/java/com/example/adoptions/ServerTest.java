package com.example.adoptions;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, properties = "spring.sql.init.mode=always")
public class ServerTest {

    @LocalServerPort
    private int port;

    @Test
    void adoptDog() {
        var prancer = inquire("Do you have any neurotic dogs?");
        assertThat(prancer.getStatusCode().is2xxSuccessful()).isTrue();
        assertThat(prancer.getBody()).contains("Prancer");

        var schedule = inquire("fantastic. when could i schedule an appointment to adopt Prancer, from the London location?");
        assertThat(schedule.getStatusCode().is2xxSuccessful()).isTrue();
        var utcNow = ZonedDateTime.now(ZoneId.of("UTC"));
        var utcPlusThreeDays = utcNow.plusDays(3);
        var formatter = DateTimeFormatter.ofPattern("MMMM d", Locale.ENGLISH);
        String formattedDate = utcPlusThreeDays.format(formatter);

        assertThat(schedule.getBody()).contains(formattedDate);
    }

    private ResponseEntity<String> inquire(String question) {
        var uri = "http://localhost:" + this.port + "/jwjl/inquire";
        var rc = RestClient
                .builder()
                .baseUrl(uri)
                .build();
        return rc
                .post()
                .uri(builder -> builder.queryParam("question", question).build())
                .retrieve()
                .toEntity(String.class);
    }

}
