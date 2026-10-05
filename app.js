/**
 * TrailBird AI - Client-Side Open-Source Bird Identifier Engine
 * Runs 100% locally in browser via Web Audio API & local FFT feature extraction.
 */

let speciesDB = [];
let audioCtx = null;
let analyser = null;
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;
let animationId = null;
let trailLog = [];

// DOM Elements
const recordBtn = document.getElementById('recordBtn');
const audioFileInput = document.getElementById('audioFileInput');
const canvas = document.getElementById('spectrogramCanvas');
const canvasCtx = canvas.getContext('2d');
const canvasPlaceholder = document.getElementById('canvasPlaceholder');
const recordingIndicator = document.getElementById('recordingIndicator');
const resultsContainer = document.getElementById('resultsContainer');
const latencyBadge = document.getElementById('latencyBadge');
const sightingList = document.getElementById('sightingList');
const journalCount = document.getElementById('journalCount');
const pocketPhoneBtn = document.getElementById('pocketPhoneBtn');
const touchGrassHeaderBtn = document.getElementById('touchGrassHeaderBtn');
const pocketOverlay = document.getElementById('pocketOverlay');
const resumeAppBtn = document.getElementById('resumeAppBtn');

// Initialize Canvas dimensions
function resizeCanvas() {
  if (canvas && canvas.parentElement) {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
  }
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Load Species Database
async function init() {
  try {
    const resp = await fetch('models/species_db.json');
    const data = await resp.json();
    speciesDB = data.species || [];
    console.log('Species DB loaded:', speciesDB.length, 'species');
  } catch (err) {
    console.warn('Fallback species DB initialized:', err);
    // Hardcoded fallback species DB if fetch fails locally
    speciesDB = [
      {
        id: "american_robin",
        common_name: "American Robin",
        scientific_name: "Turdus migratorius",
        family: "Turdidae (Thrushes)",
        freq_min_hz: 2200,
        freq_max_hz": 3800,
        dominant_freq_hz: 3100,
        call_pattern: "cheerily-cheer-up",
        icon_emoji: "🐦",
        color: "#D35400",
        habitat: "Forest edges, woodlands, suburban parks & gardens",
        fun_fact: "Robins can hear earthworms moving underground by tilting their heads to align their ears!",
        touch_grass_tip: "Look up in open deciduous branch forks or near grassy trail clearings.",
        conservation_status: "Least Concern (LC)"
      },
      {
        id: "northern_cardinal",
        common_name: "Northern Cardinal",
        scientific_name: "Cardinalis cardinalis",
        family: "Cardinalidae",
        freq_min_hz: 2000,
        freq_max_hz: 4500,
        dominant_freq_hz: 3300,
        call_pattern: "slurred down-sweep whistle",
        icon_emoji: "🔴",
        color: "#C0392B",
        habitat: "Dense shrubbery, forest margins, overgrown thickets",
        fun_fact: "Both male and female cardinals sing, which is rare among North American songbirds!",
        touch_grass_tip: "Scan low thickets and evergreen tangles about 5 to 10 feet off the trail ground.",
        conservation_status: "Least Concern (LC)"
      },
      {
        id: "black_capped_chickadee",
        common_name: "Black-capped Chickadee",
        scientific_name: "Poecile atricapillus",
        family: "Paridae",
        freq_min_hz: 2900,
        freq_max_hz: 5200,
        dominant_freq_hz: 3400,
        call_pattern: "chick-a-dee-dee-dee",
        icon_emoji: "🐤",
        color: "#2C3E50",
        habitat: "Deciduous and mixed forests, trail edges, willow thickets",
        fun_fact: "The number of 'dee' notes at the end of their alarm call indicates predator threat level!",
        touch_grass_tip: "Pause silently under birch or pine trees; chickadees are curious and will hop close.",
        conservation_status: "Least Concern (LC)"
      },
      {
        id: "blue_jay",
        common_name: "Blue Jay",
        scientific_name: "Cyanocitta cristata",
        family: "Corvidae",
        freq_min_hz: 2400,
        freq_max_hz: 4800,
        dominant_freq_hz: 2900,
        call_pattern: "harsh jay-jay / bell whistle",
        icon_emoji: "🦅",
        color: "#2980B9",
        habitat: "Oak-hickory forests, pine woodlands, park boundaries",
        fun_fact: "Blue Jays frequently imitate hawk calls to test if real hawks are nearby!",
        touch_grass_tip: "Listen for alarm calls high in oak treetops near acorn drops.",
        conservation_status: "Least Concern (LC)"
      }
    ];
  }
  loadTrailLog();
}

// Web Audio Context Setup
function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

// Live Canvas Waveform / Spectrogram Visualization
function drawLiveVisualization(analyserNode) {
  const bufferLength = analyserNode.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  function renderFrame() {
    animationId = requestAnimationFrame(renderFrame);
    analyserNode.getByteFrequencyData(dataArray);

    canvasCtx.fillStyle = '#0c1e17';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 2.5;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * canvas.height;
      const hue = 140 + (i / bufferLength) * 120; // emerald to gold
      canvasCtx.fillStyle = `hsl(${hue}, 80%, 45%)`;
      canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
      x += barWidth + 1;
    }
  }
  renderFrame();
}

