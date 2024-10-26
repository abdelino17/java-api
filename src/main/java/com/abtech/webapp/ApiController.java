package com.abtech.webapp;

import java.io.IOException;
import java.io.Writer;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.boot.web.servlet.ServletRegistrationBean;

import io.prometheus.metrics.core.metrics.Counter;

@RestController
class ApiController {
  private final Counter requestCounter;

  public ApiController(Counter requestCounter) {
    this.requestCounter = requestCounter;
  }

  @GetMapping("/ping")
  public String ping() {
    requestCounter.labelValues("/ping").inc();
    return "pong";
  }

  @GetMapping("/hello")
  public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {
    requestCounter.labelValues("/hello").inc();
    return String.format("Hello %s!", name);
  }
}
