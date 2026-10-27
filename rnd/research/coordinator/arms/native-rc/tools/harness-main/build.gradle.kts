// Desktop harness around the maintainer's native Kotlin engine (pure JVM compile of engine/src/main/java).
// ENGINE_SRC = a scratch copy of wt/native-qa/android-native/engine/src/main/java (made by tools/run.sh, cutoff patch applied).
plugins {
    kotlin("jvm") version "2.3.0"
    kotlin("plugin.serialization") version "2.3.0"
    application
}
val engineSrc = System.getenv("ENGINE_SRC") ?: error("ENGINE_SRC not set")
layout.buildDirectory.set(file(System.getenv("BUILD_DIR") ?: "build"))
kotlin { jvmToolchain(17) }
sourceSets["main"].kotlin.srcDirs("src/main/kotlin", engineSrc)
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.9.0")
    implementation("org.xerial:sqlite-jdbc:3.50.3.0")
    implementation("com.github.luben:zstd-jni:1.5.7-4")
    implementation("org.json:json:20240303") // Android ships org.json; the JVM needs it
}
application { mainClass.set("NativeParityKt") }
tasks.named<JavaExec>("run") { workingDir = file(System.getenv("RUN_DIR") ?: "."); jvmArgs("-Xmx4g") }
