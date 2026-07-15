<script setup>
import { ref } from "vue"

const image = ref(null)
const loading = ref(false)
const message = ref("")

async function scanFingerprint() {
  loading.value = true
  message.value = "Place your finger on scanner..."

  try {
    const response = await fetch("http://localhost:8000/capture", {
      method: "POST"
    })

    const data = await response.json()

    if (data.success) {
      image.value = "http://127.0.0.1:8000" + data.image + "?t=" + Date.now()
      message.value = "Fingerprint captured successfully"
    } else {
      message.value = "Capture failed. Please try again."
    }
  } catch (error) {
    message.value = error.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="scanner-card">
    <div class="header">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 16H11V14H13V16ZM13 12H11V8H13V12Z" fill="currentColor"/>
        </svg>
      </div>
      <h1>CS9711 Biometric Scanner</h1>
      <p class="subtitle">Secure Device Bridge Client</p>
    </div>

    <div class="action-zone">
      <button 
        @click="scanFingerprint" 
        :disabled="loading"
        :class="{ 'btn-loading': loading }"
        class="scan-btn"
      >
        <span class="btn-ripple" v-if="loading"></span>
        <span class="btn-text">
          {{ loading ? "Scanning Device..." : "Scan Fingerprint" }}
        </span>
      </button>
    </div>

    <div class="status-zone" v-if="message">
      <div class="status-badge" :class="{ 'status-info': loading, 'status-success': !loading && image, 'status-error': !loading && !image }">
        <span class="status-dot"></span>
        <span class="status-text">{{ message }}</span>
      </div>
    </div>

    <div class="image-zone" v-if="image">
      <div class="fingerprint-frame">
        <div class="scan-line" v-if="loading"></div>
        <img 
          :src="image" 
          class="fingerprint-img" 
          alt="Fingerprint Scan"
        />
        <div class="corner corner-tl"></div>
        <div class="corner corner-tr"></div>
        <div class="corner corner-bl"></div>
        <div class="corner corner-br"></div>
      </div>
      <div class="frame-label">Captured Biometric Frame</div>
    </div>
  </div>
</template>

<style scoped>
.scanner-card {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 3rem 2.5rem;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 80px rgba(56, 189, 248, 0.1);
  text-align: center;
  font-family: 'Outfit', 'Inter', system-ui, -apple-system, sans-serif;
  color: #f8fafc;
  transition: all 0.3s ease;
}

.header {
  margin-bottom: 2.5rem;
}

.logo-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #38bdf8, #0284c7);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 8px 16px rgba(56, 189, 248, 0.2);
}

.logo-icon svg {
  width: 28px;
  height: 28px;
}

h1 {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin-bottom: 0.25rem;
  background: linear-gradient(to right, #f8fafc, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 0.9rem;
  color: #94a3b8;
  font-weight: 500;
}

.action-zone {
  margin-bottom: 2rem;
}

.scan-btn {
  position: relative;
  width: 100%;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  border: none;
  border-radius: 14px;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.scan-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4);
  background: linear-gradient(135deg, #0ea5e9, #0284c7);
}

.scan-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.scan-btn:disabled {
  background: #334155;
  color: #64748b;
  cursor: not-allowed;
  box-shadow: none;
}

.btn-ripple {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: loading-pulse 1.5s infinite;
}

@keyframes loading-pulse {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.status-zone {
  margin-bottom: 2rem;
  display: flex;
  justify-content: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 500;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-info .status-dot {
  background: #38bdf8;
  box-shadow: 0 0 8px #38bdf8;
  animation: blink 1s infinite alternate;
}
.status-info .status-text { color: #38bdf8; }

.status-success .status-dot {
  background: #4ade80;
  box-shadow: 0 0 8px #4ade80;
}
.status-success .status-text { color: #4ade80; }

.status-error .status-dot {
  background: #f87171;
  box-shadow: 0 0 8px #f87171;
}
.status-error .status-text { color: #f87171; }

@keyframes blink {
  0% { opacity: 0.3; }
  100% { opacity: 1; }
}

.image-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1rem;
}

.fingerprint-frame {
  position: relative;
  width: 240px;
  height: 380px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.6);
  overflow: hidden;
}

.fingerprint-img {
  max-width: 100%;
  max-height: 100%;
  width: 200px;
  height: auto;
  border-radius: 8px;
  filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.15)) contrast(1.1) brightness(1.05);
  image-rendering: pixelated;
  transition: all 0.3s ease;
}

/* Sci-fi frame corners */
.corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border-color: #38bdf8;
  border-style: solid;
  opacity: 0.8;
}
.corner-tl { top: 12px; left: 12px; border-width: 2px 0 0 2px; border-top-left-radius: 4px; }
.corner-tr { top: 12px; right: 12px; border-width: 2px 2px 0 0; border-top-right-radius: 4px; }
.corner-bl { bottom: 12px; left: 12px; border-width: 0 0 2px 2px; border-bottom-left-radius: 4px; }
.corner-br { bottom: 12px; right: 12px; border-width: 0 2px 2px 0; border-bottom-right-radius: 4px; }

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(to right, transparent, #38bdf8, transparent);
  box-shadow: 0 0 10px #38bdf8;
  animation: scan-anim 2s linear infinite;
  z-index: 10;
}

@keyframes scan-anim {
  0% { top: 10px; }
  50% { top: calc(100% - 10px); }
  100% { top: 10px; }
}

.frame-label {
  font-size: 0.8rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  margin-top: 0.75rem;
}
</style>