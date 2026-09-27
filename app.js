const defaults = {
  investment: 100000,
  pessimistic: 70000,
  likely: 140000,
  optimistic: 240000,
  riskCount: 3,
};

const form = document.querySelector("#riskForm");
const resultsColumn = document.querySelector("#resultsColumn");
const submitButton = document.querySelector("#submitButton");
const formError = document.querySelector("#formError");

const fields = {
  investment: document.querySelector("#investment"),
  pessimistic: document.querySelector("#pessimistic"),
  likely: document.querySelector("#likely"),
  optimistic: document.querySelector("#optimistic"),
  riskCount: document.querySelector("#riskCount"),
};

const ui = {
  probability: document.querySelector("#probability"),
  gaugeProgress: document.querySelector("#gaugeProgress"),
  trafficLight: document.querySelector("#trafficLight"),
  verdictTitle: document.querySelector("#verdictTitle"),
  verdictText: document.querySelector("#verdictText"),
  expectedResult: document.querySelector("#expectedResult"),
  safeFloor: document.querySelector("#safeFloor"),
  realCeiling: document.querySelector("#realCeiling"),
  complexityCard: document.querySelector("#complexityCard"),
  ockhamTitle: document.querySelector("#ockhamTitle"),
  ockhamIcon: document.querySelector("#ockhamIcon"),
  ockhamText: document.querySelector("#ockhamText"),
  complexityPenalty: document.querySelector("#complexityPenalty"),
  penaltyFormula: document.querySelector("#penaltyFormula"),
};

const moneyFormatter = new Intl.NumberFormat("pl-PL", {
  style: "currency",
  currency: "PLN",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const percentFormatter = new Intl.NumberFormat("pl-PL", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

function readInput() {
  const values = Object.fromEntries(
    Object.entries(fields).map(([key, field]) => [key, Number(field.value)]),
  );

  if (Object.values(values).some((value) => !Number.isFinite(value))) {
    throw new Error("Wszystkie pola muszą zawierać poprawne liczby.");
  }
  if (values.investment < 0) {
    throw new Error("Początkowa inwestycja nie może być ujemna.");
  }
  if (!Number.isInteger(values.riskCount) || values.riskCount < 0) {
    throw new Error("Liczba ryzyk musi być nieujemną liczbą całkowitą.");
  }
  if (!(values.pessimistic <= values.likely && values.likely <= values.optimistic)) {
    throw new Error("Scenariusze muszą rosnąć: pesymistyczny ≤ prawdopodobny ≤ optymistyczny.");
  }

  return {
    inwestycja: values.investment,
    pesymistyczny: values.pessimistic,
    prawdopodobny: values.likely,
    optymistyczny: values.optimistic,
    liczba_ryzyk: values.riskCount,
  };
}

function setLoading(isLoading) {
  resultsColumn.setAttribute("aria-busy", String(isLoading));
  submitButton.disabled = isLoading;
  submitButton.classList.toggle("is-loading", isLoading);
  submitButton.querySelector(".button-label").textContent = isLoading
    ? "Symulacja w toku…"
    : "Uruchom 10 000 symulacji";
}

function showError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

function clearError() {
  formError.hidden = true;
  formError.textContent = "";
}

function lightConfig(light) {
  const configurations = {
    ZIELONE: {
      color: "#26735f",
      title: "Decyzja ma mocne podstawy",
      description: "Więcej niż 75% symulacji kończy się dodatnim wynikiem po uwzględnieniu kosztu złożoności.",
    },
    ŻÓŁTE: {
      color: "#b29525",
      title: "Potrzebna jest ostrożność",
      description: "Od 50% do 75% symulacji kończy się dodatnio. Warto zmniejszyć inwestycję lub ograniczyć zależności.",
    },
    CZERWONE: {
      color: "#bc4b3f",
      title: "Ryzyko dominuje nad szansą",
      description: "Mniej niż połowa symulacji przynosi dodatni wynik. Założenia wymagają istotnej zmiany.",
    },
  };
  return configurations[light] || configurations.CZERWONE;
}

function renderResult(result, input) {
  const probability = result.prawdopodobienstwo_sukcesu;
  const config = lightConfig(result.swiatlo);
  const roundedProbability = Math.max(0, Math.min(100, probability));

  ui.probability.textContent = `${percentFormatter.format(probability)}%`;
  ui.gaugeProgress.style.strokeDasharray = `${roundedProbability} ${100 - roundedProbability}`;
  ui.gaugeProgress.style.stroke = config.color;

  ui.trafficLight.textContent = `ŚWIATŁO ${result.swiatlo}`;
  ui.trafficLight.style.color = config.color;
  ui.trafficLight.style.background = `${config.color}14`;
  ui.verdictTitle.textContent = config.title;
  ui.verdictText.textContent = config.description;

  ui.expectedResult.textContent = moneyFormatter.format(result.sredni_wynik_netto);
  ui.safeFloor.textContent = moneyFormatter.format(result.bezpieczny_dol);
  ui.realCeiling.textContent = moneyFormatter.format(result.realny_sufit);

  const isComplex = input.liczba_ryzyk > 3;
  ui.complexityCard.classList.toggle("is-complex", isComplex);
  ui.ockhamIcon.textContent = isComplex ? "!" : "✓";
  ui.ockhamTitle.textContent = isComplex ? "Plan jest zbyt skomplikowany" : "Plan zachowuje prostotę";
  ui.ockhamText.textContent = isComplex
    ? `Wykryto ${input.liczba_ryzyk} zewnętrznych zależności. Ograniczenie ich liczby zmniejszy ukryty koszt i przestrzeń możliwych awarii.`
    : `Plan ma ${input.liczba_ryzyk} ${input.liczba_ryzyk === 1 ? "zewnętrzną zależność" : "zewnętrzne zależności"}, więc mieści się w przyjętym limicie prostoty.`;
  ui.complexityPenalty.textContent = `−${moneyFormatter.format(result.koszt_skomplikowania)}`;
  ui.penaltyFormula.textContent = `${input.liczba_ryzyk} × 5% × ${moneyFormatter.format(input.inwestycja)}`;
}

async function runSimulation(event) {
  event?.preventDefault();
  clearError();

  let input;
  try {
    input = readInput();
  } catch (error) {
    showError(error.message);
    return;
  }

  setLoading(true);
  try {
    const response = await fetch("/api/symulacja", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || "Silnik symulacji zwrócił błąd.");
    }
    renderResult(payload, input);
  } catch (error) {
    showError(
      error instanceof TypeError
        ? "Nie udało się połączyć z silnikiem Python. Uruchom aplikację przez serwer lokalny lub Vercel."
        : error.message,
    );
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", runSimulation);

document.querySelector("#resetButton").addEventListener("click", () => {
  Object.entries(defaults).forEach(([key, value]) => {
    fields[key].value = value;
  });
  runSimulation();
});

const methodDialog = document.querySelector("#methodDialog");
document.querySelector("#methodButton").addEventListener("click", () => methodDialog.showModal());
document.querySelector("#closeDialog").addEventListener("click", () => methodDialog.close());
methodDialog.addEventListener("click", (event) => {
  if (event.target === methodDialog) methodDialog.close();
});

runSimulation();
