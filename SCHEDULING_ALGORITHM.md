# Google OR-Tools CP-SAT Production Scheduling Optimization

This document provides the mathematical formulation of the production scheduling optimization model implemented via **Google OR-Tools CP-SAT** (`ortools.sat.python.cp_model`).

---

## 1. Problem Formulation

Film production scheduling is a variant of the **Multi-Capacity Bin Packing Problem** and the **Vehicle Routing Problem with Pickup/Delivery**, where scenes must be packed into shooting days subject to non-linear constraints (continuous location clustering, daily hour limits, crew turnaround, and cast availability).

---

## 2. Mathematical Definition

### Sets and Indices
- $S = \{1, 2, \dots, N\}$: Set of scenes to be shot.
- $D = \{1, 2, \dots, M\}$: Set of candidate shooting days ($M \le N$).
- $L = \{l_1, l_2, \dots\}$: Set of distinct physical locations.
- $C = \{c_1, c_2, \dots\}$: Set of all speaking cast members.
- $L_s \in L$: The location of scene $s$.
- $C_s \subseteq C$: The subset of cast members required in scene $s$.
- $T_s$: Estimated shooting duration of scene $s$ (in minutes).
- $B$: Setup and changeover buffer per scene (default 30 minutes).
- $H_{\max}$: Maximum daily shooting limit (default 600 minutes = 10 hours).

---

### Decision Variables
1. **Scene Assignment Variable**:
   $$\text{scene\_day}[s, d] \in \{0, 1\} \quad \forall s \in S, d \in D$$
   Equals 1 if scene $s$ is scheduled on day $d$, and 0 otherwise.

2. **Day Active Variable**:
   $$\text{day\_active}[d] \in \{0, 1\} \quad \forall d \in D$$
   Equals 1 if day $d$ has at least one scene assigned, and 0 otherwise.

3. **Location Active Variable**:
   $$\text{loc\_on\_day}[l, d] \in \{0, 1\} \quad \forall l \in L, d \in D$$
   Equals 1 if location $l$ is utilized on day $d$.

4. **Cast Active Variable**:
   $$\text{cast\_on\_day}[c, d] \in \{0, 1\} \quad \forall c \in C, d \in D$$
   Equals 1 if actor $c$ is called to set on day $d$.

---

### Constraints

#### 1. Exact Assignment Constraint
Every scene must be shot exactly once:
$$\sum_{d \in D} \text{scene\_day}[s, d] = 1 \quad \forall s \in S$$

#### 2. Day Activation Linking
A day is active if any scene is assigned to it:
$$\text{scene\_day}[s, d] \le \text{day\_active}[d] \quad \forall s \in S, d \in D$$

#### 3. Symmetry Breaking (Consecutive Day Usage)
To avoid permutation symmetries in the solver search space, shooting days must be filled consecutively:
$$\text{day\_active}[d] \ge \text{day\_active}[d + 1] \quad \forall d \in \{1, \dots, M-1\}$$

#### 4. Maximum Daily Shooting Duration Constraint
The sum of scene durations plus turnaround buffer on any day $d$ cannot exceed $H_{\max}$:
$$\sum_{s \in S} (T_s + B) \cdot \text{scene\_day}[s, d] \le H_{\max} \cdot \text{day\_active}[d] \quad \forall d \in D$$

#### 5. Location Tracking Constraint
If scene $s$ at location $L_s$ is assigned to day $d$, then that location is active on day $d$:
$$\text{loc\_on\_day}[L_s, d] \ge \text{scene\_day}[s, d] \quad \forall s \in S, d \in D$$

#### 6. Cast Working Day Tracking Constraint
If actor $c$ appears in scene $s$ on day $d$, that actor must be called on day $d$:
$$\text{cast\_on\_day}[c, d] \ge \text{scene\_day}[s, d] \quad \forall s \in S, c \in C_s, d \in D$$

---

## 3. Objective Function

The objective is to minimize a multi-criteria weighted cost function:

$$\min \left( W_{\text{days}} \sum_{d \in D} \text{day\_active}[d] + W_{\text{loc}} \sum_{l \in L} \sum_{d \in D} \text{loc\_on\_day}[l, d] + W_{\text{cast}} \sum_{c \in C} \sum_{d \in D} \text{cast\_on\_day}[c, d] \right)$$

Where the priority weights are defined as:
- $W_{\text{days}} = 1000$: **Primary Objective** — Minimizing total shooting days reduces overall crew rental and stage overhead.
- $W_{\text{loc}} = 100$: **Secondary Objective** — Clumping scenes at the same location eliminates costly company moves.
- $W_{\text{cast}} = 10$: **Tertiary Objective** — Minimizing cast call days reduces standby holding fees and actor travel.

---

## 4. Post-Optimization Sequencing

Once CP-SAT returns optimal day assignments:
1. Within each shooting day, scenes are sequenced to group identical sets consecutively.
2. Day exterior/interior scenes are placed first, and Night scenes are placed last to align with natural lighting.
3. Start times, company move buffers (45 minutes per move), courtesy lunch breaks (after 4-5 hours), and wrap times are calculated deterministically.
