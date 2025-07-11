
package org.springframework.api_tests.RoostIoSampleApiRefsHeadsMainApisAddressValidationMqas100Swagger;

import com.intuit.karate.Results;
import com.intuit.karate.Runner;
// import com.intuit.karate.http.HttpServer;
// import com.intuit.karate.http.ServerConfig;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class RoostIoSampleApiRefsHeadsMainApisAddressValidationMqas100SwaggerTest {

	@Test
	void testAll() {
		String APIHOST11 = System.getenv().get("API_HOST11");
		String AUTHTOKEN11 = System.getenv().get("AUTH_TOKEN11");
		Results results = Runner.path(
				"src/test/java/org/springframework/api_tests/RoostIoSampleApiRefsHeadsMainApisAddressValidationMqas100Swagger")
			.systemProperty("API_HOST11", APIHOST11)
			.systemProperty("AUTH_TOKEN11", AUTHTOKEN11)
			.reportDir("testReport")
			.parallel(1);
		assertEquals(0, results.getFailCount(), results.getErrorMessages());
	}

}
