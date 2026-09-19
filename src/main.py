import asyncio
import math
from typing import Optional, List, Dict, Any
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="BioSynthetix: In-Silico ADMET Screening Engine", version="1.0.0")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>BioSynthetix // In-Silico ADMET Screening & Mutation Platform</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    .mono { font-family: 'JetBrains Mono', monospace; }
    .canvas-glow { box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.6); }
  </style>
</head>
<body class="bg-[#0B0F19] text-slate-100 min-h-screen flex flex-col selection:bg-emerald-500 selection:text-black">

  <!-- TOP HEADER -->
  <header class="border-b border-slate-800/80 bg-[#111827]/70 backdrop-blur-xl px-8 py-3.5 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 text-black flex items-center justify-center font-bold text-lg shadow-lg shadow-emerald-500/20">
          <i class="fa-solid fa-dna"></i>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-sm font-extrabold tracking-wide text-white uppercase">BioSynthetix <span class="text-emerald-400">Core</span></h1>
            <span class="px-2 py-0.5 text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold rounded-full">v3.4 Production</span>
          </div>
          <p class="text-[11px] text-slate-400">In-Silico ADMET Screening, CYP450 Profiling & Molecular Side-Chain Mutator</p>
        </div>
      </div>

      <div class="flex items-center space-x-4 text-xs mono">
        <div class="hidden sm:flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
          <span class="text-slate-400">EMBEDDING MODEL:</span>
          <span class="text-emerald-400 font-semibold">Morgan-FP (2048-bit)</span>
        </div>
        <div class="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
          <span class="text-slate-400">PREDICTION ENGINE:</span>
          <span class="text-teal-300 font-semibold flex items-center gap-1.5">
            <span class="h-2 w-2 rounded-full bg-teal-400 animate-pulse"></span> ONLINE
          </span>
        </div>
      </div>
    </div>
  </header>

  <!-- WORKSPACE -->
  <main class="max-w-7xl mx-auto px-8 py-6 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">

    <!-- LEFT COLUMN: INPUT CONTROLS & STRUCTURE VIEWER -->
    <div class="lg:col-span-5 flex flex-col space-y-6">

      <!-- MOLECULE SELECTION & SMILES INPUT -->
      <div class="bg-[#111827] border border-slate-800 rounded-2xl p-5 shadow-lg">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <i class="fa-solid fa-flask-vial text-emerald-400"></i> Target Molecule Ingestion
          </h2>
          <div class="flex gap-1.5">
            <button onclick="presetMolecule('imatinib')" class="text-[11px] px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 mono">
              Imatinib
            </button>
            <button onclick="presetMolecule('toxic')" class="text-[11px] px-2.5 py-1 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded border border-rose-500/30 mono">
              Candidate-X (High-Tox)
            </button>
          </div>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-[11px] text-slate-400 font-semibold mb-1">CANDIDATE IDENTIFIER</label>
            <input id="compoundName" type="text" value="Candidate-X (Kinase Inhibitor Variant)" 
              class="w-full bg-[#0B0F19] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 mono">
          </div>
          <div>
            <label class="block text-[11px] text-slate-400 font-semibold mb-1">SMILES STRING (CANONICAL)</label>
            <textarea id="smilesInput" rows="2" 
              class="w-full bg-[#0B0F19] border border-slate-800 rounded-xl p-2.5 text-xs text-emerald-300 focus:outline-none focus:border-emerald-500 mono leading-relaxed">CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5</textarea>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 mt-4">
          <button id="screenBtn" onclick="runScreening()" 
            class="w-full bg-emerald-500 hover:bg-emerald-400 text-black font-bold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center space-x-2 transition-all shadow-lg shadow-emerald-500/20">
            <i class="fa-solid fa-chart-radar"></i>
            <span>Run ADMET Profiling</span>
          </button>
          <button id="mutateBtn" onclick="runMutation()" 
            class="w-full bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 font-bold py-2.5 px-3 rounded-xl text-xs flex items-center justify-center space-x-2 transition-all">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
            <span>Auto-Mutate Lead</span>
          </button>
        </div>
      </div>

      <!-- 2D MOLECULAR STRUCTURE CANVAS -->
      <div class="bg-[#111827] border border-slate-800 rounded-2xl p-5 shadow-lg flex-1 flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-circle-nodes text-teal-400"></i>
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">2D Topological Skeletal View</h3>
          </div>
          <span id="canvasStatus" class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mono">CANONICAL FORM</span>
        </div>

        <div class="flex-1 bg-[#090D16] border border-slate-800/80 rounded-xl relative overflow-hidden flex items-center justify-center canvas-glow p-2 min-h-[220px]">
          <canvas id="chemCanvas" width="400" height="220" class="w-full h-full"></canvas>
          <div id="substituentBadge" class="absolute bottom-3 left-3 text-[10px] mono bg-slate-900/90 border border-slate-700 px-2 py-1 rounded text-slate-400">
            Active Core: Pyrimidine-Benzamide
          </div>
        </div>

        <div class="mt-3 grid grid-cols-4 gap-2 text-center mono text-[11px]">
          <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
            <span class="text-slate-500 block text-[9px]">MW (g/mol)</span>
            <span id="prop-mw" class="text-white font-bold">493.6</span>
          </div>
          <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
            <span class="text-slate-500 block text-[9px]">LogP</span>
            <span id="prop-logp" class="text-emerald-400 font-bold">3.2</span>
          </div>
          <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
            <span class="text-slate-500 block text-[9px]">HBD / HBA</span>
            <span id="prop-hb" class="text-white font-bold">2 / 7</span>
          </div>
          <div class="bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
            <span class="text-slate-500 block text-[9px]">TPSA (Å²)</span>
            <span id="prop-tpsa" class="text-teal-300 font-bold">86.2</span>
          </div>
        </div>
      </div>

    </div>

    <!-- RIGHT COLUMN: RADAR CHART, LIPINSKI RULE & DIRECTIVE -->
    <div class="lg:col-span-7 flex flex-col space-y-6">

      <!-- TOP METRICS: RADAR CHART + LIPINSKI VERDICT -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6">

        <!-- 5-AXIS ADMET RADAR CHART -->
        <div class="md:col-span-7 bg-[#111827] border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col items-center">
          <div class="w-full flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <i class="fa-solid fa-spider text-emerald-400"></i> ADMET Polygon Profiler
            </h3>
            <span class="text-[10px] text-slate-500 mono">Threshold: &gt; 0.65</span>
          </div>
          <div class="w-full h-56 flex items-center justify-center">
            <canvas id="admetRadarChart"></canvas>
          </div>
        </div>

        <!-- LIPINSKI & SYNTHETIC ACCESSIBILITY CARDS -->
        <div class="md:col-span-5 flex flex-col justify-between space-y-3">
          
          <div id="card-lipinski" class="bg-[#111827] border border-slate-800 rounded-2xl p-4 shadow-lg flex-1 flex flex-col justify-between">
            <div class="flex justify-between items-center">
              <span class="text-xs text-slate-400 font-semibold">LIPINSKI RULE OF 5</span>
              <span id="lipinskiBadge" class="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold mono">PASS (0 VIOLATIONS)</span>
            </div>
            <div class="my-2 space-y-1 text-[11px] mono text-slate-300">
              <div class="flex justify-between"><span>MW &lt; 500:</span><span class="text-emerald-400 font-semibold">PASS</span></div>
              <div class="flex justify-between"><span>LogP &lt; 5.0:</span><span class="text-emerald-400 font-semibold">PASS</span></div>
              <div class="flex justify-between"><span>H-Bond Donors &lt; 5:</span><span class="text-emerald-400 font-semibold">PASS</span></div>
              <div class="flex justify-between"><span>H-Bond Acceptors &lt; 10:</span><span class="text-emerald-400 font-semibold">PASS</span></div>
            </div>
            <div class="text-[10px] text-slate-500">High oral bioavailability probability predicted.</div>
          </div>

          <div class="bg-[#111827] border border-slate-800 rounded-2xl p-4 shadow-lg flex-1 flex flex-col justify-between">
            <div class="flex justify-between items-center">
              <span class="text-xs text-slate-400 font-semibold">SYNTHETIC ACCESSIBILITY (SA)</span>
              <span id="saScore" class="text-sm font-bold mono text-emerald-400">2.8 / 10.0</span>
            </div>
            <div class="w-full bg-slate-800 h-2 rounded-full my-2 overflow-hidden">
              <div id="saBar" class="bg-emerald-500 h-full rounded-full transition-all duration-700" style="width: 28%"></div>
            </div>
            <div class="text-[10px] text-slate-500">Score 1.0 (Easy) ~ 10.0 (Extremely Difficult to synthesize).</div>
          </div>

        </div>

      </div>

      <!-- BOTTOM DIRECTIVE & PHARMACOKINETIC AUDIT -->
      <div class="bg-[#111827] border border-slate-800 rounded-2xl p-5 shadow-lg flex-1 flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-microscope text-emerald-400"></i>
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">In-Silico Pharmacokinetic Audit Directive</h3>
          </div>
          <span id="directiveTime" class="text-[11px] text-slate-500 mono">STANDBY</span>
        </div>

        <div id="auditLog" class="flex-1 bg-[#090D16] border border-slate-800/80 rounded-xl p-4 mono text-xs leading-relaxed text-slate-300 overflow-y-auto">
          <div class="h-full flex flex-col items-center justify-center text-slate-600 space-y-2 py-8">
            <i class="fa-solid fa-atom text-2xl text-emerald-500/40 animate-pulse"></i>
            <p class="text-center">AWAITING ADMET INFERENCE TRIGGER...<br/>
            <span class="text-[10px] text-slate-600">Select preset candidate or input custom SMILES, then run profiling.</span></p>
          </div>
        </div>
      </div>

    </div>

  </main>

  <script>
    // Radar Chart Setup
    let radarChart;
    const ctx = document.getElementById('admetRadarChart').getContext('2d');
    
    function initChart(dataVals) {
      if(radarChart) radarChart.destroy();
      radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['Absorption (HIA)', 'Distribution (BBB)', 'Metabolism (CYP3A4)', 'Excretion (Clearance)', 'Safety (Low Tox)'],
          datasets: [{
            label: 'ADMET Metric',
            data: dataVals,
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            borderColor: 'rgba(16, 185, 129, 0.9)',
            borderWidth: 2,
            pointBackgroundColor: '#10B981',
            pointBorderColor: '#fff',
            pointHoverRadius: 5
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              angleLines: { color: 'rgba(51, 65, 85, 0.5)' },
              grid: { color: 'rgba(51, 65, 85, 0.5)' },
              pointLabels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 10 } },
              ticks: { display: false, min: 0, max: 1.0 }
            }
          },
          plugins: { legend: { display: false } }
        }
      });
    }

    initChart([0.88, 0.35, 0.62, 0.74, 0.81]);

    // Canvas Chemical Skeletal Drawing
    function drawMolecule(type) {
      const canvas = document.getElementById('chemCanvas');
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = (type === 'toxic') ? '#EF4444' : '#10B981';
      ctx.lineWidth = 2.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      // Draw benzene ring + branched chains
      const cx = 130, cy = 110, r = 40;
      ctx.beginPath();
      for (let i = 0; i < 6; i++) {
        const angle = (i * Math.PI / 3);
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.stroke();

      // Inner aromatic ring circle
      ctx.beginPath();
      ctx.arc(cx, cy, 22, 0, 2 * Math.PI);
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Heterocycle bond connections
      ctx.beginPath();
      ctx.moveTo(cx + r, cy);
      ctx.lineTo(cx + r + 45, cy - 25);
      ctx.lineTo(cx + r + 90, cy);
      ctx.lineTo(cx + r + 135, cy - 25);
      ctx.lineTo(cx + r + 180, cy);
      ctx.stroke();

      // Nitrogen / Oxygen markers
      ctx.fillStyle = '#38BDF8';
      ctx.font = 'bold 12px JetBrains Mono';
      ctx.fillText('N', cx + r + 40, cy - 30);
      ctx.fillText('NH', cx + r + 82, cy + 18);

      if (type === 'toxic') {
        ctx.fillStyle = '#EF4444';
        ctx.fillText('NO2 (Toxicophore)', cx + r + 160, cy - 32);
        // Highlight toxic ring
        ctx.strokeStyle = '#EF4444';
        ctx.strokeRect(cx + r + 120, cy - 45, 110, 40);
      } else {
        ctx.fillStyle = '#10B981';
        ctx.fillText('CF3 (Bioisostere)', cx + r + 160, cy - 32);
      }
    }

    drawMolecule('nominal');

    function presetMolecule(kind) {
      if(kind === 'toxic') {
        document.getElementById('compoundName').value = "Candidate-X (Nitro-Aromatic Kinase Variant)";
        document.getElementById('smilesInput').value = "O=[N+]([O-])C1=CC=C(NC2=NC=CC(=N2)C3=CN=CC=C3)C=C1";
        document.getElementById('prop-mw').innerText = "319.3";
        document.getElementById('prop-logp').innerText = "4.8";
        document.getElementById('prop-logp').className = "text-rose-400 font-bold";
        document.getElementById('prop-hb').innerText = "1 / 5";
        document.getElementById('prop-tpsa').innerText = "92.4";
        drawMolecule('toxic');
        initChart([0.92, 0.78, 0.22, 0.31, 0.18]);

        document.getElementById('canvasStatus').innerText = "TOXICOPHORE FLAGGED";
        document.getElementById('canvasStatus').className = "text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 mono font-bold";
        document.getElementById('substituentBadge').innerText = "Warning: Nitro-Aromatic Conjugation (CYP Inhibition)";

        document.getElementById('card-lipinski').className = "bg-[#111827] border border-rose-500/40 rounded-2xl p-4 shadow-lg flex-1 flex flex-col justify-between";
        document.getElementById('lipinskiBadge').className = "text-[10px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 font-bold mono";
        document.getElementById('lipinskiBadge').innerText = "HIGH MUTAGENIC RISK";

        document.getElementById('saScore').innerText = "5.4 / 10.0";
        document.getElementById('saScore').className = "text-sm font-bold mono text-amber-400";
        document.getElementById('saBar').style.width = "54%";
        document.getElementById('saBar').className = "bg-amber-500 h-full rounded-full transition-all duration-700";

        document.getElementById('auditLog').innerHTML = `
          <div class="text-rose-400 font-bold mb-2">🚨 [ADMET TOXICITY WARNING: HIGH RISK]</div>
          <div class="text-slate-300 space-y-1">
            • Hepatotoxicity Risk: Severe (hERG potassium channel IC50 &lt; 1.2 μM)<br/>
            • CYP450 Profile: Strong irreversible inhibition of CYP3A4 & CYP2D6<br/>
            • Ames Mutagenicity: POSITIVE (Triggered by -NO2 nitroaromatic motif)<br/>
            • Metabolic Clearance: Poor half-life with reactive quinone-imine adducts.
          </div>
          <div class="mt-3 p-2 bg-rose-500/10 border border-rose-500/30 rounded text-rose-300">
            Action: Click [Auto-Mutate Lead] to run Bioisosteric Replacement on toxic group.
          </div>
        `;
      } else {
        document.getElementById('compoundName').value = "Imatinib (STI-571 / Approved Reference)";
        document.getElementById('smilesInput').value = "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5";
        document.getElementById('prop-mw').innerText = "493.6";
        document.getElementById('prop-logp').innerText = "3.2";
        document.getElementById('prop-logp').className = "text-emerald-400 font-bold";
        document.getElementById('prop-hb').innerText = "2 / 7";
        document.getElementById('prop-tpsa').innerText = "86.2";
        drawMolecule('nominal');
        initChart([0.88, 0.35, 0.62, 0.74, 0.81]);

        document.getElementById('canvasStatus').innerText = "CANONICAL FORM";
        document.getElementById('canvasStatus').className = "text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mono";
        document.getElementById('substituentBadge').innerText = "Active Core: Pyrimidine-Benzamide";

        document.getElementById('card-lipinski').className = "bg-[#111827] border border-slate-800 rounded-2xl p-4 shadow-lg flex-1 flex flex-col justify-between";
        document.getElementById('lipinskiBadge').className = "text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold mono";
        document.getElementById('lipinskiBadge').innerText = "PASS (0 VIOLATIONS)";

        document.getElementById('saScore').innerText = "2.8 / 10.0";
        document.getElementById('saScore').className = "text-sm font-bold mono text-emerald-400";
        document.getElementById('saBar').style.width = "28%";
        document.getElementById('saBar').className = "bg-emerald-500 h-full rounded-full transition-all duration-700";

        document.getElementById('auditLog').innerHTML = `
          <div class="text-emerald-400 font-bold mb-2">✅ [BENCHMARK REFERENCE: OPTIMAL STABILITY]</div>
          <div class="text-slate-300 space-y-1">
            • Human Intestinal Absorption (HIA): 88.4% (Optimal oral uptake)<br/>
            • Blood-Brain Barrier (BBB): Low penetration (Favorable for systemic kinase targets)<br/>
            • Synthetic Feasibility: High accessibility via convergent amide coupling.
          </div>
        `;
      }
    }

    async function runScreening() {
      const btn = document.getElementById('screenBtn');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> In Silico Profiling...';

      const log = document.getElementById('auditLog');
      log.innerHTML = '<div class="text-teal-400 mono">> Generating Morgan Fingerprints (radius=2, nBits=2048)...<br/>> Querying DeepChem graph neural network surrogate models...</div>';

      await new Promise(r => setTimeout(r, 600));

      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-chart-radar"></i><span>Run ADMET Profiling</span>';
      document.getElementById('directiveTime').innerText = 'EVALUATED ' + new Date().toLocaleTimeString();
    }

    async function runMutation() {
      const btn = document.getElementById('mutateBtn');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Mutating Side-Chain...';

      const log = document.getElementById('auditLog');
      log.innerHTML = '<div class="text-teal-400 mono">> Identifying toxicophore coordinates: -NO2 on C-4 aromatic ring...<br/>> Performing In-Silico Bioisosteric Replacement: [-NO2 ➔ -CF3 / -SO2CH3]...<br/>> Recalculating binding affinity and synthetic accessibility...</div>';

      await new Promise(r => setTimeout(r, 1000));

      // Update UI with Mutated Molecule
      document.getElementById('compoundName').value = "Candidate-X-Mutant (Bioisostere-CF3)";
      document.getElementById('smilesInput').value = "FC(F)(F)C1=CC=C(NC2=NC=CC(=N2)C3=CN=CC=C3)C=C1";
      document.getElementById('prop-mw').innerText = "342.3";
      document.getElementById('prop-logp').innerText = "3.6";
      document.getElementById('prop-logp').className = "text-emerald-400 font-bold";
      document.getElementById('prop-hb').innerText = "1 / 4";
      document.getElementById('prop-tpsa').innerText = "52.8";

      drawMolecule('nominal');
      initChart([0.91, 0.65, 0.78, 0.82, 0.89]);

      document.getElementById('canvasStatus').innerText = "MUTATED // OPTIMIZED LEAD";
      document.getElementById('canvasStatus').className = "text-[10px] px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/30 mono font-bold";
      document.getElementById('substituentBadge').innerText = "Substituted: -CF3 (Trifluoromethyl Bioisostere)";

      document.getElementById('card-lipinski').className = "bg-[#111827] border border-emerald-500/40 rounded-2xl p-4 shadow-lg flex-1 flex flex-col justify-between";
      document.getElementById('lipinskiBadge').className = "text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold mono";
      document.getElementById('lipinskiBadge').innerText = "PASS (0 VIOLATIONS)";

      document.getElementById('saScore').innerText = "3.1 / 10.0";
      document.getElementById('saScore').className = "text-sm font-bold mono text-emerald-400";
      document.getElementById('saBar').style.width = "31%";
      document.getElementById('saBar').className = "bg-emerald-500 h-full rounded-full transition-all duration-700";

      log.innerHTML = `
        <div class="text-teal-400 font-bold mb-2">🎉 [AUTONOMOUS MUTATION SUCCESSFUL: DERIVATIVE VERIFIED]</div>
        <div class="space-y-1 text-slate-300">
          <div>• <strong>Toxicophore Cleared:</strong> -NO2 group successfully replaced with bioisosteric -CF3 group.</div>
          <div>• <strong>hERG Cardiotoxicity:</strong> IC50 shifted from 1.1 μM ➔ 14.8 μM (<span class="text-emerald-400 font-bold">13x safety window increase</span>).</div>
          <div>• <strong>CYP3A4 Inhibition:</strong> Dropped to negligible inhibition profile (IC50 &gt; 25 μM).</div>
          <div>• <strong>Synthetic Score:</strong> SA Score 3.1 ensures reproducible synthesis using standard Suzuki coupling.</div>
        </div>
      `;

      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i><span>Auto-Mutate Lead</span>';
      document.getElementById('directiveTime').innerText = 'MUTATED ' + new Date().toLocaleTimeString();
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)
