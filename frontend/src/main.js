import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')

const scanBtn = document.getElementById("scanBtn");
const statusText = document.getElementById("status");
const fingerprintImg = document.getElementById("fingerprintImg");

scanBtn.addEventListener("click", async () => {
    try {
        scanBtn.disabled = true;
        statusText.innerText = "Scanning....";

        const response = await fetch(`http://localhost:8000/capture`, {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success) {
            statusText.innerText = "Scan complete!";
            
            const base64String = "data:image/png;base64," + data.image_base64;

            fingerprintImg.src = base64String;
            fingerprintImg.style.display = "block";
            
            try {
                const saveResponse = await fetch("http://localhost:8000/save", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        userId: "user_123",
                        fingerprintData: data.image_base64 
                    })
                });
                
                if (saveResponse.ok) {
                    console.log("Successfully saved fingerprint to database!");
                }
            } catch (err) {
                console.error("Failed to save to database:", err);
            }
            
        } else {
            statusText.innerText = "Scan failed";
        }
    } catch (error) {
        console.error("Error during scan:", error);
        statusText.innerText = "Error: " + error.message;
    } finally {
        scanBtn.disabled = false;
    }
});