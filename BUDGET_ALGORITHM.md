# Production Budgeting Algorithm & Financial Model

This document outlines the budgeting methodology, formula calculations, rate cards, and financial structures implemented in the budgeting engine.

---

## 1. Structure of Accounts

The chart of accounts reflects standard independent and studio film budgeting templates:

### Above-The-Line (ATL)
- **1100 Direction**: Director agreements across pre-production, principal photography, and post supervision.
- **1200 Producers**: Line producer, executive producers, production manager.
- **1300 Writing**: Screenplay rights acquisition, treatment, production revisions.
- **1400 Principal Cast**: Lead actors (day player rates based on SAG-AFTRA Modified Low Budget standards).
- **1410 Supporting Cast**: Day players, secondary speaking roles.

### Below-The-Line (BTL)
- **2000 Camera Department**: Director of Photography (DP), 1st AC, 2nd AC, digital utility.
- **2050 Camera Equipment**: Digital cinema camera packages (ARRI / RED), prime lenses, monitors.
- **2100 Lighting & Grip**: Gaffer, key grip, best boy electric, lighting packages.
- **2200 Sound**: Production sound mixer, boom operator, wireless lavalier kits.
- **2300 Art Department**: Production designer, art director, set dressing.
- **2350 Props**: Key hero props, weapons handling, practical effect dressing.
- **2400 Costume & Wardrobe**: Costume designer, wardrobe supervisor, fittings.
- **2500 Makeup & Hair**: Key makeup artist, prosthetic effects, continuity touch-ups.
- **2600 Locations**: Permits, site fees, security, cleaning, and restoration.
- **2700 Catering & Craft Service**: Daily breakfast, hot lunch, continuous craft service per headcount.
- **2800 Transportation**: Equipment trucks, cast passenger vans, fuel, mileage.
- **3100 Visual Effects (VFX)**: CGI composites, wire removal, muzzle flashes, holographic interfaces.
- **3200 Post-Production**: Picture editing, color grading, ADR, Foley, sound design, final mix.
- **3900 Insurance & Legal**: General liability, inland marine equipment coverage, workers comp.

---

## 2. Mathematical Calculations

For every line item $i$:
$$\text{Subtotal}_i = \text{Quantity}_i \times \text{UnitRate}_i \times \text{Days}_i$$

The direct production subtotal is:
$$\text{Subtotal} = \sum_{i \in \text{Items}} \text{Subtotal}_i$$

The contingency buffer covers unexpected weather delays, camera equipment faults, or overtime:
$$\text{Contingency} = \text{Subtotal} \times R_{\text{contingency}} \quad (\text{Default } R_{\text{contingency}} = 0.10)$$

Taxes, municipal permitting fees, and state incentives are calculated as:
$$\text{Tax} = (\text{Subtotal} + \text{Contingency}) \times R_{\text{tax}} \quad (\text{Default } R_{\text{tax}} = 0.08)$$

The final budget grand total is:
$$\text{GrandTotal} = \text{Subtotal} + \text{Contingency} + \text{Tax}$$

---

## 3. Dynamic Scaling

When a screenplay is analyzed:
- $\text{Days}$ is automatically seeded from the **Google OR-Tools** optimal shooting days count.
- $\text{Cast Count}$ scales Above-the-Line day player items.
- $\text{Location Count}$ scales municipal permit items.
- Line items are fully interactive, enabling producers to override rates, quantities, and contingencies in real-time.
