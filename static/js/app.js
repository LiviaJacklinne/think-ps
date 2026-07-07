document.querySelectorAll("[data-sidebar-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const shell = button.closest(".dashboard-shell");

    if (!shell) {
      return;
    }

    const isMobile = window.matchMedia("(max-width: 860px)").matches;

    if (isMobile) {
      const isOpen = shell.classList.toggle("sidebar-open");
      button.setAttribute("aria-expanded", String(isOpen));
      return;
    }

    const isClosed = shell.classList.toggle("sidebar-collapsed");
    button.setAttribute("aria-expanded", String(!isClosed));
  });
});

document.querySelectorAll("[data-profile-edit]").forEach((button) => {
  button.addEventListener("click", () => {
    const panel = button.closest(".profile-panel");

    if (!panel) {
      return;
    }

    panel.querySelectorAll("[data-profile-field]").forEach((field) => {
      field.removeAttribute("readonly");
    });

    const saveButton = panel.querySelector("[data-profile-save]");

    if (saveButton) {
      saveButton.hidden = false;
    }

    const firstField = panel.querySelector("[data-profile-field]");

    if (firstField) {
      firstField.focus();
    }
  });
});

document.querySelectorAll(".messages").forEach((toast) => {
  window.setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-8px)";
    toast.style.transition = "opacity 180ms ease, transform 180ms ease";

    window.setTimeout(() => {
      toast.remove();
    }, 220);
  }, 3200);
});
