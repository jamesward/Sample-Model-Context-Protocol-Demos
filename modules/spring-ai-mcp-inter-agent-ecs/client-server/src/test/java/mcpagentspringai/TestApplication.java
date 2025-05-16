package mcpagentspringai;

import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class TestApplication {

    @Bean
    ApplicationRunner query(EmployeeQueries employeeQueries) {
        return args ->
            System.out.println(employeeQueries.query("Get employees that have skills related to Java"));
//            System.out.println(employeeQueries.query("What skills do our employees have?"));
    }

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
