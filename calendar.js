const hostMap = {};
const holidayMap = {};
let currentYear, currentMonth;
let latestTerm = [];
let latestPeriodLabel = "";

async function init() {
  const today = new Date();
  currentYear = today.getFullYear();
  currentMonth = today.getMonth();

  try {
    const manifest = await fetch("periods.json").then((r) => r.json());

    const fetches = [
      ...manifest.periods.map((p) =>
        fetch(`data/hosts_${p}.json`)
          .then((r) => r.json())
          .then((data) => ({ kind: "hosts", data, period: p }))
      ),
      ...manifest.holiday_years.map((y) =>
        fetch(`data/holidays_${y}.json`)
          .then((r) => r.json())
          .then((data) => ({ kind: "holidays", data, period: y }))
      ),
    ];

    const results = await Promise.all(fetches);
    const latestPeriod = manifest.periods[manifest.periods.length - 1];

    for (const { kind, data, period } of results) {
      for (const entry of data) {
        const isHoliday = !entry.email;
        for (const dateStr of entry.hostdate) {
          if (isHoliday) {
            holidayMap[dateStr] = entry.name;
          } else {
            hostMap[dateStr] = entry.name;
          }
        }
      }

      if (kind === "hosts" && period === latestPeriod) {
        const [year, termNum] = latestPeriod.split("_");
        latestTerm = data
          .filter((entry) => entry.email)
          .map((entry) => ({
            name: entry.name,
            dates: [...entry.hostdate].sort(),
          }))
          .sort((a, b) => a.name.localeCompare(b.name));
        latestPeriodLabel = `Term ${termNum} ${year}`;
      }
    }

    renderLatestAssignments();
    renderCalendar();
  } catch (e) {
    document.getElementById("loading").textContent =
      "Failed to load calendar data.";
  }
}

function formatDate(d) {
  return (
    d.getFullYear() +
    "-" +
    String(d.getMonth() + 1).padStart(2, "0") +
    "-" +
    String(d.getDate()).padStart(2, "0")
  );
}

function formatLongDate(dateStr) {
  const date = new Date(`${dateStr}T00:00:00`);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function renderLatestAssignments() {
  const label = document.getElementById("latest-term-label");
  const count = document.getElementById("latest-term-count");
  const list = document.getElementById("latest-term-list");

  if (!label || !count || !list) return;

  label.textContent = latestPeriodLabel ? `Period ${latestPeriodLabel}` : "";
  count.textContent = latestTerm.length ? `${latestTerm.length} hosts` : "";
  list.innerHTML = "";

  if (!latestTerm.length) {
    const empty = document.createElement("div");
    empty.className = "term-panel-empty";
    empty.textContent = "No assignment data found for the latest term.";
    list.appendChild(empty);
    return;
  }

  for (const person of latestTerm) {
    const item = document.createElement("div");
    item.className = "term-panel-item";

    const name = document.createElement("div");
    name.className = "term-panel-name";
    name.textContent = person.name;

    const dates = document.createElement("div");
    dates.className = "term-panel-dates";
    for (const dateStr of person.dates) {
      const pill = document.createElement("span");
      pill.className = "term-date-pill";
      pill.textContent = formatLongDate(dateStr);
      dates.appendChild(pill);
    }

    item.appendChild(name);
    item.appendChild(dates);
    list.appendChild(item);
  }
}

function renderCalendar() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayStr = formatDate(today);

  document.getElementById("month-label").textContent = new Date(
    currentYear,
    currentMonth,
    1
  ).toLocaleDateString("en-US", { month: "long", year: "numeric" });

  const firstDow = new Date(currentYear, currentMonth, 1).getDay();
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  const grid = document.getElementById("calendar-grid");
  grid.innerHTML = "";

  for (const label of ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]) {
    const dow = document.createElement("div");
    dow.className = "cal-dow";
    dow.textContent = label;
    grid.appendChild(dow);
  }

  for (let i = 0; i < firstDow; i++) {
    const cell = document.createElement("div");
    cell.className = "cal-cell cal-empty";
    grid.appendChild(cell);
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const date = new Date(currentYear, currentMonth, d);
    date.setHours(0, 0, 0, 0);
    const dateStr = formatDate(date);
    const dow = date.getDay();
    const isWeekend = dow === 0 || dow === 6;
    const isPast = date < today;
    const isToday = dateStr === todayStr;

    const cell = document.createElement("div");
    cell.className = "cal-cell";
    if (isWeekend) cell.classList.add("cal-weekend");
    if (isPast) cell.classList.add("cal-past");
    if (isToday) cell.classList.add("cal-today");

    const dateNum = document.createElement("span");
    dateNum.className = "cal-date-num";
    dateNum.textContent = d;
    cell.appendChild(dateNum);

    if (!isWeekend) {
      if (hostMap[dateStr]) {
        const host = document.createElement("span");
        host.className = "cal-host";
        host.textContent = hostMap[dateStr];
        cell.appendChild(host);
      } else if (holidayMap[dateStr]) {
        const hol = document.createElement("span");
        hol.className = "cal-holiday";
        hol.textContent = holidayMap[dateStr];
        cell.appendChild(hol);
      } else {
        const unassigned = document.createElement("span");
        unassigned.className = "cal-unassigned";
        unassigned.textContent = "Unassigned";
        cell.appendChild(unassigned);
      }
    }

    grid.appendChild(cell);
  }

  document.getElementById("loading").style.display = "none";
  document.getElementById("calendar-wrap").style.display = "flex";
}

document.getElementById("prev-month").onclick = () => {
  currentMonth--;
  if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  }
  renderCalendar();
};

document.getElementById("next-month").onclick = () => {
  currentMonth++;
  if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  }
  renderCalendar();
};

document.getElementById("today-btn").onclick = () => {
  const today = new Date();
  currentYear = today.getFullYear();
  currentMonth = today.getMonth();
  renderCalendar();
};

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowLeft") document.getElementById("prev-month").click();
  else if (e.key === "ArrowRight") document.getElementById("next-month").click();
});

init();
