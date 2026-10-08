const API_BASE = "";


async function loadInfo() {
  try {
    const response = await fetch(`${API_BASE}/api/info`);
    const data = await response.json();

    document.getElementById("backend-pod").textContent =
      data.pod;

    document.getElementById("environment").textContent =
      data.environment;

    document.getElementById("api-key").textContent =
      data.secret.value;

  } catch (error) {
    showError(error);
  }
}


async function writeData() {
  try {
    clearError();

    const message =
      document.getElementById("message").value;

    const response = await fetch(`${API_BASE}/api/data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    await readData();

  } catch (error) {
    showError(error);
  }
}


async function readData() {
  try {
    clearError();

    const response =
      await fetch(`${API_BASE}/api/data`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    document.getElementById("data-message").textContent =
      data.message;

    document.getElementById("written-by").textContent =
      data.written_by;

    document.getElementById("read-by").textContent =
      data.read_by;

  } catch (error) {
    showError(error);
  }
}


function showError(error) {
  document.getElementById("error").textContent =
    `Error: ${error.message}`;
}


function clearError() {
  document.getElementById("error").textContent = "";
}


loadInfo();