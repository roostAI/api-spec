
    package org.springframework.integration_tests;
  
    import com.intuit.karate.Results;
    import com.intuit.karate.Runner;
    // import com.intuit.karate.http.HttpServer;
    // import com.intuit.karate.http.ServerConfig;
    import org.junit.jupiter.api.Test;
  
    import static org.junit.jupiter.api.Assertions.assertEquals;
  
    class FeatureFileGherkinCredentialAllTest {
  
        @Test
        void testAll() {
            String 061reb413_employee_service_0_1_resolved_0c74426493_url = System.getenv().getOrDefault("061REB413_EMPLOYEE_SERVICE_0_1_RESOLVED_0C74426493_URL", "https://127.0.0.1:4010");
            Results results = Runner.path("src/test/java/org/springframework/integration_tests/FeatureFileGherkinCredentialAll")
                    .systemProperty("061REB413_EMPLOYEE_SERVICE_0_1_RESOLVED_0C74426493_URL",061reb413_employee_service_0_1_resolved_0c74426493_url)
                    .reportDir("testReport").parallel(1);
            assertEquals(0, results.getFailCount(), results.getErrorMessages());
        }
  
    }
