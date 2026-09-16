const revealItems = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.14 }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}

document.querySelectorAll(".mobile-menu a").forEach((link) => {
  link.addEventListener("click", () => {
    link.closest("details")?.removeAttribute("open");
  });
});

const copyStatus = document.querySelector("#copy-status");

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const value = button.dataset.copy;
    const originalLabel = button.textContent;

    try {
      await navigator.clipboard.writeText(value);
      button.textContent = "Kopirano";
      if (copyStatus) copyStatus.textContent = `Kopirana je naredba: ${value}`;
    } catch {
      const temporaryInput = document.createElement("textarea");
      temporaryInput.value = value;
      temporaryInput.setAttribute("readonly", "");
      temporaryInput.style.position = "fixed";
      temporaryInput.style.opacity = "0";
      document.body.appendChild(temporaryInput);
      temporaryInput.select();
      document.execCommand("copy");
      temporaryInput.remove();
      button.textContent = "Kopirano";
    }

    window.setTimeout(() => {
      button.textContent = originalLabel;
    }, 1800);
  });
});

const previewDialog = document.querySelector("#preview-dialog");
const dialogImage = document.querySelector("#dialog-image");
const dialogCaption = document.querySelector("#dialog-caption");

document.querySelectorAll("[data-preview]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!previewDialog || !dialogImage || !dialogCaption) return;
    dialogImage.src = button.dataset.preview;
    dialogImage.alt = button.dataset.caption;
    dialogCaption.textContent = button.dataset.caption;
    previewDialog.showModal();
  });
});

document.querySelector(".dialog-close")?.addEventListener("click", () => {
  previewDialog?.close();
});

previewDialog?.addEventListener("click", (event) => {
  if (event.target === previewDialog) previewDialog.close();
});

document.querySelector("#current-year").textContent = new Date().getFullYear();
