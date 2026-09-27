const controls = {
  projectName: document.querySelector("#projectName"),
  baseRate: document.querySelector("#baseRate"),
  preparation: document.querySelector("#preparation"),
  resources: document.querySelector("#resources"),
  complexity: document.querySelector("#complexity"),
  volatility: document.querySelector("#volatility"),
  dependency: document.querySelector("#dependency"),
  attempts: document.querySelector("#attempts"),
  impact: document.querySelector("#impact"),
  confidence: document.querySelector("#confidence"),
};

const defaults = {
  projectName: "Nowe przedsięwzięcie",
  baseRate: 50,
  preparation: 65,
  resources: 60,
  complexity: 45,
  volatility: 35,
  dependency: 85,
  attempts: 1,
  impact: 2,
  confidence: 0.75,
};

const ui = {
  resultProjectName: document.querySelector("#resultProjectName"),
  probability: document.querySelector("#probability"),
  gaugeProgress: document.querySelector("#gaugeProgress"),
  riskBadge: document.querySelector("#riskBadge"),
  verdictTitle: document.querySelector("#verdictTitle"),
  verdictText: document.querySelector("#verdictText"),
  interval: document.querySelector("#interval"),
  singleRisk: document.querySelector("#singleRisk"),
  expectedLoss: document.querySelector("#expectedLoss"),
  factorChart: document.querySelector("#factorChart"),
  recommendation: document.querySelector("#recommendation"),
};

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
const logistic = (value) => 1 / (1 + Math.exp(-value));
const logit = (probability) => Math.log(probability / (1 - probability));

