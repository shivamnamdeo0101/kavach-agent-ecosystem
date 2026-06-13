const navToggle = document.querySelector(".nav-toggle");
const siteMenu = document.querySelector(".site-menu");
const menuLinks = document.querySelectorAll(".site-menu a");
const revealItems = document.querySelectorAll(".reveal");
const sections = document.querySelectorAll("main section[id]");
const ruleButtons = document.querySelectorAll(".rule-tile");
const ruleTitle = document.querySelector("#rule-title");
const ruleStatus = document.querySelector("#rule-status");
const ruleCopy = document.querySelector("#rule-copy");
const copyButton = document.querySelector(".copy-code");
const codeBlock = document.querySelector(".code-window code");

const ruleDetails = {
  prompt: {
    title: "Prompt Injection",
    status: "High confidence block",
    copy: "Detects attempts to override system instructions, reveal hidden context, or redirect tool calls through malicious natural language."
  },
  exfiltration: {
    title: "Data Exfiltration",
    status: "Outbound payload denied",
    copy: "Flags requests that try to move protected context, internal files, or customer data into untrusted destinations."
  },
  secrets: {
    title: "Secret Exposure",
    status: "Credential masked",
    copy: "Finds API keys, tokens, passwords, and private configuration values before they enter logs or external tools."
  },
  pii: {
    title: "PII Leakage",
    status: "Sensitive fields redacted",
    copy: "Masks personal identifiers such as email addresses, phone numbers, access IDs, and user-specific metadata."
  },
  sql: {
    title: "SQL Injection",
    status: "Query intent reviewed",
    copy: "Catches suspicious query fragments, destructive statements, and agent-generated database actions that violate policy."
  },
  execution: {
    title: "Dangerous Execution",
    status: "Execution requires policy approval",
    copy: "Stops shell commands, file writes, package installs, and other high-impact actions unless explicitly allowed."
  }
};

function closeMenu() {
  siteMenu.classList.remove("open");
  navToggle.setAttribute("aria-expanded", "false");
  navToggle.setAttribute("aria-label", "Open menu");
}

navToggle.addEventListener("click", () => {
  const isOpen = siteMenu.classList.toggle("open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
  navToggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
});

menuLinks.forEach((link) => {
  link.addEventListener("click", closeMenu);
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
      revealObserver.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.14
});

revealItems.forEach((item, index) => {
  item.style.transitionDelay = `${Math.min(index * 35, 220)}ms`;
  revealObserver.observe(item);
});

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) {
      return;
    }

    const activeLink = document.querySelector(`.site-menu a[href="#${entry.target.id}"]`);
    menuLinks.forEach((link) => link.classList.remove("active"));

    if (activeLink) {
      activeLink.classList.add("active");
    }
  });
}, {
  rootMargin: "-35% 0px -55% 0px",
  threshold: 0
});

sections.forEach((section) => sectionObserver.observe(section));

ruleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const detail = ruleDetails[button.dataset.rule];

    if (!detail) {
      return;
    }

    ruleButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    ruleTitle.textContent = detail.title;
    ruleStatus.textContent = detail.status;
    ruleCopy.textContent = detail.copy;
  });
});

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(codeBlock.textContent.trim());
    copyButton.textContent = "Copied";
    window.setTimeout(() => {
      copyButton.textContent = "Copy";
    }, 1600);
  } catch {
    copyButton.textContent = "Select";
  }
});
