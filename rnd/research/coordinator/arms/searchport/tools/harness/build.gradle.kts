// SEARCHPORT harness = native-rc harness + a hook source dir (HOOK_SRC): hook-b0 (engine 078a2627, no port API) or hook-port
// (boarlite/search-port, switch on/off from --port). ENGINE_SRC = a scratch copy of the engine's src/main/java.
plugins {
    kotlin("jvm") version "2.3.0"
    kotlin("plugin.serialization") version "2.3.0"
    application
}
val engineSrc = System.getenv("ENGINE_SRC") ?: error("ENGINE_SRC not set")
val hookSrc = System.getenv("HOOK_SRC") ?: error("HOOK_SRC not set")
layout.buildDirectory.set(file(System.getenv("BUILD_DIR") ?: "build"))
kotlin { jvmToolchain(17) }
sourceSets["main"].kotlin.srcDirs("src/main/kotlin", hookSrc, engineSrc)
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
    implementation("org.xerial:sqlite-jdbc:3.50.3.0")
    implementation("com.github.luben:zstd-jni:1.5.7-4")
    implementation("org.json:json:20240303")
}
application { mainClass.set("NativeParityKt") }
