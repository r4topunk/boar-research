// RC1-LABS: desktop run of the maintainer's Labs tool slot (AnswerTools.run order) at tag v2.0.0-rc1 (0 LLM).
// ENGINE_SRC = scratch copy of the tag's android-native/engine/src/main/java (tools/run_labs.sh, git archive; unchanged).
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
    implementation("org.json:json:20240303")
}
application { mainClass.set("Rc1LabsKt") }
