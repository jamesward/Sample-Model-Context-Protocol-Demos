plugins {
    kotlin("jvm")
    kotlin("plugin.spring")
    id("org.springframework.boot")
    id("io.spring.dependency-management")
}

dependencies {
    implementation(platform("org.springframework.ai:spring-ai-bom:1.0.0-M6"))

    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.ai:spring-ai-bedrock-converse-spring-boot-starter")
    implementation("org.springframework.ai:spring-ai-mcp-client-spring-boot-starter")

    runtimeOnly("org.jetbrains.kotlin:kotlin-reflect")
    runtimeOnly("org.springframework.boot:spring-boot-starter-actuator")
}

kotlin {
    jvmToolchain(21)
}
