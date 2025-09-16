const axios = require("axios");

async function registerUser() {
  try {
    console.log("Attempting to register user...");

    const response = await axios.post(
      "http://localhost:8002/api/auth/register",
      {
        email: "jc@razorflow-ai.com",
        password: "Password123!",
        first_name: "Razor303",
        last_name: "JC",
        company_name: "RazorFlow-AI",
        phone: "+1-555-0123",
      }
    );

    console.log("Registration successful:", response.data);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.log(
        "Registration failed:",
        error.response.status,
        error.response.data
      );
    } else {
      console.log("Error:", error.message);
    }
  }
}

async function loginUser() {
  try {
    console.log("Attempting to login...");

    const response = await axios.post("http://localhost:8002/api/auth/login", {
      email: "jc@razorflow-ai.com",
      password: "Password123!",
    });

    console.log("Login successful:", response.data);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.log("Login failed:", error.response.status, error.response.data);
    } else {
      console.log("Error:", error.message);
    }
  }
}

async function main() {
  // Try to register first (might fail if user exists)
  await registerUser();

  // Then try to login
  await loginUser();
}

main();