// Deterministyczny generator pozwala porównywać scenariusze bez migotania wyniku.
function mulberry32(seed) {
  return function random() {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function gaussian(random) {
  const u = Math.max(random(), Number.EPSILON);
  const v = Math.max(random(), Number.EPSILON);
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}

function readValues() {
  return {
    projectName: controls.projectName.value.trim() || "Bez nazwy",
    baseRate: clamp(Number(controls.baseRate.value), 1, 99),
    preparation: clamp(Number(controls.preparation.value), 0, 100),
    resources: clamp(Number(controls.resources.value), 0, 100),
    complexity: clamp(Number(controls.complexity.value), 0, 100),
    volatility: clamp(Number(controls.volatility.value), 0, 100),
    dependency: clamp(Number(controls.dependency.value) || 1, 1, 100),
    attempts: clamp(Math.round(Number(controls.attempts.value) || 1), 1, 50),
    impact: clamp(Number(controls.impact.value), 1, 4),
    confidence: clamp(Number(controls.confidence.value), 0.5, 1),
  };
}

function chanceFor(values, noise = 0) {
  const base = logit(values.baseRate / 100);
  const preparationEffect = ((values.preparation - 50) / 50) * 0.95;
  const resourceEffect = ((values.resources - 50) / 50) * 0.7;
  const complexityEffect = ((values.complexity - 50) / 50) * -0.85;
  const volatilityEffect = ((values.volatility - 50) / 50) * -0.6;
  const singleBeforeDependency = logistic(
    base + preparationEffect + resourceEffect + complexityEffect + volatilityEffect + noise,
  );
  const single = singleBeforeDependency * (values.dependency / 100);
  return {
    single,
    total: 1 - Math.pow(1 - single, values.attempts),
  };
}

function simulate(values) {
  const random = mulberry32(74291);
  const spread = 0.12 + (values.volatility / 100) * 0.48 + (1 - values.confidence) * 0.72;
  const outcomes = new Array(10000);
  for (let i = 0; i < outcomes.length; i += 1) {
    outcomes[i] = chanceFor(values, gaussian(random) * spread).total;
  }
  outcomes.sort((a, b) => a - b);
  const mean = outcomes.reduce((sum, value) => sum + value, 0) / outcomes.length;
  return {
    mean,
    low: outcomes[1000],
    high: outcomes[8999],
  };
}

function classify(probability, impact) {
  const failure = 1 - probability;
  const exposure = failure * impact;
  if (exposure >= 2.2) return { label: "RYZYKO KRYTYCZNE", title: "Najpierw ogranicz straty", color: "#bc4b3f" };
  if (exposure >= 1.25) return { label: "RYZYKO WYSOKIE", title: "Potrzebny plan awaryjny", color: "#d26a3d" };
  if (exposure >= 0.55) return { label: "RYZYKO UMIARKOWANE", title: "Warunki są obiecujące", color: "#b29525" };
  return { label: "RYZYKO KONTROLOWANE", title: "Silny scenariusz działania", color: "#26735f" };
}

function calculateFactors(values, currentProbability) {
  const candidates = [
    { key: "preparation", name: "Przygotowanie", target: Math.min(100, values.preparation + 10), type: "positive" },
    { key: "resources", name: "Zasoby", target: Math.min(100, values.resources + 10), type: "positive" },
    { key: "complexity", name: "Mniejsza złożoność", target: Math.max(0, values.complexity - 10), type: "negative" },
    { key: "volatility", name: "Mniejsza zmienność", target: Math.max(0, values.volatility - 10), type: "negative" },
    { key: "dependency", name: "Niezawodność", target: Math.min(100, values.dependency + 10), type: "positive" },
  ];

  return candidates
    .map((candidate) => {
      const changed = { ...values, [candidate.key]: candidate.target };
      const gain = chanceFor(changed).total - currentProbability;
      return { ...candidate, gain };
    })
    .sort((a, b) => b.gain - a.gain);
}

function render() {
  const values = readValues();
  const deterministic = chanceFor(values);
  const simulation = simulate(values);
  const result = simulation.mean;
  const percent = Math.round(result * 100);
  const risk = classify(result, values.impact);
  const impactNames = ["", "niska", "średnia", "wysoka", "krytyczna"];

  Object.entries(controls).forEach(([key, element]) => {
    if (element.type === "range") {
      const output = document.querySelector(`#${key}Value`);
      if (output) output.textContent = key === "baseRate" ? `${element.value}%` : element.value;
      const fill = ((element.value - element.min) / (element.max - element.min)) * 100;
      element.style.setProperty("--fill", `${fill}%`);
    }
  });

  ui.resultProjectName.textContent = values.projectName;
  ui.probability.textContent = `${percent}%`;
  ui.gaugeProgress.style.strokeDasharray = `${percent} ${100 - percent}`;
  ui.gaugeProgress.style.stroke = risk.color;
  ui.riskBadge.textContent = risk.label;
  ui.riskBadge.style.color = risk.color;
  ui.riskBadge.style.background = `${risk.color}14`;
  ui.verdictTitle.textContent = risk.title;
  ui.verdictText.textContent = `Przy ${values.attempts === 1 ? "jednej próbie" : `${values.attempts} niezależnych próbach`} i ${impactNames[values.impact]} dotkliwości porażki model wskazuje ${risk.label.toLowerCase()}.`;
  ui.interval.textContent = `${Math.round(simulation.low * 100)}–${Math.round(simulation.high * 100)}%`;
  ui.singleRisk.textContent = `${Math.round((1 - deterministic.single) * 100)}%`;
  ui.expectedLoss.textContent = `${((1 - result) * values.impact * 25).toFixed(0)} / 100`;

  const factors = calculateFactors(values, deterministic.total);
  const maxGain = Math.max(...factors.map((factor) => factor.gain), 0.01);
  ui.factorChart.innerHTML = factors
    .map(
      (factor) => `
        <div class="factor-row">
          <span class="factor-name">${factor.name}</span>
          <div class="factor-track"><div class="factor-bar ${factor.type === "negative" ? "negative" : ""}" style="width:${Math.max(2, (factor.gain / maxGain) * 100)}%"></div></div>
          <span class="factor-value">+${(factor.gain * 100).toFixed(1)} pp</span>
        </div>`,
    )
    .join("");

  const best = factors[0];
  ui.recommendation.innerHTML = `<strong>Najsilniejsza dostępna dźwignia: ${best.name.toLowerCase()}.</strong> Zmiana tego parametru o 10 punktów podnosi szansę o około ${(best.gain * 100).toFixed(1)} punktu procentowego w tym modelu.`;
}

let renderTimer;
function queueRender() {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(render, 70);
}

Object.values(controls).forEach((control) => {
  control.addEventListener("input", queueRender);
  control.addEventListener("change", render);
});

document.querySelector("#resetButton").addEventListener("click", () => {
  Object.entries(defaults).forEach(([key, value]) => {
    controls[key].value = value;
  });
  render();
});

const methodDialog = document.querySelector("#methodDialog");
document.querySelector("#methodButton").addEventListener("click", () => methodDialog.showModal());
document.querySelector("#closeDialog").addEventListener("click", () => methodDialog.close());
methodDialog.addEventListener("click", (event) => {
  if (event.target === methodDialog) methodDialog.close();
});

render();
