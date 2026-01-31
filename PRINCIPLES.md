# 🧠 Project Principles

**The foundation of how we build and maintain ClusterML**

---

## Why These Principles Matter

To keep ClusterML **healthy**, **maintainable**, and **enjoyable** to work on, we follow a few simple rules.

These rules exist to prevent the project from becoming complex, fragile, or abandoned halfway.

> 💡 **Every contributor should read and follow these principles.**

---

## 🔥 Rule #1: No Feature Without Documentation

If you add or change a feature, **update the relevant documentation** in `docs/`.

Code without docs is considered **incomplete**.

Documentation ensures:
- New contributors can understand features
- Users can learn how to use them
- Maintainers can remember decisions

---

## 🧩 Rule #2: Every Module Must Run Independently

Each major component should be **runnable and testable on its own**:
- `master/`
- `worker/`
- `cli/`
- `sdk/`
- `dashboard/`

Avoiding tight coupling:
- Makes debugging easier
- Enables parallel development
- Simplifies testing

---

## 💻 Rule #3: CLI and SDK Are First-Class Citizens

Anything that can be done internally should be accessible via:
- The Terminal CLI
- The Python SDK

This keeps ClusterML **developer-friendly**:
- Automation becomes possible
- Scripting is easy
- No GUI dependency

---

## 📈 Rule #4: Start Single-Node, Then Scale

All features should work correctly on a **single machine** before being extended to multi-node or distributed setups.

This approach:
- Catches bugs early
- Simplifies development
- Ensures core logic works

---

## 🎯 The Goal

Following these principles helps us build a **reliable system** without unnecessary complexity.

**Simple. Modular. Developer-First.**

<div align="center">

**Simple. Modular. Developer-First.**

</div>
