
    package org.springframework.api_tests;
  
    import com.intuit.karate.Results;
    import com.intuit.karate.Runner;
    // import com.intuit.karate.http.HttpServer;
    // import com.intuit.karate.http.ServerConfig;
    import org.junit.jupiter.api.Test;
  
    import static org.junit.jupiter.api.Assertions.assertEquals;
  
    class CredentialRegisterSwaggerServerSwaggerSwaggerTest {
  
        @Test
        void testAll() {
            String swagger_184f1d2b61_url = System.getenv().getOrDefault("SWAGGER_184F1D2B61_URL", "http://127.0.0.1:4010");
String auth_token = System.getenv().getOrDefault("AUTH_TOKEN", "dummy_AUTH_TOKEN");
            Results results = Runner.path("src/test/java/org/springframework/api_tests/CredentialRegisterSwaggerServerSwaggerSwagger")
                    .systemProperty("SWAGGER_184F1D2B61_URL",swagger_184f1d2b61_url)
.systemProperty("AUTH_TOKEN", auth_token)
                    .reportDir("testReport").parallel(1);
            assertEquals(0, results.getFailCount(), results.getErrorMessages());
        }
  
    }