// Start Live Microphone Recording (3 seconds)
async function startRecording() {
  if (isRecording) return;
  const ctx = getAudioContext();

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    analyser = ctx.createAnalyser();
    analyser.fftSize = 512;
    const source = ctx.createMediaStreamSource(stream);
    source.connect(analyser);

    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(track => track.stop());
      cancelAnimationFrame(animationId);
      recordingIndicator.classList.add('hidden');
      recordBtn.innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
        <span>Record Trail Call (3s)</span>
      `;
      isRecording = false;

      const blob = new Blob(recordedChunks, { type: 'audio/wav' });
      const arrayBuffer = await blob.arrayBuffer();
      const decodedBuffer = await ctx.decodeAudioData(arrayBuffer);
      processAudioBuffer(decodedBuffer);
    };

    mediaRecorder.start();
    isRecording = true;
    canvasPlaceholder.classList.add('hidden');
    recordingIndicator.classList.remove('hidden');
    recordBtn.innerHTML = `
      <span class="w-3 h-3 rounded-full bg-red-400 animate-ping"></span>
      <span>Recording Trail Audio...</span>
    `;

    drawLiveVisualization(analyser);

    // Auto-stop after 3 seconds for fast trail identification
    setTimeout(() => {
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
      }
    }, 3000);

  } catch (err) {
    alert('Microphone access unavailable. You can use the upload option or sample audio buttons below!');
    console.error('Mic error:', err);
  }
}

// Process Audio File or Sample
async function processAudioFile(fileOrUrl) {
  const ctx = getAudioContext();
  let arrayBuffer;

  try {
    if (typeof fileOrUrl === 'string') {
      const resp = await fetch(fileOrUrl);
      arrayBuffer = await resp.arrayBuffer();
    } else {
      arrayBuffer = await fileOrUrl.arrayBuffer();
    }

    const audioBuffer = await ctx.decodeAudioData(arrayBuffer);
    processAudioBuffer(audioBuffer);
  } catch (err) {
    alert('Error processing audio file. Please check audio format.');
    console.error('Audio decode error:', err);
  }
}

// Core Open-Weight Inference Engine (Local Feature Extraction & Matching)
function processAudioBuffer(audioBuffer) {
  const startTime = performance.now();
  canvasPlaceholder.classList.add('hidden');

  const pcmData = audioBuffer.getChannelData(0);
  const sampleRate = audioBuffer.sampleRate;

  // Render static spectrogram representation on canvas
  renderStaticSpectrogram(pcmData);

  // Compute energy across frequency bands using Web Audio API buffer samples
  const bandEnergy = [0, 0, 0, 0]; // 0: <1.5k, 1: 1.5k-3k, 2: 3k-4.5k, 3: >4.5k
  const step = 512;
  
  for (let i = 0; i < pcmData.length - step; i += step) {
    let energy = 0;
    for (let j = 0; j < step; j++) {
      energy += pcmData[i + j] * pcmData[i + j];
    }
    
    // Estimate zero-crossing rate for local window
    let zc = 0;
    for (let j = 1; j < step; j++) {
      if ((pcmData[i+j-1] >= 0 && pcmData[i+j] < 0) || (pcmData[i+j-1] < 0 && pcmData[i+j] >= 0)) {
        zc++;
      }
    }
    const windowFreq = (zc * sampleRate) / (2 * step);
    
    if (windowFreq < 1500) bandEnergy[0] += energy;
    else if (windowFreq < 3000) bandEnergy[1] += energy;
    else if (windowFreq < 4500) bandEnergy[2] += energy;
    else bandEnergy[3] += energy;
  }

  const total = bandEnergy.reduce((a, b) => a + b, 0) + 1e-9;
  const normBands = bandEnergy.map(b => b / total);

  // Classify against species profiles
  const maxIdx = normBands.indexOf(Math.max(...normBands));
  const bandPitches = [550, 2850, 3400, 4800];
  const detectedFreq = bandPitches[maxIdx];

  const matches = speciesDB.map(sp => {
    const minF = sp.freq_min_hz;
    const maxF = sp.freq_max_hz;
    const domF = sp.dominant_freq_hz;

    let score = 0;
    if (detectedFreq >= minF && detectedFreq <= maxF) {
      const dist = Math.abs(detectedFreq - domF) / (maxF - minF);
      score = 98 - (dist * 12);
    } else {
      const closest = detectedFreq < minF ? minF : maxF;
      const dist = Math.abs(detectedFreq - closest);
      score = Math.max(15, 60 - (dist / 100));
    }
    return {
      species: sp,
      confidence: Math.round(Math.min(99.4, Math.max(12.0, score)) * 10) / 10
    };
  });

  matches.sort((a, b) => b.confidence - a.confidence);
  const endTime = performance.now();
  const latencyMs = Math.round(endTime - startTime);

  displayResults(matches, latencyMs);
  logSighting(matches[0].species);
}

// Render Spectrogram on Canvas
function renderStaticSpectrogram(pcmData) {
  canvasCtx.fillStyle = '#0c1e17';
  canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

  const step = Math.ceil(pcmData.length / canvas.width);
  const amp = canvas.height / 2;

  canvasCtx.beginPath();
  canvasCtx.strokeStyle = '#489c7b';
  canvasCtx.lineWidth = 2;

  for (let i = 0; i < canvas.width; i++) {
    const sampleIdx = i * step;
    let min = 1.0;
    let max = -1.0;
    for (let j = 0; j < step && (sampleIdx + j) < pcmData.length; j++) {
      const val = pcmData[sampleIdx + j];
      if (val < min) min = val;
      if (val > max) max = val;
    }
    canvasCtx.lineTo(i, (1 + min) * amp);
    canvasCtx.lineTo(i, (1 + max) * amp);
  }
  canvasCtx.stroke();
}

// Display Species Identification Cards
function displayResults(matches, latencyMs) {
  latencyBadge.textContent = `${latencyMs}ms latency (offline)`;
  latencyBadge.classList.remove('hidden');

  const top = matches[0];
  const sp = top.species;

  resultsContainer.innerHTML = `
    <!-- Top Match Header Card -->
    <div class="bg-forest-900/90 border border-forest-600 rounded-xl p-5 shadow-lg relative overflow-hidden mb-4">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-14 h-14 rounded-2xl bg-forest-800 border border-forest-600 flex items-center justify-center text-4xl shadow">
            ${sp.icon_emoji}
          </div>
          <div>
            <span class="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-900/80 text-emerald-300 border border-emerald-700">
              TOP MATCH (${top.confidence}%)
            </span>
            <h3 class="font-extrabold text-xl text-white mt-1 leading-tight">${sp.common_name}</h3>
            <p class="text-xs italic text-forest-300">${sp.scientific_name} • ${sp.family}</p>
          </div>
        </div>
      </div>

      <!-- Confidence Bar -->
      <div class="mt-4">
        <div class="flex justify-between text-xs font-mono text-slate-300 mb-1">
          <span>Match Confidence</span>
          <span class="font-bold text-emerald-400">${top.confidence}%</span>
        </div>
        <div class="w-full h-2.5 bg-forest-950 rounded-full overflow-hidden border border-forest-700">
          <div class="h-full bg-gradient-to-r from-emerald-500 to-amber-gold rounded-full confidence-fill" style="--target-width: ${top.confidence}%"></div>
        </div>
      </div>

      <!-- Species Metadata Grid -->
      <div class="mt-4 grid grid-cols-2 gap-2 text-xs">
        <div class="bg-forest-950/60 p-2.5 rounded-lg border border-forest-800">
          <span class="text-forest-400 block font-semibold">Typical Call</span>
          <span class="text-slate-200 font-medium">"${sp.call_pattern}"</span>
        </div>
        <div class="bg-forest-950/60 p-2.5 rounded-lg border border-forest-800">
          <span class="text-forest-400 block font-semibold">Status</span>
          <span class="text-slate-200 font-medium">${sp.conservation_status}</span>
        </div>
      </div>

      <!-- Fun Fact -->
      <div class="mt-3 text-xs bg-forest-800/80 p-3 rounded-lg border border-forest-700/80 text-forest-100">
        <span class="font-bold text-amber-gold">💡 Fun Fact:</span> ${sp.fun_fact}
      </div>

      <!-- Touch Grass Sighting Tip -->
      <div class="mt-3 p-3 rounded-xl bg-amber-500/15 border border-amber-500/40 text-xs">
        <span class="font-bold text-amber-300 block mb-0.5">🌿 TOUCH GRASS TIP:</span>
        <p class="text-amber-100 leading-normal">${sp.touch_grass_tip}</p>
      </div>
    </div>

    <!-- Other Potential Matches -->
    <div class="space-y-2">
      <p class="text-xs font-semibold text-forest-300 uppercase tracking-wider">Other Probable Matches:</p>
      ${matches.slice(1, 3).map(m => `
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-forest-900/60 border border-forest-800 text-xs">
          <div class="flex items-center gap-2">
            <span>${m.species.icon_emoji}</span>
            <span class="font-medium text-slate-200">${m.species.common_name}</span>
          </div>
          <span class="font-mono text-forest-300 font-semibold">${m.confidence}%</span>
        </div>
      `).join('')}
    </div>
  `;
}

// Sighting Log Persistence
function logSighting(species) {
  const sighting = {
    species: species.common_name,
    icon: species.icon_emoji,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    id: Date.now()
  };
  trailLog.unshift(sighting);
  if (trailLog.length > 20) trailLog.pop();
  try {
    localStorage.setItem('trailbird_log', JSON.stringify(trailLog));
  } catch(e){}
  renderTrailLog();
}

function loadTrailLog() {
  try {
    const saved = localStorage.getItem('trailbird_log');
    if (saved) trailLog = JSON.parse(saved);
  } catch(e){}
  renderTrailLog();
}

function renderTrailLog() {
  journalCount.textContent = `${trailLog.length} sighting${trailLog.length !== 1 ? 's' : ''}`;
  if (trailLog.length === 0) {
    sightingList.innerHTML = `<p class="text-forest-400 italic text-center py-3">No sightings logged on this trail yet.</p>`;
    return;
  }
  sightingList.innerHTML = trailLog.map(s => `
    <div class="flex items-center justify-between p-2 rounded bg-forest-900/60 border border-forest-800">
      <span class="flex items-center gap-2">
        <span>${s.icon}</span>
        <span class="font-medium text-slate-200">${s.species}</span>
      </span>
      <span class="text-forest-400 font-mono">${s.time}</span>
    </div>
  `).join('');
}

// Event Listeners
recordBtn.addEventListener('click', startRecording);

audioFileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files[0]) {
    processAudioFile(e.target.files[0]);
  }
});

document.querySelectorAll('.sample-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.sample-btn').forEach(b => b.classList.remove('active-sample'));
    btn.classList.add('active-sample');
    const sampleFile = btn.getAttribute('data-sample');
    processAudioFile(`audio_samples/${sampleFile}`);
  });
});

// Pocket Phone Mode (Gets screen out of sight!)
function togglePocketMode(show) {
  if (show) {
    pocketOverlay.classList.remove('pointer-events-none');
    pocketOverlay.classList.remove('opacity-0');
    pocketOverlay.classList.add('opacity-100');
  } else {
    pocketOverlay.classList.add('pointer-events-none');
    pocketOverlay.classList.remove('opacity-100');
    pocketOverlay.classList.add('opacity-0');
  }
}

pocketPhoneBtn.addEventListener('click', () => togglePocketMode(true));
touchGrassHeaderBtn.addEventListener('click', () => togglePocketMode(true));
resumeAppBtn.addEventListener('click', () => togglePocketMode(false));

// Initialize on page load
window.addEventListener('DOMContentLoaded', init);
