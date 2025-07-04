plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "com.example.collegeassistant"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.example.collegeassistant"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = "11"
    }
    buildFeatures {
        compose = true
    }
}

dependencies {

    // AndroidX core & AppCompat
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.9.0")

    // Jetpack Compose (already likely present)
    implementation("androidx.compose.ui:ui:1.5.0")
    implementation("androidx.compose.material3:material3:1.2.0")
    implementation("androidx.activity:activity-compose:1.8.0")

    // Retrofit & Gson
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    // Kotlin Coroutines (for async)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4")

    // DataStore Preferences
    implementation("androidx.datastore:datastore-preferences:1.0.0")

    // Lifecycle & ViewModel (optional but helpful)
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.2")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
    implementation("com.airbnb.android:lottie-compose:6.3.0")

    // **Add these test dependencies**

    // Unit test framework (JUnit 4)
    testImplementation("junit:junit:4.13.2")

    // Android instrumented tests with JUnit4 support
    androidTestImplementation("androidx.test.ext:junit:1.1.5")

    // Android UI testing with Espresso
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")



}
