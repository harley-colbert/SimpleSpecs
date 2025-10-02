(function () {
  const state = {
    lastHealth: null,
  };

  window.SimpleSpecsState = {
    get() {
      return state;
    },
    setHealth(payload) {
      state.lastHealth = payload;
      const output = document.getElementById("output");
      if (output) {
        output.textContent = JSON.stringify(payload, null, 2);
      }
    },
  };
})();
