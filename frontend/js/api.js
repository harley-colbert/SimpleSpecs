document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("ping");
  if (!button) {
    return;
  }

  button.addEventListener("click", async () => {
    try {
      const response = await fetch("/healthz");
      const payload = await response.json();
      window.SimpleSpecsState.setHealth(payload);
    } catch (error) {
      window.SimpleSpecsState.setHealth({ error: String(error) });
    }
  });
});
